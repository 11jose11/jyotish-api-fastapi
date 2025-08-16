"""Calendar router for monthly and daily panchanga."""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.swe import swe_service
from app.services.places import places_service
from app.services.panchanga import panchanga_service
from app.util.logging import get_logger, RequestLogger

logger = get_logger("calendar")

router = APIRouter(prefix="/v1/calendar", tags=["calendar"])


@router.get("/month")
async def get_monthly_calendar(
    year: int = Query(..., description="Year"),
    month: int = Query(..., description="Month (1-12)"),
    place_id: str = Query(..., description="Google Place ID"),
    anchor: str = Query("sunrise", description="Anchor time: sunrise, midnight, noon, custom"),
    custom_time: Optional[str] = Query(None, description="Custom time in HH:MM format"),
    format: str = Query("compact", description="Format: compact or detailed"),
    planets: str = Query("Sun,Moon,Mercury,Venus,Mars,Jupiter,Saturn,Rahu,Ketu", description="Comma-separated list of planets"),
    units: str = Query("both", description="Units: decimal, dms, or both")
):
    """Get monthly calendar with planetary positions."""
    with RequestLogger("calendar.month") as req_log:
        try:
            # Validate inputs
            if month < 1 or month > 12:
                raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
            
            if anchor == "custom" and not custom_time:
                raise HTTPException(status_code=400, detail="Custom time required when anchor is custom")
            
            # Resolve place
            place_info = places_service.resolve_place(place_id)
            
            # Parse planets
            planet_list = [p.strip() for p in planets.split(",")]
            
            # Calculate month data
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1) - timedelta(days=1)
            
            days = []
            current_date = start_date
            
            while current_date <= end_date:
                # Calculate anchor time for the day
                anchor_dt = current_date
                
                if anchor == "sunrise":
                    # Simplified sunrise calculation (6 AM local)
                    anchor_dt = current_date.replace(hour=6, minute=0, second=0, microsecond=0)
                elif anchor == "midnight":
                    anchor_dt = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
                elif anchor == "noon":
                    anchor_dt = current_date.replace(hour=12, minute=0, second=0, microsecond=0)
                elif anchor == "custom":
                    hour, minute = map(int, custom_time.split(":"))
                    anchor_dt = current_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # Convert to UTC
                import zoneinfo
                tz = zoneinfo.ZoneInfo(place_info["timezone"]["timeZoneId"])
                anchor_dt = anchor_dt.replace(tzinfo=tz)
                anchor_utc = anchor_dt.astimezone(zoneinfo.ZoneInfo("UTC"))
                
                # Calculate planetary positions
                planet_data = swe_service.calculate_planets(anchor_utc, planet_list)
                
                # Format planet data
                formatted_planets = {}
                for planet, data in planet_data.items():
                    formatted_planet = {
                        "lon_decimal": round(data["lon"], 6),
                        "retrograde": data["retrograde"],
                        "motion_state": data.get("motion_state", "sama"),
                        "rasi": data["rasi"],
                        "rasi_index": data["rasi_index"],
                        "nakshatra": data["nakshatra"],
                        "nak_index": data["nak_index"],
                        "pada": data["pada"],
                        "changedNakshatra": False,  # TODO: implement change detection
                        "changedPada": False,
                        "changedRasi": False
                    }
                    
                    if units in ["dms", "both"]:
                        formatted_planet["lon_dms"] = panchanga_service.to_dms(data["lon"])
                    
                    formatted_planets[planet] = formatted_planet
                
                day_data = {
                    "date": current_date.date().isoformat(),
                    "anchor_ts_local": anchor_dt.isoformat(),
                    "planets": formatted_planets
                }
                
                if format == "detailed":
                    # TODO: implement detailed events
                    day_data["events"] = []
                
                days.append(day_data)
                current_date += timedelta(days=1)
            
            return {
                "year": year,
                "month": month,
                "place": {
                    "place_id": place_info["place"]["id"],
                    "name": place_info["place"]["name"],
                    "tz": place_info["timezone"]["timeZoneId"]
                },
                "anchor": anchor,
                "days": days
            }
            
        except Exception as e:
            logger.error(f"Monthly calendar calculation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/day")
async def get_daily_calendar(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    place_id: str = Query(..., description="Google Place ID")
):
    """Get daily panchanga with exact windows."""
    with RequestLogger("calendar.day") as req_log:
        try:
            # Parse date
            dt = datetime.fromisoformat(date)
            
            # Resolve place
            place_info = places_service.resolve_place(place_id)
            
            # Get daily panchanga
            panchanga_data = panchanga_service.get_daily_panchanga(dt, place_info)
            
            return panchanga_data
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
        except Exception as e:
            logger.error(f"Daily calendar calculation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
