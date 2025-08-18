"""Cache service with Redis support."""

import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta

import redis.asyncio as redis
from app.config import settings
from app.util.logging import get_logger

logger = get_logger("cache")


class CacheService:
    """Redis cache service."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = False
        self._initialize()
    
    def _initialize(self):
        """Initialize Redis connection."""
        if settings.redis_url:
            try:
                self.redis_client = redis.from_url(
                    settings.redis_url,
                    decode_responses=False,  # Keep binary for pickle
                    socket_connect_timeout=settings.http_connect_timeout,
                    socket_timeout=settings.http_timeout
                )
                self.enabled = True
                logger.info("Redis cache initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis cache: {e}")
                self.enabled = False
        else:
            logger.info("Redis cache disabled (no URL configured)")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value:
                return pickle.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set value in cache."""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            serialized_value = pickle.dumps(value)
            if ttl:
                if isinstance(ttl, timedelta):
                    ttl = int(ttl.total_seconds())
                await self.redis_client.setex(key, ttl, serialized_value)
            else:
                await self.redis_client.set(key, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching pattern."""
        if not self.enabled or not self.redis_client:
            return 0
        
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return 0
    
    def generate_key(self, prefix: str, *args) -> str:
        """Generate cache key from prefix and arguments."""
        key_parts = [prefix] + [str(arg) for arg in args]
        return ":".join(key_parts)


# Global cache service instance
cache_service = CacheService()


# Cache decorator
def cached(prefix: str, ttl: int = 600):
    """Cache decorator for functions."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [prefix] + [str(arg) for arg in args]
            if kwargs:
                sorted_kwargs = sorted(kwargs.items())
                key_parts.extend([f"{k}={v}" for k, v in sorted_kwargs])
            
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_result = await cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_service.set(cache_key, result, ttl)
            logger.debug(f"Cache miss for key: {cache_key}")
            
            return result
        return wrapper
    return decorator
