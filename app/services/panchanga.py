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
    
    def calculate_tithi(self, sun_lon: float, moon_lon: float) -> dict:
        """Calculate tithi with paksha information."""
        diff = (moon_lon - sun_lon) % 360
        tithi_number = int(diff // 12) + 1
        
        # Determine paksha based on difference
        if diff < 180:
            paksha = "Shukla"  # Waxing moon (0° to 180°)
            paksha_short = "S"
        else:
            paksha = "Krishna"  # Waning moon (180° to 360°)
            paksha_short = "K"
            # For Krishna paksha, adjust tithi number
            if tithi_number > 15:
                tithi_number = tithi_number - 15
        
        # Ensure tithi_number is in correct range
        if tithi_number < 1:
            tithi_number = 1
        elif tithi_number > 15:
            tithi_number = 15
        
        tithi_names = [
            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", "Saptami", "Ashtami",
            "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", "Saptami", "Ashtami",
            "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"
        ]
        
        return {
            "tithi_number": tithi_number,
            "tithi_name": tithi_names[tithi_number - 1],
            "paksha": paksha,
            "paksha_short": paksha_short,
            "display": f"{paksha_short}{tithi_number}",
            "sun_longitude": sun_lon,
            "moon_longitude": moon_lon,
            "difference": diff
        }
    
    def calculate_vara(self, date: datetime) -> dict:
        """Calculate vara (day of week) with Sanskrit names."""
        # Get weekday (0=Monday, 6=Sunday in Python)
        weekday_index = date.weekday()
        
        # Convert to Jyotish format (0=Sunday, 6=Saturday)
        jyotish_weekday = (weekday_index + 1) % 7
        
        varas = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        vara_sanskrit = {
            "Sunday": "रविवार",
            "Monday": "सोमवार", 
            "Tuesday": "मंगलवार",
            "Wednesday": "बुधवार",
            "Thursday": "गुरुवार",
            "Friday": "शुक्रवार",
            "Saturday": "शनिवार"
        }
        
        vara_name = varas[jyotish_weekday]
        
        return {
            "index": jyotish_weekday,
            "name": vara_name,
            "sanskrit": vara_sanskrit[vara_name],
            "date": date.date().isoformat()
        }
    
    def calculate_karana(self, tithi_number: int) -> dict:
        """Calculate karana based on tithi."""
        # Mapping of Tithi to Karana
        karana_mapping = {
            1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6,  # Bava to Vishti
            8: 7, 9: 8, 10: 9, 11: 10,  # Shakuni, Chatushpada, Naga, Kimstughna
            16: 0, 17: 1, 18: 2, 19: 3, 20: 4, 21: 5, 22: 6,  # Repeat for Krishna Paksha
            23: 7, 24: 8, 25: 9, 26: 10,  # Repeat for Krishna Paksha
            15: 6, 30: 6  # Purnima and Amavasya always have Vishti
        }
        
        karanas = [
            "Bava", "Balava", "Kaulava", "Taitila", "Garija", "Vanija", "Vishti",
            "Shakuni", "Chatushpada", "Naga", "Kimstughna"
        ]
        
        karana_sanskrit = {
            "Bava": "बव",
            "Balava": "बालव",
            "Kaulava": "कौलव",
            "Taitila": "तैतिल",
            "Garija": "गरिज",
            "Vanija": "वणिज",
            "Vishti": "विष्टि",
            "Shakuni": "शकुनि",
            "Chatushpada": "चतुष्पाद",
            "Naga": "नाग",
            "Kimstughna": "किंस्तुघ्न"
        }
        
        karana_index = karana_mapping.get(tithi_number, 0)
        karana_name = karanas[karana_index]
        
        return {
            "index": karana_index,
            "name": karana_name,
            "sanskrit": karana_sanskrit[karana_name],
            "tithi_number": tithi_number
        }
    
    def calculate_yoga(self, sun_lon: float, moon_lon: float) -> dict:
        """Calculate yoga (combination of Sun and Moon)."""
        # Sum of Sun and Moon longitudes
        total_longitude = (sun_lon + moon_lon) % 360
        
        # Yoga = sum / 13°20'
        yoga_span = 13 + 1/3
        yoga_index = int(total_longitude / yoga_span)
        
        nitya_yogas = [
            "Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarman",
            "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
            "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha",
            "Shukla", "Brahma", "Indra", "Vaidhriti"
        ]
        
        yoga_sanskrit = {
            "Vishkumbha": "विश्कुम्भ",
            "Priti": "प्रीति",
            "Ayushman": "आयुष्मान्",
            "Saubhagya": "सौभाग्य",
            "Shobhana": "शोभन",
            "Atiganda": "अतिगण्ड",
            "Sukarman": "सुकर्मन्",
            "Dhriti": "धृति",
            "Shula": "शूल",
            "Ganda": "गण्ड",
            "Vriddhi": "वृद्धि",
            "Dhruva": "ध्रुव",
            "Vyaghata": "व्याघात",
            "Harshana": "हर्षण",
            "Vajra": "वज्र",
            "Siddhi": "सिद्धि",
            "Vyatipata": "व्यतिपात",
            "Variyan": "वरीयान्",
            "Parigha": "परिघ",
            "Shiva": "शिव",
            "Siddha": "सिद्ध",
            "Sadhya": "साध्य",
            "Shubha": "शुभ",
            "Shukla": "शुक्ल",
            "Brahma": "ब्रह्म",
            "Indra": "इन्द्र",
            "Vaidhriti": "वैधृति"
        }
        
        yoga_name = nitya_yogas[yoga_index]
        
        return {
            "index": yoga_index,
            "name": yoga_name,
            "sanskrit": yoga_sanskrit.get(yoga_name, yoga_name),
            "sun_longitude": sun_lon,
            "moon_longitude": moon_lon,
            "total_longitude": total_longitude
        }
    
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
        """Get complete panchanga for a day with all 5 elements: Nakshatra, Tithi, Karana, Vara, Yoga."""
        try:
            # Calculate planetary positions
            planet_data = self.swe_service.calculate_planets(date, ["Sun", "Moon"])
            
            sun_lon = planet_data["Sun"]["lon"]
            moon_lon = planet_data["Moon"]["lon"]
            
            # Calculate all 5 elements of Panchanga
            nakshatra, nak_index, pada = self.get_nakshatra(moon_lon)
            tithi_data = self.calculate_tithi(sun_lon, moon_lon)
            karana_data = self.calculate_karana(tithi_data["tithi_number"])
            vara_data = self.calculate_vara(date)
            yoga_data = self.calculate_yoga(sun_lon, moon_lon)
            
            # Find exact windows
            tithi_windows = self.find_tithi_changes(date, place_info)
            nakshatra_windows = self.find_nakshatra_changes(date, place_info)
            
            return {
                "date": date.date().isoformat(),
                "nakshatra": {
                    "index": nak_index,
                    "name": nakshatra,
                    "pada": pada,
                    "longitude": moon_lon,
                    "position_in_nakshatra": moon_lon % (13 + 1/3)
                },
                "tithi": tithi_data,
                "karana": karana_data,
                "vara": vara_data,
                "yoga": yoga_data,
                "timestamp": date.isoformat(),
                "tithi_windows": tithi_windows,
                "nakshatra_windows": nakshatra_windows
            }
            
        except Exception as e:
            logger.error(f"Error calculating daily panchanga: {e}")
            raise


# Global service instance
panchanga_service = PanchangaService()
