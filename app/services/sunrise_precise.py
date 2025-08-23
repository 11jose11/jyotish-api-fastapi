"""Precise sunrise calculation service using Swiss Ephemeris."""

import swisseph as swe
from datetime import datetime, timedelta
from typing import Tuple, Optional
import math

from app.util.logging import get_logger

logger = get_logger("sunrise_precise")


class PreciseSunriseService:
    """Service for precise sunrise/sunset calculations using Swiss Ephemeris."""
    
    def __init__(self):
        # Set Swiss Ephemeris path if needed
        # swe.set_ephe_path('/path/to/ephemeris')
        pass
    
    def calculate_sunrise_sunset(
        self, 
        date: datetime, 
        latitude: float, 
        longitude: float, 
        altitude: float = 0.0
    ) -> Tuple[datetime, datetime]:
        """
        Calculate precise sunrise and sunset times for a given date and location.
        
        Args:
            date: Date for calculation
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            altitude: Altitude above sea level in meters
            
        Returns:
            Tuple of (sunrise_time, sunset_time) as datetime objects
        """
        try:
            # Convert date to Julian Day Number
            jd = self._datetime_to_jd(date)
            
            # Calculate sunrise
            sunrise_jd = self._calculate_sunrise_jd(jd, latitude, longitude, altitude)
            sunrise_dt = self._jd_to_datetime(sunrise_jd)
            
            # Calculate sunset
            sunset_jd = self._calculate_sunset_jd(jd, latitude, longitude, altitude)
            sunset_dt = self._jd_to_datetime(sunset_jd)
            
            return sunrise_dt, sunset_dt
            
        except Exception as e:
            logger.error(f"Error calculating sunrise/sunset: {e}")
            # Fallback to approximate calculation
            return self._fallback_sunrise_sunset(date, latitude, longitude)
    
    def calculate_sunrise(
        self, 
        date: datetime, 
        latitude: float, 
        longitude: float, 
        altitude: float = 0.0
    ) -> datetime:
        """Calculate precise sunrise time."""
        sunrise_dt, _ = self.calculate_sunrise_sunset(date, latitude, longitude, altitude)
        return sunrise_dt
    
    def calculate_sunset(
        self, 
        date: datetime, 
        latitude: float, 
        longitude: float, 
        altitude: float = 0.0
    ) -> datetime:
        """Calculate precise sunset time."""
        _, sunset_dt = self.calculate_sunrise_sunset(date, latitude, longitude, altitude)
        return sunset_dt
    
    def _calculate_sunrise_jd(
        self, 
        jd: float, 
        latitude: float, 
        longitude: float, 
        altitude: float
    ) -> float:
        """Calculate Julian Day Number for sunrise."""
        try:
            # Calculate sunrise
            result = swe.rise_trans(
                swe.SUN,  # Sun
                jd,       # Julian Day Number
                longitude, latitude, altitude,  # Location
                swe.CALC_RISE,  # Calculate rise time
                0  # No additional flags
            )
            
            if result[0] == 0:  # Success
                return result[1][0]  # Return sunrise Julian Day
            else:
                raise ValueError(f"Sunrise calculation failed: {result[0]}")
        except Exception as e:
            logger.error(f"Sunrise calculation error: {e}")
            raise
    
    def _calculate_sunset_jd(
        self, 
        jd: float, 
        latitude: float, 
        longitude: float, 
        altitude: float
    ) -> float:
        """Calculate Julian Day Number for sunset."""
        try:
            # Calculate sunset
            result = swe.rise_trans(
                swe.SUN,  # Sun
                jd,       # Julian Day Number
                longitude, latitude, altitude,  # Location
                swe.CALC_SET,  # Calculate set time
                0  # No additional flags
            )
            
            if result[0] == 0:  # Success
                return result[1][0]  # Return sunset Julian Day
            else:
                raise ValueError(f"Sunset calculation failed: {result[0]}")
        except Exception as e:
            logger.error(f"Sunset calculation error: {e}")
            raise
    
    def _datetime_to_jd(self, dt: datetime) -> float:
        """Convert datetime to Julian Day Number."""
        # Convert to UTC if timezone aware
        if dt.tzinfo is not None:
            dt = dt.astimezone().replace(tzinfo=None)
        
        # Convert to Julian Day
        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0 + dt.second/3600.0)
        return jd
    
    def _jd_to_datetime(self, jd: float) -> datetime:
        """Convert Julian Day Number to datetime."""
        try:
            # Convert Julian Day to calendar date and time
            year, month, day, hour = swe.revjul(jd)
            
            # Convert hour to hours, minutes, seconds
            hours = int(hour)
            minutes = int((hour - hours) * 60)
            seconds = int(((hour - hours) * 60 - minutes) * 60)
            
            return datetime(year, month, day, hours, minutes, seconds)
        except Exception as e:
            logger.error(f"Error converting JD to datetime: {e}")
            # Fallback to current date
            return datetime.now()
    
    def _fallback_sunrise_sunset(
        self, 
        date: datetime, 
        latitude: float, 
        longitude: float
    ) -> Tuple[datetime, datetime]:
        """Fallback calculation using simplified astronomical formulas."""
        try:
            # Simplified sunrise/sunset calculation
            # This is a basic implementation - for production, use more sophisticated algorithms
            
            # Approximate sunrise at 6 AM local time
            sunrise = date.replace(hour=6, minute=0, second=0, microsecond=0)
            
            # Approximate sunset at 6 PM local time
            sunset = date.replace(hour=18, minute=0, second=0, microsecond=0)
            
            # Adjust based on latitude and season (simplified)
            day_of_year = date.timetuple().tm_yday
            
            # Simple seasonal adjustment
            if latitude > 0:  # Northern hemisphere
                if day_of_year < 80 or day_of_year > 266:  # Winter
                    sunrise = sunrise - timedelta(hours=1)
                    sunset = sunset - timedelta(hours=1)
                elif day_of_year > 172 and day_of_year < 266:  # Summer
                    sunrise = sunrise + timedelta(hours=1)
                    sunset = sunset + timedelta(hours=1)
            else:  # Southern hemisphere
                if day_of_year > 172 and day_of_year < 266:  # Winter
                    sunrise = sunrise - timedelta(hours=1)
                    sunset = sunset - timedelta(hours=1)
                elif day_of_year < 80 or day_of_year > 266:  # Summer
                    sunrise = sunrise + timedelta(hours=1)
                    sunset = sunset + timedelta(hours=1)
            
            return sunrise, sunset
            
        except Exception as e:
            logger.error(f"Fallback sunrise calculation failed: {e}")
            # Ultimate fallback
            sunrise = date.replace(hour=6, minute=0, second=0, microsecond=0)
            sunset = date.replace(hour=18, minute=0, second=0, microsecond=0)
            return sunrise, sunset


# Create service instance
precise_sunrise_service = PreciseSunriseService()
