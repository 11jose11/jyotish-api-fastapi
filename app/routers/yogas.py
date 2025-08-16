"""Yogas router for panchanga yoga detection."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.yogas import yogas_service
from app.util.logging import get_logger, RequestLogger

logger = get_logger("yogas")

router = APIRouter(prefix="/v1/panchanga/yogas", tags=["yogas"])


class YogaDetectionRequest(BaseModel):
    """Yoga detection request model."""
    start: str
    end: str
    place_id: str
    granularity: str = "day"
    includeNotes: bool = True


@router.post("/detect")
async def detect_yogas(request: YogaDetectionRequest):
    """Detect panchanga yogas in date range."""
    with RequestLogger("yogas.detect") as req_log:
        try:
            # Validate granularity
            if request.granularity not in ["day", "intervals"]:
                raise HTTPException(
                    status_code=400, 
                    detail="Granularity must be 'day' or 'intervals'"
                )
            
            # Detect yogas
            yogas = yogas_service.detect_yogas(
                request.start,
                request.end,
                request.place_id,
                request.granularity,
                request.includeNotes
            )
            
            return {
                "start": request.start,
                "end": request.end,
                "place_id": request.place_id,
                "granularity": request.granularity,
                "yogas": yogas
            }
            
        except Exception as e:
            logger.error(f"Yoga detection failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
