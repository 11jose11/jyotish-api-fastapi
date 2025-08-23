"""
Navatāra Chakra Service for Jyotiṣa API
Unified service for calculating Navatāra Chakra based on birth nakshatra
"""

from datetime import datetime
from typing import Dict, List, Optional, Union
import swisseph as swe
from app.services.swe import swe_service
from app.util.logging import get_logger

logger = get_logger("navatara")

class NavataraService:
    """Navatāra Chakra calculation service."""
    
    def __init__(self):
        self.nakshatras_27 = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
            "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]
        
        self.nakshatras_28 = self.nakshatras_27 + ["Abhijit"]
        
        self.group_deities = {
            "Agni": ["Ashwini", "Magha", "Mula"],
            "Vayu": ["Bharani", "Purva Phalguni", "Purva Ashadha"],
            "Surya": ["Krittika", "Uttara Phalguni", "Uttara Ashadha"],
            "Varuna": ["Rohini", "Hasta", "Shravana"],
            "Indra": ["Mrigashira", "Chitra", "Dhanishta"],
            "Vishnu": ["Ardra", "Swati", "Shatabhisha"],
            "Ashwini Kumaras": ["Punarvasu", "Vishakha", "Purva Bhadrapada"],
            "Rudra": ["Pushya", "Anuradha", "Uttara Bhadrapada"],
            "Ganesha": ["Ashlesha", "Jyeshtha", "Revati"]
        }
        
        self.lokas = {
            "Bhuloka": ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha"],
            "Bhuvarloka": ["Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha"],
            "Svarloka": ["Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
        }
        
        self.special_taras = {
            "Mangala": ["Ashwini", "Magha", "Mula"],
            "Pitra": ["Bharani", "Purva Phalguni", "Purva Ashadha"],
            "Ati-Mangala": ["Krittika", "Uttara Phalguni", "Uttara Ashadha"],
            "Mrityu": ["Rohini", "Hasta", "Shravana"],
            "Kshipra": ["Mrigashira", "Chitra", "Dhanishta"],
            "Ugra": ["Ardra", "Swati", "Shatabhisha"],
            "Adhi-Mrityu": ["Punarvasu", "Vishakha", "Purva Bhadrapada"],
            "Kaal": ["Pushya", "Anuradha", "Uttara Bhadrapada"],
            "Maitri": ["Ashlesha", "Jyeshtha", "Revati"]
        }

    def get_nakshatra_index(self, nakshatra_name: str, scheme: int = 27) -> Optional[int]:
        """Get nakshatra index by name."""
        nakshatras = self.nakshatras_28 if scheme == 28 else self.nakshatras_27
        try:
            return nakshatras.index(nakshatra_name)
        except ValueError:
            return None

    def get_nakshatra_name(self, index: int, scheme: int = 27) -> Optional[str]:
        """Get nakshatra name by index."""
        nakshatras = self.nakshatras_28 if scheme == 28 else self.nakshatras_27
        if 0 <= index < len(nakshatras):
            return nakshatras[index]
        return None

    def normalize_index(self, index: int, scheme: int = 27) -> int:
        """Normalize index to valid range."""
        max_index = 28 if scheme == 28 else 27
        return index % max_index

    def relative_to_absolute(self, relative_index: int, start_index: int, scheme: int = 27) -> int:
        """Convert relative index to absolute index."""
        max_index = 28 if scheme == 28 else 27
        absolute_index = start_index + relative_index
        return self.normalize_index(absolute_index, scheme)

    def group_of_9(self, nakshatra_index: int, scheme: int = 27) -> int:
        """Get group of 9 for nakshatra."""
        max_index = 28 if scheme == 28 else 27
        return (nakshatra_index // 9) + 1

    def cycle_of(self, nakshatra_index: int, scheme: int = 27) -> int:
        """Get cycle number for nakshatra."""
        max_index = 28 if scheme == 28 else 27
        return (nakshatra_index // 3) + 1

    def loka_of(self, nakshatra_index: int, scheme: int = 27) -> str:
        """Get loka for nakshatra."""
        nakshatra_name = self.get_nakshatra_name(nakshatra_index, scheme)
        if not nakshatra_name:
            return "Unknown"
        
        for loka, nakshatras in self.lokas.items():
            if nakshatra_name in nakshatras:
                return loka
        return "Unknown"

    def special_taras_for(self, nakshatra_index: int, scheme: int = 27) -> List[str]:
        """Get special taras for nakshatra."""
        nakshatra_name = self.get_nakshatra_name(nakshatra_index, scheme)
        if not nakshatra_name:
            return []
        
        special_taras = []
        for tara, nakshatras in self.special_taras.items():
            if nakshatra_name in nakshatras:
                special_taras.append(tara)
        return special_taras

    def get_group_deity(self, nakshatra_index: int, scheme: int = 27) -> str:
        """Get group deity for nakshatra."""
        nakshatra_name = self.get_nakshatra_name(nakshatra_index, scheme)
        if not nakshatra_name:
            return "Unknown"
        
        for deity, nakshatras in self.group_deities.items():
            if nakshatra_name in nakshatras:
                return deity
        return "Unknown"

    def get_start_nakshatra(self, date: str, latitude: float, longitude: float, 
                           start_type: str = "moon", time: str = "12:00:00") -> Dict:
        """Get starting nakshatra based on birth data."""
        try:
            # Parse date and time
            dt_str = f"{date}T{time}"
            dt = datetime.fromisoformat(dt_str)
            
            # Calculate planetary positions
            planet_data = swe_service.calculate_planets(dt, [start_type.capitalize()])
            
            if start_type.lower() == "moon" and "Moon" in planet_data:
                longitude = planet_data["Moon"]["longitude"]
            elif start_type.lower() == "sun" and "Sun" in planet_data:
                longitude = planet_data["Sun"]["longitude"]
            elif start_type.lower() == "lagna":
                # Calculate Lagna (Ascendant)
                jd = swe.julday(dt.year, dt.month, dt.day, 
                               dt.hour + dt.minute/60.0 + dt.second/3600.0)
                longitude = swe.houses(jd, latitude, longitude)[0]
            else:
                raise ValueError(f"Invalid start type: {start_type}")
            
            # Calculate nakshatra
            nakshatra_num = int(longitude * 27 / 360) + 1
            nakshatra_name = self.get_nakshatra_name(nakshatra_num - 1, 27)
            
            return {
                "nakshatra_index": nakshatra_num - 1,
                "nakshatra_name": nakshatra_name,
                "longitude": longitude,
                "start_type": start_type,
                "date": date,
                "time": time
            }
            
        except Exception as e:
            logger.error(f"Error calculating start nakshatra: {e}")
            raise

    def build_navatara_map(self, start_nakshatra_index: int, scheme: int = 27, 
                          lang: str = "en") -> List[Dict]:
        """Build complete Navatāra mapping."""
        mapping = []
        max_index = 28 if scheme == 28 else 27
        
        for i in range(max_index):
            absolute_index = self.relative_to_absolute(i, start_nakshatra_index, scheme)
            nakshatra_name = self.get_nakshatra_name(absolute_index, scheme)
            
            if not nakshatra_name:
                continue
            
            mapping.append({
                "position": i + 1,
                "nakshatra_index": absolute_index,
                "nakshatra_name": nakshatra_name,
                "group": self.group_of_9(absolute_index, scheme),
                "cycle": self.cycle_of(absolute_index, scheme),
                "loka": self.loka_of(absolute_index, scheme),
                "group_deity": self.get_group_deity(absolute_index, scheme),
                "special_taras": self.special_taras_for(absolute_index, scheme)
            })
        
        return mapping

    def generate_metadata(self, scheme: int = 27, lang: str = "en") -> Dict:
        """Generate metadata for Navatāra calculation."""
        return {
            "scheme": scheme,
            "language": lang,
            "total_nakshatras": scheme,
            "description": f"Navatāra Chakra based on {scheme} nakshatra scheme",
            "calculation_method": "Based on birth nakshatra position",
            "ayanamsa": "True Citra Paksha"
        }

    def calculate_navatara(self, date: str, latitude: float, longitude: float,
                          start_type: str = "moon", time: str = "12:00:00",
                          scheme: int = 27, lang: str = "en") -> Dict:
        """Calculate complete Navatāra Chakra."""
        try:
            # Get starting nakshatra
            start_data = self.get_start_nakshatra(date, latitude, longitude, start_type, time)
            
            # Build mapping
            mapping = self.build_navatara_map(start_data["nakshatra_index"], scheme, lang)
            
            # Generate metadata
            metadata = self.generate_metadata(scheme, lang)
            
            return {
                "start_nakshatra": start_data,
                "mapping": mapping,
                "metadata": metadata,
                "calculation_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating Navatāra: {e}")
            raise

# Global service instance
navatara_service = NavataraService()
