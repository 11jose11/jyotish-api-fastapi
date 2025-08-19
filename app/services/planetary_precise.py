import ephem
from datetime import datetime
from .astronomical import LahiriAyanamsa

class PlanetaryPreciseService:
    """Servicio para cálculos planetarios precisos usando ephem"""
    
    @staticmethod
    def get_planetary_positions(date: str, time: str, lat: float, lng: float) -> dict:
        """Obtener posiciones planetarias precisas al amanecer"""
        
        # Configurar observador
        observer = ephem.Observer()
        observer.lat = str(lat)
        observer.lon = str(lng)
        observer.date = f"{date} {time}"
        
        # Calcular posiciones
        sun = ephem.Sun()
        moon = ephem.Moon()
        
        sun.compute(observer)
        moon.compute(observer)
        
        # Obtener longitudes tropicales
        sun_longitude_tropical = float(sun.hlong) * 180 / ephem.pi
        moon_longitude_tropical = float(moon.hlong) * 180 / ephem.pi
        
        # Convertir a longitudes siderales usando Lahiri Ayanamsa
        date_obj = datetime.fromisoformat(f"{date}T{time}")
        sun_longitude_sidereal = LahiriAyanamsa.to_sidereal(sun_longitude_tropical, date_obj)
        moon_longitude_sidereal = LahiriAyanamsa.to_sidereal(moon_longitude_tropical, date_obj)
        
        return {
            'sun': {
                'tropical': sun_longitude_tropical,
                'sidereal': sun_longitude_sidereal
            },
            'moon': {
                'tropical': moon_longitude_tropical,
                'sidereal': moon_longitude_sidereal
            }
        }
