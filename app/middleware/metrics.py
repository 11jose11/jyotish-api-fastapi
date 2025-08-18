"""Metrics middleware for performance monitoring."""

import time
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from app.util.logging import get_logger

logger = get_logger("metrics")

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'http_active_requests',
    'Number of active HTTP requests',
    ['method', 'endpoint']
)

ERROR_COUNT = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'error_type']
)

# Business metrics
EPHEMERIS_CALCULATIONS = Counter(
    'ephemeris_calculations_total',
    'Total ephemeris calculations',
    ['planets_count']
)

PLACE_LOOKUPS = Counter(
    'place_lookups_total',
    'Total place lookups',
    ['type']
)

YOGA_DETECTIONS = Counter(
    'yoga_detections_total',
    'Total yoga detections',
    ['granularity']
)


async def metrics_middleware(request: Request, call_next):
    """Metrics middleware for request monitoring."""
    start_time = time.time()
    
    # Extract endpoint from path
    endpoint = request.url.path
    method = request.method
    
    # Increment active requests
    ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).inc()
    
    try:
        response = await call_next(request)
        
        # Record metrics
        duration = time.time() - start_time
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status=response.status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        return response
        
    except Exception as e:
        # Record error metrics
        ERROR_COUNT.labels(
            method=method,
            endpoint=endpoint,
            error_type=type(e).__name__
        ).inc()
        raise
    
    finally:
        # Decrement active requests
        ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).dec()


def get_metrics():
    """Get Prometheus metrics."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


def record_business_metric(metric_name: str, labels: Dict[str, str] = None, value: float = 1.0):
    """Record business-specific metrics."""
    try:
        if metric_name == "ephemeris_calculations":
            planets_count = labels.get("planets_count", "unknown")
            EPHEMERIS_CALCULATIONS.labels(planets_count=planets_count).inc()
        
        elif metric_name == "place_lookups":
            lookup_type = labels.get("type", "unknown")
            PLACE_LOOKUPS.labels(type=lookup_type).inc()
        
        elif metric_name == "yoga_detections":
            granularity = labels.get("granularity", "unknown")
            YOGA_DETECTIONS.labels(granularity=granularity).inc()
            
    except Exception as e:
        logger.error(f"Failed to record metric {metric_name}: {e}")
