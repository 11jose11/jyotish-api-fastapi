"""Motion router for planetary motion states."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.motion import motion_service
from app.util.logging import get_logger, RequestLogger

logger = get_logger("motion")

router = APIRouter(prefix="/v1/motion", tags=["motion"])


@router.get("/states")
async def get_motion_states(
    start: str = Query(..., description="Start time in ISO-8601 format"),
    end: str = Query(..., description="End time in ISO-8601 format"),
    tzname: str = Query("UTC", description="Timezone name"),
    step_minutes: int = Query(60, description="Step interval in minutes"),
    mode: str = Query("classic", description="Mode: classic or adaptive"),
    planets: str = Query("Mars,Venus", description="Comma-separated list of planets")
):
    """Get planetary motion states over time period."""
    with RequestLogger("motion.states") as req_log:
        try:
            # Parse timestamps
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
            
            # Parse planets
            planet_list = [p.strip() for p in planets.split(",")]
            
            # Get motion states
            result = motion_service.get_motion_states(
                start_dt, end_dt, step_minutes, mode, planet_list
            )
            
            return result
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid timestamp format: {e}")
        except Exception as e:
            logger.error(f"Motion states calculation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
