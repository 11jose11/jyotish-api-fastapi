"""Google Timezone API service."""

import time
from datetime import datetime
from typing import Dict, Optional

import httpx
from app.config import settings
from app.util.logging import get_logger

logger = get_logger("timezone")


class TimezoneService:
    """Google Timezone API service."""
    
    def __init__(self):
        self.api_key = settings.google_maps_api_key
        self.base_url = "https://maps.googleapis.com/maps/api/timezone/json"
        self.cache = {}
        self.cache_ttl = settings.cache_ttl
    
    def _make_request(self, params: Dict) -> Dict:
        """Make HTTP request to Google Timezone API."""
        params["key"] = self.api_key
        
        timeout = httpx.Timeout(
            settings.http_timeout,
            connect=settings.http_connect_timeout
        )
        
        with httpx.Client(timeout=timeout) as client:
            try:
                response = client.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                if data.get("status") != "OK":
                    logger.warning(f"Timezone API error: {data.get('status')}")
                    return {
                        "timeZoneId": None,
                        "rawOffset": None,
                        "dstOffset": None
                    }
                
                return data
                
            except Exception as e:
                logger.error(f"Timezone API request failed: {e}")
                return {
                    "timeZoneId": None,
                    "rawOffset": None,
                    "dstOffset": None
                }
    
    def _get_cache_key(self, lat: float, lng: float, timestamp: Optional[int]) -> str:
        """Generate cache key for timezone request."""
        return f"timezone:{lat:.6f},{lng:.6f},{timestamp or 'now'}"
    
    def get_timezone(self, lat: float, lng: float, timestamp: Optional[int] = None) -> Dict:
        """Get timezone information for coordinates."""
        if timestamp is None:
            timestamp = int(time.time())
        
        cache_key = self._get_cache_key(lat, lng, timestamp)
        
        # Check cache
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return cached_data
            else:
                del self.cache[cache_key]
        
        # Make API request
        params = {
            "location": f"{lat},{lng}",
            "timestamp": timestamp
        }
        
        try:
            result = self._make_request(params)
            
            # Format response
            timezone_info = {
                "timeZoneId": result.get("timeZoneId"),
                "timeZoneName": result.get("timeZoneName"),
                "rawOffset": result.get("rawOffset"),
                "dstOffset": result.get("dstOffset")
            }
            
            # Cache result
            self.cache[cache_key] = (timezone_info, time.time())
            
            return timezone_info
            
        except Exception as e:
            logger.error(f"Failed to get timezone: {e}")
            # Return fallback timezone info
            return {
                "timeZoneId": "UTC",
                "timeZoneName": "Coordinated Universal Time",
                "rawOffset": 0,
                "dstOffset": 0
            }


# Global service instance
timezone_service = TimezoneService()