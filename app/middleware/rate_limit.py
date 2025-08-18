"""Rate limiting middleware for API protection."""

import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import Request, HTTPException, status
from app.config import settings
from app.util.logging import get_logger

logger = get_logger("rate_limit")

# In-memory storage for rate limiting (use Redis in production)
rate_limit_store: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, 0))


class RateLimiter:
    """Simple rate limiter implementation."""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # 1 minute window
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client."""
        current_time = time.time()
        requests, window_start = rate_limit_store[client_id]
        
        # Reset window if expired
        if current_time - window_start > self.window_size:
            rate_limit_store[client_id] = (1, current_time)
            return True
        
        # Check if within limit
        if requests < self.requests_per_minute:
            rate_limit_store[client_id] = (requests + 1, window_start)
            return True
        
        return False
    
    def get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client."""
        current_time = time.time()
        requests, window_start = rate_limit_store[client_id]
        
        if current_time - window_start > self.window_size:
            return self.requests_per_minute
        
        return max(0, self.requests_per_minute - requests)


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=60)


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    # Get client identifier (IP or API key)
    client_id = request.headers.get("X-API-Key", request.client.host)
    
    # Check rate limit
    if not rate_limiter.is_allowed(client_id):
        remaining_time = 60 - (time.time() - rate_limit_store[client_id][1])
        
        logger.warning(f"Rate limit exceeded for client: {client_id}")
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "retry_after": int(remaining_time),
                "limit": rate_limiter.requests_per_minute,
                "window": "1 minute"
            },
            headers={
                "X-RateLimit-Limit": str(rate_limiter.requests_per_minute),
                "X-RateLimit-Remaining": str(rate_limiter.get_remaining_requests(client_id)),
                "X-RateLimit-Reset": str(int(time.time() + 60)),
                "Retry-After": str(int(remaining_time))
            }
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.requests_per_minute)
    response.headers["X-RateLimit-Remaining"] = str(rate_limiter.get_remaining_requests(client_id))
    
    return response
