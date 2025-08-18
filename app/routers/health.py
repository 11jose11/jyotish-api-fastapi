"""Health check router."""

from fastapi import APIRouter, HTTPException
from app.services.swe import swe_service
from app.services.places import places_service
from app.util.logging import get_logger

logger = get_logger("health")

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/healthz")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok"}


@router.get("/readyz")
async def readiness_check():
    """Readiness check endpoint."""
    missing = []
    
    # Check Swiss Ephemeris
    if not swe_service.initialized:
        missing.append("swiss_ephemeris")
    
    # Check Google API key (optional for basic functionality)
    if not places_service.api_key:
        missing.append("google_maps_api_key")
    
    # Consider ready if Swiss Ephemeris is working (Google Maps is optional)
    ready = swe_service.initialized
    
    return {
        "ready": ready,
        "missing": missing,
        "precision": swe_service.precision,
        "swiss_ephemeris_status": "working" if swe_service.initialized else "failed",
        "google_maps_status": "configured" if places_service.api_key else "not_configured"
    }
