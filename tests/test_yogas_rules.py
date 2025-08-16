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
            moon_lon=0.0
        )
        
        guru_pushya_found = any(yoga["name"] == "Guru Pushya" for yoga in result)
        assert guru_pushya_found
    
    def test_negative_yoga_detection(self):
        """Test negative yoga detection."""
        # Test Dagdha (Sunday + tithi 1,6,11,16,21,26)
        result = yogas_service._check_negative_yogas(
            weekday="Sunday",
            tithi=1,
            nakshatra="Ashwini"
        )
        
        dagdha_found = any(yoga["name"] == "Dagdha" for yoga in result)
        assert dagdha_found
        
        # Test Visha (Monday + tithi 2,7,12,17,22,27)
        result = yogas_service._check_negative_yogas(
            weekday="Monday",
            tithi=2,
            nakshatra="Bharani"
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
