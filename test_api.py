#!/usr/bin/env python3
"""Test script for the API."""

import requests
import json

def test_ephemeris():
    """Test the ephemeris endpoint."""
    url = "http://localhost:8080/v1/ephemeris/"
    params = {
        "when_utc": "2025-08-01T12:00:00Z",
        "place_id": "ChIJgTwKgJcpQg0RaSKMYcHeNsQ",
        "planets": "Sun"
    }
    
    print(f"Testing: {url}")
    print(f"Params: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Raw Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"JSON Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_ephemeris()
