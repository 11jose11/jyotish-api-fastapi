#!/usr/bin/env python3
"""
Direct test script to verify True Citra Paksha Ayanamsa precision
Uses internal services without HTTP
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.swe import swe_service
from app.services.panchanga_precise import panchanga_service
from datetime import datetime
import pyswisseph as swe

def test_ayanamsa_direct():
    """Test ayanamsa precision directly using internal services"""
    
    print("🔍 TESTING AYANAMSA PRECISION (DIRECT)")
    print("=" * 60)
    
    # Test case 1: Known birth data for comparison
    test_date = "1988-01-11"
    test_time = "22:53:00"
    latitude = -12.0464  # Lima, Peru
    longitude = -77.0428
    
    print(f"📅 Test Date: {test_date} {test_time}")
    print(f"📍 Location: Lima, Peru ({latitude}, {longitude})")
    print()
    
    # Test 1: Direct SWE calculation
    print("1️⃣ Testing Direct SWE Calculation...")
    try:
        # Calculate Julian Day
        dt = datetime.strptime(f"{test_date} {test_time}", "%Y-%m-%d %H:%M:%S")
        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0 + dt.second/3600.0)
        
        print(f"📊 Julian Day: {jd:.6f}")
        
        # Get ayanamsa
        ayanamsa = swe.get_ayanamsa_ut(jd)
        print(f"🌌 Ayanamsa (SWE): {ayanamsa:.6f}°")
        
        # Test planetary positions
        planets_to_test = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
        
        print("\n📊 PLANETARY POSITIONS (Direct SWE):")
        print("-" * 50)
        
        for planet in planets_to_test:
            try:
                # Get planet number
                planet_num = swe_service._get_planet_number(planet)
                if planet_num is not None:
                    # Calculate position
                    result = swe.calc_ut(jd, planet_num)
                    if result[0] == 0:  # Success
                        longitude = result[1][0]
                        print(f"{planet:8}: {longitude:8.4f}°")
                    else:
                        print(f"{planet:8}: Error {result[0]}")
                else:
                    print(f"{planet:8}: Not found")
            except Exception as e:
                print(f"{planet:8}: Error - {e}")
        
        print()
        
    except Exception as e:
        print(f"❌ Direct SWE error: {e}")
    
    print("=" * 60)
    
    # Test 2: Using our service
    print("2️⃣ Testing Our Service Calculation...")
    try:
        # Use our ephemeris service
        result = swe_service.calculate_planets(
            date=test_date,
            time=test_time,
            latitude=latitude,
            longitude=longitude,
            timezone="America/Lima"
        )
        
        if result:
            print("✅ Our service calculation successful")
            
            # Show ayanamsa
            ayanamsa = result.get('ayanamsa', 0)
            print(f"🌌 Our Ayanamsa: {ayanamsa:.6f}°")
            
            # Show planetary positions
            planets = result.get('planets', {})
            print("\n📊 PLANETARY POSITIONS (Our Service):")
            print("-" * 50)
            
            for planet, info in planets.items():
                if isinstance(info, dict):
                    longitude = info.get('longitude', 0)
                    nakshatra = info.get('nakshatra', '')
                    pada = info.get('pada', 0)
                    print(f"{planet:8}: {longitude:8.4f}° | {nakshatra:12} (Pada {pada})")
            
        else:
            print("❌ Our service returned None")
            
    except Exception as e:
        print(f"❌ Our service error: {e}")
    
    print("=" * 60)
    
    # Test 3: Current date
    print("3️⃣ Testing Current Date...")
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")
    
    print(f"📅 Current Date: {current_date} {current_time}")
    print(f"📍 Location: Marseille, France")
    
    try:
        # Current ayanamsa
        current_jd = swe.julday(
            datetime.now().year,
            datetime.now().month,
            datetime.now().day,
            datetime.now().hour + datetime.now().minute/60.0 + datetime.now().second/3600.0
        )
        current_ayanamsa = swe.get_ayanamsa_ut(current_jd)
        print(f"🌌 Current Ayanamsa: {current_ayanamsa:.6f}°")
        
        # Expected ayanamsa for 2024-2025 (Lahiri)
        expected_ayanamsa_2024 = 23.85  # Approximate for 2024
        expected_ayanamsa_2025 = 23.86  # Approximate for 2025
        
        print(f"📊 Expected Ayanamsa 2024: {expected_ayanamsa_2024:.2f}°")
        print(f"📊 Expected Ayanamsa 2025: {expected_ayanamsa_2025:.2f}°")
        
        # Check precision
        diff_2024 = abs(current_ayanamsa - expected_ayanamsa_2024)
        diff_2025 = abs(current_ayanamsa - expected_ayanamsa_2025)
        
        print(f"📊 Difference from 2024: {diff_2024:.4f}°")
        print(f"📊 Difference from 2025: {diff_2025:.4f}°")
        
        if diff_2025 < 0.1:
            print("✅ Ayanamsa precision is EXCELLENT")
        elif diff_2025 < 0.5:
            print("✅ Ayanamsa precision is GOOD")
        else:
            print("⚠️  Ayanamsa precision needs attention")
        
    except Exception as e:
        print(f"❌ Current date error: {e}")
    
    print("=" * 60)
    
    # Test 4: Panchanga calculation
    print("4️⃣ Testing Panchanga Calculation...")
    try:
        panchanga_result = panchanga_service.get_precise_panchanga(
            date=test_date,
            time=test_time,
            latitude=latitude,
            longitude=longitude,
            timezone="America/Lima"
        )
        
        if panchanga_result:
            print("✅ Panchanga calculation successful")
            
            panchanga = panchanga_result.get('panchanga', {})
            print("\n📅 PANCHANGA ELEMENTS:")
            print("-" * 40)
            
            for element, value in panchanga.items():
                if isinstance(value, dict):
                    print(f"{element:12}: {value.get('name', 'N/A')} ({value.get('value', 'N/A')})")
                else:
                    print(f"{element:12}: {value}")
            
            # Check sunrise/sunset
            sunrise = panchanga_result.get('sunrise', '')
            sunset = panchanga_result.get('sunset', '')
            print(f"\n🌅 Sunrise: {sunrise}")
            print(f"🌇 Sunset: {sunset}")
            
        else:
            print("❌ Panchanga returned None")
            
    except Exception as e:
        print(f"❌ Panchanga error: {e}")
    
    print("=" * 60)
    print("🎯 COMPARISON WITH DEVA.GURU")
    print("=" * 60)
    print("📋 Please compare these values with deva.guru:")
    print("   - Planetary longitudes")
    print("   - Nakshatra positions")
    print("   - Ayanamsa value")
    print("   - Panchanga elements")
    print()
    print("🔍 Expected Ayanamsa (Lahiri/True Citra Paksha): ~23.85° (2024)")
    print("📊 Tolerance: ±0.1° for planetary positions")
    print("🌌 Tolerance: ±0.01° for ayanamsa")
    print()
    print("✅ If ayanamsa is within ±0.1° of expected, your API is using")
    print("   True Citra Paksha (Lahiri) correctly!")

if __name__ == "__main__":
    test_ayanamsa_direct()
