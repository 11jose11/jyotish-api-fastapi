#!/usr/bin/env python3
"""
Calculate correct longitude for offset 4.
"""

nakshatra_span = 13 + 1/3

# For offset 4, we need moon_nak = sun_nak + 4
# sun_nak = 0 (Ashwini)
# moon_nak = 4 (Pushya)

moon_lon = 4 * nakshatra_span + (nakshatra_span / 2)  # Center in nakshatra

print(f"Nakshatra span: {nakshatra_span}")
print(f"Moon longitude for offset 4: {moon_lon}")

# Verify
sun_nak = int(0 // nakshatra_span)
moon_nak = int(moon_lon // nakshatra_span)
offset = (moon_nak - sun_nak) % 27

print(f"Sun nakshatra index: {sun_nak}")
print(f"Moon nakshatra index: {moon_nak}")
print(f"Calculated offset: {offset}")
