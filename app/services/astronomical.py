import ephem
from datetime import datetime

class LahiriAyanamsa:
    """Configuración para Lahiri Ayanamsa (23°51' en 2000)"""
    
    @staticmethod
    def get_ayanamsa(date: datetime) -> float:
        """Calcular Ayanamsa de Lahiri para una fecha específica"""
        # Lahiri Ayanamsa: 23°51' en 2000, incremento anual de 50.3"
        base_date = datetime(2000, 1, 1)
        years_diff = (date - base_date).days / 365.25
        ayanamsa = 23.85 + (years_diff * 50.3 / 3600)  # Convertir segundos a grados
        return ayanamsa
    
    @staticmethod
    def to_sidereal(longitude: float, date: datetime) -> float:
        """Convertir longitud tropical a sideral usando Lahiri Ayanamsa"""
        ayanamsa = LahiriAyanamsa.get_ayanamsa(date)
        sidereal_longitude = longitude + ayanamsa
        return sidereal_longitude % 360
