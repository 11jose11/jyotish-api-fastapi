#!/usr/bin/env python3
"""
Debug script for Ravi Yoga calculation.
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.yogas import yogas_service

def debug_ravi_yoga():
    """Debug Ravi Yoga calculation."""
    print("🔍 Debugging Ravi Yoga Calculation")
    print("=" * 40)
    
    # Test case from the failing test
    sun_lon = 0.0  # Ashwini
    moon_lon = 71.11  # Pushya
    
    print(f"Sun longitude: {sun_lon}")
    print(f"Moon longitude: {moon_lon}")
    
    # Calculate nakshatra indices
    sun_nak = yogas_service._get_nakshatra_index(sun_lon)
    moon_nak = yogas_service._get_nakshatra_index(moon_lon)
    
    print(f"Sun nakshatra index: {sun_nak}")
    print(f"Moon nakshatra index: {moon_nak}")
    
    # Calculate offset
    offset = (moon_nak - sun_nak) % 27
    print(f"Calculated offset: {offset}")
    
    # Check what offsets are expected
    expected_offsets = [4, 6, 9, 10, 13, 20]
    print(f"Expected offsets: {expected_offsets}")
    print(f"Offset {offset} in expected offsets: {offset in expected_offsets}")
    
    # Test the actual yoga detection
    result = yogas_service._check_positive_yogas(
        weekday="Thursday",
        tithi=15,
        nakshatra="Pushya",
        sun_lon=sun_lon,
        moon_lon=moon_lon,
        sun_nakshatra="Ashwini"
    )
    
    print(f"\nYogas found: {len(result)}")
    for yoga in result:
        print(f"  - {yoga['name']}")
    
    # Test the criteria matching directly
    yoga_rule = {
        "type": "sun+moon",
        "criteria": {"offset": [4, 6, 9, 10, 13, 20]}
    }
    
    matches = yogas_service._matches_yoga_criteria(
        yoga_rule, "Thursday", 15, "Rohini", sun_lon, moon_lon
    )
    
    print(f"\nDirect criteria match: {matches}")

if __name__ == "__main__":
    debug_ravi_yoga()
