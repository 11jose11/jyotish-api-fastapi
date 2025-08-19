import requests
import googlemaps
from datetime import datetime
import pytz
from typing import Optional

class SunriseService:
    """Servicio para calcular hora exacta del amanecer"""
    
    def __init__(self, google_api_key: Optional[str] = None):
        self.google_api_key = google_api_key
        if google_api_key:
            self.gmaps = googlemaps.Client(key=google_api_key)
        else:
            self.gmaps = None
    
    def get_sunrise_time(self, date: str, lat: float, lng: float) -> str:
        """Obtener hora exacta del amanecer usando APIs"""
        try:
            # Usar Sunrise-Sunset.org API
            url = "https://api.sunrise-sunset.org/json"
            params = {
                'lat': lat,
                'lng': lng,
                'date': date,
                'formatted': 0
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            sunrise_utc = datetime.fromisoformat(data['results']['sunrise'].replace('Z', '+00:00'))
            
            # Si tenemos Google API Key, usar para timezone preciso
            if self.gmaps:
                try:
                    timezone_result = self.gmaps.timezone((lat, lng), date)
                    timezone_id = timezone_result['timeZoneId']
                    local_tz = pytz.timezone(timezone_id)
                    sunrise_local = sunrise_utc.astimezone(local_tz)
                except Exception as e:
                    # Fallback a timezone aproximado basado en longitud
                    timezone_offset = self._get_timezone_offset(lng)
                    sunrise_local = sunrise_utc.replace(tzinfo=pytz.UTC).astimezone(
                        pytz.FixedOffset(timezone_offset)
                    )
            else:
                # Usar timezone aproximado basado en longitud
                timezone_offset = self._get_timezone_offset(lng)
                sunrise_local = sunrise_utc.replace(tzinfo=pytz.UTC).astimezone(
                    pytz.FixedOffset(timezone_offset)
                )
            
            return sunrise_local.strftime('%H:%M:%S')
            
        except Exception as e:
            raise Exception(f"Error calculating sunrise: {str(e)}")
    
    def _get_timezone_offset(self, lng: float) -> int:
        """Obtener offset de timezone aproximado basado en longitud"""
        # Mapeo simplificado de coordenadas a timezone offset (en minutos)
        if lng >= -7.5 and lng < 7.5:
            return 0  # UTC
        elif lng >= 7.5 and lng < 22.5:
            return 60  # UTC+1 (Europa Central)
        elif lng >= 22.5 and lng < 37.5:
            return 120  # UTC+2
        elif lng >= 37.5 and lng < 52.5:
            return 180  # UTC+3
        elif lng >= 52.5 and lng < 67.5:
            return 240  # UTC+4
        elif lng >= 67.5 and lng < 82.5:
            return 300  # UTC+5
        elif lng >= 82.5 and lng < 97.5:
            return 330  # UTC+5:30 (India)
        elif lng >= 97.5 and lng < 112.5:
            return 360  # UTC+6
        elif lng >= 112.5 and lng < 127.5:
            return 420  # UTC+7
        elif lng >= 127.5 and lng < 142.5:
            return 480  # UTC+8
        elif lng >= 142.5 and lng < 157.5:
            return 540  # UTC+9
        elif lng >= 157.5 and lng < 172.5:
            return 600  # UTC+10
        elif lng >= 172.5 and lng < 187.5:
            return 660  # UTC+11
        elif lng >= 187.5 and lng < 202.5:
            return 720  # UTC+12
        
        # Para longitudes negativas (oeste)
        elif lng >= -22.5 and lng < -7.5:
            return -60  # UTC-1
        elif lng >= -37.5 and lng < -22.5:
            return -120  # UTC-2
        elif lng >= -52.5 and lng < -37.5:
            return -180  # UTC-3
        elif lng >= -67.5 and lng < -52.5:
            return -240  # UTC-4
        elif lng >= -82.5 and lng < -67.5:
            return -300  # UTC-5
        elif lng >= -97.5 and lng < -82.5:
            return -360  # UTC-6
        elif lng >= -112.5 and lng < -97.5:
            return -420  # UTC-7
        elif lng >= -127.5 and lng < -112.5:
            return -480  # UTC-8
        elif lng >= -142.5 and lng < -127.5:
            return -540  # UTC-9
        elif lng >= -157.5 and lng < -142.5:
            return -600  # UTC-10
        
        return 0  # UTC como fallback
