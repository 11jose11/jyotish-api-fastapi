"""Main FastAPI application for Jyotiṣa API."""

import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.util.logging import setup_logging, get_logger, RequestLogger
from app.routers import health, ephemeris, calendar, motion, yogas, panchanga_precise, chesta_bala, navatara, places
from app.middleware.auth import verify_api_key
from app.middleware.rate_limit import rate_limit_middleware
from app.middleware.circuit_breaker import get_circuit_breaker
from app.middleware.performance import performance_middleware
from app.middleware.metrics import metrics_middleware, get_metrics


# Setup logging
setup_logging()
logger = get_logger("main")

# Create FastAPI app
app = FastAPI(
    title="Jyotiṣa API",
    description="""
    **Vedic Astrology API with Swiss Ephemeris and Google APIs**
    
    ## Ayanamsa Configuration
    This API uses **True Citra Paksha ayanamsa** for all sidereal calculations.
    - Ayanamsa Type: True Citra Paksha (SIDM_TRUE_CITRA)
    - Current Value (2024): ~24°11'14"
    - All planetary positions are calculated in sidereal coordinates
    
    ## Key Features
    - Precise panchanga calculations with percentage remaining
    - Accurate sunrise/sunset times using Swiss Ephemeris
    - Planetary positions in nakshatras and rashis
    - High-precision astronomical calculations
    - Frontend-friendly CORS configuration
    """,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enhanced CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
    expose_headers=settings.cors_expose_headers,
    max_age=settings.cors_max_age,
)

# Security headers middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next: Callable):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-API-Version"] = settings.api_version
    
    # Add timing header
    if hasattr(request.state, 'start_time'):
        processing_time = time.time() - request.state.start_time
        response.headers["X-Response-Time"] = f"{processing_time:.3f}s"
    
    return response

# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next: Callable):
    """Add request ID to all requests."""
    request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
    
    # Add request_id to request state
    if not hasattr(request.state, 'request_id'):
        request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    return response

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_requests(request: Request, call_next: Callable):
    """Apply rate limiting to requests."""
    return await rate_limit_middleware(request, call_next)

# Authentication middleware
@app.middleware("http")
async def authenticate_requests(request: Request, call_next: Callable):
    """Authenticate requests with API key."""
    try:
        await verify_api_key(request)
        response = await call_next(request)
        return response
    except Exception as e:
        return JSONResponse(
            status_code=401,
            content={
                "error": "Authentication failed",
                "detail": str(e)
            }
        )

# Logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next: Callable):
    """Log all requests with timing."""
    start_time = time.time()
    request.state.start_time = start_time
    
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    
    with RequestLogger(f"{request.method} {request.url.path}", request_id) as req_log:
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise

# Include routers
app.include_router(health.router)
app.include_router(ephemeris.router)
app.include_router(calendar.router)
app.include_router(motion.router)
app.include_router(yogas.router)
app.include_router(panchanga_precise.router)
app.include_router(chesta_bala.router)
app.include_router(navatara.router)
app.include_router(places.router)

# CORS test endpoint
@app.get("/cors-test")
async def cors_test():
    """Test endpoint to verify CORS configuration."""
    return {
        "message": "CORS is working correctly!",
        "environment": settings.environment,
        "allowed_origin": settings.allowed_origin,
        "cors_origins": settings.cors_origins if settings.environment == "development" else ["<hidden>"],
        "timestamp": time.time()
    }

# Add metrics endpoint
@app.get("/metrics")
async def get_metrics_endpoint():
    """Get application metrics."""
    return get_metrics()

# Add circuit breaker status endpoint
@app.get("/circuit-breaker/status")
async def get_circuit_breaker_status():
    """Get circuit breaker status."""
    cb = get_circuit_breaker()
    return {
        "state": cb.state,
        "failure_count": cb.failure_count,
        "last_failure_time": cb.last_failure_time.isoformat() if cb.last_failure_time else None,
        "next_attempt_time": cb.next_attempt_time.isoformat() if cb.next_attempt_time else None
    }

# Add API info endpoint
@app.get("/info")
async def get_api_info():
    """Get API information and configuration."""
    return {
        "name": "Jyotiṣa API",
        "version": settings.api_version,
        "description": "Vedic astrology API with Swiss Ephemeris",
        "ayanamsa": {
            "type": "True Citra Paksha",
            "description": "All calculations use True Citra Paksha ayanamsa for sidereal coordinates",
            "current_value_2024": "24°11'14\"",
            "swiss_ephemeris_mode": "SIDM_TRUE_CITRA"
        },
        "features": [
            "Precise panchanga calculations",
            "Accurate sunrise/sunset times", 
            "Planetary positions in nakshatras",
            "High-precision astronomical calculations",
            "Percentage remaining for all elements",
            "Frontend-friendly CORS configuration"
        ],
        "cors": {
            "enabled": True,
            "origins_count": len(settings.cors_origins),
            "credentials_allowed": settings.cors_allow_credentials,
            "methods": settings.cors_allow_methods
        },
        "precision": "high",
        "swiss_ephemeris": "enabled"
    }

# CORS preflight handler (handled automatically by FastAPI CORS middleware)
@app.options("/{full_path:path}")
async def cors_preflight_handler(request: Request):
    """Handle CORS preflight requests."""
    return JSONResponse(
        content={"message": "CORS preflight request handled"},
        headers={
            "Access-Control-Allow-Origin": request.headers.get("Origin", "*"),
            "Access-Control-Allow-Methods": ", ".join(settings.cors_allow_methods),
            "Access-Control-Allow-Headers": ", ".join(settings.cors_allow_headers),
            "Access-Control-Allow-Credentials": str(settings.cors_allow_credentials).lower(),
            "Access-Control-Max-Age": str(settings.cors_max_age),
        }
    )

# Add root endpoint with CORS headers
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Jyotiṣa API - Vedic Astrology API",
        "version": settings.api_version,
        "docs": "/docs",
        "health": "/health/healthz",
        "info": "/info",
        "cors_enabled": True,
        "frontend_integration": "Ready for calendar and panchanga display"
    }

# Add health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "api_version": settings.api_version,
        "cors_status": "enabled",
        "swiss_ephemeris": "initialized"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with CORS headers."""
    logger.error(f"Unhandled exception: {exc}")
    
    # Add CORS headers to error responses
    headers = {
        "Access-Control-Allow-Origin": request.headers.get("Origin", "*"),
        "Access-Control-Allow-Credentials": str(settings.cors_allow_credentials).lower(),
    }
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.enable_test_mode else "An unexpected error occurred"
        },
        headers=headers
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
