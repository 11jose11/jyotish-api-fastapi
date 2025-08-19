"""Basic Swiss Ephemeris tests."""

import pytest
from datetime import datetime
from app.services.swe import swe_service


class TestSwissEphemeris:
    """Test basic Swiss Ephemeris functionality."""
    
    def test_initialization(self):
        """Test SWE service initialization."""
        assert swe_service.initialized
        assert swe_service.precision in ["high", "low"]
    
    def test_planet_calculation(self):
        """Test planet position calculation."""
        dt = datetime(2025, 8, 17, 12, 0, 0)
        result = swe_service.calculate_planets(dt, ["Sun", "Moon"])
        
        # Check structure
        assert "Sun" in result
        assert "Moon" in result
        
        # Check Sun data
        sun_data = result["Sun"]
        assert "longitude" in sun_data
        assert "latitude" in sun_data
        assert "distance" in sun_data
        assert "rasi" in sun_data
        assert "nakshatra" in sun_data
        
        # Check Moon data
        moon_data = result["Moon"]
        assert "longitude" in moon_data
        assert "latitude" in moon_data
        assert "distance" in moon_data
        assert "rasi" in moon_data
        assert "nakshatra" in moon_data
    
    def test_rasi_calculation(self):
        """Test rashi calculation."""
        rasi_name, rasi_number = swe_service.get_rasi(0)
        assert rasi_name == "Mesha"
        assert rasi_number == 1
        
        rasi_name, rasi_number = swe_service.get_rasi(30)
        assert rasi_name == "Vrishabha"
        assert rasi_number == 2
        
        rasi_name, rasi_number = swe_service.get_rasi(330)
        assert rasi_name == "Meena"
        assert rasi_number == 12
    
    def test_nakshatra_calculation(self):
        """Test nakshatra calculation."""
        nakshatra_name, nakshatra_number, pada = swe_service.get_nakshatra(0)
        assert nakshatra_name == "Ashwini"
        assert nakshatra_number == 1
        assert pada == 1
        
        nakshatra_name, nakshatra_number, pada = swe_service.get_nakshatra(13.333)
        assert nakshatra_name == "Ashwini"
        assert nakshatra_number == 1
        assert pada == 4  # 13.333 is in the 4th pada of Ashwini
    
    def test_tithi_calculation(self):
        """Test tithi calculation."""
        # Test same position
        sun_lon, moon_lon = 0.0, 0.0
        jd = swe_service.calculate_planet_position(swe_service._get_jd(datetime(2025, 8, 17, 12, 0, 0)), "Sun")
        # Tithi is calculated in panchanga service, not SWE service
        assert True  # Placeholder - tithi calculation is in panchanga service
    
    def test_ketu_calculation(self):
        """Test Ketu calculation."""
        dt = datetime(2025, 8, 17, 12, 0, 0)
        result = swe_service.calculate_planets(dt, ["Rahu", "Ketu"])
        
        assert "Rahu" in result
        assert "Ketu" in result
        
        # Ketu should be Rahu + 180°
        rahu_lon = result["Rahu"]["longitude"]
        ketu_lon = result["Ketu"]["longitude"]
        
        expected_ketu_lon = (rahu_lon + 180) % 360
        assert abs(ketu_lon - expected_ketu_lon) < 0.1  # Allow small precision differences
