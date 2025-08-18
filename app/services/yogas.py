"""Yogas service for detecting panchanga combinations."""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.services.swe import swe_service
from app.util.logging import get_logger

logger = get_logger("yogas")

# Yoga definitions with Sanskrit and Spanish names
YOGAS_DEFINITIONS = {
    "Amrita Siddhi": {
        "name_sanskrit": "Amṛta Siddhi",
        "name_spanish": "Amrita Siddhi",
        "polarity": "positive",
        "type": "vara+nakshatra",
        "description": "Yoga auspicioso para todas las actividades",
        "color": "#10b981"
    },
    "Sarvartha Siddhi": {
        "name_sanskrit": "Sarvārtha Siddhi",
        "name_spanish": "Sarvartha Siddhi",
        "polarity": "positive",
        "type": "vara+nakshatra",
        "description": "Yoga auspicioso para todos los propósitos",
        "color": "#10b981"
    },
    "Siddha": {
        "name_sanskrit": "Siddha",
        "name_spanish": "Siddha",
        "polarity": "positive",
        "type": "vara+nakshatra",
        "description": "Yoga auspicioso para actividades espirituales",
        "color": "#10b981"
    },
    "Guru Pushya": {
        "name_sanskrit": "Guru Puṣya",
        "name_spanish": "Guru Pushya",
        "polarity": "positive",
        "type": "vara+nakshatra",
        "description": "Excelente para educación y negocios",
        "color": "#8b5cf6"
    },
    "Ravi Pushya": {
        "name_sanskrit": "Ravi Puṣya",
        "name_spanish": "Ravi Pushya",
        "polarity": "positive",
        "type": "sun+nakshatra",
        "description": "Ideal para actividades espirituales",
        "color": "#f59e0b"
    },
    "Ravi Yoga": {
        "name_sanskrit": "Ravi Yoga",
        "name_spanish": "Ravi Yoga",
        "polarity": "positive",
        "type": "sun+moon",
        "description": "Yoga auspicioso basado en la relación Sol-Luna",
        "color": "#f59e0b"
    },
    "Dvipushkara": {
        "name_sanskrit": "Dvipuṣkara",
        "name_spanish": "Dvipushkara",
        "polarity": "positive",
        "type": "vara+tithi+nakshatra",
        "description": "Yoga auspicioso para actividades importantes",
        "color": "#10b981"
    },
    "Tripushkara": {
        "name_sanskrit": "Tripuṣkara",
        "name_spanish": "Tripushkara",
        "polarity": "positive",
        "type": "vara+tithi+nakshatra",
        "description": "Yoga muy auspicioso para actividades importantes",
        "color": "#10b981"
    },
    "Dagdha": {
        "name_sanskrit": "Dagdha",
        "name_spanish": "Dagdha",
        "polarity": "negative",
        "type": "vara+tithi",
        "description": "Evitar matrimonio, viajes, nueva casa",
        "color": "#ef4444"
    },
    "Visha": {
        "name_sanskrit": "Viṣa",
        "name_spanish": "Visha",
        "polarity": "negative",
        "type": "vara+tithi",
        "description": "Evitar procedimientos médicos y viajes",
        "color": "#dc2626"
    },
    "Hutasana": {
        "name_sanskrit": "Hutāsana",
        "name_spanish": "Hutasana",
        "polarity": "negative",
        "type": "vara+tithi",
        "description": "Evitar actividades importantes",
        "color": "#dc2626"
    },
    "Krakacha": {
        "name_sanskrit": "Krakacha",
        "name_spanish": "Krakacha",
        "polarity": "negative",
        "type": "vara+tithi",
        "description": "Evitar actividades importantes",
        "color": "#dc2626"
    },
    "Samvartaka": {
        "name_sanskrit": "Samvartaka",
        "name_spanish": "Samvartaka",
        "polarity": "negative",
        "type": "vara+tithi",
        "description": "Evitar actividades importantes",
        "color": "#dc2626"
    },
    "Asubha": {
        "name_sanskrit": "Aśubha",
        "name_spanish": "Asubha",
        "polarity": "negative",
        "type": "tithi+nakshatra",
        "description": "Evitar actividades importantes",
        "color": "#dc2626"
    },
    "Vinasa": {
        "name_sanskrit": "Vināśa",
        "name_spanish": "Vinasa",
        "polarity": "negative",
        "type": "triple",
        "description": "Evitar actividades importantes",
        "color": "#dc2626"
    },
    "Panchaka": {
        "name_sanskrit": "Pañcaka",
        "name_spanish": "Panchaka",
        "polarity": "negative",
        "type": "nakshatra+weekday",
        "description": "Evitar actividades importantes",
        "color": "#dc2626"
    }
}


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
                sun_nakshatra = self._get_nakshatra(sun_lon)
                weekday = self.get_weekday(current_dt)
                
                # Check positive yogas
                positive_yogas = self._check_positive_yogas(weekday, tithi, nakshatra, sun_lon, moon_lon, sun_nakshatra)
                
                # Check negative yogas
                negative_yogas = self._check_negative_yogas(weekday, tithi, nakshatra, sun_nakshatra)
                
                # Combine results
                day_yogas = positive_yogas + negative_yogas
                
                for yoga in day_yogas:
                    yoga_name = yoga["name"]
                    yoga_def = YOGAS_DEFINITIONS.get(yoga_name, {})
                    
                    yoga_data = {
                        "name": yoga_name,
                        "name_sanskrit": yoga_def.get("name_sanskrit", yoga_name),
                        "name_spanish": yoga_def.get("name_spanish", yoga_name),
                        "polarity": yoga["polarity"],
                        "kind": yoga["kind"],
                        "type": yoga_def.get("type", yoga["kind"]),
                        "description": yoga_def.get("description", ""),
                        "color": yoga_def.get("color", "#6b7280"),
                        "day": current_dt.date().isoformat(),
                        "window": {
                            "start": current_dt.isoformat(),
                            "end": (current_dt + timedelta(days=1)).isoformat()
                        },
                        "source": "compiled_rules_v1"
                    }
                    
                    # Add classification for Panchaka yoga
                    if yoga_name == "Panchaka" and "classification" in yoga:
                        yoga_data["classification"] = yoga["classification"]
                    
                    if include_notes:
                        yoga_data["flags"] = self._get_yoga_flags(yoga_name)
                    
                    yogas.append(yoga_data)
                
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
        moon_lon: float,
        sun_nakshatra: str
    ) -> List[Dict]:
        """Check for positive yogas."""
        yogas = []
        
        for yoga_name, yoga_rule in self.rules.get("positive", {}).items():
            if self._matches_yoga_criteria(yoga_rule, weekday, tithi, nakshatra, sun_lon, moon_lon, sun_nakshatra):
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
        nakshatra: str,
        sun_nakshatra: str
    ) -> List[Dict]:
        """Check for negative yogas."""
        yogas = []
        
        for yoga_name, yoga_rule in self.rules.get("negative", {}).items():
            if self._matches_yoga_criteria(yoga_rule, weekday, tithi, nakshatra, sun_nakshatra=sun_nakshatra):
                yoga_data = {
                    "name": yoga_name,
                    "polarity": "negative",
                    "kind": yoga_rule["type"],
                    "criteria": yoga_rule["criteria"]
                }
                
                # Add classification for Panchaka yoga
                if yoga_name == "Panchaka" and "classification" in yoga_rule["criteria"]:
                    yoga_data["classification"] = yoga_rule["criteria"]["classification"].get(weekday, "")
                
                yogas.append(yoga_data)
        
        return yogas
    
    def _matches_yoga_criteria(
        self, 
        yoga_rule: Dict, 
        weekday: str, 
        tithi: int, 
        nakshatra: str,
        sun_lon: float = None,
        moon_lon: float = None,
        sun_nakshatra: str = None
    ) -> bool:
        """Check if current panchanga matches yoga criteria."""
        criteria = yoga_rule["criteria"]
        yoga_type = yoga_rule.get("type", "")
        
        # Handle triple type (Vinasa yoga)
        if yoga_type == "triple":
            if weekday in criteria and nakshatra in criteria[weekday]:
                return True
            return False
        
        # Handle nakshatra+weekday type (Panchaka yoga)
        if yoga_type == "nakshatra+weekday":
            if "nakshatra" in criteria and "classification" in criteria:
                if nakshatra in criteria["nakshatra"] and weekday in criteria["classification"]:
                    return True
            return False
        
        # Handle sun+nakshatra type (Ravi Pushya)
        if yoga_type == "sun+nakshatra":
            if "nakshatra" in criteria and sun_nakshatra:
                if isinstance(criteria["nakshatra"], list):
                    if sun_nakshatra not in criteria["nakshatra"]:
                        return False
                else:
                    if sun_nakshatra != criteria["nakshatra"]:
                        return False
            return True
        
        # Handle sun+moon type (Ravi Yoga)
        if yoga_type == "sun+moon":
            if sun_lon is not None and moon_lon is not None and "offset" in criteria:
                sun_nak = self._get_nakshatra_index(sun_lon)
                moon_nak = self._get_nakshatra_index(moon_lon)
                offset = (moon_nak - sun_nak) % 27
                if offset not in criteria["offset"]:
                    return False
            return True
        
        # Handle standard criteria (weekday, tithi, nakshatra)
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
        
        # Check nakshatra (for standard types, use lunar nakshatra)
        if "nakshatra" in criteria:
            if isinstance(criteria["nakshatra"], list):
                if nakshatra not in criteria["nakshatra"]:
                    return False
            else:
                if nakshatra != criteria["nakshatra"]:
                    return False
        
        return True
    
    def _get_nakshatra_index(self, longitude: float) -> int:
        """Get nakshatra index from longitude."""
        nakshatra_span = 13 + 1/3
        return int(longitude // nakshatra_span)
    
    def _get_yoga_flags(self, yoga_name: str) -> List[str]:
        """Get flags for yoga."""
        flags_map = {
            "Amrita Siddhi": ["recommendedFor: all_activities"],
            "Sarvartha Siddhi": ["recommendedFor: all_activities"],
            "Siddha": ["recommendedFor: spiritual_activities"],
            "Guru Pushya": ["recommendedFor: education, business"],
            "Ravi Pushya": ["recommendedFor: spiritual_activities"],
            "Ravi Yoga": ["recommendedFor: spiritual_activities"],
            "Dvipushkara": ["recommendedFor: important_activities"],
            "Tripushkara": ["recommendedFor: important_activities"],
            "Dagdha": ["notRecommendedFor: marriage, travel, newHouse"],
            "Visha": ["notRecommendedFor: medical_procedures, travel"],
            "Hutasana": ["notRecommendedFor: important_activities"],
            "Krakacha": ["notRecommendedFor: important_activities"],
            "Samvartaka": ["notRecommendedFor: important_activities"],
            "Asubha": ["notRecommendedFor: important_activities"],
            "Vinasa": ["notRecommendedFor: important_activities"],
            "Panchaka": ["notRecommendedFor: important_activities"]
        }
        return flags_map.get(yoga_name, [])


# Global service instance
yogas_service = YogasService()
