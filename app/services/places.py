"""Google Places API service with caching and circuit breaker."""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import httpx
from app.config import settings
from app.util.logging import get_logger

logger = get_logger("places")


class CircuitBreaker:
    """Simple circuit breaker implementation."""
    
    def __init__(self, failure_threshold: int, timeout: int):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            
            raise e


class PlacesService:
    """Google Places API service."""
    
    def __init__(self):
        self.api_key = settings.google_maps_api_key
        self.base_url = "https://maps.googleapis.com/maps/api"
        self.circuit_breaker = CircuitBreaker(
            settings.circuit_breaker_failure_threshold,
            settings.circuit_breaker_timeout
        )
        self.cache = {}
        self.cache_ttl = settings.cache_ttl
    
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """Make HTTP request to Google Places API."""
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
    
    def _get_cache_key(self, method: str, **kwargs) -> str:
        """Generate cache key for method and parameters."""
        params = sorted(kwargs.items())
        return f"{method}:{hash(str(params))}"
    
    def _get_cached(self, cache_key: str) -> Optional[Dict]:
        """Get cached result if not expired."""
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
            else:
                del self.cache[cache_key]
        return None
    
    def _set_cached(self, cache_key: str, data: Dict):
        """Cache result with timestamp."""
        self.cache[cache_key] = (data, time.time())
    
    def autocomplete(self, query: str, language: str = "en") -> List[Dict]:
        """Get place autocomplete suggestions."""
        cache_key = self._get_cache_key("autocomplete", query=query, language=language)
        
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        def _autocomplete():
            params = {
                "input": query,
                "language": language,
                "types": "geocode"
            }
            data = self._make_request("place/autocomplete/json", params)
            return data.get("predictions", [])
        
        try:
            result = self.circuit_breaker.call(_autocomplete)
            self._set_cached(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"Autocomplete failed: {e}")
            raise
    
    def get_place_details(self, place_id: str) -> Dict:
        """Get detailed place information."""
        cache_key = self._get_cache_key("details", place_id=place_id)
        
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        def _get_details():
            params = {
                "place_id": place_id,
                "fields": "place_id,name,formatted_address,geometry"
            }
            data = self._make_request("place/details/json", params)
            return data.get("result", {})
        
        try:
            result = self.circuit_breaker.call(_get_details)
            self._set_cached(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"Get place details failed: {e}")
            raise
    
    def resolve_place(self, place_id: str, timestamp: Optional[int] = None) -> Dict:
        """Resolve place with timezone information."""
        try:
            # Get place details
            place_details = self.get_place_details(place_id)
            
            if not place_details:
                raise Exception("Place not found")
            
            # Get timezone information
            from app.services.timezone import timezone_service
            
            lat = place_details["geometry"]["location"]["lat"]
            lng = place_details["geometry"]["location"]["lng"]
            
            timezone_info = timezone_service.get_timezone(lat, lng, timestamp)
            
            return {
                "place": {
                    "id": place_details["place_id"],
                    "name": place_details.get("name", ""),
                    "formatted_address": place_details.get("formatted_address", ""),
                    "lat": lat,
                    "lon": lng
                },
                "timezone": timezone_info
            }
            
        except Exception as e:
            logger.error(f"Resolve place failed: {e}")
            raise


# Global service instance
places_service = PlacesService()
