#!/usr/bin/env python3

# Script para corregir el cálculo de tithi en yogas.py

with open('app/services/yogas.py', 'r') as f:
    content = f.read()

# Reemplazar la función _calculate_tithi
old_function = '''    def _calculate_tithi(self, sun_lon: float, moon_lon: float) -> int:
        """Calculate tithi from Sun and Moon longitudes using the same method as panchanga service."""

        diff = (moon_lon - sun_lon) % 360
        tithi_number = int(diff // 12) + 1
        
        # Determine paksha based on difference (same logic as panchanga service)
        if diff < 180:
            # Shukla paksha - no adjustment needed
            pass
        else:
            # Krishna paksha - adjust tithi number
            if tithi_number > 15:
                tithi_number = tithi_number - 15
        
        # Ensure tithi_number is in correct range
        if tithi_number < 1:
            tithi_number = 1
        elif tithi_number > 15:
            tithi_number = 15
            
        return tithi_number'''

new_function = '''    def _calculate_tithi(self, sun_lon: float, moon_lon: float) -> int:
        """Calculate tithi from Sun and Moon longitudes using the same method as panchanga service."""

        diff = (moon_lon - sun_lon) % 360
        
        # Calcular tithi_number correctamente
        tithi_number = int(diff // 12) + 1
        
        # Determinar paksha basado en diferencia
        if diff < 180:
            # Shukla paksha - no adjustment needed
            pass
        else:
            # Krishna paksha - adjust tithi number
            tithi_number = tithi_number - 15
            if tithi_number <= 0:
                tithi_number += 15
        
        # Ensure tithi_number is in correct range
        if tithi_number < 1:
            tithi_number = 1
        elif tithi_number > 15:
            tithi_number = 15
            
        return tithi_number'''

content = content.replace(old_function, new_function)

with open('app/services/yogas.py', 'w') as f:
    f.write(content)

print("Función _calculate_tithi en yogas.py corregida exitosamente")
