"""Configuration settings for Jyotiṣa API."""

import os
from typing import Optional, List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Google APIs
    google_maps_api_key: Optional[str] = Field(None, description="Google Maps API key")
    
    # API Authentication
    api_key: Optional[str] = Field(None, description="API key for authentication")
    api_key_header: str = Field("X-API-Key", description="Header name for API key")
    require_api_key: bool = Field(False, description="Whether API key is required")
    
    # Swiss Ephemeris - Lahiri Ayanamsa Configuration
    swiss_ephe_path: Optional[str] = Field(None, description="Path to Swiss Ephemeris files")
    node_mode: str = Field("true", description="Node calculation mode: true or mean")
    ayanamsa_mode: str = Field("lahiri", description="Ayanamsa mode: lahiri, raman, krishnamurti, etc.")
    sidereal_mode: int = Field(1, description="Sidereal mode: 1=Lahiri, 2=Raman, 3=Krishnamurti")
    
    # CORS Configuration
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:3000",  # React/Next.js default
            "http://localhost:3001",  # Alternative React port
            "http://localhost:5173",  # Vite default
            "http://localhost:8080",  # Alternative dev port
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001", 
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8080",
            "https://localhost:3000",  # HTTPS versions
            "https://localhost:3001",
            "https://localhost:5173",
            "https://localhost:8080",
        ],
        description="Allowed CORS origins for frontend"
    )
    cors_allow_credentials: bool = Field(True, description="Allow credentials in CORS")
    cors_allow_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        description="Allowed HTTP methods for CORS"
    )
    cors_allow_headers: List[str] = Field(
        default=[
            "Accept",
            "Accept-Language", 
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-API-Key",
            "X-Requested-With",
            "X-Request-Id",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers"
        ],
        description="Allowed headers for CORS"
    )
    cors_expose_headers: List[str] = Field(
        default=[
            "X-Request-Id",
            "X-Total-Count",
            "X-Page-Count"
        ],
        description="Headers to expose to frontend"
    )
    cors_max_age: int = Field(86400, description="CORS preflight cache time in seconds")
    
    # Redis (optional)
    redis_url: Optional[str] = Field(None, description="Redis URL for caching")
    
    # App settings
    log_level: str = Field("INFO", description="Logging level")
    cache_ttl: int = Field(600, description="Cache TTL in seconds")
    api_version: str = Field("0.2.0", description="API version")
    
    # HTTP client settings
    http_timeout: int = Field(5, description="HTTP timeout in seconds")
    http_connect_timeout: int = Field(3, description="HTTP connect timeout in seconds")
    http_max_retries: int = Field(2, description="Maximum HTTP retries")
    
    # Circuit breaker settings
    circuit_breaker_failure_threshold: int = Field(5, description="Circuit breaker failure threshold")
    circuit_breaker_timeout: int = Field(30, description="Circuit breaker timeout in seconds")
    
    # Performance settings
    enable_async: bool = Field(True, description="Enable async operations")
    enable_caching: bool = Field(True, description="Enable caching")
    enable_metrics: bool = Field(True, description="Enable metrics collection")
    max_concurrent_requests: int = Field(100, description="Maximum concurrent requests")
    batch_size_limit: int = Field(50, description="Maximum batch size for calculations")
    
    # Cache settings
    ephemeris_cache_ttl: int = Field(300, description="Ephemeris cache TTL in seconds")
    place_cache_ttl: int = Field(3600, description="Place cache TTL in seconds")
    panchanga_cache_ttl: int = Field(600, description="Panchanga cache TTL in seconds")
    
    # Rate limiting
    rate_limit_requests_per_minute: int = Field(60, description="Rate limit requests per minute")
    rate_limit_burst: int = Field(10, description="Rate limit burst allowance")
    
    # Testing settings
    enable_test_mode: bool = Field(False, description="Enable test mode for development")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }


# Global settings instance
settings = Settings()
