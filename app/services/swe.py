"""Swiss Ephemeris wrapper with Lahiri sidereal mode."""

import math
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import swisseph as swe
from app.config import settings
from app.util.logging import get_logger

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
    """Swiss Ephemeris service with Lahiri sidereal mode."""
    
    def __init__(self):
        self.initialized = False
        self.precision = "high"
        self._initialize()
    
    def _initialize(self):
        """Initialize Swiss Ephemeris with Lahiri sidereal mode."""
        try:
            # Set ephemeris path if provided
            if settings.swiss_ephe_path:
                swe.set_ephe_path(settings.swiss_ephe_path)
                logger.info(f"Using Swiss Ephemeris path: {settings.swiss_ephe_path}")
            else:
                logger.warning("No SWISS_EPHE_PATH set, using default path")
            
            # Set Lahiri sidereal mode
            swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
            logger.info("Swiss Ephemeris initialized with Lahiri sidereal mode")
            
            # Test calculation to verify setup
            test_jd = swe.julday(2024, 1, 1, 12.0)
            flags = swe.FLG_SIDEREAL
            result = swe.calc_ut(test_jd, swe.SUN, flags)
            
            if result[0] == 0:  # Success
                self.initialized = True
                logger.info("Swiss Ephemeris test calculation successful")
            else:
                logger.error(f"Swiss Ephemeris test calculation failed: {result[0]}")
                self.precision = "low"
                
        except Exception as e:
            logger.error(f"Failed to initialize Swiss Ephemeris: {e}")
            self.precision = "low"
    
    def _get_planet_id(self, planet_name: str) -> int:
        """Get Swiss Ephemeris planet ID."""
        planet_name = planet_name.title()
        if planet_name not in PLANETS:
            raise ValueError(f"Unknown planet: {planet_name}")
        
        planet_id = PLANETS[planet_name]
        if planet_name == "Rahu":
            # Use true or mean nodes based on settings
            if settings.node_mode.lower() == "true":
                planet_id = swe.TRUE_NODE
        elif planet_name == "Ketu":
            # Ketu is calculated as Rahu + 180°
            return None
            
        return planet_id
    
    def _calculate_ketu(self, rahu_lon: float) -> float:
        """Calculate Ketu longitude (Rahu + 180°)."""
        return (rahu_lon + 180.0) % 360.0
    
    def calculate_planets(
        self, 
        dt: datetime, 
        planets: Optional[List[str]] = None
    ) -> Dict[str, Dict]:
        """Calculate planetary positions for given datetime."""
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
        flags = swe.FLG_SIDEREAL
        
        # Calculate Rahu first if needed for Ketu
        rahu_lon = None
        if "Ketu" in planets and "Rahu" not in planets:
            rahu_planet_id = self._get_planet_id("Rahu")
            if rahu_planet_id:
                rahu_result = swe.calc_ut(jd, rahu_planet_id, flags)
                if rahu_result[0] == 0:
                    rahu_lon = rahu_result[0]
        
        for planet_name in planets:
            try:
                planet_id = self._get_planet_id(planet_name)
                
                if planet_name == "Ketu":
                    if rahu_lon is None:
                        # Calculate Rahu for Ketu
                        rahu_planet_id = self._get_planet_id("Rahu")
                        if rahu_planet_id:
                            rahu_result = swe.calc_ut(jd, rahu_planet_id, flags)
                            if rahu_result[0] == 0:
                                rahu_lon = rahu_result[0]
                    
                    if rahu_lon is not None:
                        ketu_lon = self._calculate_ketu(rahu_lon)
                        results[planet_name] = {
                            "lon": ketu_lon,
                            "lat": 0.0,  # Ketu has no latitude
                            "dist": 0.0,  # Ketu has no distance
                            "speedDegPerDay": 0.0,  # Ketu moves with Rahu
                            "retrograde": False,
                            "rasi": self._get_rasi(ketu_lon),
                            "rasi_index": self._get_rasi_index(ketu_lon),
                            "nakshatra": self._get_nakshatra(ketu_lon),
                            "nak_index": self._get_nakshatra_index(ketu_lon),
                            "pada": self._get_pada(ketu_lon)
                        }
                    continue
                
                if planet_id is None:
                    continue
                
                # Calculate planet position
                result = swe.calc_ut(jd, planet_id, flags)
                
                if result[0] == 0:  # Success
                    lon = result[0]
                    lat = result[1]
                    dist = result[2]
                    
                    # Calculate speed (approximate)
                    jd_next = jd + 1.0  # Next day
                    result_next = swe.calc_ut(jd_next, planet_id, flags)
                    if result_next[0] == 0:
                        speed = (result_next[0] - lon) % 360.0
                        if speed > 180:
                            speed -= 360
                    else:
                        speed = 0.0
                    
                    # Determine if retrograde
                    retrograde = speed < 0
                    
                    results[planet_name] = {
                        "lon": lon,
                        "lat": lat,
                        "dist": dist,
                        "speedDegPerDay": abs(speed),
                        "retrograde": retrograde,
                        "rasi": self._get_rasi(lon),
                        "rasi_index": self._get_rasi_index(lon),
                        "nakshatra": self._get_nakshatra(lon),
                        "nak_index": self._get_nakshatra_index(lon),
                        "pada": self._get_pada(lon)
                    }
                else:
                    logger.error(f"Failed to calculate {planet_name}: {result[0]}")
                    
            except Exception as e:
                logger.error(f"Error calculating {planet_name}: {e}")
        
        return results
    
    def _get_rasi(self, lon: float) -> str:
        """Get rashi name from longitude."""
        rasi_index = self._get_rasi_index(lon)
        return RASHIS[rasi_index - 1]
    
    def _get_rasi_index(self, lon: float) -> int:
        """Get rashi index (1-12) from longitude."""
        return int(lon // 30) + 1
    
    def _get_nakshatra(self, lon: float) -> str:
        """Get nakshatra name from longitude."""
        nak_index = self._get_nakshatra_index(lon)
        return NAKSHATRAS[nak_index - 1]
    
    def _get_nakshatra_index(self, lon: float) -> int:
        """Get nakshatra index (1-27) from longitude."""
        # Each nakshatra spans 13°20' = 13.333... degrees
        return int(lon // (13 + 1/3)) + 1
    
    def _get_pada(self, lon: float) -> int:
        """Get pada (1-4) from longitude."""
        # Each pada spans 3°20' = 3.333... degrees
        nakshatra_lon = lon % (13 + 1/3)
        return int(nakshatra_lon // (3 + 1/3)) + 1
    
    def calculate_tithi(self, sun_lon: float, moon_lon: float) -> int:
        """Calculate tithi (1-30) from Sun and Moon longitudes."""
        diff = (moon_lon - sun_lon) % 360
        return int(diff // 12) + 1
    
    def calculate_panchanga(
        self, 
        dt: datetime, 
        planets: Optional[List[str]] = None
    ) -> Dict:
        """Calculate panchanga elements."""
        planet_data = self.calculate_planets(dt, planets or ["Sun", "Moon"])
        
        sun_lon = planet_data["Sun"]["lon"]
        moon_lon = planet_data["Moon"]["lon"]
        
        tithi = self.calculate_tithi(sun_lon, moon_lon)
        nakshatra = planet_data["Moon"]["nakshatra"]
        nak_index = planet_data["Moon"]["nak_index"]
        pada = planet_data["Moon"]["pada"]
        
        return {
            "tithi": tithi,
            "nakshatra": {
                "index": nak_index,
                "name": nakshatra,
                "pada": pada
            }
        }


# Global service instance
swe_service = SwissEphService()
