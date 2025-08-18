"""Panchanga service for tithi, nakshatra, and rashi calculations."""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from app.services.swe import swe_service
from app.util.logging import get_logger

logger = get_logger("panchanga")


class PanchangaService:
    """Service for panchanga calculations."""
    
    def __init__(self):
        self.swe_service = swe_service
    
    def to_dms(self, decimal_degrees: float) -> str:
        """Convert decimal degrees to DMS format."""
        degrees = int(decimal_degrees)
        minutes_decimal = (decimal_degrees - degrees) * 60
        minutes = int(minutes_decimal)
        seconds = (minutes_decimal - minutes) * 60
        
        return f"{degrees}°{minutes:02d}'{seconds:04.1f}\""
    
    def get_rasi(self, longitude: float) -> Tuple[str, int]:
        """Get rashi name and index from longitude."""
        rasi_index = int(longitude // 30) + 1
        rasis = [
            "Mesha", "Vrishabha", "Mithuna", "Karka",
            "Simha", "Kanya", "Tula", "Vrishchika",
            "Dhanu", "Makara", "Kumbha", "Meena"
        ]
        return rasis[rasi_index - 1], rasi_index
    
    def get_nakshatra(self, longitude: float) -> Tuple[str, int, int]:
        """Get nakshatra name, index, and pada from longitude."""
        # Each nakshatra spans 13°20' = 13.333... degrees
        nakshatra_span = 13 + 1/3
        nak_index = int(longitude // nakshatra_span) + 1
        
        nakshatras = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
            "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]
        
        # Calculate pada
        nakshatra_lon = longitude % nakshatra_span
        pada_span = nakshatra_span / 4  # 3°20' = 3.333... degrees
        pada = int(nakshatra_lon // pada_span) + 1
        
        # Ensure pada is within 1-4 range
        if pada > 4:
            pada = 4
        elif pada < 1:
            pada = 1
        
        return nakshatras[nak_index - 1], nak_index, pada
    
    def calculate_tithi(self, sun_lon: float, moon_lon: float) -> int:
        """Calculate tithi (1-30) from Sun and Moon longitudes."""
        diff = (moon_lon - sun_lon) % 360
        return int(diff // 12) + 1
    
    def find_tithi_changes(
        self, 
        date: datetime, 
        place_info: Dict,
        precision_minutes: int = 2
    ) -> List[Dict]:
        """Find exact tithi change times for a day."""
        changes = []
        
        # Start at midnight local time
        start_dt = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = start_dt + timedelta(days=1)
        
        # Sample every hour to find potential changes
        current_dt = start_dt
        prev_tithi = None
        
        while current_dt < end_dt:
            try:
                planet_data = self.swe_service.calculate_planets(current_dt, ["Sun", "Moon"])
                sun_lon = planet_data["Sun"]["lon"]
                moon_lon = planet_data["Moon"]["lon"]
                current_tithi = self.calculate_tithi(sun_lon, moon_lon)
                
                if prev_tithi is not None and prev_tithi != current_tithi:
                    # Binary search for exact change time
                    change_dt = self._binary_search_tithi_change(
                        current_dt - timedelta(hours=1),
                        current_dt,
                        precision_minutes
                    )
                    
                    if change_dt:
                        changes.append({
                            "tithi": current_tithi,
                            "start": change_dt.isoformat(),
                            "end": None  # Will be set by next change
                        })
                
                prev_tithi = current_tithi
                current_dt += timedelta(hours=1)
                
            except Exception as e:
                logger.error(f"Error calculating tithi changes: {e}")
                current_dt += timedelta(hours=1)
        
        # Set end times
        for i in range(len(changes) - 1):
            changes[i]["end"] = changes[i + 1]["start"]
        
        if changes:
            changes[-1]["end"] = end_dt.isoformat()
        
        return changes
    
    def find_nakshatra_changes(
        self, 
        date: datetime, 
        place_info: Dict,
        precision_minutes: int = 2
    ) -> List[Dict]:
        """Find exact nakshatra change times for a day."""
        changes = []
        
        # Start at midnight local time
        start_dt = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = start_dt + timedelta(days=1)
        
        # Sample every hour to find potential changes
        current_dt = start_dt
        prev_nakshatra = None
        
        while current_dt < end_dt:
            try:
                planet_data = self.swe_service.calculate_planets(current_dt, ["Moon"])
                moon_lon = planet_data["Moon"]["lon"]
                current_nakshatra, nak_index, pada = self.get_nakshatra(moon_lon)
                
                if prev_nakshatra is not None and prev_nakshatra != current_nakshatra:
                    # Binary search for exact change time
                    change_dt = self._binary_search_nakshatra_change(
                        current_dt - timedelta(hours=1),
                        current_dt,
                        precision_minutes
                    )
                    
                    if change_dt:
                        # Get nakshatra details at change time
                        change_data = self.swe_service.calculate_planets(change_dt, ["Moon"])
                        change_lon = change_data["Moon"]["lon"]
                        _, change_nak_index, change_pada = self.get_nakshatra(change_lon)
                        
                        changes.append({
                            "nakshatra": {
                                "index": change_nak_index,
                                "name": current_nakshatra,
                                "pada": change_pada
                            },
                            "start": change_dt.isoformat(),
                            "end": None  # Will be set by next change
                        })
                
                prev_nakshatra = current_nakshatra
                current_dt += timedelta(hours=1)
                
            except Exception as e:
                logger.error(f"Error calculating nakshatra changes: {e}")
                current_dt += timedelta(hours=1)
        
        # Set end times
        for i in range(len(changes) - 1):
            changes[i]["end"] = changes[i + 1]["start"]
        
        if changes:
            changes[-1]["end"] = end_dt.isoformat()
        
        return changes
    
    def _binary_search_tithi_change(
        self,
        start_dt: datetime,
        end_dt: datetime,
        precision_minutes: int
    ) -> Optional[datetime]:
        """Binary search for exact tithi change time."""
        while (end_dt - start_dt).total_seconds() > precision_minutes * 60:
            mid_dt = start_dt + (end_dt - start_dt) / 2
            
            try:
                start_data = self.swe_service.calculate_planets(start_dt, ["Sun", "Moon"])
                mid_data = self.swe_service.calculate_planets(mid_dt, ["Sun", "Moon"])
                
                start_tithi = self.calculate_tithi(start_data["Sun"]["lon"], start_data["Moon"]["lon"])
                mid_tithi = self.calculate_tithi(mid_data["Sun"]["lon"], mid_data["Moon"]["lon"])
                
                if start_tithi != mid_tithi:
                    end_dt = mid_dt
                else:
                    start_dt = mid_dt
                    
            except Exception:
                return None
        
        return start_dt
    
    def _binary_search_nakshatra_change(
        self,
        start_dt: datetime,
        end_dt: datetime,
        precision_minutes: int
    ) -> Optional[datetime]:
        """Binary search for exact nakshatra change time."""
        while (end_dt - start_dt).total_seconds() > precision_minutes * 60:
            mid_dt = start_dt + (end_dt - start_dt) / 2
            
            try:
                start_data = self.swe_service.calculate_planets(start_dt, ["Moon"])
                mid_data = self.swe_service.calculate_planets(mid_dt, ["Moon"])
                
                start_nak = self.get_nakshatra(start_data["Moon"]["lon"])[1]
                mid_nak = self.get_nakshatra(mid_data["Moon"]["lon"])[1]
                
                if start_nak != mid_nak:
                    end_dt = mid_dt
                else:
                    start_dt = mid_dt
                    
            except Exception:
                return None
        
        return start_dt
    
    def get_daily_panchanga(
        self, 
        date: datetime, 
        place_info: Dict
    ) -> Dict:
        """Get complete panchanga for a day."""
        try:
            # Calculate planetary positions
            planet_data = self.swe_service.calculate_planets(date, ["Sun", "Moon"])
            
            sun_lon = planet_data["Sun"]["lon"]
            moon_lon = planet_data["Moon"]["lon"]
            
            # Calculate tithi
            tithi = self.calculate_tithi(sun_lon, moon_lon)
            
            # Calculate nakshatra
            nakshatra, nak_index, pada = self.get_nakshatra(moon_lon)
            
            # Find exact windows
            tithi_windows = self.find_tithi_changes(date, place_info)
            nakshatra_windows = self.find_nakshatra_changes(date, place_info)
            
            return {
                "date": date.date().isoformat(),
                "tithi": tithi,
                "nakshatra": {
                    "index": nak_index,
                    "name": nakshatra,
                    "pada": pada
                },
                "tithi_windows": tithi_windows,
                "nakshatra_windows": nakshatra_windows
            }
            
        except Exception as e:
            logger.error(f"Error calculating daily panchanga: {e}")
            raise


# Global service instance
panchanga_service = PanchangaService()
