"""Places router for Google Places API integration."""

import os
import time
from typing import Optional, List, Dict
import httpx

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from app.config import settings
from app.util.logging import get_logger, RequestLogger

logger = get_logger("places")

router = APIRouter(prefix="/v1/places", tags=["places"])


class PlaceAutocompleteResponse(BaseModel):
    """Response model for place autocomplete."""
    predictions: List[Dict]
    status: str
    query: str


class PlaceDetailsResponse(BaseModel):
    """Response model for place details."""
    place_id: str
    name: str
    formatted_address: str
    geometry: Dict
    timezone: Optional[Dict] = None


@router.get("/autocomplete")
async def place_autocomplete(
    query: str = Query(..., description="Search query for place autocomplete"),
    language: str = Query("en", description="Language code (e.g., en, es, hi)"),
    types: Optional[str] = Query(None, description="Place types filter"),
    components: Optional[str] = Query(None, description="Component restrictions"),
    sessiontoken: Optional[str] = Query(None, description="Session token for billing")
):
    """Get place autocomplete suggestions from Google Places API."""
    with RequestLogger("places.autocomplete") as req_log:
        try:
            if not settings.google_maps_api_key:
                # Fallback response when no API key is available
                return PlaceAutocompleteResponse(
                    predictions=[
                        {
                            "place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",  # Sydney, Australia
                            "description": "Sydney, NSW, Australia",
                            "structured_formatting": {
                                "main_text": "Sydney",
                                "secondary_text": "NSW, Australia"
                            }
                        },
                        {
                            "place_id": "ChIJ7cv00dwsDogUkHmCUbIuAAY",  # Chicago, USA
                            "description": "Chicago, IL, USA",
                            "structured_formatting": {
                                "main_text": "Chicago",
                                "secondary_text": "IL, USA"
                            }
                        },
                        {
                            "place_id": "ChIJdd4hrwug2EcRmSrV3Vo6llI",  # London, UK
                            "description": "London, UK",
                            "structured_formatting": {
                                "main_text": "London",
                                "secondary_text": "UK"
                            }
                        }
                    ],
                    status="OK",
                    query=query
                )
            
            # Build Google Places API URL
            base_url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
            params = {
                "input": query,
                "key": settings.google_maps_api_key,
                "language": language,
                "types": types,
                "components": components,
                "sessiontoken": sessiontoken
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("status") != "OK":
                    logger.warning(f"Google Places API error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
                    # Return fallback data on API error
                    return PlaceAutocompleteResponse(
                        predictions=[],
                        status="ZERO_RESULTS",
                        query=query
                    )
                
                req_log.success()
                return PlaceAutocompleteResponse(
                    predictions=data.get("predictions", []),
                    status=data.get("status", "OK"),
                    query=query
                )
                
        except httpx.TimeoutException:
            logger.error("Google Places API timeout")
            raise HTTPException(status_code=408, detail="Places API request timeout")
        except httpx.HTTPStatusError as e:
            logger.error(f"Google Places API HTTP error: {e}")
            raise HTTPException(status_code=502, detail=f"Places API error: {e}")
        except Exception as e:
            logger.error(f"Place autocomplete failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/details/{place_id}")
async def place_details(
    place_id: str,
    language: str = Query("en", description="Language code"),
    fields: Optional[str] = Query(None, description="Comma-separated list of fields to return"),
    sessiontoken: Optional[str] = Query(None, description="Session token for billing")
):
    """Get detailed information about a specific place."""
    with RequestLogger("places.details") as req_log:
        try:
            if not settings.google_maps_api_key:
                # Fallback response when no API key is available
                return PlaceDetailsResponse(
                    place_id=place_id,
                    name="Sample Place",
                    formatted_address="123 Sample Street, Sample City, Sample Country",
                    geometry={
                        "location": {"lat": 0.0, "lng": 0.0},
                        "viewport": {
                            "northeast": {"lat": 0.1, "lng": 0.1},
                            "southwest": {"lat": -0.1, "lng": -0.1}
                        }
                    },
                    timezone={"timeZoneId": "UTC"}
                )
            
            # Build Google Places API URL
            base_url = f"https://maps.googleapis.com/maps/api/place/details/json"
            params = {
                "place_id": place_id,
                "key": settings.google_maps_api_key,
                "language": language,
                "fields": fields or "place_id,name,formatted_address,geometry,utc_offset",
                "sessiontoken": sessiontoken
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("status") != "OK":
                    logger.warning(f"Google Places API error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
                    raise HTTPException(status_code=404, detail="Place not found")
                
                result = data.get("result", {})
                
                # Extract timezone information
                timezone_info = None
                if "utc_offset" in result:
                    # Convert UTC offset to timezone ID (simplified)
                    offset_minutes = result["utc_offset"]
                    if offset_minutes == 0:
                        timezone_info = {"timeZoneId": "UTC"}
                    else:
                        # This is a simplified approach - in production you'd want a proper mapping
                        timezone_info = {"timeZoneId": "UTC"}
                
                place_details = PlaceDetailsResponse(
                    place_id=result.get("place_id", place_id),
                    name=result.get("name", "Unknown Place"),
                    formatted_address=result.get("formatted_address", "Address not available"),
                    geometry=result.get("geometry", {}),
                    timezone=timezone_info
                )
                
                req_log.success()
                return place_details
                
        except httpx.TimeoutException:
            logger.error("Google Places API timeout")
            raise HTTPException(status_code=408, detail="Places API request timeout")
        except httpx.HTTPStatusError as e:
            logger.error(f"Google Places API HTTP error: {e}")
            raise HTTPException(status_code=502, detail=f"Places API error: {e}")
        except Exception as e:
            logger.error(f"Place details failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def place_search(
    query: str = Query(..., description="Search query for places"),
    location: Optional[str] = Query(None, description="Location bias (lat,lng)"),
    radius: Optional[int] = Query(50000, description="Search radius in meters"),
    language: str = Query("en", description="Language code"),
    types: Optional[str] = Query(None, description="Place types filter")
):
    """Search for places using Google Places API."""
    with RequestLogger("places.search") as req_log:
        try:
            if not settings.google_maps_api_key:
                # Fallback response when no API key is available
                return {
                    "results": [],
                    "status": "ZERO_RESULTS",
                    "query": query
                }
            
            # Build Google Places API URL
            base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                "query": query,
                "key": settings.google_maps_api_key,
                "language": language,
                "radius": radius,
                "types": types
            }
            
            if location:
                params["location"] = location
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("status") != "OK":
                    logger.warning(f"Google Places API error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
                    return {
                        "results": [],
                        "status": data.get("status", "ZERO_RESULTS"),
                        "query": query
                    }
                
                req_log.success()
                return {
                    "results": data.get("results", []),
                    "status": data.get("status", "OK"),
                    "query": query
                }
                
        except httpx.TimeoutException:
            logger.error("Google Places API timeout")
            raise HTTPException(status_code=408, detail="Places API request timeout")
        except httpx.HTTPStatusError as e:
            logger.error(f"Google Places API HTTP error: {e}")
            raise HTTPException(status_code=502, detail=f"Places API error: {e}")
        except Exception as e:
            logger.error(f"Place search failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

