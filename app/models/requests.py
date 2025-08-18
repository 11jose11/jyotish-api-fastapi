"""Request models for API validation."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator, root_validator


class EphemerisRequest(BaseModel):
    """Ephemeris calculation request."""
    when_utc: Optional[str] = Field(None, description="ISO-8601 timestamp in UTC")
    when_local: Optional[str] = Field(None, description="ISO-8601 timestamp without timezone")
    place_id: Optional[str] = Field(None, description="Google Place ID for local time conversion")
    planets: str = Field(
        default="Sun,Moon,Mercury,Venus,Mars,Jupiter,Saturn,Rahu,Ketu",
        description="Comma-separated list of planets"
    )
    
    @root_validator
    def validate_timestamp_combination(cls, values):
        """Validate timestamp parameters."""
        when_utc = values.get('when_utc')
        when_local = values.get('when_local')
        place_id = values.get('place_id')
        
        if when_utc and (when_local or place_id):
            raise ValueError("Cannot use when_utc with when_local or place_id")
        
        if when_local and not place_id:
            raise ValueError("place_id is required when using when_local")
        
        if not when_utc and not when_local:
            raise ValueError("Either when_utc or when_local must be provided")
        
        return values
    
    @validator('planets')
    def validate_planets(cls, v):
        """Validate planet list."""
        valid_planets = {
            'Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 
            'Jupiter', 'Saturn', 'Rahu', 'Ketu'
        }
        
        planet_list = [p.strip() for p in v.split(',')]
        invalid_planets = [p for p in planet_list if p not in valid_planets]
        
        if invalid_planets:
            raise ValueError(f"Invalid planets: {invalid_planets}")
        
        return v


class CalendarRequest(BaseModel):
    """Calendar request."""
    year: int = Field(..., ge=1900, le=2100, description="Year (1900-2100)")
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    place_id: str = Field(..., min_length=1, description="Google Place ID")
    anchor: str = Field(
        default="sunrise",
        regex="^(sunrise|midnight|noon|custom)$",
        description="Anchor time"
    )
    custom_time: Optional[str] = Field(None, regex="^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    format: str = Field(default="compact", regex="^(compact|detailed)$")
    planets: str = Field(
        default="Sun,Moon,Mercury,Venus,Mars,Jupiter,Saturn,Rahu,Ketu"
    )
    units: str = Field(default="both", regex="^(decimal|dms|both)$")
    
    @validator('custom_time')
    def validate_custom_time(cls, v, values):
        """Validate custom time when anchor is custom."""
        if values.get('anchor') == 'custom' and not v:
            raise ValueError("custom_time is required when anchor is custom")
        return v


class MotionRequest(BaseModel):
    """Motion analysis request."""
    start: str = Field(..., description="Start time in ISO-8601 format")
    end: str = Field(..., description="End time in ISO-8601 format")
    tzname: str = Field(default="UTC", description="Timezone name")
    step_minutes: int = Field(default=60, ge=1, le=1440, description="Step interval in minutes")
    mode: str = Field(default="classic", regex="^(classic|adaptive)$")
    planets: str = Field(default="Mars,Venus", description="Comma-separated list of planets")
    
    @validator('start', 'end')
    def validate_iso_timestamp(cls, v):
        """Validate ISO timestamp format."""
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError("Invalid ISO timestamp format")


class YogaDetectionRequest(BaseModel):
    """Yoga detection request."""
    start: str = Field(..., description="Start date in YYYY-MM-DD format")
    end: str = Field(..., description="End date in YYYY-MM-DD format")
    place_id: str = Field(..., min_length=1, description="Place ID")
    granularity: str = Field(default="day", regex="^(day|intervals)$")
    includeNotes: bool = Field(default=True, description="Include yoga notes")
    
    @validator('start', 'end')
    def validate_date_format(cls, v):
        """Validate date format."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")


class PlaceAutocompleteRequest(BaseModel):
    """Place autocomplete request."""
    q: str = Field(..., min_length=1, max_length=100, description="Search query")
    language: str = Field(default="en", regex="^[a-z]{2}$", description="Language code")


class PlaceResolveRequest(BaseModel):
    """Place resolve request."""
    place_id: str = Field(..., min_length=1, description="Google Place ID")
    timestamp: Optional[int] = Field(None, ge=0, description="Unix timestamp for historical timezone")
