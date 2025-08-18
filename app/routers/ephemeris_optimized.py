"""Optimized ephemeris router with async operations and caching."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, ValidationError

from app.services.swe_optimized import swe_optimized_service
from app.services.places import places_service
from app.services.cache import cache_service
from app.models.requests import EphemerisRequest
from app.middleware.metrics import record_business_metric
from app.util.logging import get_logger, RequestLogger

logger = get_logger("ephemeris_optimized")

router = APIRouter(prefix="/v2/ephemeris", tags=["ephemeris"])


class EphemerisResponse(BaseModel):
    """Ephemeris response model."""
    timestamp: str
    planets: dict
    panchanga: dict
    precision: str
    cached: bool = False


async def validate_ephemeris_request(
    when_utc: Optional[str] = Query(None),
    when_local: Optional[str] = Query(None),
    place_id: Optional[str] = Query(None),
    planets: str = Query("Sun,Moon,Mercury,Venus,Mars,Jupiter,Saturn,Rahu,Ketu")
) -> EphemerisRequest:
    """Validate and parse ephemeris request."""
    try:
        return EphemerisRequest(
            when_utc=when_utc,
            when_local=when_local,
            place_id=place_id,
            planets=planets
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
async def get_ephemeris_optimized(
    request: EphemerisRequest = Depends(validate_ephemeris_request)
):
    """Get planetary positions and panchanga with optimizations."""
    with RequestLogger("ephemeris_optimized.get") as req_log:
        try:
            # Parse timestamp
            dt = await _parse_timestamp_async(request)
            
            # Parse planets list
            planet_list = [p.strip() for p in request.planets.split(",")]
            
            # Generate cache key
            cache_key = f"ephemeris:{dt.isoformat()}:{','.join(planet_list)}"
            
            # Try to get from cache first
            cached_result = await cache_service.get(cache_key)
            if cached_result:
                logger.info(f"Cache hit for ephemeris calculation: {cache_key}")
                record_business_metric("ephemeris_calculations", {"planets_count": len(planet_list)})
                return {**cached_result, "cached": True}
            
            # Calculate planetary positions with optimizations
            planet_data = await swe_optimized_service.calculate_planets_async(dt, planet_list)
            
            # Calculate panchanga
            panchanga_data = await swe_optimized_service.calculate_panchanga_async(dt, ["Sun", "Moon"])
            
            # Format response
            response = {
                "timestamp": dt.isoformat(),
                "planets": planet_data,
                "panchanga": panchanga_data,
                "precision": swe_optimized_service.precision,
                "cached": False
            }
            
            # Cache the result for 5 minutes
            await cache_service.set(cache_key, response, 300)
            
            # Record metrics
            record_business_metric("ephemeris_calculations", {"planets_count": len(planet_list)})
            
            return response
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid timestamp format: {e}")
        except Exception as e:
            logger.error(f"Ephemeris calculation failed: {type(e).__name__}: {e}")
            raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")


async def _parse_timestamp_async(request: EphemerisRequest) -> datetime:
    """Parse timestamp asynchronously with place resolution."""
    if request.when_utc:
        return datetime.fromisoformat(request.when_utc.replace('Z', '+00:00'))
    
    elif request.when_local and request.place_id:
        # Resolve place and convert to UTC
        place_info = await _resolve_place_async(request.place_id)
        timezone_id = place_info["timezone"]["timeZoneId"]
        
        import zoneinfo
        tz = zoneinfo.ZoneInfo(timezone_id)
        dt = datetime.fromisoformat(request.when_local).replace(tzinfo=tz)
        return dt.astimezone(zoneinfo.ZoneInfo("UTC"))
    
    else:
        raise ValueError("Either when_utc or both when_local and place_id must be provided")


async def _resolve_place_async(place_id: str) -> dict:
    """Resolve place asynchronously with caching."""
    cache_key = f"place:{place_id}"
    
    # Try cache first
    cached_place = await cache_service.get(cache_key)
    if cached_place:
        return cached_place
    
    # Resolve from service
    place_info = places_service.resolve_place(place_id)
    
    # Cache for 1 hour
    await cache_service.set(cache_key, place_info, 3600)
    
    return place_info


@router.get("/batch")
async def get_ephemeris_batch(
    timestamps: str = Query(..., description="Comma-separated ISO timestamps"),
    planets: str = Query("Sun,Moon", description="Comma-separated list of planets")
):
    """Get planetary positions for multiple timestamps efficiently."""
    with RequestLogger("ephemeris_optimized.batch") as req_log:
        try:
            # Parse timestamps
            timestamp_list = [ts.strip() for ts in timestamps.split(",")]
            dt_list = [datetime.fromisoformat(ts.replace('Z', '+00:00')) for ts in timestamp_list]
            
            # Parse planets
            planet_list = [p.strip() for p in planets.split(",")]
            
            # Calculate for all timestamps
            results = []
            for dt in dt_list:
                planet_data = await swe_optimized_service.calculate_planets_async(dt, planet_list)
                results.append({
                    "timestamp": dt.isoformat(),
                    "planets": planet_data
                })
            
            # Record metrics
            record_business_metric("ephemeris_calculations", {
                "planets_count": len(planet_list),
                "batch_size": len(dt_list)
            })
            
            return {
                "results": results,
                "count": len(results)
            }
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid timestamp format: {e}")
        except Exception as e:
            logger.error(f"Batch ephemeris calculation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance")
async def get_performance_stats():
    """Get performance statistics for ephemeris calculations."""
    try:
        # Get cache statistics
        cache_stats = {
            "enabled": cache_service.enabled,
            "redis_connected": cache_service.redis_client is not None
        }
        
        # Get SWE service stats
        swe_stats = {
            "initialized": swe_optimized_service.initialized,
            "precision": swe_optimized_service.precision,
            "cache_sizes": {
                "rasi_cache": swe_optimized_service._get_rasi_cached.cache_info(),
                "nakshatra_cache": swe_optimized_service._get_nakshatra_cached.cache_info(),
                "pada_cache": swe_optimized_service._get_pada_cached.cache_info()
            }
        }
        
        return {
            "cache": cache_stats,
            "swiss_ephemeris": swe_stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get performance stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-cache")
async def clear_ephemeris_cache():
    """Clear ephemeris-related caches."""
    try:
        # Clear SWE caches
        swe_optimized_service.clear_caches()
        
        # Clear Redis caches
        if cache_service.enabled:
            await cache_service.clear_pattern("ephemeris:*")
            await cache_service.clear_pattern("place:*")
        
        return {"message": "Caches cleared successfully"}
        
    except Exception as e:
        logger.error(f"Failed to clear caches: {e}")
        raise HTTPException(status_code=500, detail=str(e))
