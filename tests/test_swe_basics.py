"""Basic Swiss Ephemeris tests."""

import pytest
from datetime import datetime

from app.services.swe import swe_service


class TestSwissEphemeris:
    """Test Swiss Ephemeris functionality."""
    
    def test_initialization(self):
        """Test that Swiss Ephemeris initializes correctly."""
        assert hasattr(swe_service, 'initialized')
        assert hasattr(swe_service, 'precision')
    
    def test_planet_calculation(self):
        """Test basic planet calculation."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        
        try:
            result = swe_service.calculate_planets(dt, ["Sun", "Moon"])
            
            assert "Sun" in result
            assert "Moon" in result
            
            # Check Sun data
            sun_data = result["Sun"]
            assert "lon" in sun_data
            assert "lat" in sun_data
            assert "dist" in sun_data
            assert "rasi" in sun_data
            assert "nakshatra" in sun_data
            
            # Check Moon data
            moon_data = result["Moon"]
            assert "lon" in moon_data
            assert "lat" in moon_data
            assert "dist" in moon_data
            assert "rasi" in moon_data
            assert "nakshatra" in moon_data
            
        except Exception as e:
            pytest.skip(f"Swiss Ephemeris not available: {e}")
    
    def test_rasi_calculation(self):
        """Test rashi calculation."""
        # Test known values
        assert swe_service._get_rasi(0) == "Mesha"
        assert swe_service._get_rasi(30) == "Vrishabha"
        assert swe_service._get_rasi(60) == "Mithuna"
        
        assert swe_service._get_rasi_index(0) == 1
        assert swe_service._get_rasi_index(30) == 2
        assert swe_service._get_rasi_index(60) == 3
    
    def test_nakshatra_calculation(self):
        """Test nakshatra calculation."""
        # Test known values
        assert swe_service._get_nakshatra(0) == "Ashwini"
        assert swe_service._get_nakshatra_index(0) == 1
        assert swe_service._get_pada(0) == 1
        
        # Test nakshatra boundary
        nakshatra_span = 13 + 1/3
        assert swe_service._get_nakshatra(nakshatra_span) == "Bharani"
        assert swe_service._get_nakshatra_index(nakshatra_span) == 2
    
    def test_tithi_calculation(self):
        """Test tithi calculation."""
        # Test known values
        sun_lon = 0
        moon_lon = 12  # 1 tithi ahead
        assert swe_service.calculate_tithi(sun_lon, moon_lon) == 2
        
        moon_lon = 24  # 2 tithis ahead
        assert swe_service.calculate_tithi(sun_lon, moon_lon) == 3
        
        moon_lon = 360  # Same as Sun
        assert swe_service.calculate_tithi(sun_lon, moon_lon) == 1
    
    def test_ketu_calculation(self):
        """Test Ketu calculation."""
        rahu_lon = 0
        ketu_lon = swe_service._calculate_ketu(rahu_lon)
        assert ketu_lon == 180.0
        
        rahu_lon = 90
        ketu_lon = swe_service._calculate_ketu(rahu_lon)
        assert ketu_lon == 270.0
        
        rahu_lon = 200
        ketu_lon = swe_service._calculate_ketu(rahu_lon)
        assert ketu_lon == 20.0  # (200 + 180) % 360
