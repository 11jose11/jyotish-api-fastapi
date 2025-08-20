#!/usr/bin/env python3
"""
Test script to verify True Citra Paksha Ayanamsa precision
Compare with deva.guru calculations
"""

import requests
import json
from datetime import datetime
import time

# API base URL
API_BASE = "http://localhost:8080"

def test_ayanamsa_precision():
    """Test ayanamsa precision with known birth data"""
    
    print("🔍 TESTING AYANAMSA PRECISION")
    print("=" * 50)
    
    # Test case 1: Known birth data for comparison
    test_data = {
        "date": "1988-01-11",
        "time": "22:53:00",
        "latitude": -12.0464,  # Lima, Peru
        "longitude": -77.0428,
        "timezone": "America/Lima"
    }
    
    print(f"📅 Test Date: {test_data['date']} {test_data['time']}")
    print(f"📍 Location: Lima, Peru ({test_data['latitude']}, {test_data['longitude']})")
    print()
    
    # Test 1: Ephemeris calculation
    print("1️⃣ Testing Ephemeris Calculation...")
    try:
        response = requests.post(
            f"{API_BASE}/v1/ephemeris/",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Ephemeris calculation successful")
            
            # Extract key planetary positions
            planets = data.get('planets', {})
            
            print("\n📊 PLANETARY POSITIONS:")
            print("-" * 40)
            
            for planet, info in planets.items():
                if isinstance(info, dict):
                    longitude = info.get('longitude', 0)
                    nakshatra = info.get('nakshatra', '')
                    pada = info.get('pada', 0)
                    print(f"{planet:8}: {longitude:8.4f}° | {nakshatra:12} (Pada {pada})")
            
            # Check ayanamsa value
            ayanamsa = data.get('ayanamsa', 0)
            print(f"\n🌌 Ayanamsa: {ayanamsa:.4f}°")
            
        else:
            print(f"❌ Ephemeris failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Ephemeris error: {e}")
    
    print("\n" + "=" * 50)
    
    # Test 2: Panchanga calculation
    print("2️⃣ Testing Panchanga Calculation...")
    try:
        response = requests.post(
            f"{API_BASE}/v1/panchanga-precise/daily",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Panchanga calculation successful")
            
            print("\n📅 PANCHANGA ELEMENTS:")
            print("-" * 40)
            
            panchanga = data.get('panchanga', {})
            for element, value in panchanga.items():
                if isinstance(value, dict):
                    print(f"{element:12}: {value.get('name', 'N/A')} ({value.get('value', 'N/A')})")
                else:
                    print(f"{element:12}: {value}")
            
            # Check sunrise/sunset
            sunrise = data.get('sunrise', '')
            sunset = data.get('sunset', '')
            print(f"\n🌅 Sunrise: {sunrise}")
            print(f"🌇 Sunset: {sunset}")
            
        else:
            print(f"❌ Panchanga failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Panchanga error: {e}")
    
    print("\n" + "=" * 50)
    
    # Test 3: Current date test (for comparison with deva.guru)
    print("3️⃣ Testing Current Date...")
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")
    
    current_test = {
        "date": current_date,
        "time": current_time,
        "latitude": 43.2965,  # Marseille, France
        "longitude": 5.3698,
        "timezone": "Europe/Paris"
    }
    
    print(f"📅 Current Date: {current_date} {current_time}")
    print(f"📍 Location: Marseille, France")
    
    try:
        response = requests.post(
            f"{API_BASE}/v1/ephemeris/",
            json=current_test,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Current date calculation successful")
            
            # Show key planets
            planets = data.get('planets', {})
            print("\n📊 CURRENT PLANETARY POSITIONS:")
            print("-" * 40)
            
            key_planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
            for planet in key_planets:
                if planet in planets:
                    info = planets[planet]
                    if isinstance(info, dict):
                        longitude = info.get('longitude', 0)
                        nakshatra = info.get('nakshatra', '')
                        print(f"{planet:8}: {longitude:8.4f}° | {nakshatra}")
            
            ayanamsa = data.get('ayanamsa', 0)
            print(f"\n🌌 Current Ayanamsa: {ayanamsa:.4f}°")
            
        else:
            print(f"❌ Current date failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Current date error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 COMPARISON WITH DEVA.GURU")
    print("=" * 50)
    print("📋 Please compare these values with deva.guru:")
    print("   - Planetary longitudes")
    print("   - Nakshatra positions")
    print("   - Ayanamsa value")
    print("   - Panchanga elements")
    print()
    print("🔍 Expected Ayanamsa (Lahiri/True Citra Paksha): ~23.85° (2024)")
    print("📊 Tolerance: ±0.1° for planetary positions")
    print("🌌 Tolerance: ±0.01° for ayanamsa")

if __name__ == "__main__":
    test_ayanamsa_precision()
