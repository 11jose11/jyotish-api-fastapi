"""Yoga rules tests."""

import pytest
from app.services.yogas import yogas_service


class TestYogaRules:
    """Test yoga detection rules."""
    
    def test_weekday_calculation(self):
        """Test weekday calculation."""
        from datetime import datetime
        
        # Test known weekdays
        assert yogas_service.get_weekday(datetime(2024, 1, 1)) == "Monday"  # Monday
        assert yogas_service.get_weekday(datetime(2024, 1, 2)) == "Tuesday"  # Tuesday
        assert yogas_service.get_weekday(datetime(2024, 1, 3)) == "Wednesday"  # Wednesday
        assert yogas_service.get_weekday(datetime(2024, 1, 4)) == "Thursday"  # Thursday
        assert yogas_service.get_weekday(datetime(2024, 1, 5)) == "Friday"  # Friday
        assert yogas_service.get_weekday(datetime(2024, 1, 6)) == "Saturday"  # Saturday
        assert yogas_service.get_weekday(datetime(2024, 1, 7)) == "Sunday"  # Sunday
    
    def test_tithi_calculation(self):
        """Test tithi calculation in yoga service."""
        # Test same position
        assert yogas_service._calculate_tithi(0.0, 0.0) == 1
        
        # Test one tithi ahead
        assert yogas_service._calculate_tithi(0.0, 12.0) == 2
        
        # Test full cycle
        assert yogas_service._calculate_tithi(0.0, 360.0) == 1
    
    def test_nakshatra_calculation(self):
        """Test nakshatra calculation in yoga service."""
        # Test first nakshatra
        assert yogas_service._get_nakshatra(0.0) == "Ashwini"
        
        # Test second nakshatra
        nakshatra_span = 13 + 1/3
        assert yogas_service._get_nakshatra(nakshatra_span) == "Bharani"
        
        # Test third nakshatra
        assert yogas_service._get_nakshatra(nakshatra_span * 2) == "Krittika"
    
    def test_positive_yoga_detection(self):
        """Test positive yoga detection."""
        # Test Guru Pushya (Thursday + Pushya)
        result = yogas_service._check_positive_yogas(
            weekday="Thursday",
            tithi=15,
            nakshatra="Pushya",
            sun_lon=0.0,
            moon_lon=0.0,
            sun_nakshatra="Ashwini"
        )
        
        guru_pushya_found = any(yoga["name"] == "Guru Pushya" for yoga in result)
        assert guru_pushya_found
    
    def test_negative_yoga_detection(self):
        """Test negative yoga detection."""
        # Test Dagdha (Sunday + tithi 1,6,11,16,21,26)
        result = yogas_service._check_negative_yogas(
            weekday="Sunday",
            tithi=1,
            nakshatra="Ashwini",
            sun_nakshatra="Ashwini"
        )
        
        dagdha_found = any(yoga["name"] == "Dagdha" for yoga in result)
        assert dagdha_found
        
        # Test Visha (Monday + tithi 2,7,12,17,22,27)
        result = yogas_service._check_negative_yogas(
            weekday="Monday",
            tithi=2,
            nakshatra="Bharani",
            sun_nakshatra="Ashwini"
        )
        
        visha_found = any(yoga["name"] == "Visha" for yoga in result)
        assert visha_found
    
    def test_yoga_criteria_matching(self):
        """Test yoga criteria matching."""
        # Test exact match
        assert yogas_service._matches_yoga_criteria(
            {"criteria": {"weekday": "Thursday"}},
            "Thursday", 1, "Ashwini"
        )
        
        # Test list match
        assert yogas_service._matches_yoga_criteria(
            {"criteria": {"weekday": ["Thursday", "Friday"]}},
            "Thursday", 1, "Ashwini"
        )
        
        # Test no match
        assert not yogas_service._matches_yoga_criteria(
            {"criteria": {"weekday": "Friday"}},
            "Thursday", 1, "Ashwini"
        )
    
    def test_yoga_flags(self):
        """Test yoga flags."""
        flags = yogas_service._get_yoga_flags("Guru Pushya")
        assert "recommendedFor: education, business" in flags
        
        flags = yogas_service._get_yoga_flags("Dagdha")
        assert "notRecommendedFor: marriage, travel, newHouse" in flags
        
        # Test unknown yoga
        flags = yogas_service._get_yoga_flags("Unknown Yoga")
        assert flags == []
    
    def test_sarvartha_siddhi_detection(self):
        """Test Sarvartha Siddhi yoga detection."""
        result = yogas_service._check_positive_yogas(
            weekday="Monday",
            tithi=15,
            nakshatra="Rohini",
            sun_lon=0.0,
            moon_lon=0.0,
            sun_nakshatra="Ashwini"
        )
        
        sarvartha_siddhi_found = any(yoga["name"] == "Sarvartha Siddhi" for yoga in result)
        assert sarvartha_siddhi_found
    
    def test_siddha_detection(self):
        """Test Siddha yoga detection."""
        result = yogas_service._check_positive_yogas(
            weekday="Tuesday",
            tithi=15,
            nakshatra="Krittika",
            sun_lon=0.0,
            moon_lon=0.0,
            sun_nakshatra="Ashwini"
        )
        
        siddha_found = any(yoga["name"] == "Siddha" for yoga in result)
        assert siddha_found
    
    def test_ravi_pushya_detection(self):
        """Test Ravi Pushya yoga detection (sun+nakshatra type)."""
        result = yogas_service._check_positive_yogas(
            weekday="Thursday",
            tithi=15,
            nakshatra="Ashwini",  # Lunar nakshatra doesn't matter for this yoga
            sun_lon=0.0,
            moon_lon=0.0,
            sun_nakshatra="Pushya"  # Sun must be in Pushya
        )
        
        ravi_pushya_found = any(yoga["name"] == "Ravi Pushya" for yoga in result)
        assert ravi_pushya_found
    
    def test_ravi_yoga_detection(self):
        """Test Ravi Yoga detection (sun+moon type)."""
        # Test with offset 4 (Ashwini to Pushya)
        sun_lon = 0.0  # Ashwini (index 0)
        moon_lon = 60.0  # Pushya (index 4, so offset = 4)
        
        result = yogas_service._check_positive_yogas(
            weekday="Thursday",
            tithi=15,
            nakshatra="Pushya",
            sun_lon=sun_lon,
            moon_lon=moon_lon,
            sun_nakshatra="Ashwini"
        )
        
        ravi_yoga_found = any(yoga["name"] == "Ravi Yoga" for yoga in result)
        assert ravi_yoga_found
    
    def test_dvipushkara_detection(self):
        """Test Dvipushkara yoga detection."""
        result = yogas_service._check_positive_yogas(
            weekday="Thursday",
            tithi=2,  # Must be tithi 2, 7, or 12
            nakshatra="Ashwini",  # Must be in first 6 nakshatras
            sun_lon=0.0,
            moon_lon=0.0,
            sun_nakshatra="Ashwini"
        )
        
        dvipushkara_found = any(yoga["name"] == "Dvipushkara" for yoga in result)
        assert dvipushkara_found
    
    def test_tripushkara_detection(self):
        """Test Tripushkara yoga detection."""
        result = yogas_service._check_positive_yogas(
            weekday="Thursday",
            tithi=2,  # Must be tithi 2, 7, or 12
            nakshatra="Pushya",  # Must be in middle 6 nakshatras
            sun_lon=0.0,
            moon_lon=0.0,
            sun_nakshatra="Ashwini"
        )
        
        tripushkara_found = any(yoga["name"] == "Tripushkara" for yoga in result)
        assert tripushkara_found
    
    def test_hutasana_detection(self):
        """Test Hutasana yoga detection."""
        result = yogas_service._check_negative_yogas(
            weekday="Tuesday",
            tithi=3,  # Must be tithi 3, 8, 13, 18, 23, 28
            nakshatra="Krittika",
            sun_nakshatra="Ashwini"
        )
        
        hutasana_found = any(yoga["name"] == "Hutasana" for yoga in result)
        assert hutasana_found
    
    def test_krakacha_detection(self):
        """Test Krakacha yoga detection."""
        result = yogas_service._check_negative_yogas(
            weekday="Wednesday",
            tithi=4,  # Must be tithi 4, 9, 14, 19, 24, 29
            nakshatra="Rohini",
            sun_nakshatra="Ashwini"
        )
        
        krakacha_found = any(yoga["name"] == "Krakacha" for yoga in result)
        assert krakacha_found
    
    def test_samvartaka_detection(self):
        """Test Samvartaka yoga detection."""
        result = yogas_service._check_negative_yogas(
            weekday="Thursday",
            tithi=5,  # Must be tithi 5, 10, 15, 20, 25, 30
            nakshatra="Mrigashira",
            sun_nakshatra="Ashwini"
        )
        
        samvartaka_found = any(yoga["name"] == "Samvartaka" for yoga in result)
        assert samvartaka_found
    
    def test_asubha_detection(self):
        """Test Asubha yoga detection."""
        result = yogas_service._check_negative_yogas(
            weekday="Thursday",
            tithi=1,  # Must be tithi 1, 6, 11, 16, 21, 26
            nakshatra="Ashlesha",  # Must be in specific nakshatras
            sun_nakshatra="Ashwini"
        )
        
        asubha_found = any(yoga["name"] == "Asubha" for yoga in result)
        assert asubha_found
    
    def test_vinasa_detection(self):
        """Test Vinasa yoga detection (triple type)."""
        result = yogas_service._check_negative_yogas(
            weekday="Sunday",
            tithi=15,
            nakshatra="Ashlesha",  # Sunday + Ashlesha should trigger Vinasa
            sun_nakshatra="Ashwini"
        )
        
        vinasa_found = any(yoga["name"] == "Vinasa" for yoga in result)
        assert vinasa_found
    
    def test_panchaka_detection(self):
        """Test Panchaka yoga detection (nakshatra+weekday type)."""
        result = yogas_service._check_negative_yogas(
            weekday="Tuesday",
            tithi=15,
            nakshatra="Dhanishtha",  # Must be in Panchaka nakshatras
            sun_nakshatra="Ashwini"
        )
        
        panchaka_found = any(yoga["name"] == "Panchaka" for yoga in result)
        assert panchaka_found
        
        # Check that classification is included
        panchaka_yoga = next((yoga for yoga in result if yoga["name"] == "Panchaka"), None)
        assert panchaka_yoga is not None
        assert "classification" in panchaka_yoga
        assert panchaka_yoga["classification"] == "agni"  # Tuesday classification
    
    def test_yoga_type_handling(self):
        """Test different yoga type handling."""
        # Test sun+nakshatra type
        assert yogas_service._matches_yoga_criteria(
            {"type": "sun+nakshatra", "criteria": {"nakshatra": ["Pushya"]}},
            "Thursday", 1, "Ashwini", sun_nakshatra="Pushya"
        )
        
        # Test triple type
        assert yogas_service._matches_yoga_criteria(
            {"type": "triple", "criteria": {"Sunday": ["Ashlesha"]}},
            "Sunday", 1, "Ashlesha"
        )
        
        # Test nakshatra+weekday type
        assert yogas_service._matches_yoga_criteria(
            {"type": "nakshatra+weekday", "criteria": {"nakshatra": ["Dhanishtha"], "classification": {"Tuesday": "agni"}}},
            "Tuesday", 1, "Dhanishtha"
        )
        
        # Test sun+moon type
        assert yogas_service._matches_yoga_criteria(
            {"type": "sun+moon", "criteria": {"offset": [4]}},
            "Thursday", 1, "Pushya", sun_lon=0.0, moon_lon=60.0
        )
