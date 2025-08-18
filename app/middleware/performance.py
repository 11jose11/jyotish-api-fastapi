"""Performance optimization middleware."""

import asyncio
import time
from typing import Callable
from contextlib import asynccontextmanager

from fastapi import Request, Response
from app.config import settings
from app.util.logging import get_logger

logger = get_logger("performance")

# Semaphore for limiting concurrent requests
request_semaphore = asyncio.Semaphore(settings.max_concurrent_requests)


class PerformanceMiddleware:
    """Performance optimization middleware."""
    
    def __init__(self):
        self.request_times = {}
        self.slow_request_threshold = 1.0  # 1 second
    
    async def __call__(self, request: Request, call_next: Callable):
        """Process request with performance optimizations."""
        start_time = time.time()
        
        # Check if we're at capacity
        if request_semaphore.locked():
            logger.warning("API at capacity, request queued")
        
        async with request_semaphore:
            try:
                # Add performance headers
                response = await call_next(request)
                
                # Calculate processing time
                processing_time = time.time() - start_time
                
                # Add performance headers
                response.headers["X-Processing-Time"] = f"{processing_time:.3f}"
                response.headers["X-Concurrent-Requests"] = str(
                    settings.max_concurrent_requests - request_semaphore._value
                )
                
                # Log slow requests
                if processing_time > self.slow_request_threshold:
                    logger.warning(
                        f"Slow request: {request.method} {request.url.path} "
                        f"took {processing_time:.3f}s"
                    )
                
                return response
                
            except asyncio.TimeoutError:
                logger.error(f"Request timeout: {request.method} {request.url.path}")
                raise
            except Exception as e:
                logger.error(f"Request error: {request.method} {request.url.path} - {e}")
                raise


# Global performance middleware instance
performance_middleware = PerformanceMiddleware()


@asynccontextmanager
async def request_timeout(timeout_seconds: float = 30.0):
    """Context manager for request timeout."""
    try:
        await asyncio.wait_for(asyncio.sleep(0), timeout=timeout_seconds)
        yield
    except asyncio.TimeoutError:
        logger.error(f"Request timeout after {timeout_seconds}s")
        raise


class BatchProcessor:
    """Batch processing for multiple calculations."""
    
    def __init__(self, max_batch_size: int = None):
        self.max_batch_size = max_batch_size or settings.batch_size_limit
    
    async def process_batch(self, items: list, processor_func: Callable, **kwargs):
        """Process items in batches."""
        if len(items) > self.max_batch_size:
            raise ValueError(f"Batch size {len(items)} exceeds limit {self.max_batch_size}")
        
        # Process items concurrently
        tasks = [processor_func(item, **kwargs) for item in items]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch item {i} failed: {result}")
                processed_results.append({"error": str(result)})
            else:
                processed_results.append(result)
        
        return processed_results


class ConnectionPool:
    """Connection pool for external services."""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self._semaphore = asyncio.Semaphore(max_connections)
    
    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool."""
        async with self._semaphore:
            try:
                yield
            except Exception as e:
                logger.error(f"Connection error: {e}")
                raise


# Global instances
batch_processor = BatchProcessor()
connection_pool = ConnectionPool()


async def optimize_response(response: Response, enable_compression: bool = True):
    """Optimize response for better performance."""
    if enable_compression:
        response.headers["Content-Encoding"] = "gzip"
    
    # Add cache headers
    response.headers["Cache-Control"] = "public, max-age=300"
    response.headers["Vary"] = "Accept-Encoding"
    
    return response


def get_performance_stats():
    """Get current performance statistics."""
    return {
        "concurrent_requests": settings.max_concurrent_requests - request_semaphore._value,
        "max_concurrent_requests": settings.max_concurrent_requests,
        "batch_size_limit": settings.batch_size_limit,
        "slow_request_threshold": performance_middleware.slow_request_threshold
    }
