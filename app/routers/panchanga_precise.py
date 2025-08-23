"""Precise Panchanga router with sunrise-based calculations."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.panchanga_precise import precise_panchanga_service
from app.services.swe import swe_service
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


@router.get("/ayanamsa")
async def get_ayanamsa_info(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    time: str = Query("12:00:00", description="Time in HH:MM:SS format")
):
    """Get current ayanamsa value and type for a specific date and time."""
    with RequestLogger("panchanga_precise.ayanamsa") as req_log:
        try:
            # Parse date and time
            dt_str = f"{date}T{time}"
            dt = datetime.fromisoformat(dt_str)
            
            # Get ayanamsa value using Swiss Ephemeris
            import swisseph as swe
            jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0 + dt.second/3600.0)
            
            # Get ayanamsa value (True Citra Paksha is already set in swe_service)
            ayanamsa = swe.get_ayanamsa(jd)
            
            # Convert to degrees, minutes, seconds
            deg = int(ayanamsa)
            min_val = int((ayanamsa % 1) * 60)
            sec_val = ((ayanamsa % 1) * 60 % 1) * 60
            
            return {
                "date": date,
                "time": time,
                "julian_day": jd,
                "ayanamsa": {
                    "type": "True Citra Paksha",
                    "value_degrees": round(ayanamsa, 6),
                    "formatted": f"{deg}°{min_val:02d}'{sec_val:04.1f}\"",
                    "degrees": deg,
                    "minutes": min_val,
                    "seconds": round(sec_val, 1)
                },
                "description": "True Citra Paksha ayanamsa used for all sidereal calculations"
            }
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date/time format: {e}")
        except Exception as e:
            logger.error(f"Ayanamsa calculation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


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
            panchanga = precise_panchanga_service.get_precise_panchanga(
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
            solar_info = precise_panchanga_service.get_precise_panchanga(dt, latitude, longitude, altitude, "sunrise")
            
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
    """Get precise sunrise time for a specific date and location."""
    with RequestLogger("panchanga_precise.sunrise") as req_log:
        try:
            # Parse date
            dt = datetime.fromisoformat(date)
            
            # Validate coordinates
            if not (-90 <= latitude <= 90):
                raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
            if not (-180 <= longitude <= 180):
                raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
            
            # Get sunrise time
            from app.services.sunrise_precise import precise_sunrise_service
            sunrise_time = precise_sunrise_service.calculate_sunrise(dt, latitude, longitude, altitude)
            
            return {
                "date": date,
                "latitude": latitude,
                "longitude": longitude,
                "altitude": altitude,
                "sunrise_time": sunrise_time.strftime('%H:%M:%S'),
                "sunrise_datetime": sunrise_time.isoformat()
            }
            
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
    """Get precise sunset time for a specific date and location."""
    with RequestLogger("panchanga_precise.sunset") as req_log:
        try:
            # Parse date
            dt = datetime.fromisoformat(date)
            
            # Validate coordinates
            if not (-90 <= latitude <= 90):
                raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
            if not (-180 <= longitude <= 180):
                raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
            
            # Get sunset time
            from app.services.sunrise_precise import precise_sunrise_service
            sunset_time = precise_sunrise_service.calculate_sunset(dt, latitude, longitude, altitude)
            
            return {
                "date": date,
                "latitude": latitude,
                "longitude": longitude,
                "altitude": altitude,
                "sunset_time": sunset_time.strftime('%H:%M:%S'),
                "sunset_datetime": sunset_time.isoformat()
            }
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
        except Exception as e:
            logger.error(f"Sunset calculation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
