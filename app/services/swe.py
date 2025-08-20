"""Swiss Ephemeris wrapper with Lahiri sidereal mode and optimizations."""

import math
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from functools import lru_cache
import asyncio

import swisseph as swe
from app.config import settings
from app.util.logging import get_logger
from app.services.cache import cache_service, cached

logger = get_logger("swe")

# Planet constants
PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,  # Will be converted to true if needed
    "Ketu": None,  # Calculated as Rahu + 180°
}

# Pre-calculated constants
NAKSHATRA_SPAN = 13 + 1/3  # 13°20'
PADA_SPAN = NAKSHATRA_SPAN / 4  # 3°20'
RASI_SPAN = 30.0

# Rashi (zodiac signs)
RASHIS = [
    "Mesha", "Vrishabha", "Mithuna", "Karka",
    "Simha", "Kanya", "Tula", "Vrishchika",
    "Dhanu", "Makara", "Kumbha", "Meena"
]

# Nakshatras
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]


class SwissEphService:
    """Swiss Ephemeris service with Lahiri sidereal mode and optimizations."""
    
    def __init__(self):
        self.initialized = False
        self.precision = "high"
        self._initialize()
        self._setup_caches()
    
    def _initialize(self):
        """Initialize Swiss Ephemeris with Lahiri sidereal mode."""
        try:
            # Set ephemeris path if provided
            if settings.swiss_ephe_path:
                swe.set_ephe_path(settings.swiss_ephe_path)
                logger.info(f"Using Swiss Ephemeris path: {settings.swiss_ephe_path}")
            else:
                logger.info("Using default Swiss Ephemeris path")
            
            # Set True Citra Paksha sidereal mode (SIDM_TRUE_CITRA = 14)
            swe.set_sid_mode(swe.SIDM_TRUE_CITRA, 0, 0)
            logger.info("Swiss Ephemeris initialized with True Citra Paksha sidereal mode")
            
            # Test calculation to verify setup
            test_jd = swe.julday(2025, 8, 17, 12.0)
            flags = swe.FLG_SIDEREAL | swe.FLG_MOSEPH
            result = swe.calc_ut(test_jd, swe.SUN, flags)
            
            if len(result) >= 1 and isinstance(result[0], (list, tuple)):
                self.initialized = True
                logger.info(f"Swiss Ephemeris test calculation successful: Sun at {result[0][0]:.2f}°")
            else:
                logger.error(f"Swiss Ephemeris test calculation failed: {result}")
                # Try with minimal flags as fallback
                flags_fallback = swe.FLG_MOSEPH
                result_fallback = swe.calc_ut(test_jd, swe.SUN, flags_fallback)
                if len(result_fallback) >= 1 and isinstance(result_fallback[0], (list, tuple)):
                    self.initialized = True
                    logger.info("Swiss Ephemeris initialized with fallback settings")
                else:
                    self.precision = "low"
                
        except Exception as e:
            logger.error(f"Failed to initialize Swiss Ephemeris: {e}")
            # Try one more time with minimal settings
            try:
                swe.set_sid_mode(swe.SIDM_TRUE_CITRA, 0, 0)
                self.initialized = True
                self.precision = "low"
                logger.warning("Swiss Ephemeris initialized with minimal settings")
            except:
                self.precision = "low"
    
    def _setup_caches(self):
        """Setup LRU caches for frequently accessed calculations."""
        self._get_rasi_cached = lru_cache(maxsize=1000)(self._get_rasi_uncached)
        self._get_nakshatra_cached = lru_cache(maxsize=1000)(self._get_nakshatra_uncached)
        self._get_pada_cached = lru_cache(maxsize=1000)(self._get_pada_uncached)
    
    def _get_planet_id(self, planet_name: str) -> Optional[int]:
        """Get Swiss Ephemeris planet ID with caching."""
        planet_name = planet_name.title()
        if planet_name not in PLANETS:
            return None
        
        planet_id = PLANETS[planet_name]
        if planet_name == "Rahu" and settings.node_mode.lower() == "true":
            planet_id = swe.TRUE_NODE
            
        return planet_id
    
    def _get_rasi_uncached(self, longitude: float) -> Tuple[str, int]:
        """Get rashi (zodiac sign) from longitude."""
        rasi_number = int(longitude // RASI_SPAN)
        rasi_name = RASHIS[rasi_number]
        return rasi_name, rasi_number + 1
    
    def _get_nakshatra_uncached(self, longitude: float) -> Tuple[str, int]:
        """Get nakshatra from longitude."""
        nakshatra_number = int(longitude // NAKSHATRA_SPAN)
        nakshatra_name = NAKSHATRAS[nakshatra_number]
        return nakshatra_name, nakshatra_number + 1
    
    def _get_pada_uncached(self, longitude: float) -> int:
        """Get pada from longitude."""
        nakshatra_longitude = longitude % NAKSHATRA_SPAN
        pada = int(nakshatra_longitude // PADA_SPAN) + 1
        return min(max(pada, 1), 4)  # Ensure pada is between 1 and 4
    
    def get_rasi(self, longitude: float) -> Tuple[str, int]:
        """Get rashi (zodiac sign) from longitude with caching."""
        return self._get_rasi_cached(longitude)
    
    def get_nakshatra(self, longitude: float) -> Tuple[str, int, int]:
        """Get nakshatra and pada from longitude with caching."""
        nakshatra_name, nakshatra_number = self._get_nakshatra_cached(longitude)
        pada = self._get_pada_cached(longitude)
        return nakshatra_name, nakshatra_number, pada
    
    def calculate_planet_position(self, jd: float, planet_name: str) -> Dict:
        """Calculate planet position at Julian Day."""
        planet_id = self._get_planet_id(planet_name)
        if planet_id is None:
            raise ValueError(f"Invalid planet: {planet_name}")
        
        # Use sidereal mode for True Citra Paksha Ayanamsa
        flags = swe.FLG_SIDEREAL | swe.FLG_MOSEPH
        
        try:
            result = swe.calc_ut(jd, planet_id, flags)
            
            if len(result) >= 1 and isinstance(result[0], (list, tuple)):
                longitude = result[0][0]
                latitude = result[0][1] if len(result[0]) > 1 else 0.0
                distance = result[0][2] if len(result[0]) > 2 else 0.0
                
                # Get rashi and nakshatra
                rasi_name, rasi_number = self.get_rasi(longitude)
                nakshatra_name, nakshatra_number, pada = self.get_nakshatra(longitude)
                
                return {
                    "longitude": longitude,
                    "latitude": latitude,
                    "distance": distance,
                    "rasi": {
                        "name": rasi_name,
                        "number": rasi_number
                    },
                    "nakshatra": {
                        "name": nakshatra_name,
                        "number": nakshatra_number,
                        "pada": pada
                    }
                }
            else:
                raise Exception(f"Calculation failed for {planet_name}: {result}")
                
        except Exception as e:
            logger.error(f"Error calculating {planet_name}: {e}")
            raise
    
    def calculate_planets(self, dt: datetime, planet_list: Optional[List[str]] = None) -> Dict:
        """Calculate positions for multiple planets."""
        if planet_list is None:
            planet_list = list(PLANETS.keys())
        
        jd = self._get_jd(dt)
        
        results = {}
        for planet in planet_list:
            try:
                if planet == "Ketu":
                    # Calculate Ketu as Rahu + 180°
                    rahu_pos = self.calculate_planet_position(jd, "Rahu")
                    ketu_longitude = (rahu_pos["longitude"] + 180) % 360
                    
                    rasi_name, rasi_number = self.get_rasi(ketu_longitude)
                    nakshatra_name, nakshatra_number, pada = self.get_nakshatra(ketu_longitude)
                    
                    results[planet] = {
                        "longitude": ketu_longitude,
                        "latitude": -rahu_pos["latitude"],  # Ketu has opposite latitude
                        "distance": rahu_pos["distance"],
                        "rasi": {
                            "name": rasi_name,
                            "number": rasi_number
                        },
                        "nakshatra": {
                            "name": nakshatra_name,
                            "number": nakshatra_number,
                            "pada": pada
                        }
                    }
                else:
                    results[planet] = self.calculate_planet_position(jd, planet)
                    
            except Exception as e:
                logger.error(f"Error calculating {planet}: {e}")
                results[planet] = {"error": str(e)}
        
        return results
    
    async def calculate_planets_async(self, dt: datetime, planet_list: Optional[List[str]] = None) -> Dict:
        """Async version of calculate_planets."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.calculate_planets, dt, planet_list
        )
    
    def _get_jd(self, dt: datetime) -> float:
        """Convert datetime to Julian Day."""
        return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0 + dt.second/3600.0)
    
    def calculate_sun_moon_positions(self, dt: datetime) -> Tuple[float, float]:
        """Calculate Sun and Moon longitudes for Panchanga."""
        jd = self._get_jd(dt)
        
        sun_pos = self.calculate_planet_position(jd, "Sun")
        moon_pos = self.calculate_planet_position(jd, "Moon")
        
        return sun_pos["longitude"], moon_pos["longitude"]
    
    async def calculate_sun_moon_positions_async(self, dt: datetime) -> Tuple[float, float]:
        """Async version of calculate_sun_moon_positions."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.calculate_sun_moon_positions, dt
        )
    
    def get_cache_info(self) -> Dict:
        """Get cache statistics."""
        return {
            "rasi_cache": self._get_rasi_cached.cache_info(),
            "nakshatra_cache": self._get_nakshatra_cached.cache_info(),
            "pada_cache": self._get_pada_cached.cache_info()
        }


# Global service instance
swe_service = SwissEphService()
