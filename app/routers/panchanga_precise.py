"""Precise Panchanga router with sunrise-based calculations."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.panchanga import panchanga_service
from app.util.logging import get_logger, RequestLogger

logger = get_logger("panchanga_precise")

router = APIRouter(prefix="/v1/panchanga/precise", tags=["panchanga_precise"])


class PrecisePanchangaRequest(BaseModel):
    """Precise panchanga request model."""
    date: str  # YYYY-MM-DD format
    latitude: float
    longitude: float
    altitude: Optional[float] = 0.0
    reference_time: Optional[str] = "sunrise"  # sunrise, sunset, noon, midnight


@router.get("/daily")
async def get_precise_daily_panchanga(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    latitude: float = Query(..., description="Latitude in decimal degrees"),
    longitude: float = Query(..., description="Longitude in decimal degrees"),
    altitude: float = Query(0.0, description="Altitude above sea level in meters"),
    reference_time: str = Query("sunrise", description="Reference time: sunrise, sunset, noon, midnight")
):
    """Get precise daily panchanga calculated at sunrise (or other reference time) for a specific location."""
    with RequestLogger("panchanga_precise.daily") as req_log:
        try:
            # Parse date
            dt = datetime.fromisoformat(date)
            
            # Validate reference time
            valid_reference_times = ["sunrise", "sunset", "noon", "midnight"]
            if reference_time not in valid_reference_times:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid reference_time. Must be one of: {valid_reference_times}"
                )
            
            # Validate coordinates
            if not (-90 <= latitude <= 90):
                raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
            if not (-180 <= longitude <= 180):
                raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
            
            # Get precise panchanga
            panchanga = panchanga_service.get_precise_panchanga(
                dt, latitude, longitude, altitude, reference_time
            )
            
            return panchanga
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
        except Exception as e:
            logger.error(f"Precise panchanga calculation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/solar-day")
async def get_solar_day_info(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    latitude: float = Query(..., description="Latitude in decimal degrees"),
    longitude: float = Query(..., description="Longitude in decimal degrees"),
    altitude: float = Query(0.0, description="Altitude above sea level in meters")
):
    """Get solar day information including sunrise, sunset, and day length for a specific location."""
    with RequestLogger("panchanga_precise.solar_day") as req_log:
        try:
            # Parse date
            dt = datetime.fromisoformat(date)
            
            # Validate coordinates
            if not (-90 <= latitude <= 90):
                raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
            if not (-180 <= longitude <= 180):
                raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
            
            # Get solar day information
            solar_info = panchanga_service.get_solar_day_info(dt, latitude, longitude, altitude)
            
            return solar_info
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
        except Exception as e:
            logger.error(f"Solar day calculation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/sunrise")
async def get_sunrise_time(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    latitude: float = Query(..., description="Latitude in decimal degrees"),
    longitude: float = Query(..., description="Longitude in decimal degrees"),
    altitude: float = Query(0.0, description="Altitude above sea level in meters")
):
    """Get precise sunrise time for a specific location and date."""
    with RequestLogger("panchanga_precise.sunrise") as req_log:
        try:
            # Parse date
            dt = datetime.fromisoformat(date)
            
            # Validate coordinates
            if not (-90 <= latitude <= 90):
                raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
            if not (-180 <= longitude <= 180):
                raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
            
            # Calculate sunrise
            sunrise = panchanga_service.calculate_sunrise(dt, latitude, longitude, altitude)
            
            if sunrise:
                return {
                    "date": date,
                    "sunrise": sunrise.isoformat(),
                    "latitude": latitude,
                    "longitude": longitude,
                    "altitude": altitude
                }
            else:
                raise HTTPException(status_code=500, detail="Could not calculate sunrise for this location/date")
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
        except Exception as e:
            logger.error(f"Sunrise calculation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/sunset")
async def get_sunset_time(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    latitude: float = Query(..., description="Latitude in decimal degrees"),
    longitude: float = Query(..., description="Longitude in decimal degrees"),
    altitude: float = Query(0.0, description="Altitude above sea level in meters")
):
    """Get precise sunset time for a specific location and date."""
    with RequestLogger("panchanga_precise.sunset") as req_log:
        try:
            # Parse date
            dt = datetime.fromisoformat(date)
            
            # Validate coordinates
            if not (-90 <= latitude <= 90):
                raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
            if not (-180 <= longitude <= 180):
                raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
            
            # Calculate sunset
            sunset = panchanga_service.calculate_sunset(dt, latitude, longitude, altitude)
            
            if sunset:
                return {
                    "date": date,
                    "sunset": sunset.isoformat(),
                    "latitude": latitude,
                    "longitude": longitude,
                    "altitude": altitude
                }
            else:
                raise HTTPException(status_code=500, detail="Could not calculate sunset for this location/date")
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
        except Exception as e:
            logger.error(f"Sunset calculation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
