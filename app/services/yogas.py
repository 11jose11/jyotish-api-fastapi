"""Yogas service for detecting panchanga combinations."""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.services.swe import swe_service
from app.util.logging import get_logger

logger = get_logger("yogas")

# Enhanced Yoga definitions with Sanskrit and Spanish names
YOGAS_DEFINITIONS = {
    "Amrita Siddhi": {
        "name_sanskrit": "Amṛta Siddhi",
        "name_spanish": "Amrita Siddhi",
        "polarity": "positive",
        "type": "vara+nakshatra",
        "description": "Yoga auspicioso para todas las actividades",
        "detailed_description": "Uno de los yogas más auspiciosos. Ideal para iniciar nuevos proyectos, matrimonios, y actividades espirituales.",
        "color": "#10b981",
        "priority": 1
    },
    "Sarvartha Siddhi": {
        "name_sanskrit": "Sarvārtha Siddhi",
        "name_spanish": "Sarvartha Siddhi",
        "polarity": "positive",
        "type": "vara+nakshatra",
        "description": "Yoga auspicioso para todos los propósitos",
        "detailed_description": "Excelente para cualquier actividad importante. Garantiza éxito en todos los esfuerzos.",
        "color": "#10b981",
        "priority": 1
    },
    "Siddha": {
        "name_sanskrit": "Siddha",
        "name_spanish": "Siddha",
        "polarity": "positive",
        "type": "vara+nakshatra",
        "description": "Yoga auspicioso para actividades espirituales",
        "detailed_description": "Perfecto para meditación, pujas, y actividades espirituales. Favorece el crecimiento interior.",
        "color": "#10b981",
        "priority": 2
    },
    "Guru Pushya": {
        "name_sanskrit": "Guru Puṣya",
        "name_spanish": "Guru Pushya",
        "polarity": "positive",
        "type": "vara+nakshatra",
        "description": "Excelente para educación y negocios",
        "detailed_description": "Ideal para iniciar estudios, firmar contratos, y actividades comerciales. Favorece el aprendizaje.",
        "color": "#8b5cf6",
        "priority": 1
    },
    "Ravi Pushya": {
        "name_sanskrit": "Ravi Puṣya",
        "name_spanish": "Ravi Pushya",
        "polarity": "positive",
        "type": "sun+nakshatra",
        "description": "Ideal para actividades espirituales",
        "detailed_description": "Excelente para pujas, iniciaciones espirituales, y actividades religiosas.",
        "color": "#f59e0b",
        "priority": 2
    },
    "Ravi Yoga": {
        "name_sanskrit": "Ravi Yoga",
        "name_spanish": "Ravi Yoga",
        "polarity": "positive",
        "type": "sun+moon",
        "description": "Yoga auspicioso basado en la relación Sol-Luna",
        "detailed_description": "Favorece la armonía entre el Sol y la Luna. Bueno para actividades que requieren balance.",
        "color": "#f59e0b",
        "priority": 3
    },
    "Dvipushkara": {
        "name_sanskrit": "Dvipuṣkara",
        "name_spanish": "Dvipushkara",
        "polarity": "positive",
        "type": "vara+tithi+nakshatra",
        "description": "Yoga auspicioso para actividades importantes",
        "detailed_description": "Favorece el éxito en actividades importantes. Bueno para inauguraciones y ceremonias.",
        "color": "#10b981",
        "priority": 2
    },
    "Tripushkara": {
        "name_sanskrit": "Tripuṣkara",
        "name_spanish": "Tripushkara",
        "polarity": "positive",
        "type": "vara+tithi+nakshatra",
        "description": "Yoga muy auspicioso para actividades importantes",
        "detailed_description": "Uno de los yogas más poderosos. Excelente para actividades de gran importancia.",
        "color": "#10b981",
        "priority": 1
    },
    "Dagdha": {
        "name_sanskrit": "Dagdha",
        "name_spanish": "Dagdha",
        "polarity": "negative",
        "type": "vara+tithi",
        "description": "Evitar matrimonio, viajes, nueva casa",
        "detailed_description": "Período desfavorable para actividades importantes. Evitar decisiones trascendentales.",
        "color": "#ef4444",
        "priority": 1
    },
    "Visha": {
        "name_sanskrit": "Viṣa",
        "name_spanish": "Visha",
        "polarity": "negative",
        "type": "vara+tithi",
        "description": "Evitar procedimientos médicos y viajes",
        "detailed_description": "Período desfavorable para tratamientos médicos y viajes largos.",
        "color": "#dc2626",
        "priority": 1
    },
    "Hutasana": {
        "name_sanskrit": "Hutāsana",
        "name_spanish": "Hutasana",
        "polarity": "negative",
        "type": "vara+tithi",
        "description": "Evitar actividades importantes",
        "detailed_description": "Período desfavorable para actividades importantes. Postergar decisiones.",
        "color": "#ef4444",
        "priority": 2
    },
    "Panchaka": {
        "name_sanskrit": "Pañcaka",
        "name_spanish": "Panchaka",
        "polarity": "negative",
        "type": "nakshatra+weekday",
        "description": "Evitar actividades importantes",
        "detailed_description": "Período desfavorable. Evitar actividades importantes según la clasificación del día.",
        "color": "#dc2626",
        "priority": 2
    },
    "Siddhi": {
        "name_sanskrit": "Siddhi",
        "name_spanish": "Siddhi",
        "polarity": "positive",
        "type": "vara+tithi_group",
        "description": "Competencias, litigios, tareas que exigen coraje",
        "detailed_description": "Favorece actividades que requieren coraje y determinación. Bueno para competencias.",
        "color": "#10b981",
        "priority": 2
    },
    "Amritasiddha": {
        "name_sanskrit": "Amṛtasiddha",
        "name_spanish": "Amritasiddha",
        "polarity": "positive",
        "type": "vara+tithi_group",
        "description": "Actividades auspiciosas, especialmente espirituales",
        "detailed_description": "Excelente para actividades espirituales y ceremonias religiosas.",
        "color": "#10b981",
        "priority": 2
    },
    "Jaya": {
        "name_sanskrit": "Jaya",
        "name_spanish": "Jaya",
        "polarity": "positive",
        "type": "vara+tithi_group",
        "description": "Victoria en competencias y litigios",
        "detailed_description": "Favorece la victoria en competencias, litigios y actividades competitivas.",
        "color": "#10b981",
        "priority": 2
    },
    "Rikta": {
        "name_sanskrit": "Rikta",
        "name_spanish": "Rikta",
        "polarity": "negative",
        "type": "vara+tithi_group",
        "description": "Evitar actividades importantes",
        "detailed_description": "Período desfavorable para actividades importantes. Evitar decisiones trascendentales.",
        "color": "#ef4444",
        "priority": 2
    },
    "Utpata": {
        "name_sanskrit": "Utpāta",
        "name_spanish": "Utpata",
        "polarity": "negative",
        "type": "vara+tithi_group",
        "description": "Evitar viajes y actividades importantes",
        "detailed_description": "Período desfavorable para viajes y actividades importantes. Postergar decisiones.",
        "color": "#dc2626",
        "priority": 1
    },
    "Mrityu": {
        "name_sanskrit": "Mṛtyu",
        "name_spanish": "Mrityu",
        "polarity": "negative",
        "type": "vara+tithi_group",
        "description": "Evitar actividades importantes",
        "detailed_description": "Período muy desfavorable. Evitar cualquier actividad importante.",
        "color": "#dc2626",
        "priority": 1
    },
    "Kana": {
        "name_sanskrit": "Kaṇa",
        "name_spanish": "Kana",
        "polarity": "negative",
        "type": "vara+tithi_group",
        "description": "Evitar actividades importantes",
        "detailed_description": "Período desfavorable. Evitar actividades importantes y decisiones trascendentales.",
        "color": "#ef4444",
        "priority": 2
    },
    # New special yogas
    "Guru Yoga": {
        "name_sanskrit": "Guru Yoga",
        "name_spanish": "Guru Yoga",
        "polarity": "positive",
        "type": "vara+nakshatra",
        "description": "Excelente para educación y sabiduría",
        "detailed_description": "Favorece el aprendizaje, la enseñanza y la adquisición de sabiduría.",
        "color": "#8b5cf6",
        "priority": 2
    },
    "Shukra Yoga": {
        "name_sanskrit": "Śukra Yoga",
        "name_spanish": "Shukra Yoga",
        "polarity": "positive",
        "type": "vara+nakshatra",
        "description": "Favorable para artes y relaciones",
        "detailed_description": "Excelente para actividades artísticas, relaciones y asuntos del corazón.",
        "color": "#ec4899",
        "priority": 2
    },
    "Mangala Yoga": {
        "name_sanskrit": "Maṅgala Yoga",
        "name_spanish": "Mangala Yoga",
        "polarity": "positive",
        "type": "vara+nakshatra",
        "description": "Favorable para coraje y energía",
        "detailed_description": "Favorece actividades que requieren coraje, energía y determinación.",
        "color": "#dc2626",
        "priority": 2
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

# Special Vara-Nakshatra combinations
VARA_NAKSHATRA_YOGAS = {
    ("Thursday", "Puṣya"): "Guru Pushya",
    ("Friday", "Citrā"): "Shukra Yoga",
    ("Tuesday", "Mṛgaśira"): "Mangala Yoga",
    ("Wednesday", "Rohiṇī"): "Budha Yoga",
    ("Monday", "Śravaṇa"): "Chandra Yoga"
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
        # In Vedic astrology, the day starts at sunrise
        # The vara is determined by the day on which the sunrise occurs
        # NOT by whether sunrise is before or after 6 AM
        
        # Get the date of the sunrise
        sunrise_date = dt.date()
        
        # Calculate weekday for the sunrise date
        # Python weekday(): Monday=0, Tuesday=1, ..., Sunday=6
        # Vedic Vara: Sunday=1, Monday=2, ..., Saturday=7
        weekday = sunrise_date.weekday()
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return weekdays[weekday]
    
    def detect_yogas(
        self,
        dt: datetime,
        latitude: float,
        longitude: float
    ) -> Dict:
        """Detect panchanga yogas for a specific date and location."""
        try:
            # Calculate actual sunrise time for the location
            from app.services.sunrise_precise import precise_sunrise_service
            
            try:
                # Get actual sunrise time for the location
                sunrise_dt = precise_sunrise_service.calculate_sunrise(dt, latitude, longitude)
                dt_with_time = sunrise_dt
            except Exception as e:
                # Fallback to approximate sunrise time (6:30 AM local time)
                logger.warning(f"Could not calculate precise sunrise, using fallback: {e}")
                dt_with_time = datetime.combine(dt.date(), datetime.strptime("06:30:00", "%H:%M:%S").time())
            
            # Calculate planetary positions using SWE service at sunrise
            planet_data = self.swe_service.calculate_planets(dt_with_time, ["Sun", "Moon"])
            
            sun_lon = planet_data["Sun"]["longitude"]
            moon_lon = planet_data["Moon"]["longitude"]
            
            # Get nakshatra names from SWE and convert to diacritic names
            sun_nakshatra_swe = planet_data["Sun"]["nakshatra"]["name"]
            moon_nakshatra_swe = planet_data["Moon"]["nakshatra"]["name"]
            
            sun_nakshatra = self._get_nakshatra_from_swe(sun_nakshatra_swe)
            nakshatra = self._get_nakshatra_from_swe(moon_nakshatra_swe)
            
            # Calculate panchanga elements
            tithi = self._calculate_tithi(sun_lon, moon_lon)
            weekday = self.get_weekday(dt_with_time)  # Use dt_with_time instead of dt
            
            # Get tithi group
            tithi_group = self._get_tithi_group(tithi)
            
            # Check special yogas
            positive_yogas = self._check_special_positive_yogas(weekday, tithi, tithi_group, nakshatra, sun_nakshatra, sun_lon, moon_lon)
            negative_yogas = self._check_special_negative_yogas(weekday, tithi, tithi_group, nakshatra, sun_nakshatra)
            
            # Sort yogas by priority
            positive_yogas.sort(key=lambda x: YOGAS_DEFINITIONS.get(x["name"], {}).get("priority", 3))
            negative_yogas.sort(key=lambda x: YOGAS_DEFINITIONS.get(x["name"], {}).get("priority", 3))
            
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
                "total_negative": len(negative_yogas),
                "summary": self._generate_yoga_summary(positive_yogas, negative_yogas)
            }
            
        except Exception as e:
            logger.error(f"Error detecting yogas: {e}")
            raise
    
    def _generate_yoga_summary(self, positive_yogas: List[Dict], negative_yogas: List[Dict]) -> Dict:
        """Generate a summary of the yogas for the day."""
        total_yogas = len(positive_yogas) + len(negative_yogas)
        
        if total_yogas == 0:
            return {
                "overall_muhurta": "neutral",
                "recommendation": "Día neutral para actividades",
                "priority_yogas": []
            }
        
        # Get highest priority yogas
        all_yogas = positive_yogas + negative_yogas
        all_yogas.sort(key=lambda x: YOGAS_DEFINITIONS.get(x["name"], {}).get("priority", 3))
        
        priority_yogas = all_yogas[:3]  # Top 3 yogas
        
        # Determine overall muhurta
        if len(positive_yogas) > len(negative_yogas):
            overall_muhurta = "auspicious"
            recommendation = "Día favorable para actividades importantes"
        elif len(negative_yogas) > len(positive_yogas):
            overall_muhurta = "inauspicious"
            recommendation = "Evitar actividades importantes"
        else:
            overall_muhurta = "mixed"
            recommendation = "Día mixto - consultar yogas específicos"
        
        return {
            "overall_muhurta": overall_muhurta,
            "recommendation": recommendation,
            "priority_yogas": priority_yogas
        }
    
    def _calculate_tithi(self, sun_lon: float, moon_lon: float) -> int:
        """Calculate tithi from Sun and Moon longitudes - corrected logic."""
        elongation = (moon_lon - sun_lon) % 360
        
        # Calculate tithi number correctly
        tithi_number = int(elongation / 12) + 1
        
        # Determine paksha and adjust tithi for Krishna paksha
        if elongation < 180:
            # Shukla paksha - tithi_number is correct (1-15)
            pass
        else:
            # Krishna paksha - adjust tithi_number to (1-15)
            tithi_number = tithi_number - 15
            if tithi_number <= 0:
                tithi_number += 15
        
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
                "detailed_description": yoga_def.get("detailed_description", ""),
                "avoid": "",
                "notes": "",
                "polarity": "positive",
                "priority": yoga_def.get("priority", 3)
            })
        
        # Check Vara-Nakshatra combinations
        if (weekday, nakshatra) in VARA_NAKSHATRA_YOGAS:
            yoga_name = VARA_NAKSHATRA_YOGAS[(weekday, nakshatra)]
            yoga_def = YOGAS_DEFINITIONS.get(yoga_name, {})
            
            yogas.append({
                "name": yoga_name,
                "type": "vara+nakshatra",
                "vara": weekday,
                "nakshatra": nakshatra,
                "beneficial": yoga_def.get("description", ""),
                "detailed_description": yoga_def.get("detailed_description", ""),
                "avoid": "",
                "notes": "",
                "polarity": "positive",
                "priority": yoga_def.get("priority", 3)
            })
        
        # Check Ravi Yoga (Sun-Moon relationship)
        sun_moon_diff = abs(sun_lon - moon_lon)
        if 0 <= sun_moon_diff <= 12 or 348 <= sun_moon_diff <= 360:
            yoga_def = YOGAS_DEFINITIONS.get("Ravi Yoga", {})
            yogas.append({
                "name": "Ravi Yoga",
                "type": "sun+moon",
                "sun_longitude": sun_lon,
                "moon_longitude": moon_lon,
                "difference": sun_moon_diff,
                "beneficial": yoga_def.get("description", ""),
                "detailed_description": yoga_def.get("detailed_description", ""),
                "avoid": "",
                "notes": "",
                "polarity": "positive",
                "priority": yoga_def.get("priority", 3)
            })
        
        # Check Ravi Pushya (Sun in Pushya)
        if sun_nakshatra == "Puṣya":
            yoga_def = YOGAS_DEFINITIONS.get("Ravi Pushya", {})
            yogas.append({
                "name": "Ravi Pushya",
                "type": "sun+nakshatra",
                "sun_nakshatra": sun_nakshatra,
                "beneficial": yoga_def.get("description", ""),
                "detailed_description": yoga_def.get("detailed_description", ""),
                "avoid": "",
                "notes": "",
                "polarity": "positive",
                "priority": yoga_def.get("priority", 3)
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
            yoga_def = YOGAS_DEFINITIONS.get("Dagdha", {})
            yogas.append({
                "name": "Dagdha",
                "type": "vara+tithi",
                "vara": weekday,
                "tithi_number": tithi,
                "beneficial": "",
                "avoid": yoga_def.get("description", ""),
                "detailed_description": yoga_def.get("detailed_description", ""),
                "notes": "",
                "polarity": "negative",
                "priority": yoga_def.get("priority", 3)
            })
        
        # Check Visha
        if (weekday, tithi) in VISHA_COMBINATIONS:
            yoga_def = YOGAS_DEFINITIONS.get("Visha", {})
            yogas.append({
                "name": "Visha",
                "type": "vara+tithi",
                "vara": weekday,
                "tithi_number": tithi,
                "beneficial": "",
                "avoid": yoga_def.get("description", ""),
                "detailed_description": yoga_def.get("detailed_description", ""),
                "notes": "",
                "polarity": "negative",
                "priority": yoga_def.get("priority", 3)
            })
        
        # Check Hutasana
        if (weekday, tithi) in HUTASANA_COMBINATIONS:
            yoga_def = YOGAS_DEFINITIONS.get("Hutasana", {})
            yogas.append({
                "name": "Hutasana",
                "type": "vara+tithi",
                "vara": weekday,
                "tithi_number": tithi,
                "beneficial": "",
                "avoid": yoga_def.get("description", ""),
                "detailed_description": yoga_def.get("detailed_description", ""),
                "notes": "",
                "polarity": "negative",
                "priority": yoga_def.get("priority", 3)
            })
        
        # Check Panchaka
        if nakshatra in PANCHAKA_NAKSHATRAS:
            classification = PANCHAKA_CLASSIFICATIONS.get(weekday, "")
            yoga_def = YOGAS_DEFINITIONS.get("Panchaka", {})
            yogas.append({
                "name": "Panchaka",
                "type": "nakshatra+weekday",
                "vara": weekday,
                "nakshatra": nakshatra,
                "classification": classification,
                "beneficial": "",
                "avoid": yoga_def.get("description", ""),
                "detailed_description": yoga_def.get("detailed_description", ""),
                "notes": f"Clasificación: {classification}",
                "polarity": "negative",
                "priority": yoga_def.get("priority", 3)
            })
        
        return yogas

# Create service instance
yogas_service = YogasService()
