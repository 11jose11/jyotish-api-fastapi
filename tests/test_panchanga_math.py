"""Panchanga mathematics tests."""

import pytest
from app.services.panchanga import panchanga_service


class TestPanchangaMath:
    """Test panchanga mathematical calculations."""
    
    def test_dms_conversion(self):
        """Test decimal to DMS conversion."""
        # Test exact degrees
        assert panchanga_service.to_dms(0.0) == "0°00'00.0\""
        assert panchanga_service.to_dms(90.0) == "90°00'00.0\""
        assert panchanga_service.to_dms(180.0) == "180°00'00.0\""
        assert panchanga_service.to_dms(270.0) == "270°00'00.0\""
        
        # Test with minutes
        assert panchanga_service.to_dms(30.5) == "30°30'00.0\""
        assert panchanga_service.to_dms(45.25) == "45°15'00.0\""
        
        # Test with seconds
        assert panchanga_service.to_dms(30.5 + 1/3600) == "30°30'01.0\""
        assert panchanga_service.to_dms(45.25 + 30/3600) == "45°15'30.0\""
    
    def test_rasi_calculation(self):
        """Test rashi calculation."""
        # Test boundary values
        assert panchanga_service.get_rasi(0.0) == ("Mesha", 1)
        assert panchanga_service.get_rasi(29.999) == ("Mesha", 1)
        assert panchanga_service.get_rasi(30.0) == ("Vrishabha", 2)
        assert panchanga_service.get_rasi(59.999) == ("Vrishabha", 2)
        assert panchanga_service.get_rasi(60.0) == ("Mithuna", 3)
        
        # Test last rashi
        assert panchanga_service.get_rasi(330.0) == ("Meena", 12)
        assert panchanga_service.get_rasi(359.999) == ("Meena", 12)
    
    def test_nakshatra_calculation(self):
        """Test nakshatra calculation."""
        nakshatra_span = 13 + 1/3  # 13°20'
        
        # Test first nakshatra
        assert panchanga_service.get_nakshatra(0.0) == ("Ashwini", 1, 1)
        assert panchanga_service.get_nakshatra(nakshatra_span - 0.001) == ("Ashwini", 1, 4)
        
        # Test second nakshatra
        assert panchanga_service.get_nakshatra(nakshatra_span) == ("Bharani", 2, 1)
        assert panchanga_service.get_nakshatra(nakshatra_span * 2 - 0.001) == ("Bharani", 2, 4)
        
        # Test pada calculation
        pada_span = nakshatra_span / 4  # 3°20'
        assert panchanga_service.get_nakshatra(pada_span) == ("Ashwini", 1, 2)
        assert panchanga_service.get_nakshatra(pada_span * 2) == ("Ashwini", 1, 3)
        assert panchanga_service.get_nakshatra(pada_span * 3) == ("Ashwini", 1, 4)
    
    def test_tithi_calculation(self):
        """Test tithi calculation."""
        # Test same position
        assert panchanga_service.calculate_tithi(0.0, 0.0) == 1
        
        # Test one tithi ahead (12 degrees)
        assert panchanga_service.calculate_tithi(0.0, 12.0) == 2
        assert panchanga_service.calculate_tithi(0.0, 11.999) == 1
        
        # Test two tithis ahead (24 degrees)
        assert panchanga_service.calculate_tithi(0.0, 24.0) == 3
        assert panchanga_service.calculate_tithi(0.0, 23.999) == 2
        
        # Test full cycle
        assert panchanga_service.calculate_tithi(0.0, 360.0) == 1
        assert panchanga_service.calculate_tithi(0.0, 359.999) == 30
        
        # Test with different Sun positions
        assert panchanga_service.calculate_tithi(90.0, 102.0) == 2  # 12 degrees ahead
        assert panchanga_service.calculate_tithi(180.0, 192.0) == 2  # 12 degrees ahead
