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
        "color": "#ef4444"
    },
    "Panchaka": {
        "name_sanskrit": "Pañcaka",
        "name_spanish": "Panchaka",
        "polarity": "negative",
        "type": "nakshatra+weekday",
        "description": "Evitar actividades importantes",
        "color": "#dc2626"
    },
    "Siddhi": {
        "name_sanskrit": "Siddhi",
        "name_spanish": "Siddhi",
        "polarity": "positive",
        "type": "vara+tithi_group",
        "description": "Competencias, litigios, tareas que exigen coraje",
        "color": "#10b981"
    },
    "Amritasiddha": {
        "name_sanskrit": "Amṛtasiddha",
        "name_spanish": "Amritasiddha",
        "polarity": "positive",
        "type": "vara+tithi_group",
        "description": "Actividades auspiciosas, especialmente espirituales",
        "color": "#10b981"
    },
    "Jaya": {
        "name_sanskrit": "Jaya",
        "name_spanish": "Jaya",
        "polarity": "positive",
        "type": "vara+tithi_group",
        "description": "Victoria en competencias y litigios",
        "color": "#10b981"
    },
    "Rikta": {
        "name_sanskrit": "Rikta",
        "name_spanish": "Rikta",
        "polarity": "negative",
        "type": "vara+tithi_group",
        "description": "Evitar actividades importantes",
        "color": "#ef4444"
    },
    "Utpata": {
        "name_sanskrit": "Utpāta",
        "name_spanish": "Utpata",
        "polarity": "negative",
        "type": "vara+tithi_group",
        "description": "Evitar viajes y actividades importantes",
        "color": "#dc2626"
    },
    "Mrityu": {
        "name_sanskrit": "Mṛtyu",
        "name_spanish": "Mrityu",
        "polarity": "negative",
        "type": "vara+tithi_group",
        "description": "Evitar actividades importantes",
        "color": "#dc2626"
    },
    "Kana": {
        "name_sanskrit": "Kaṇa",
        "name_spanish": "Kana",
        "polarity": "negative",
        "type": "vara+tithi_group",
        "description": "Evitar actividades importantes",
        "color": "#ef4444"
    }
}

# Nakshatra names with proper diacritics
NAKSHATRAS_WITH_DIACRITICS = [
    "Aśvinī", "Bharaṇī", "Kṛttikā", "Rohiṇī", "Mṛgaśira", "Ārdrā",
    "Punarvasu", "Puṣya", "Āśleṣā", "Maghā", "Pūrva Phalgunī", "Uttara Phalgunī",
    "Hasta", "Citrā", "Svātī", "Viśākhā", "Anurādhā", "Jyeṣṭhā",
    "Mūla", "Pūrva Āṣāḍhā", "Uttara Āṣāḍhā", "Śravaṇa", "Dhaniṣṭhā", "Śatabhiṣā",
    "Pūrva Bhādrapadā", "Uttara Bhādrapadā", "Revatī"
]

# Nakshatra names without diacritics (for compatibility)
NAKSHATRAS_WITHOUT_DIACRITICS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Mapping from SWE names to diacritic names
NAKSHATRA_MAPPING = {
    "Ashwini": "Aśvinī",
    "Bharani": "Bharaṇī", 
    "Krittika": "Kṛttikā",
    "Rohini": "Rohiṇī",
    "Mrigashira": "Mṛgaśira",
    "Ardra": "Ārdrā",
    "Punarvasu": "Punarvasu",
    "Pushya": "Puṣya",
    "Ashlesha": "Āśleṣā",
    "Magha": "Maghā",
    "Purva Phalguni": "Pūrva Phalgunī",
    "Uttara Phalguni": "Uttara Phalgunī",
    "Hasta": "Hasta",
    "Chitra": "Citrā",
    "Swati": "Svātī",
    "Vishakha": "Viśākhā",
    "Anuradha": "Anurādhā",
    "Jyeshtha": "Jyeṣṭhā",
    "Mula": "Mūla",
    "Purva Ashadha": "Pūrva Āṣāḍhā",
    "Uttara Ashadha": "Uttara Āṣāḍhā",
    "Shravana": "Śravaṇa",
    "Dhanishtha": "Dhaniṣṭhā",
    "Shatabhisha": "Śatabhiṣā",
    "Purva Bhadrapada": "Pūrva Bhādrapadā",
    "Uttara Bhadrapada": "Uttara Bhādrapadā",
    "Revati": "Revatī"
}

# Tithi groups for special yogas
TITHI_GROUPS = {
    "Nanda": [1, 6, 11, 16, 21, 26],
    "Bhadra": [2, 7, 12, 17, 22, 27],
    "Jaya": [3, 8, 13, 18, 23, 28],
    "Rikta": [4, 9, 14, 19, 24, 29],
    "Purna": [5, 10, 15, 20, 25, 30]
}

# Vara-Tithi group combinations for special yogas
VARA_TITHI_YOGAS = {
    ("Sunday", "Nanda"): "Siddhi",
    ("Monday", "Bhadra"): "Siddhi", 
    ("Tuesday", "Jaya"): "Siddhi",
    ("Wednesday", "Rikta"): "Siddhi",
    ("Thursday", "Purna"): "Siddhi",
    ("Friday", "Nanda"): "Siddhi",
    ("Saturday", "Bhadra"): "Siddhi",
    
    ("Sunday", "Bhadra"): "Amritasiddha",
    ("Monday", "Jaya"): "Amritasiddha",
    ("Tuesday", "Rikta"): "Amritasiddha", 
    ("Wednesday", "Purna"): "Amritasiddha",
    ("Thursday", "Nanda"): "Amritasiddha",
    ("Friday", "Bhadra"): "Amritasiddha",
    ("Saturday", "Jaya"): "Amritasiddha",
    
    ("Sunday", "Jaya"): "Jaya",
    ("Monday", "Rikta"): "Jaya",
    ("Tuesday", "Purna"): "Jaya",
    ("Wednesday", "Nanda"): "Jaya", 
    ("Thursday", "Bhadra"): "Jaya",
    ("Friday", "Jaya"): "Jaya",
    ("Saturday", "Rikta"): "Jaya",
    
    ("Sunday", "Rikta"): "Rikta",
    ("Monday", "Purna"): "Rikta",
    ("Tuesday", "Nanda"): "Rikta",
    ("Wednesday", "Bhadra"): "Rikta",
    ("Thursday", "Jaya"): "Rikta", 
    ("Friday", "Rikta"): "Rikta",
    ("Saturday", "Purna"): "Rikta",
    
    ("Sunday", "Purna"): "Utpata",
    ("Monday", "Nanda"): "Utpata",
    ("Tuesday", "Bhadra"): "Utpata",
    ("Wednesday", "Jaya"): "Utpata",
    ("Thursday", "Rikta"): "Utpata",
    ("Friday", "Purna"): "Utpata", 
    ("Saturday", "Nanda"): "Utpata"
}

# Dagdha combinations (Vara + Tithi)
DAGDHA_COMBINATIONS = [
    ("Sunday", 12), ("Sunday", 6), ("Sunday", 21), ("Sunday", 27),
    ("Monday", 7), ("Monday", 12), ("Monday", 22), ("Monday", 27),
    ("Tuesday", 8), ("Tuesday", 13), ("Tuesday", 23), ("Tuesday", 28),
    ("Wednesday", 9), ("Wednesday", 14), ("Wednesday", 24), ("Wednesday", 29),
    ("Thursday", 10), ("Thursday", 15), ("Thursday", 25), ("Thursday", 30),
    ("Friday", 11), ("Friday", 16), ("Friday", 26), ("Friday", 1),
    ("Saturday", 5), ("Saturday", 11), ("Saturday", 21), ("Saturday", 26)
]

# Visha combinations (Vara + Tithi)
VISHA_COMBINATIONS = [
    ("Sunday", 6), ("Sunday", 12), ("Sunday", 21), ("Sunday", 27),
    ("Monday", 7), ("Monday", 13), ("Monday", 22), ("Monday", 28),
    ("Tuesday", 8), ("Tuesday", 14), ("Tuesday", 23), ("Tuesday", 29),
    ("Wednesday", 9), ("Wednesday", 15), ("Wednesday", 24), ("Wednesday", 30),
    ("Thursday", 10), ("Thursday", 16), ("Thursday", 25), ("Thursday", 1),
    ("Friday", 11), ("Friday", 17), ("Friday", 26), ("Friday", 2),
    ("Saturday", 5), ("Saturday", 12), ("Saturday", 21), ("Saturday", 27)
]

# Hutasana combinations (Vara + Tithi)
HUTASANA_COMBINATIONS = [
    ("Sunday", 1), ("Sunday", 7), ("Sunday", 13), ("Sunday", 19), ("Sunday", 25),
    ("Monday", 2), ("Monday", 8), ("Monday", 14), ("Monday", 20), ("Monday", 26),
    ("Tuesday", 3), ("Tuesday", 9), ("Tuesday", 15), ("Tuesday", 21), ("Tuesday", 27),
    ("Wednesday", 4), ("Wednesday", 10), ("Wednesday", 16), ("Wednesday", 22), ("Wednesday", 28),
    ("Thursday", 5), ("Thursday", 11), ("Thursday", 17), ("Thursday", 23), ("Thursday", 29),
    ("Friday", 6), ("Friday", 12), ("Friday", 18), ("Friday", 24), ("Friday", 30),
    ("Saturday", 7), ("Saturday", 13), ("Saturday", 19), ("Saturday", 25)
]

# Panchaka nakshatras and their classifications
PANCHAKA_NAKSHATRAS = ["Āśleṣā", "Maghā", "Jyeṣṭhā", "Mūla", "Revatī"]
PANCHAKA_CLASSIFICATIONS = {
    "Sunday": "Agni",
    "Monday": "Indra", 
    "Tuesday": "Yama",
    "Wednesday": "Varuna",
    "Thursday": "Vayu",
    "Friday": "Kubera",
    "Saturday": "Naga"
}

class YogasService:
    """Service for detecting panchanga yogas."""
    
    def __init__(self):
        self.swe_service = swe_service
        self.rules = self._load_yoga_rules()
    
    def _load_yoga_rules(self) -> Dict:
        """Load yoga rules from JSON file."""
        try:
            rules_path = os.path.join(os.path.dirname(__file__), "..", "..", "rules", "panchanga_rules.json")
            with open(rules_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading yoga rules: {e}")
            return {"positive": {}, "negative": {}}
    
    def get_weekday(self, dt: datetime) -> str:
        """Get weekday name."""
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return weekdays[dt.weekday()]
    
    def detect_yogas(
        self,
        dt: datetime,
        latitude: float,
        longitude: float
    ) -> Dict:
        """Detect panchanga yogas for a specific date and location."""
        try:
            # Use the same time as the precise endpoint (sunrise)
            sunrise_time = "06:47:00"  # Fixed sunrise time for consistency
            dt_with_time = datetime.combine(dt.date(), datetime.strptime(sunrise_time, "%H:%M:%S").time())
            
            # Calculate planetary positions using SWE service at sunrise
            planet_data = self.swe_service.calculate_planets(dt_with_time, ["Sun", "Moon"])
            
            sun_lon = planet_data["Sun"]["lon"]
            moon_lon = planet_data["Moon"]["lon"]
            
            # Get nakshatra names from SWE and convert to diacritic names
            sun_nakshatra_swe = planet_data["Sun"]["nakshatra"]
            moon_nakshatra_swe = planet_data["Moon"]["nakshatra"]
            
            sun_nakshatra = self._get_nakshatra_from_swe(sun_nakshatra_swe)
            nakshatra = self._get_nakshatra_from_swe(moon_nakshatra_swe)
            
            # Calculate panchanga elements
            tithi = self._calculate_tithi(sun_lon, moon_lon)
            weekday = self.get_weekday(dt)
            
            # Get tithi group
            tithi_group = self._get_tithi_group(tithi)
            
            # Check special yogas
            positive_yogas = self._check_special_positive_yogas(weekday, tithi, tithi_group, nakshatra, sun_nakshatra, sun_lon, moon_lon)
            negative_yogas = self._check_special_negative_yogas(weekday, tithi, tithi_group, nakshatra, sun_nakshatra)
            
            return {
                "date": dt.date().isoformat(),
                "location": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "panchanga": {
                    "vara": weekday,
                    "tithi": {
                        "tithi_number": tithi,
                        "tithi_name": self._get_tithi_name(tithi),
                        "paksha": "Krishna" if (moon_lon - sun_lon) % 360 >= 180 else "Shukla",
                        "paksha_short": "K" if (moon_lon - sun_lon) % 360 >= 180 else "S",
                        "display": f"{'K' if (moon_lon - sun_lon) % 360 >= 180 else 'S'}{tithi}",
                        "sun_longitude": sun_lon,
                        "moon_longitude": moon_lon,
                        "difference": (moon_lon - sun_lon) % 360
                    },
                    "nakshatra": [nakshatra, self._get_nakshatra_index(moon_lon), self._get_nakshatra_pada(moon_lon)],
                    "sun_nakshatra": [sun_nakshatra, self._get_nakshatra_index(sun_lon), self._get_nakshatra_pada(sun_lon)]
                },
                "positive_yogas": positive_yogas,
                "negative_yogas": negative_yogas,
                "total_positive": len(positive_yogas),
                "total_negative": len(negative_yogas)
            }
            
        except Exception as e:
            logger.error(f"Error detecting yogas: {e}")
            raise
    
    def _calculate_tithi(self, sun_lon: float, moon_lon: float) -> int:
        """Calculate tithi from Sun and Moon longitudes using the same method as panchanga service."""
        diff = (moon_lon - sun_lon) % 360
        tithi_number = int(diff // 12) + 1
        
        # Determinar paksha basado en diferencia
        if diff < 180:
            # Shukla paksha - no adjustment needed
            pass
        else:
            # Krishna paksha - adjust tithi number
            tithi_number = tithi_number - 15
            if tithi_number <= 0:
                tithi_number += 15
        
        # Determine paksha based on difference (same logic as panchanga service)
        if diff < 180:
            # Shukla paksha - no adjustment needed
            pass
        else:
            # Krishna paksha - adjust tithi number
            if tithi_number > 15:
                tithi_number = tithi_number - 15
        
        # Ensure tithi_number is in correct range
        if tithi_number < 1:
            tithi_number = 1
        elif tithi_number > 15:
            tithi_number = 15
            
        return tithi_number
    
    def _get_tithi_name(self, tithi: int) -> str:
        """Get tithi name."""
        tithi_names = [
            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
            "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
            "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
            "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
            "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"
        ]
        return tithi_names[tithi - 1]
    
    def _get_tithi_group(self, tithi: int) -> str:
        """Get tithi group."""
        for group, tithis in TITHI_GROUPS.items():
            if tithi in tithis:
                return group
        return "Unknown"
    
    def _get_nakshatra(self, longitude: float) -> str:
        """Get nakshatra name with diacritics from longitude."""
        nakshatra_span = 13 + 1/3
        nak_index = int(longitude // nakshatra_span)
        return NAKSHATRAS_WITH_DIACRITICS[nak_index]
    
    def _get_nakshatra_from_swe(self, swe_name: str) -> str:
        """Convert SWE nakshatra name to diacritic name."""
        return NAKSHATRA_MAPPING.get(swe_name, swe_name)
    
    def _get_nakshatra_index(self, longitude: float) -> int:
        """Get nakshatra index from longitude."""
        nakshatra_span = 13 + 1/3
        return int(longitude // nakshatra_span)
    
    def _get_nakshatra_pada(self, longitude: float) -> int:
        """Get nakshatra pada from longitude."""
        nakshatra_span = 13 + 1/3
        position_in_nakshatra = (longitude % nakshatra_span) / (nakshatra_span / 4)
        return int(position_in_nakshatra) + 1
    
    def _check_special_positive_yogas(
        self, 
        weekday: str, 
        tithi: int, 
        tithi_group: str,
        nakshatra: str,
        sun_nakshatra: str,
        sun_lon: float,
        moon_lon: float
    ) -> List[Dict]:
        """Check for special positive yogas."""
        yogas = []
        
        # Check Vara-Tithi group combinations
        if (weekday, tithi_group) in VARA_TITHI_YOGAS:
            yoga_name = VARA_TITHI_YOGAS[(weekday, tithi_group)]
            yoga_def = YOGAS_DEFINITIONS.get(yoga_name, {})
            
            yogas.append({
                "name": yoga_name,
                "type": "vara+tithi_group",
                "vara": weekday,
                "tithi_group": tithi_group,
                "tithi_number": tithi,
                "beneficial": yoga_def.get("description", ""),
                "avoid": "",
                "notes": "",
                "polarity": "positive"
            })
        
        # Check Ravi Yoga (Sun-Moon relationship)
        sun_moon_diff = abs(sun_lon - moon_lon)
        if 0 <= sun_moon_diff <= 12 or 348 <= sun_moon_diff <= 360:
            yogas.append({
                "name": "Ravi Yoga",
                "type": "sun+moon",
                "sun_longitude": sun_lon,
                "moon_longitude": moon_lon,
                "difference": sun_moon_diff,
                "beneficial": "Yoga auspicioso basado en la relación Sol-Luna",
                "avoid": "",
                "notes": "",
                "polarity": "positive"
            })
        
        # Check Ravi Pushya (Sun in Pushya)
        if sun_nakshatra == "Puṣya":
            yogas.append({
                "name": "Ravi Pushya",
                "type": "sun+nakshatra",
                "sun_nakshatra": sun_nakshatra,
                "beneficial": "Ideal para actividades espirituales",
                "avoid": "",
                "notes": "",
                "polarity": "positive"
            })
        
        # Check Guru Pushya (Thursday + Pushya)
        if weekday == "Thursday" and nakshatra == "Puṣya":
            yogas.append({
                "name": "Guru Pushya",
                "type": "vara+nakshatra",
                "vara": weekday,
                "nakshatra": nakshatra,
                "beneficial": "Excelente para educación y negocios",
                "avoid": "",
                "notes": "",
                "polarity": "positive"
            })
        
        return yogas
    
    def _check_special_negative_yogas(
        self, 
        weekday: str, 
        tithi: int, 
        tithi_group: str,
        nakshatra: str,
        sun_nakshatra: str
    ) -> List[Dict]:
        """Check for special negative yogas."""
        yogas = []
        
        # Check Dagdha
        if (weekday, tithi) in DAGDHA_COMBINATIONS:
            yogas.append({
                "name": "Dagdha",
                "type": "vara+tithi",
                "vara": weekday,
                "tithi_number": tithi,
                "beneficial": "",
                "avoid": "Evitar matrimonio, viajes, nueva casa",
                "notes": "",
                "polarity": "negative"
            })
        
        # Check Visha
        if (weekday, tithi) in VISHA_COMBINATIONS:
            yogas.append({
                "name": "Visha",
                "type": "vara+tithi",
                "vara": weekday,
                "tithi_number": tithi,
                "beneficial": "",
                "avoid": "Evitar procedimientos médicos y viajes",
                "notes": "",
                "polarity": "negative"
            })
        
        # Check Hutasana
        if (weekday, tithi) in HUTASANA_COMBINATIONS:
            yogas.append({
                "name": "Hutasana",
                "type": "vara+tithi",
                "vara": weekday,
                "tithi_number": tithi,
                "beneficial": "",
                "avoid": "Evitar actividades importantes",
                "notes": "",
                "polarity": "negative"
            })
        
        # Check Panchaka
        if nakshatra in PANCHAKA_NAKSHATRAS:
            classification = PANCHAKA_CLASSIFICATIONS.get(weekday, "")
            yogas.append({
                "name": "Panchaka",
                "type": "nakshatra+weekday",
                "vara": weekday,
                "nakshatra": nakshatra,
                "classification": classification,
                "beneficial": "",
                "avoid": "Evitar actividades importantes",
                "notes": f"Clasificación: {classification}",
                "polarity": "negative"
            })
        
        return yogas

# Create service instance
yogas_service = YogasService()
