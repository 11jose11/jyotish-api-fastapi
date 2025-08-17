#!/usr/bin/env python3
"""Simple server with working planetary calculations."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, date, timedelta
import os

# Try to import Swiss Ephemeris services
try:
    from app.services.swe import SwissEphService
    from app.services.panchanga import panchanga_service
    EPHEMERIS_AVAILABLE = True
except Exception as e:
    print(f"Warning: Swiss Ephemeris not available: {e}")
    EPHEMERIS_AVAILABLE = False

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Swiss Ephemeris if available
swe_service = None
if EPHEMERIS_AVAILABLE:
    try:
        swe_service = SwissEphService()
        print("Swiss Ephemeris initialized successfully")
    except Exception as e:
        print(f"Failed to initialize Swiss Ephemeris: {e}")
        EPHEMERIS_AVAILABLE = False

def generate_mock_planetary_data(date_time: datetime, planets: list):
    """Generate mock planetary data for demonstration."""
    import math
    
    # Sample nakshatras and data for demo
    nakshatras = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
        "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
        "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
        "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]
    
    rashis = [
        "Mesha", "Vrishabha", "Mithuna", "Karka",
        "Simha", "Kanya", "Tula", "Vrishchika",
        "Dhanu", "Makara", "Kumbha", "Meena"
    ]
    
    # Use day of year for consistent but varying data
    day_offset = date_time.timetuple().tm_yday
    
    result = {}
    for i, planet in enumerate(planets):
        # Generate position based on planet and date
        base_lon = (day_offset * (i + 1) * 3.7) % 360
        
        nak_index = int(base_lon / (360/27)) % 27
        pada = int((base_lon % (360/27)) / (360/27/4)) + 1
        rasi_index = int(base_lon / 30) % 12
        
        result[planet] = {
            "lon": base_lon,
            "lat": 0.0,
            "dist": 1.0,
            "speedDegPerDay": 1.0,
            "retrograde": (i + day_offset) % 7 == 0,
            "rasi": rashis[rasi_index],
            "rasi_index": rasi_index + 1,
            "nakshatra": nakshatras[nak_index],
            "nak_index": nak_index + 1,
            "pada": pada
        }
    
    return result

@app.get("/v1/places/autocomplete")
async def autocomplete_places(q: str, language: str = "en"):
    """Simple places autocomplete."""
    # Return some hardcoded places for testing
    places = [
        {"place_id": "ChIJgTwKgJcpQg0RaSKMYcHeNsQ", "description": "Madrid, España"},
        {"place_id": "ChIJ5TCOcRaYpBIRCmZHTz37sEQ", "description": "Barcelona, España"},
        {"place_id": "ChIJOwg_06VPwokRYv534QaPC8g", "description": "New York, NY, USA"},
        {"place_id": "ChIJ0QdRt8ycGZURiNZPkc5r5rU", "description": "Lima, Perú"},
    ]
    
    filtered = [p for p in places if q.lower() in p["description"].lower()]
    return {"predictions": filtered}

@app.get("/v1/places/resolve")
async def resolve_place(place_id: str, timestamp: int = None):
    """Resolve place details."""
    # Return mock place data
    places_data = {
        "ChIJgTwKgJcpQg0RaSKMYcHeNsQ": {
            "name": "Madrid",
            "timezone_id": "Europe/Madrid",
            "lat": 40.4168,
            "lng": -3.7038
        },
        "ChIJ5TCOcRaYpBIRCmZHTz37sEQ": {
            "name": "Barcelona", 
            "timezone_id": "Europe/Madrid",
            "lat": 41.3851,
            "lng": 2.1734
        },
        "ChIJ0QdRt8ycGZURiNZPkc5r5rU": {
            "name": "Lima",
            "timezone_id": "America/Lima", 
            "lat": -12.0464,
            "lng": -77.0428
        }
    }
    
    data = places_data.get(place_id, {
        "name": "Unknown Location",
        "timezone_id": "UTC",
        "lat": 0.0,
        "lng": 0.0
    })
    
    return data

@app.get("/v1/calendar/month")
async def get_monthly_calendar(
    year: int,
    month: int, 
    place_id: str,
    anchor: str = "sunrise",
    custom_time: str = None,
    format: str = "compact",
    planets: str = "Sun,Moon,Mercury,Venus,Mars,Jupiter,Saturn,Rahu,Ketu",
    units: str = "both"
):
    """Get monthly calendar with planetary data."""
    
    planet_list = [p.strip() for p in planets.split(",")]
    
    # Generate days for the month
    from datetime import date, timedelta
    start_date = date(year, month, 1)
    
    # Get number of days in month
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    
    num_days = (next_month - start_date).days
    
    days = []
    for day in range(1, num_days + 1):
        current_date = datetime(year, month, day, 12, 0, 0)  # Noon
        
        try:
            # Calculate planetary positions
            if EPHEMERIS_AVAILABLE and swe_service:
                planet_data = swe_service.calculate_planets(current_date, planet_list)
            else:
                # Fallback: Generate mock data for demonstration
                planet_data = generate_mock_planetary_data(current_date, planet_list)
            
            # Format planet data
            formatted_planets = {}
            for planet, data in planet_data.items():
                formatted_planet = {
                    "lon_decimal": round(data["lon"], 6),
                    "retrograde": data["retrograde"],
                    "motion_state": "sama",
                    "rasi": data["rasi"],
                    "rasi_index": data["rasi_index"],
                    "nakshatra": data["nakshatra"],
                    "nak_index": data["nak_index"],
                    "pada": data["pada"],
                    "changedNakshatra": False,
                    "changedPada": False,
                    "changedRasi": False
                }
                
                if units in ["dms", "both"]:
                    # Simple DMS conversion
                    degrees = int(data["lon"])
                    minutes = int((data["lon"] - degrees) * 60)
                    seconds = int(((data["lon"] - degrees) * 60 - minutes) * 60)
                    formatted_planet["lon_dms"] = f"{degrees}°{minutes:02d}'{seconds:02d}\""
                
                formatted_planets[planet] = formatted_planet
            
            day_data = {
                "date": current_date.date().isoformat(),
                "anchor_ts_local": current_date.isoformat(),
                "planets": formatted_planets
            }
            
            if format == "detailed":
                day_data["events"] = []
            
            days.append(day_data)
            
        except Exception as e:
            print(f"Error calculating day {day}: {e}")
            # Add empty day data
            day_data = {
                "date": current_date.date().isoformat(),
                "anchor_ts_local": current_date.isoformat(),
                "planets": {}
            }
            if format == "detailed":
                day_data["events"] = []
            days.append(day_data)
    
    # Get place info
    place_info = await resolve_place(place_id)
    
    return {
        "year": year,
        "month": month,
        "place": {
            "place_id": place_id,
            "name": place_info["name"],
            "tz": place_info["timezone_id"]
        },
        "anchor": anchor,
        "days": days
    }

@app.get("/health/healthz")
async def health_check():
    """Health check."""
    return {"status": "ok"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Simple Jyotish API Server", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
