"""Main FastAPI application for Jyotiṣa API."""

import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.util.logging import setup_logging, get_logger, RequestLogger
from app.routers import health, places, ephemeris, calendar, motion, yogas

# Setup logging
setup_logging()
logger = get_logger("main")

# Create FastAPI app
app = FastAPI(
    title="Jyotiṣa API",
    description="Vedic astrology API with Swiss Ephemeris and Google APIs",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next: Callable):
    """Log all requests with timing."""
    start_time = time.time()
    
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
app.include_router(places.router)
app.include_router(ephemeris.router)
app.include_router(calendar.router)
app.include_router(motion.router)
app.include_router(yogas.router)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Jyotiṣa API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health/healthz"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    request_id = getattr(request.state, 'request_id', None)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "request_id": request_id
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
