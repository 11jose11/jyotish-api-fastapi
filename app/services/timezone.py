"""Google Time Zone API service with historical timezone support."""

import time
from datetime import datetime
from typing import Dict, Optional

import httpx
from app.config import settings
from app.util.logging import get_logger

logger = get_logger("timezone")


class TimezoneService:
    """Google Time Zone API service."""
    
    def __init__(self):
        self.api_key = settings.google_maps_api_key
        self.base_url = "https://maps.googleapis.com/maps/api"
        self.cache = {}
        self.cache_ttl = settings.cache_ttl
    
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """Make HTTP request to Google Time Zone API."""
        params["key"] = self.api_key
        
        timeout = httpx.Timeout(
            settings.http_timeout,
            connect=settings.http_connect_timeout
        )
        
        with httpx.Client(timeout=timeout) as client:
            for attempt in range(settings.http_max_retries + 1):
                try:
                    response = client.get(f"{self.base_url}/{endpoint}", params=params)
                    response.raise_for_status()
                    
                    data = response.json()
                    if data.get("status") != "OK":
                        raise Exception(f"Google API error: {data.get('status')}")
                    
                    return data
                    
                except httpx.TimeoutException:
                    if attempt == settings.http_max_retries:
                        raise Exception("Request timeout")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
                except Exception as e:
                    if attempt == settings.http_max_retries:
                        raise e
                    time.sleep(2 ** attempt)
    
    def _get_cache_key(self, lat: float, lng: float, timestamp: Optional[int]) -> str:
        """Generate cache key for coordinates and timestamp."""
        return f"timezone:{lat}:{lng}:{timestamp}"
    
    def _get_cached(self, cache_key: str) -> Optional[Dict]:
        """Get cached result if not expired."""
        if cache_key in self.cache:
            cached_data, cache_time = self.cache[cache_key]
            if time.time() - cache_time < self.cache_ttl:
                return cached_data
            else:
                del self.cache[cache_key]
        return None
    
    def _set_cached(self, cache_key: str, data: Dict):
        """Cache result with timestamp."""
        self.cache[cache_key] = (data, time.time())
    
    def get_timezone(
        self, 
        lat: float, 
        lng: float, 
        timestamp: Optional[int] = None
    ) -> Dict:
        """Get timezone information for coordinates and timestamp."""
        cache_key = self._get_cache_key(lat, lng, timestamp)
        
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        # If no timestamp provided, use current time
        if timestamp is None:
            timestamp = int(time.time())
        
        params = {
            "location": f"{lat},{lng}",
            "timestamp": timestamp
        }
        
        try:
            data = self._make_request("timezone/json", params)
            result = data.get("result", {})
            
            timezone_info = {
                "timeZoneId": result.get("timeZoneId"),
                "rawOffset": result.get("rawOffset"),
                "dstOffset": result.get("dstOffset")
            }
            
            self._set_cached(cache_key, timezone_info)
            return timezone_info
            
        except Exception as e:
            logger.error(f"Get timezone failed: {e}")
            raise


# Global service instance
timezone_service = TimezoneService()
