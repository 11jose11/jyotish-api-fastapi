"""Yogas service for detecting panchanga combinations."""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.services.swe import swe_service
from app.util.logging import get_logger

logger = get_logger("yogas")


class YogasService:
    """Service for detecting panchanga yogas."""
    
    def __init__(self):
        self.swe_service = swe_service
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict:
        """Load yoga rules from JSON file."""
        try:
            rules_path = os.path.join(os.path.dirname(__file__), "..", "..", "rules", "panchanga_rules.json")
            with open(rules_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("panchanga_rules.json not found, using default rules")
            return self._get_default_rules()
        except Exception as e:
            logger.error(f"Error loading yoga rules: {e}")
            return self._get_default_rules()
    
    def _get_default_rules(self) -> Dict:
        """Get default yoga rules."""
        return {
            "positive": {
                "Amrita Siddhi": {
                    "type": "vara+nakshatra",
                    "criteria": {
                        "weekday": "Sunday",
                        "nakshatra": ["Ashwini", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
                    }
                },
                "Guru Pushya": {
                    "type": "vara+nakshatra",
                    "criteria": {
                        "weekday": "Thursday",
                        "nakshatra": ["Pushya"]
                    }
                },
                "Ravi Pushya": {
                    "type": "sun+nakshatra",
                    "criteria": {
                        "nakshatra": ["Pushya"]
                    }
                }
            },
            "negative": {
                "Dagdha": {
                    "type": "vara+tithi",
                    "criteria": {
                        "weekday": "Sunday",
                        "tithi": [1, 6, 11, 16, 21, 26]
                    }
                },
                "Visha": {
                    "type": "vara+tithi",
                    "criteria": {
                        "weekday": "Monday",
                        "tithi": [2, 7, 12, 17, 22, 27]
                    }
                }
            }
        }
    
    def get_weekday(self, dt: datetime) -> str:
        """Get weekday name."""
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return weekdays[dt.weekday()]
    
    def detect_yogas(
        self,
        start_date: str,
        end_date: str,
        place_id: str,
        granularity: str = "day",
        include_notes: bool = True
    ) -> List[Dict]:
        """Detect yogas in the given date range."""
        try:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
            
            # Resolve place information
            from app.services.places import places_service
            place_info = places_service.resolve_place(place_id)
            
            yogas = []
            current_dt = start_dt
            
            while current_dt.date() <= end_dt.date():
                # Calculate planetary positions
                planet_data = self.swe_service.calculate_planets(current_dt, ["Sun", "Moon"])
                
                sun_lon = planet_data["Sun"]["lon"]
                moon_lon = planet_data["Moon"]["lon"]
                
                # Calculate panchanga elements
                tithi = self._calculate_tithi(sun_lon, moon_lon)
                nakshatra = self._get_nakshatra(moon_lon)
                weekday = self.get_weekday(current_dt)
                
                # Check positive yogas
                positive_yogas = self._check_positive_yogas(weekday, tithi, nakshatra, sun_lon, moon_lon)
                
                # Check negative yogas
                negative_yogas = self._check_negative_yogas(weekday, tithi, nakshatra)
                
                # Combine results
                day_yogas = positive_yogas + negative_yogas
                
                for yoga in day_yogas:
                    yoga["day"] = current_dt.date().isoformat()
                    yoga["window"] = {
                        "start": current_dt.isoformat(),
                        "end": (current_dt + timedelta(days=1)).isoformat()
                    }
                    yoga["source"] = "compiled_rules_v1"
                    
                    if include_notes:
                        yoga["flags"] = self._get_yoga_flags(yoga["name"])
                
                yogas.extend(day_yogas)
                current_dt += timedelta(days=1)
            
            return yogas
            
        except Exception as e:
            logger.error(f"Error detecting yogas: {e}")
            raise
    
    def _calculate_tithi(self, sun_lon: float, moon_lon: float) -> int:
        """Calculate tithi from Sun and Moon longitudes."""
        diff = (moon_lon - sun_lon) % 360
        return int(diff // 12) + 1
    
    def _get_nakshatra(self, longitude: float) -> str:
        """Get nakshatra name from longitude."""
        nakshatras = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
            "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]
        
        nakshatra_span = 13 + 1/3
        nak_index = int(longitude // nakshatra_span)
        return nakshatras[nak_index]
    
    def _check_positive_yogas(
        self, 
        weekday: str, 
        tithi: int, 
        nakshatra: str,
        sun_lon: float,
        moon_lon: float
    ) -> List[Dict]:
        """Check for positive yogas."""
        yogas = []
        
        for yoga_name, yoga_rule in self.rules.get("positive", {}).items():
            if self._matches_yoga_criteria(yoga_rule, weekday, tithi, nakshatra, sun_lon, moon_lon):
                yogas.append({
                    "name": yoga_name,
                    "polarity": "positive",
                    "kind": yoga_rule["type"],
                    "criteria": yoga_rule["criteria"]
                })
        
        return yogas
    
    def _check_negative_yogas(
        self, 
        weekday: str, 
        tithi: int, 
        nakshatra: str
    ) -> List[Dict]:
        """Check for negative yogas."""
        yogas = []
        
        for yoga_name, yoga_rule in self.rules.get("negative", {}).items():
            if self._matches_yoga_criteria(yoga_rule, weekday, tithi, nakshatra):
                yogas.append({
                    "name": yoga_name,
                    "polarity": "negative",
                    "kind": yoga_rule["type"],
                    "criteria": yoga_rule["criteria"]
                })
        
        return yogas
    
    def _matches_yoga_criteria(
        self, 
        yoga_rule: Dict, 
        weekday: str, 
        tithi: int, 
        nakshatra: str,
        sun_lon: float = None,
        moon_lon: float = None
    ) -> bool:
        """Check if current panchanga matches yoga criteria."""
        criteria = yoga_rule["criteria"]
        
        # Check weekday
        if "weekday" in criteria:
            if isinstance(criteria["weekday"], list):
                if weekday not in criteria["weekday"]:
                    return False
            else:
                if weekday != criteria["weekday"]:
                    return False
        
        # Check tithi
        if "tithi" in criteria:
            if isinstance(criteria["tithi"], list):
                if tithi not in criteria["tithi"]:
                    return False
            else:
                if tithi != criteria["tithi"]:
                    return False
        
        # Check nakshatra
        if "nakshatra" in criteria:
            if isinstance(criteria["nakshatra"], list):
                if nakshatra not in criteria["nakshatra"]:
                    return False
            else:
                if nakshatra != criteria["nakshatra"]:
                    return False
        
        # Check Ravi Yoga (Sun-Moon offset)
        if yoga_rule["type"] == "sun+moon" and sun_lon is not None and moon_lon is not None:
            sun_nak = self._get_nakshatra_index(sun_lon)
            moon_nak = self._get_nakshatra_index(moon_lon)
            offset = (moon_nak - sun_nak) % 27
            ravi_offsets = [4, 6, 9, 10, 13, 20]
            if offset not in ravi_offsets:
                return False
        
        return True
    
    def _get_nakshatra_index(self, longitude: float) -> int:
        """Get nakshatra index from longitude."""
        nakshatra_span = 13 + 1/3
        return int(longitude // nakshatra_span) + 1
    
    def _get_yoga_flags(self, yoga_name: str) -> List[str]:
        """Get flags for yoga."""
        flags_map = {
            "Amrita Siddhi": ["recommendedFor: all_activities"],
            "Guru Pushya": ["recommendedFor: education, business"],
            "Ravi Pushya": ["recommendedFor: spiritual_activities"],
            "Dagdha": ["notRecommendedFor: marriage, travel, newHouse"],
            "Visha": ["notRecommendedFor: medical_procedures, travel"]
        }
        return flags_map.get(yoga_name, [])


# Global service instance
yogas_service = YogasService()
