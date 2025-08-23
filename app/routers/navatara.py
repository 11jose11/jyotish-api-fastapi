"""
Navatāra Chakra router for Jyotiṣa API.
Unified router for Navatāra Chakra calculations.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.navatara import navatara_service
from app.util.logging import get_logger, RequestLogger

logger = get_logger("navatara")

router = APIRouter(prefix="/v1/navatara", tags=["navatara"])


class NavataraRequest(BaseModel):
    """Navatāra calculation request model."""
    date: str  # YYYY-MM-DD format
    latitude: float
    longitude: float
    time: Optional[str] = "12:00:00"  # HH:MM:SS format
    start_type: Optional[str] = "moon"  # moon, sun, lagna
    scheme: Optional[int] = 27  # 27 or 28 nakshatras
    language: Optional[str] = "en"  # en, es


@router.get("/calculate")
async def calculate_navatara(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    latitude: float = Query(..., description="Latitude in decimal degrees"),
    longitude: float = Query(..., description="Longitude in decimal degrees"),
    time: str = Query("12:00:00", description="Time in HH:MM:SS format"),
    start_type: str = Query("moon", description="Start type: moon, sun, lagna"),
    scheme: int = Query(27, description="Nakshatra scheme: 27 or 28"),
    language: str = Query("en", description="Language: en, es")
):
    """Calculate Navatāra Chakra based on birth data."""
    with RequestLogger("navatara.calculate") as req_log:
        try:
            # Validate inputs
            if scheme not in [27, 28]:
                raise HTTPException(
                    status_code=400,
                    detail="Scheme must be 27 or 28"
                )
            
            if start_type.lower() not in ["moon", "sun", "lagna"]:
                raise HTTPException(
                    status_code=400,
                    detail="Start type must be moon, sun, or lagna"
                )
            
            if language not in ["en", "es"]:
                raise HTTPException(
                    status_code=400,
                    detail="Language must be en or es"
                )
            
            # Validate coordinates
            if not (-90 <= latitude <= 90):
                raise HTTPException(
                    status_code=400,
                    detail="Latitude must be between -90 and 90"
                )
            if not (-180 <= longitude <= 180):
                raise HTTPException(
                    status_code=400,
                    detail="Longitude must be between -180 and 180"
                )
            
            # Calculate Navatāra
            result = navatara_service.calculate_navatara(
                date=date,
                latitude=latitude,
                longitude=longitude,
                start_type=start_type.lower(),
                time=time,
                scheme=scheme,
                lang=language
            )
            
            logger.info(f"Navatāra calculated successfully for {date}")
            return result
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid input: {e}")
        except Exception as e:
            logger.error(f"Navatāra calculation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/start-nakshatra")
async def get_start_nakshatra(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    latitude: float = Query(..., description="Latitude in decimal degrees"),
    longitude: float = Query(..., description="Longitude in decimal degrees"),
    time: str = Query("12:00:00", description="Time in HH:MM:SS format"),
    start_type: str = Query("moon", description="Start type: moon, sun, lagna")
):
    """Get starting nakshatra for Navatāra calculation."""
    with RequestLogger("navatara.start_nakshatra") as req_log:
        try:
            # Validate inputs
            if start_type.lower() not in ["moon", "sun", "lagna"]:
                raise HTTPException(
                    status_code=400,
                    detail="Start type must be moon, sun, or lagna"
                )
            
            # Get starting nakshatra
            result = navatara_service.get_start_nakshatra(
                date=date,
                latitude=latitude,
                longitude=longitude,
                start_type=start_type.lower(),
                time=time
            )
            
            logger.info(f"Start nakshatra calculated: {result['nakshatra_name']}")
            return result
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid input: {e}")
        except Exception as e:
            logger.error(f"Start nakshatra calculation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/nakshatra-info")
async def get_nakshatra_info(
    nakshatra_name: str = Query(..., description="Nakshatra name"),
    scheme: int = Query(27, description="Nakshatra scheme: 27 or 28")
):
    """Get detailed information about a nakshatra."""
    with RequestLogger("navatara.nakshatra_info") as req_log:
        try:
            # Validate scheme
            if scheme not in [27, 28]:
                raise HTTPException(
                    status_code=400,
                    detail="Scheme must be 27 or 28"
                )
            
            # Get nakshatra index
            nakshatra_index = navatara_service.get_nakshatra_index(nakshatra_name, scheme)
            if nakshatra_index is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Nakshatra '{nakshatra_name}' not found in scheme {scheme}"
                )
            
            # Build response
            result = {
                "nakshatra_name": nakshatra_name,
                "nakshatra_index": nakshatra_index,
                "scheme": scheme,
                "group": navatara_service.group_of_9(nakshatra_index, scheme),
                "cycle": navatara_service.cycle_of(nakshatra_index, scheme),
                "loka": navatara_service.loka_of(nakshatra_index, scheme),
                "group_deity": navatara_service.get_group_deity(nakshatra_index, scheme),
                "special_taras": navatara_service.special_taras_for(nakshatra_index, scheme)
            }
            
            logger.info(f"Nakshatra info retrieved: {nakshatra_name}")
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Nakshatra info retrieval failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_navatara_info():
    """Get information about the Navatāra service."""
    return {
        "name": "Navatāra Chakra Service",
        "description": "Calculates Navatāra Chakra based on birth nakshatra",
        "version": "1.0.0",
        "features": [
            "27 and 28 nakshatra schemes",
            "Multiple start types (Moon, Sun, Lagna)",
            "Group deities and lokas",
            "Special taras",
            "Multi-language support"
        ],
        "start_types": {
            "moon": "Based on Moon's nakshatra at birth",
            "sun": "Based on Sun's nakshatra at birth",
            "lagna": "Based on Ascendant's nakshatra at birth"
        },
        "schemes": {
            "27": "Classical 27 nakshatra scheme",
            "28": "Extended scheme including Abhijit"
        },
        "languages": ["en", "es"],
        "endpoints": {
            "calculate": "POST /v1/navatara/calculate - Calculate complete Navatāra",
            "start_nakshatra": "GET /v1/navatara/start-nakshatra - Get starting nakshatra",
            "nakshatra_info": "GET /v1/navatara/nakshatra-info - Get nakshatra details",
            "info": "GET /v1/navatara/info - Service information"
        },
        "calculation_method": "Based on Swiss Ephemeris with True Citra Paksha ayanamsa"
    }
