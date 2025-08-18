"""Optimized Swiss Ephemeris service with caching and performance improvements."""

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

logger = get_logger("swe_optimized")

# Planet constants
PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,
    "Ketu": None,
}

# Pre-calculated constants
NAKSHATRA_SPAN = 13 + 1/3  # 13°20'
PADA_SPAN = NAKSHATRA_SPAN / 4  # 3°20'
RASI_SPAN = 30.0

# Pre-calculated arrays for faster lookups
RASHIS = [
    "Mesha", "Vrishabha", "Mithuna", "Karka",
    "Simha", "Kanya", "Tula", "Vrishchika",
    "Dhanu", "Makara", "Kumbha", "Meena"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]


class OptimizedSwissEphService:
    """Optimized Swiss Ephemeris service with caching and performance improvements."""
    
    def __init__(self):
        self.initialized = False
        self.precision = "high"
        self._initialize()
        self._setup_caches()
    
    def _initialize(self):
        """Initialize Swiss Ephemeris with optimizations."""
        try:
            if settings.swiss_ephe_path:
                swe.set_ephe_path(settings.swiss_ephe_path)
            
            # Set Lahiri sidereal mode
            swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
            
            # Test calculation
            test_jd = swe.julday(2025, 8, 17, 12.0)
            flags = swe.FLG_SIDEREAL | swe.FLG_MOSEPH
            result = swe.calc_ut(test_jd, swe.SUN, flags)
            
            if len(result) >= 1 and not isinstance(result[0], int):
                self.initialized = True
                logger.info("Optimized Swiss Ephemeris initialized successfully")
            else:
                self.precision = "low"
                
        except Exception as e:
            logger.error(f"Failed to initialize Swiss Ephemeris: {e}")
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
        """Get rashi without caching."""
        rasi_index = int(longitude // RASI_SPAN) + 1
        if rasi_index > 12:
            rasi_index = 12
        return RASHIS[rasi_index - 1], rasi_index
    
    def _get_rasi(self, longitude: float) -> Tuple[str, int]:
        """Get rashi with caching."""
        return self._get_rasi_cached(longitude)
    
    def _get_nakshatra_uncached(self, longitude: float) -> Tuple[str, int]:
        """Get nakshatra without caching."""
        nak_index = int(longitude // NAKSHATRA_SPAN) + 1
        if nak_index > 27:
            nak_index = 27
        return NAKSHATRAS[nak_index - 1], nak_index
    
    def _get_nakshatra(self, longitude: float) -> Tuple[str, int]:
        """Get nakshatra with caching."""
        return self._get_nakshatra_cached(longitude)
    
    def _get_pada_uncached(self, longitude: float) -> int:
        """Get pada without caching."""
        nakshatra_lon = longitude % NAKSHATRA_SPAN
        pada = int(nakshatra_lon // PADA_SPAN) + 1
        return min(max(pada, 1), 4)
    
    def _get_pada(self, longitude: float) -> int:
        """Get pada with caching."""
        return self._get_pada_cached(longitude)
    
    def _calculate_ketu(self, rahu_lon: float) -> float:
        """Calculate Ketu longitude."""
        return (rahu_lon + 180.0) % 360.0
    
    @cached("planets", 300)  # Cache for 5 minutes
    async def calculate_planets_async(
        self, 
        dt: datetime, 
        planets: Optional[List[str]] = None
    ) -> Dict[str, Dict]:
        """Calculate planetary positions asynchronously with caching."""
        return self.calculate_planets(dt, planets)
    
    def calculate_planets(
        self, 
        dt: datetime, 
        planets: Optional[List[str]] = None
    ) -> Dict[str, Dict]:
        """Calculate planetary positions with optimizations."""
        if not self.initialized:
            raise RuntimeError("Swiss Ephemeris not initialized")
        
        if planets is None:
            planets = list(PLANETS.keys())
        
        # Convert datetime to Julian Day
        jd = swe.julday(
            dt.year, dt.month, dt.day,
            dt.hour + dt.minute / 60.0 + dt.second / 3600.0
        )
        
        results = {}
        flags = swe.FLG_SIDEREAL | swe.FLG_MOSEPH
        
        # Pre-calculate Rahu if needed for Ketu
        rahu_lon = None
        if "Ketu" in planets and "Rahu" not in planets:
            rahu_planet_id = self._get_planet_id("Rahu")
            if rahu_planet_id:
                rahu_result = swe.calc_ut(jd, rahu_planet_id, flags)
                if len(rahu_result) >= 2 and len(rahu_result[0]) >= 1:
                    rahu_lon = rahu_result[0][0]
        
        # Batch calculate for better performance
        planet_calculations = []
        for planet_name in planets:
            if planet_name == "Ketu":
                continue
            planet_id = self._get_planet_id(planet_name)
            if planet_id:
                planet_calculations.append((planet_name, planet_id))
        
        # Calculate all planets in batch
        for planet_name, planet_id in planet_calculations:
            try:
                result = swe.calc_ut(jd, planet_id, flags)
                
                if len(result) >= 2 and len(result[0]) >= 3:
                    lon = result[0][0]
                    lat = result[0][1]
                    dist = result[0][2]
                    
                    # Calculate speed efficiently
                    speed = self._calculate_speed(jd, planet_id, flags)
                    retrograde = speed < 0
                    
                    # Get rashi and nakshatra with caching
                    rashi_name, rashi_index = self._get_rasi(lon)
                    nakshatra_name, nakshatra_index = self._get_nakshatra(lon)
                    pada = self._get_pada(lon)
                    
                    results[planet_name] = {
                        "lon": lon,
                        "lat": lat,
                        "dist": dist,
                        "speedDegPerDay": abs(speed),
                        "retrograde": retrograde,
                        "motion_state": "vakri" if retrograde else "sama",
                        "rasi": rashi_name,
                        "rasi_index": rashi_index,
                        "nakshatra": nakshatra_name,
                        "nak_index": nakshatra_index,
                        "pada": pada
                    }
                    
            except Exception as e:
                logger.error(f"Error calculating {planet_name}: {e}")
        
        # Handle Ketu calculation
        if "Ketu" in planets:
            if rahu_lon is None:
                rahu_planet_id = self._get_planet_id("Rahu")
                if rahu_planet_id:
                    rahu_result = swe.calc_ut(jd, rahu_planet_id, flags)
                    if len(rahu_result) >= 2 and len(rahu_result[0]) >= 1:
                        rahu_lon = rahu_result[0][0]
            
            if rahu_lon is not None:
                ketu_lon = self._calculate_ketu(rahu_lon)
                rashi_name, rashi_index = self._get_rasi(ketu_lon)
                nakshatra_name, nakshatra_index = self._get_nakshatra(ketu_lon)
                pada = self._get_pada(ketu_lon)
                
                results["Ketu"] = {
                    "lon": ketu_lon,
                    "lat": 0.0,
                    "dist": 0.0,
                    "speedDegPerDay": 0.0,
                    "retrograde": False,
                    "motion_state": "sama",
                    "rasi": rashi_name,
                    "rasi_index": rashi_index,
                    "nakshatra": nakshatra_name,
                    "nak_index": nakshatra_index,
                    "pada": pada
                }
        
        return results
    
    def _calculate_speed(self, jd: float, planet_id: int, flags: int) -> float:
        """Calculate planetary speed efficiently."""
        try:
            # Calculate position at current time
            result1 = swe.calc_ut(jd, planet_id, flags)
            if len(result1) < 2 or len(result1[0]) < 1:
                return 0.0
            
            # Calculate position 1 day later
            result2 = swe.calc_ut(jd + 1.0, planet_id, flags)
            if len(result2) < 2 or len(result2[0]) < 1:
                return 0.0
            
            # Calculate speed
            speed = (result2[0][0] - result1[0][0]) % 360.0
            if speed > 180:
                speed -= 360
            
            return speed
            
        except Exception:
            return 0.0
    
    @cached("panchanga", 600)  # Cache for 10 minutes
    async def calculate_panchanga_async(
        self, 
        dt: datetime, 
        planets: List[str] = None
    ) -> Dict:
        """Calculate panchanga asynchronously with caching."""
        return self.calculate_panchanga(dt, planets)
    
    def calculate_panchanga(
        self, 
        dt: datetime, 
        planets: List[str] = None
    ) -> Dict:
        """Calculate panchanga elements efficiently."""
        if planets is None:
            planets = ["Sun", "Moon"]
        
        planet_data = self.calculate_planets(dt, planets)
        
        if "Sun" not in planet_data or "Moon" not in planet_data:
            raise ValueError("Sun and Moon positions required for panchanga")
        
        sun_lon = planet_data["Sun"]["lon"]
        moon_lon = planet_data["Moon"]["lon"]
        
        # Calculate tithi
        diff = (moon_lon - sun_lon) % 360
        tithi = int(diff // 12) + 1
        
        # Get nakshatra and pada
        nakshatra_name, nakshatra_index = self._get_nakshatra(moon_lon)
        pada = self._get_pada(moon_lon)
        
        # Get rashi
        rashi_name, rashi_index = self._get_rasi(moon_lon)
        
        return {
            "tithi": tithi,
            "nakshatra": nakshatra_name,
            "nak_index": nakshatra_index,
            "pada": pada,
            "rasi": rashi_name,
            "rasi_index": rashi_index,
            "sun_lon": sun_lon,
            "moon_lon": moon_lon
        }
    
    def clear_caches(self):
        """Clear all LRU caches."""
        self._get_rasi_cached.cache_clear()
        self._get_nakshatra_cached.cache_clear()
        self._get_pada_cached.cache_clear()
        logger.info("Swiss Ephemeris caches cleared")


# Global optimized service instance
swe_optimized_service = OptimizedSwissEphService()
