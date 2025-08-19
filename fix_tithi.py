#!/usr/bin/env python3

# Script para corregir el cálculo de tithi en panchanga.py

with open('app/services/panchanga.py', 'r') as f:
    content = f.read()

# Reemplazar la función calculate_tithi
old_function = '''    def calculate_tithi(self, sun_lon: float, moon_lon: float) -> dict:
        """Calculate tithi with paksha information."""
        diff = (moon_lon - sun_lon) % 360
        tithi_number = int(diff // 12) + 1
        
        # Determine paksha based on difference
        if diff < 180:
            paksha = "Shukla"  # Waxing moon (0° to 180°)
            paksha_short = "S"
        else:
            paksha = "Krishna"  # Waning moon (180° to 360°)
            paksha_short = "K"
            # For Krishna paksha, adjust tithi number
            if tithi_number > 15:
                tithi_number = tithi_number - 15'''

new_function = '''    def calculate_tithi(self, sun_lon: float, moon_lon: float) -> dict:
        """Calculate tithi with paksha information."""
        diff = (moon_lon - sun_lon) % 360
        
        # Calcular tithi_number correctamente
        tithi_number = int(diff // 12) + 1
        
        # Determinar paksha basado en diferencia
        if diff < 180:
            paksha = "Shukla"  # Luna creciente (0° a 180°)
            paksha_short = "S"
            # Para Shukla Paksha, tithi_number ya está correcto (1-15)
        else:
            paksha = "Krishna"  # Luna menguante (180° a 360°)
            paksha_short = "K"
            # Para Krishna Paksha, ajustar tithi_number (1-15)
            tithi_number = tithi_number - 15
            if tithi_number <= 0:
                tithi_number += 15'''

content = content.replace(old_function, new_function)

with open('app/services/panchanga.py', 'w') as f:
    f.write(content)

print("Función calculate_tithi corregida exitosamente")
