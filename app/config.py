"""Configuration settings for Jyotiṣa API."""

import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Google APIs
    google_maps_api_key: Optional[str] = Field(None, description="Google Maps API key")
    
    # Swiss Ephemeris
    swiss_ephe_path: Optional[str] = Field(None, description="Path to Swiss Ephemeris files")
    node_mode: str = Field("true", description="Node calculation mode: true or mean")
    
    # Redis (optional)
    redis_url: Optional[str] = Field(None, description="Redis URL for caching")
    
    # App settings
    log_level: str = Field("INFO", description="Logging level")
    cache_ttl: int = Field(600, description="Cache TTL in seconds")
    
    # HTTP client settings
    http_timeout: int = Field(5, description="HTTP timeout in seconds")
    http_connect_timeout: int = Field(3, description="HTTP connect timeout in seconds")
    http_max_retries: int = Field(2, description="Maximum HTTP retries")
    
    # Circuit breaker settings
    circuit_breaker_failure_threshold: int = Field(5, description="Circuit breaker failure threshold")
    circuit_breaker_timeout: int = Field(30, description="Circuit breaker timeout in seconds")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
