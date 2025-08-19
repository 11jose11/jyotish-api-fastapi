"""Yogas router for panchanga yoga detection."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.yogas import yogas_service
from app.util.logging import get_logger, RequestLogger

logger = get_logger("yogas")

router = APIRouter(prefix="/v1/panchanga/yogas", tags=["yogas"])


class YogaDetectionRequest(BaseModel):
    """Yoga detection request model."""
    date: str
    latitude: float
    longitude: float
    altitude: Optional[float] = 0.0


@router.get("/detect")
async def detect_yogas_get(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    latitude: float = Query(..., description="Latitude in decimal degrees"),
    longitude: float = Query(..., description="Longitude in decimal degrees"),
    altitude: float = Query(0.0, description="Altitude above sea level in meters")
):
    """Detect panchanga yogas for a specific date and location."""
    with RequestLogger("yogas.detect") as req_log:
        try:
            # Validate date format
            try:
                dt = datetime.fromisoformat(date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
            
            # Validate coordinates
            if not (-90 <= latitude <= 90):
                raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
            if not (-180 <= longitude <= 180):
                raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
            
            # Detect yogas
            result = yogas_service.detect_yogas(dt, latitude, longitude)
            
            return result
            
        except Exception as e:
            logger.error(f"Yoga detection failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect")
async def detect_yogas_post(request: YogaDetectionRequest):
    """Detect panchanga yogas for a specific date and location (POST method)."""
    with RequestLogger("yogas.detect") as req_log:
        try:
            # Validate date format
            try:
                dt = datetime.fromisoformat(request.date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
            
            # Validate coordinates
            if not (-90 <= request.latitude <= 90):
                raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
            if not (-180 <= request.longitude <= 180):
                raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
            
            # Detect yogas
            result = yogas_service.detect_yogas(dt, request.latitude, request.longitude)
            
            return result
            
        except Exception as e:
            logger.error(f"Yoga detection failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
