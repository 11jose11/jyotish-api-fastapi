"""Ephemeris router for planetary calculations."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.swe import swe_service
from app.services.places import places_service
from app.services.panchanga import panchanga_service
from app.util.logging import get_logger, RequestLogger

logger = get_logger("ephemeris")

router = APIRouter(prefix="/v1/ephemeris", tags=["ephemeris"])


class EphemerisResponse(BaseModel):
    """Ephemeris response model."""
    timestamp: str
    planets: dict
    panchanga: dict
    precision: str


@router.get("/")
async def get_ephemeris(
    when_utc: Optional[str] = Query(None, description="ISO-8601 timestamp in UTC"),
    when_local: Optional[str] = Query(None, description="ISO-8601 timestamp without timezone"),
    place_id: Optional[str] = Query(None, description="Google Place ID for local time conversion"),
    planets: Optional[str] = Query("Sun,Moon,Mercury,Venus,Mars,Jupiter,Saturn,Rahu,Ketu", description="Comma-separated list of planets")
):
    """Get planetary positions and panchanga."""
    with RequestLogger("ephemeris.get") as req_log:
        try:
            # Parse timestamp
            if when_utc:
                dt = datetime.fromisoformat(when_utc.replace('Z', '+00:00'))
            elif when_local and place_id:
                # Resolve place and convert to UTC
                place_info = places_service.resolve_place(place_id)
                timezone_id = place_info["timezone"]["timeZoneId"]
                
                import zoneinfo
                tz = zoneinfo.ZoneInfo(timezone_id)
                dt = datetime.fromisoformat(when_local).replace(tzinfo=tz)
                dt = dt.astimezone(zoneinfo.ZoneInfo("UTC"))
            else:
                raise HTTPException(
                    status_code=400, 
                    detail="Either when_utc or both when_local and place_id must be provided"
                )
            
            # Parse planets list
            planet_list = [p.strip() for p in planets.split(",")] if planets else None
            
            # Calculate planetary positions
            planet_data = swe_service.calculate_planets(dt, planet_list)
            
            # Calculate panchanga with all 5 elements
            panchanga_data = panchanga_service.get_daily_panchanga(dt, {"timezone": {"timeZoneId": "UTC"}})
            
            # Format response
            response = {
                "timestamp": dt.isoformat(),
                "planets": planet_data,
                "panchanga": panchanga_data,
                "precision": swe_service.precision
            }
            
            return response
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid timestamp format: {e}")
        except Exception as e:
            logger.error(f"Ephemeris calculation failed: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")
