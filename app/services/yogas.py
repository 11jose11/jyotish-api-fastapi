"""Yogas service for detecting panchanga combinations."""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.services.swe import swe_service
from app.util.logging import get_logger

logger = get_logger("yogas")

class YogasService:
    def __init__(self):
        self.swe_service = swe_service
        self.rules_file = os.path.join(os.path.dirname(__file__), "..", "..", "rules", "panchanga_rules.json")
        self.yoga_rules = self._load_yoga_rules()
        
    def _load_yoga_rules(self) -> Dict:
        """Load yoga rules from JSON file."""
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading yoga rules: {e}")
            return {"positive": {}, "negative": {}}
    
    def get_tithi_group(self, tithi_number: int) -> str:
        """Get tithi group (Nanda, Bhadra, Jaya, Rikta, Purna)."""
        if tithi_number in [1, 6, 11]:
            return "Nanda"
        elif tithi_number in [2, 7, 12]:
            return "Bhadra"
        elif tithi_number in [3, 8, 13]:
            return "Jaya"
        elif tithi_number in [4, 9, 14]:
            return "Rikta"
        elif tithi_number in [5, 10, 15, 30]:
            return "Purna"
        else:
            return "Unknown"
    
    def check_siddhi_yoga(self, vara: str, tithi_number: int) -> Optional[Dict]:
        """Check for Siddhi Yoga (vara + tithi group)."""
        if "Siddhi" not in self.yoga_rules["positive"]:
            return None
            
        tithi_group = self.get_tithi_group(tithi_number)
        
        for rule in self.yoga_rules["positive"]["Siddhi"]["rules"]:
            if rule["vara"] == vara and rule["tithi_group"] == tithi_group:
                return {
                    "name": "Siddhi",
                    "type": "vara+tithi_group",
                    "vara": vara,
                    "tithi_group": tithi_group,
                    "tithi_number": tithi_number,
                    "beneficial": rule["beneficial"],
                    "avoid": rule["avoid"],
                    "notes": rule.get("notes", ""),
                    "polarity": "positive"
                }
        return None
    
    def check_sarvarthasiddhi_yoga(self, vara: str, nakshatra: str) -> Optional[Dict]:
        """Check for Sarvarthasiddhi Yoga (vara + nakshatra)."""
        if "Sarvarthasiddhi" not in self.yoga_rules["positive"]:
            return None
            
        for rule in self.yoga_rules["positive"]["Sarvarthasiddhi"]["rules"]:
            if rule["vara"] == vara and nakshatra in rule["nakshatras"]:
                return {
                    "name": "Sarvarthasiddhi",
                    "type": "vara+nakshatra",
                    "vara": vara,
                    "nakshatra": nakshatra,
                    "beneficial": rule["beneficial"],
                    "avoid": rule["avoid"],
                    "polarity": "positive"
                }
        return None
    
    def check_amritasiddhi_yoga(self, vara: str, nakshatra: str) -> Optional[Dict]:
        """Check for Amritasiddhi Yoga (vara + nakshatra)."""
        if "Amritasiddhi" not in self.yoga_rules["positive"]:
            return None
            
        for rule in self.yoga_rules["positive"]["Amritasiddhi"]["rules"]:
            if rule["vara"] == vara and rule["nakshatra"] == nakshatra:
                return {
                    "name": "Amritasiddhi",
                    "type": "vara+nakshatra",
                    "vara": vara,
                    "nakshatra": nakshatra,
                    "beneficial": rule["beneficial"],
                    "avoid": rule["avoid"],
                    "polarity": "positive"
                }
        return None
    
    def check_siddha_yoga(self, vara: str, nakshatra: str) -> Optional[Dict]:
        """Check for Siddha Yoga (fourth group of Utpata-Mrityu-Kana-Siddha)."""
        if "Siddha" not in self.yoga_rules["positive"]:
            return None
            
        for rule in self.yoga_rules["positive"]["Siddha"]["rules"]:
            if rule["vara"] == vara and rule["nakshatra"] == nakshatra:
                return {
                    "name": "Siddha",
                    "type": "vara+nakshatra",
                    "vara": vara,
                    "nakshatra": nakshatra,
                    "beneficial": rule["beneficial"],
                    "avoid": rule["avoid"],
                    "polarity": "positive"
                }
        return None
    
    def check_ravi_yoga(self, sun_nakshatra: str, moon_nakshatra: str) -> Optional[Dict]:
        """Check for Ravi Yoga based on Sun-Moon nakshatra offset."""
        if "Ravi Yoga" not in self.yoga_rules["positive"]:
            return None
            
        # Get nakshatra indices
        nakshatras = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha",
            "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]
        
        try:
            sun_index = nakshatras.index(sun_nakshatra)
            moon_index = nakshatras.index(moon_nakshatra)
            
            # Calculate offset
            offset = (moon_index - sun_index) % 27
            if offset == 0:
                offset = 27
                
            if offset in self.yoga_rules["positive"]["Ravi Yoga"]["criteria"]["offset"]:
                return {
                    "name": "Ravi Yoga",
                    "type": "sun+moon_offset",
                    "sun_nakshatra": sun_nakshatra,
                    "moon_nakshatra": moon_nakshatra,
                    "offset": offset,
                    "beneficial": self.yoga_rules["positive"]["Ravi Yoga"]["beneficial"],
                    "avoid": self.yoga_rules["positive"]["Ravi Yoga"]["avoid"],
                    "polarity": "positive"
                }
        except ValueError:
            logger.warning(f"Invalid nakshatra names: {sun_nakshatra}, {moon_nakshatra}")
            
        return None
    
    def check_tripushkara_yoga(self, vara: str, tithi_number: int, nakshatra: str) -> Optional[Dict]:
        """Check for Tripushkara Yoga."""
        if "Tripushkara" not in self.yoga_rules["positive"]:
            return None
            
        criteria = self.yoga_rules["positive"]["Tripushkara"]["criteria"]
        
        # Check tithi group
        if tithi_number not in criteria["tithis"]:
            return None
            
        # Check vara
        if vara not in criteria["varas"]:
            return None
            
        # Check nakshatra families
        sun_nakshatras = criteria["nakshatra_families"]["Sun"]
        jupiter_nakshatras = criteria["nakshatra_families"]["Jupiter"]
        
        if nakshatra in sun_nakshatras or nakshatra in jupiter_nakshatras:
            return {
                "name": "Tripushkara",
                "type": "vara+tithi+nakshatra",
                "vara": vara,
                "tithi_number": tithi_number,
                "nakshatra": nakshatra,
                "beneficial": self.yoga_rules["positive"]["Tripushkara"]["beneficial"],
                "avoid": self.yoga_rules["positive"]["Tripushkara"]["avoid"],
                "notes": self.yoga_rules["positive"]["Tripushkara"]["notes"],
                "polarity": "positive"
            }
            
        return None
    
    def check_special_yogas(self, vara: str, nakshatra: str) -> List[Dict]:
        """Check for special yogas like Ravi Pushya and Guru Pushya."""
        special_yogas = []
        
        # Check Ravi Pushya
        if "Ravi Pushya" in self.yoga_rules["positive"]:
            criteria = self.yoga_rules["positive"]["Ravi Pushya"]["criteria"]
            if vara == criteria["vara"] and nakshatra == criteria["nakshatra"]:
                special_yogas.append({
                    "name": "Ravi Pushya",
                    "type": "vara+nakshatra",
                    "vara": vara,
                    "nakshatra": nakshatra,
                    "beneficial": self.yoga_rules["positive"]["Ravi Pushya"]["beneficial"],
                    "avoid": self.yoga_rules["positive"]["Ravi Pushya"]["avoid"],
                    "polarity": "positive"
                })
        
        # Check Guru Pushya
        if "Guru Pushya" in self.yoga_rules["positive"]:
            criteria = self.yoga_rules["positive"]["Guru Pushya"]["criteria"]
            if vara == criteria["vara"] and nakshatra == criteria["nakshatra"]:
                special_yogas.append({
                    "name": "Guru Pushya",
                    "type": "vara+nakshatra",
                    "vara": vara,
                    "nakshatra": nakshatra,
                    "beneficial": self.yoga_rules["positive"]["Guru Pushya"]["beneficial"],
                    "avoid": self.yoga_rules["positive"]["Guru Pushya"]["avoid"],
                    "polarity": "positive"
                })
                
        return special_yogas
    
    def check_negative_yogas(self, vara: str, tithi_number: int, nakshatra: str) -> List[Dict]:
        """Check for negative yogas."""
        negative_yogas = []
        
        # Check Adhama
        if "Adhama" in self.yoga_rules["negative"]:
            for rule in self.yoga_rules["negative"]["Adhama"]["rules"]:
                if rule["tithi"] == tithi_number:
                    if isinstance(rule["nakshatra"], list):
                        if nakshatra in rule["nakshatra"]:
                            negative_yogas.append({
                                "name": "Adhama",
                                "type": "tithi+nakshatra",
                                "tithi_number": tithi_number,
                                "nakshatra": nakshatra,
                                "effect": rule["effect"],
                                "polarity": "negative"
                            })
                    elif rule["nakshatra"] == nakshatra:
                        negative_yogas.append({
                            "name": "Adhama",
                            "type": "tithi+nakshatra",
                            "tithi_number": tithi_number,
                            "nakshatra": nakshatra,
                            "effect": rule["effect"],
                            "polarity": "negative"
                        })
        
        # Check Utpata
        if "Utpata" in self.yoga_rules["negative"]:
            for rule in self.yoga_rules["negative"]["Utpata"]["rules"]:
                if rule["vara"] == vara and rule["nakshatra"] == nakshatra:
                    negative_yogas.append({
                        "name": "Utpata",
                        "type": "vara+nakshatra",
                        "vara": vara,
                        "nakshatra": nakshatra,
                        "effect": rule["effect"],
                        "polarity": "negative"
                    })
        
        # Check Mrityu
        if "Mrityu" in self.yoga_rules["negative"]:
            for rule in self.yoga_rules["negative"]["Mrityu"]["rules"]:
                if rule["vara"] == vara and rule["nakshatra"] == nakshatra:
                    negative_yogas.append({
                        "name": "Mrityu",
                        "type": "vara+nakshatra",
                        "vara": vara,
                        "nakshatra": nakshatra,
                        "effect": rule["effect"],
                        "polarity": "negative"
                    })
        
        # Check Kana
        if "Kana" in self.yoga_rules["negative"]:
            for rule in self.yoga_rules["negative"]["Kana"]["rules"]:
                if rule["vara"] == vara and rule["nakshatra"] == nakshatra:
                    negative_yogas.append({
                        "name": "Kana",
                        "type": "vara+nakshatra",
                        "vara": vara,
                        "nakshatra": nakshatra,
                        "effect": rule["effect"],
                        "polarity": "negative"
                    })
        
        # Check Dagdha
        if "Dagdha" in self.yoga_rules["negative"]:
            for rule in self.yoga_rules["negative"]["Dagdha"]["rules"]:
                if rule["vara"] == vara:
                    if isinstance(rule["tithi"], list):
                        if tithi_number in rule["tithi"]:
                            negative_yogas.append({
                                "name": "Dagdha",
                                "type": "vara+tithi",
                                "vara": vara,
                                "tithi_number": tithi_number,
                                "effect": rule["effect"],
                                "polarity": "negative"
                            })
                    elif rule["tithi"] == tithi_number:
                        negative_yogas.append({
                            "name": "Dagdha",
                            "type": "vara+tithi",
                            "vara": vara,
                            "tithi_number": tithi_number,
                            "effect": rule["effect"],
                            "polarity": "negative"
                        })
        
        # Check Hutasana
        if "Hutasana" in self.yoga_rules["negative"]:
            for rule in self.yoga_rules["negative"]["Hutasana"]["rules"]:
                if rule["vara"] == vara and rule["tithi"] == tithi_number:
                    negative_yogas.append({
                        "name": "Hutasana",
                        "type": "vara+tithi",
                        "vara": vara,
                        "tithi_number": tithi_number,
                        "effect": rule["effect"],
                        "polarity": "negative"
                    })
        
        # Check Visha
        if "Visha" in self.yoga_rules["negative"]:
            for rule in self.yoga_rules["negative"]["Visha"]["rules"]:
                if rule["vara"] == vara and rule["tithi"] == tithi_number:
                    negative_yogas.append({
                        "name": "Visha",
                        "type": "vara+tithi",
                        "vara": vara,
                        "tithi_number": tithi_number,
                        "effect": rule["effect"],
                        "polarity": "negative"
                    })
        
        # Check Samvartaka
        if "Samvartaka" in self.yoga_rules["negative"]:
            for rule in self.yoga_rules["negative"]["Samvartaka"]["rules"]:
                if rule["vara"] == vara and rule["tithi"] == tithi_number:
                    negative_yogas.append({
                        "name": "Samvartaka",
                        "type": "vara+tithi",
                        "vara": vara,
                        "tithi_number": tithi_number,
                        "effect": rule["effect"],
                        "polarity": "negative"
                    })
        
        # Check Shoonya Nakshatra
        if "Shoonya Nakshatra" in self.yoga_rules["negative"]:
            for rule in self.yoga_rules["negative"]["Shoonya Nakshatra"]["rules"]:
                if rule["tithi"] == tithi_number:
                    if isinstance(rule["nakshatra"], list):
                        if nakshatra in rule["nakshatra"]:
                            negative_yogas.append({
                                "name": "Shoonya Nakshatra",
                                "type": "tithi+nakshatra",
                                "tithi_number": tithi_number,
                                "nakshatra": nakshatra,
                                "use": rule["use"],
                                "avoid": rule["avoid"],
                                "polarity": "negative"
                            })
                    elif rule["nakshatra"] == nakshatra:
                        negative_yogas.append({
                            "name": "Shoonya Nakshatra",
                            "type": "tithi+nakshatra",
                            "tithi_number": tithi_number,
                            "nakshatra": nakshatra,
                            "use": rule["use"],
                            "avoid": rule["avoid"],
                            "polarity": "negative"
                        })
        
        return negative_yogas
    
    def check_gandamula(self, nakshatra: str) -> Optional[Dict]:
        """Check for Gandamula yoga."""
        if "Gandamula" in self.yoga_rules["negative"]:
            if nakshatra in self.yoga_rules["negative"]["Gandamula"]["nakshatras"]:
                return {
                    "name": "Gandamula",
                    "type": "nakshatra",
                    "nakshatra": nakshatra,
                    "effect": self.yoga_rules["negative"]["Gandamula"]["effect"],
                    "recommendation": self.yoga_rules["negative"]["Gandamula"]["recommendation"],
                    "polarity": "negative"
                }
        return None
    
    def check_panchaka(self, nakshatra: str) -> Optional[Dict]:
        """Check for Panchaka yoga."""
        if "Panchaka" in self.yoga_rules["negative"]:
            sequence = self.yoga_rules["negative"]["Panchaka"]["nakshatra_sequence"]
            if nakshatra in sequence:
                return {
                    "name": "Panchaka",
                    "type": "nakshatra_sequence",
                    "nakshatra": nakshatra,
                    "sequence": sequence,
                    "effect": self.yoga_rules["negative"]["Panchaka"]["effect"],
                    "recommendation": self.yoga_rules["negative"]["Panchaka"]["recommendation"],
                    "polarity": "negative"
                }
        return None
    
    def detect_yogas(self, date: datetime, latitude: float, longitude: float) -> Dict:
        """Detect all yogas for a given date and location."""
        try:
            # Calculate planetary positions
            planet_data = self.swe_service.calculate_planets(date, ["Sun", "Moon"])
            
            sun_lon = planet_data["Sun"]["lon"]
            moon_lon = planet_data["Moon"]["lon"]
            
            # Get panchanga elements
            from app.services.panchanga import panchanga_service
            
            # Calculate tithi
            tithi_data = panchanga_service.calculate_tithi(sun_lon, moon_lon)
            tithi_number = tithi_data["tithi_number"]
            
            # Get nakshatra
            nakshatra_data = panchanga_service.get_nakshatra(moon_lon)
            nakshatra = nakshatra_data[0]
            
            # Get vara
            vara_data = panchanga_service.calculate_vara(date)
            vara = vara_data["name"]
            
            # Get Sun nakshatra
            sun_nakshatra_data = panchanga_service.get_nakshatra(sun_lon)
            sun_nakshatra = sun_nakshatra_data[0]
            
            # Detect positive yogas
            positive_yogas = []
            
            # Check Siddhi Yoga
            siddhi = self.check_siddhi_yoga(vara, tithi_number)
            if siddhi:
                positive_yogas.append(siddhi)
            
            # Check Sarvarthasiddhi Yoga
            sarvarthasiddhi = self.check_sarvarthasiddhi_yoga(vara, nakshatra)
            if sarvarthasiddhi:
                positive_yogas.append(sarvarthasiddhi)
            
            # Check Amritasiddhi Yoga
            amritasiddhi = self.check_amritasiddhi_yoga(vara, nakshatra)
            if amritasiddhi:
                positive_yogas.append(amritasiddhi)
            
            # Check Siddha Yoga
            siddha = self.check_siddha_yoga(vara, nakshatra)
            if siddha:
                positive_yogas.append(siddha)
            
            # Check Ravi Yoga
            ravi = self.check_ravi_yoga(sun_nakshatra, nakshatra)
            if ravi:
                positive_yogas.append(ravi)
            
            # Check Tripushkara Yoga
            tripushkara = self.check_tripushkara_yoga(vara, tithi_number, nakshatra)
            if tripushkara:
                positive_yogas.append(tripushkara)
            
            # Check special yogas
            special_yogas = self.check_special_yogas(vara, nakshatra)
            positive_yogas.extend(special_yogas)
            
            # Detect negative yogas
            negative_yogas = self.check_negative_yogas(vara, tithi_number, nakshatra)
            
            # Check Gandamula
            gandamula = self.check_gandamula(nakshatra)
            if gandamula:
                negative_yogas.append(gandamula)
            
            # Check Panchaka
            panchaka = self.check_panchaka(nakshatra)
            if panchaka:
                negative_yogas.append(panchaka)
            
            return {
                "date": date.date().isoformat(),
                "location": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "panchanga": {
                    "vara": vara,
                    "tithi": tithi_data,
                    "nakshatra": nakshatra_data,
                    "sun_nakshatra": sun_nakshatra_data
                },
                "positive_yogas": positive_yogas,
                "negative_yogas": negative_yogas,
                "total_positive": len(positive_yogas),
                "total_negative": len(negative_yogas)
            }
            
        except Exception as e:
            logger.error(f"Error detecting yogas: {e}")
            raise

# Create service instance
yogas_service = YogasService()
