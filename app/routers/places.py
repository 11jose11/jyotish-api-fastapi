"""Places router for Google Places API endpoints."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.places import places_service
from app.util.logging import get_logger, RequestLogger

logger = get_logger("places")

router = APIRouter(prefix="/v1/places", tags=["places"])


class PlaceResponse(BaseModel):
    """Place response model."""
    place_id: str
    description: str
    place_id: str


class PlaceDetailsResponse(BaseModel):
    """Place details response model."""
    place: dict
    timezone: dict


@router.get("/autocomplete")
async def autocomplete(
    q: str = Query(..., description="Search query"),
    language: str = Query("en", description="Language code")
):
    """Get place autocomplete suggestions."""
    with RequestLogger("places.autocomplete") as req_log:
        try:
            predictions = places_service.autocomplete(q, language)
            
            return {
                "query": q,
                "language": language,
                "predictions": predictions
            }
            
        except Exception as e:
            logger.error(f"Autocomplete failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/resolve")
async def resolve_place(
    place_id: str = Query(..., description="Google Place ID"),
    timestamp: Optional[int] = Query(None, description="Unix timestamp for historical timezone")
):
    """Resolve place with timezone information."""
    with RequestLogger("places.resolve") as req_log:
        try:
            result = places_service.resolve_place(place_id, timestamp)
            
            return result
            
        except Exception as e:
            logger.error(f"Resolve place failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
