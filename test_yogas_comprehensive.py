#!/usr/bin/env python3
"""
Comprehensive test script for Panchanga Yogas detection.
This script tests all yoga types and verifies they are detected correctly.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.yogas import yogas_service


def test_all_yogas():
    """Test all yoga types comprehensively."""
    print("🧘 Testing Panchanga Yogas Detection")
    print("=" * 50)
    
    # Test data: specific dates and conditions for each yoga
    test_cases = [
        # Positive Yogas
        {
            "name": "Amrita Siddhi",
            "date": "2024-01-07",  # Sunday
            "nakshatra": "Ashwini",
            "expected": True
        },
        {
            "name": "Sarvartha Siddhi", 
            "date": "2024-01-01",  # Monday
            "nakshatra": "Rohini",
            "tithi": 1,  # Force tithi to avoid calculation issues
            "expected": True
        },
        {
            "name": "Siddha",
            "date": "2024-01-02",  # Tuesday
            "nakshatra": "Krittika", 
            "expected": True
        },
        {
            "name": "Guru Pushya",
            "date": "2024-01-04",  # Thursday
            "nakshatra": "Pushya",
            "expected": True
        },
        {
            "name": "Ravi Pushya",
            "date": "2024-01-04",  # Any day
            "nakshatra": "Pushya",
            "sun_nakshatra": "Pushya",  # Sun must be in Pushya
            "expected": True
        },
        {
            "name": "Dvipushkara",
            "date": "2024-01-04",  # Thursday
            "nakshatra": "Ashwini",
            "tithi": 2,
            "expected": True
        },
        {
            "name": "Tripushkara",
            "date": "2024-01-04",  # Thursday
            "nakshatra": "Pushya",
            "tithi": 2,
            "expected": True
        },
        
        # Negative Yogas
        {
            "name": "Dagdha",
            "date": "2024-01-07",  # Sunday
            "nakshatra": "Ashwini",
            "tithi": 1,
            "expected": True
        },
        {
            "name": "Visha",
            "date": "2024-01-01",  # Monday
            "nakshatra": "Bharani",
            "tithi": 2,
            "expected": True
        },
        {
            "name": "Hutasana",
            "date": "2024-01-02",  # Tuesday
            "nakshatra": "Krittika",
            "tithi": 3,
            "expected": True
        },
        {
            "name": "Krakacha",
            "date": "2024-01-03",  # Wednesday
            "nakshatra": "Rohini",
            "tithi": 4,
            "expected": True
        },
        {
            "name": "Samvartaka",
            "date": "2024-01-04",  # Thursday
            "nakshatra": "Mrigashira",
            "tithi": 5,
            "expected": True
        },
        {
            "name": "Asubha",
            "date": "2024-01-04",  # Any day
            "nakshatra": "Ashlesha",
            "tithi": 1,
            "expected": True
        },
        {
            "name": "Vinasa",
            "date": "2024-01-07",  # Sunday
            "nakshatra": "Ashlesha",
            "expected": True
        },
        {
            "name": "Panchaka",
            "date": "2024-01-02",  # Tuesday
            "nakshatra": "Dhanishtha",
            "expected": True
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🔍 Testing {test_case['name']}...")
        
        try:
            # Create test date
            test_date = datetime.fromisoformat(test_case['date'])
            
            # Calculate planetary positions (simplified for testing)
            sun_lon = 0.0  # Ashwini
            moon_lon = 0.0  # Will be adjusted based on nakshatra
            
            # Adjust moon longitude based on nakshatra
            nakshatras = [
                "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
                "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
                "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
                "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
                "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
            ]
            
            nakshatra_index = nakshatras.index(test_case['nakshatra'])
            nakshatra_span = 13 + 1/3
            moon_lon = nakshatra_index * nakshatra_span + (nakshatra_span / 2)  # Center in nakshatra
            
            # Adjust sun longitude if specified
            if 'sun_nakshatra' in test_case:
                sun_nakshatra_index = nakshatras.index(test_case['sun_nakshatra'])
                sun_lon = sun_nakshatra_index * nakshatra_span + (nakshatra_span / 2)  # Center in nakshatra
            
            # Calculate panchanga elements
            if 'tithi' in test_case:
                # Override tithi for specific test cases
                tithi = test_case['tithi']
            else:
                tithi = yogas_service._calculate_tithi(sun_lon, moon_lon)
            
            nakshatra = yogas_service._get_nakshatra(moon_lon)
            sun_nakshatra = yogas_service._get_nakshatra(sun_lon)
            weekday = yogas_service.get_weekday(test_date)
            
            # Check positive yogas
            positive_yogas = yogas_service._check_positive_yogas(
                weekday, tithi, nakshatra, sun_lon, moon_lon, sun_nakshatra
            )
            
            # Check negative yogas
            negative_yogas = yogas_service._check_negative_yogas(
                weekday, tithi, nakshatra, sun_nakshatra
            )
            
            # Combine results
            all_yogas = positive_yogas + negative_yogas
            
            # Check if yoga was detected
            yoga_found = any(yoga["name"] == test_case["name"] for yoga in all_yogas)
            
            if yoga_found == test_case["expected"]:
                status = "✅ PASS"
                results.append(True)
            else:
                status = "❌ FAIL"
                results.append(False)
            
            print(f"   {status} {test_case['name']}")
            print(f"   Date: {test_date.strftime('%Y-%m-%d')} ({weekday})")
            print(f"   Tithi: {tithi}, Nakshatra: {nakshatra}, Sun Nakshatra: {sun_nakshatra}")
            print(f"   Expected: {test_case['expected']}, Found: {yoga_found}")
            
            if yoga_found:
                yoga_data = next((yoga for yoga in all_yogas if yoga["name"] == test_case["name"]), None)
                if yoga_data and "classification" in yoga_data:
                    print(f"   Classification: {yoga_data['classification']}")
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All yoga tests passed!")
        return True
    else:
        print("⚠️  Some yoga tests failed. Please review the implementation.")
        return False


def test_yoga_rules_loading():
    """Test that yoga rules are loaded correctly."""
    print("\n📋 Testing Yoga Rules Loading")
    print("-" * 30)
    
    try:
        rules = yogas_service.rules
        
        # Check structure
        assert "positive" in rules
        assert "negative" in rules
        assert "metadata" in rules
        
        # Count yogas
        positive_count = len(rules["positive"])
        negative_count = len(rules["negative"])
        
        print(f"✅ Rules loaded successfully")
        print(f"   Positive yogas: {positive_count}")
        print(f"   Negative yogas: {negative_count}")
        
        # List all yogas
        print("\n📝 Positive Yogas:")
        for yoga_name in rules["positive"].keys():
            print(f"   • {yoga_name}")
        
        print("\n📝 Negative Yogas:")
        for yoga_name in rules["negative"].keys():
            print(f"   • {yoga_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading rules: {e}")
        return False


if __name__ == "__main__":
    print("🧘 Panchanga Yogas Comprehensive Test")
    print("=" * 60)
    
    # Test rules loading
    rules_ok = test_yoga_rules_loading()
    
    # Test all yogas
    yogas_ok = test_all_yogas()
    
    # Final result
    print("\n" + "=" * 60)
    if rules_ok and yogas_ok:
        print("🎉 ALL TESTS PASSED - Yoga detection is working correctly!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED - Please review the implementation.")
        sys.exit(1)
