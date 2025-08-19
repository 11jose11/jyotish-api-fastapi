from typing import Dict, Any
from .planetary_precise import PlanetaryPreciseService
from .sunrise import SunriseService

class PrecisePanchangaService:
    """Servicio para cálculos precisos del Panchanga"""
    
    def __init__(self, google_api_key: str = None):
        self.sunrise_service = SunriseService(google_api_key)
    
    def calculate_panchanga(self, date: str, lat: float, lng: float) -> Dict[str, Any]:
        """Calcular Panchanga preciso para una fecha y ubicación"""
        
        # 1. Obtener hora exacta del amanecer
        sunrise_time = self.sunrise_service.get_sunrise_time(date, lat, lng)
        
        # 2. Obtener posiciones planetarias al amanecer
        positions = PlanetaryPreciseService.get_planetary_positions(date, sunrise_time, lat, lng)
        
        # 3. Calcular elementos del Panchanga usando longitudes siderales
        sun_longitude = positions['sun']['sidereal']
        moon_longitude = positions['moon']['sidereal']
        
        # Calcular Tithi
        tithi = self._calculate_tithi(sun_longitude, moon_longitude)
        
        # Calcular Nakshatra
        nakshatra = self._calculate_nakshatra(moon_longitude)
        
        # Calcular Yoga
        yoga = self._calculate_yoga(sun_longitude, moon_longitude)
        
        # Calcular Karana
        karana = self._calculate_karana(tithi)
        
        # Calcular Vara
        vara = self._calculate_vara(sunrise_time)
        
        return {
            'date': date,
            'sunrise_time': sunrise_time,
            'panchanga': {
                'tithi': tithi,
                'nakshatra': nakshatra,
                'yoga': yoga,
                'karana': karana,
                'vara': vara
            },
            'positions': {
                'sun': positions['sun'],
                'moon': positions['moon']
            }
        }
    
    def _calculate_tithi(self, sun_longitude: float, moon_longitude: float) -> Dict[str, Any]:
        """Calcular Tithi usando elongación lunar sideral"""
        elongation = moon_longitude - sun_longitude
        if elongation < 0:
            elongation += 360
        
        tithi_number = int(elongation / 12) + 1
        paksha = "Shukla" if elongation < 180 else "Krishna"
        
        tithi_names = [
            'Pratipada', 'Dwitiya', 'Tritiya', 'Chaturthi', 'Panchami',
            'Shashthi', 'Saptami', 'Ashtami', 'Navami', 'Dashami',
            'Ekadashi', 'Dwadashi', 'Trayodashi', 'Chaturdashi', 'Purnima/Amavasya'
        ]
        
        return {
            'number': tithi_number,
            'paksha': paksha,
            'display': f"{'S' if paksha == 'Shukla' else 'K'}{tithi_number}",
            'name': tithi_names[tithi_number - 1],
            'elongation': elongation
        }
    
    def _calculate_nakshatra(self, moon_longitude: float) -> Dict[str, Any]:
        """Calcular Nakshatra usando longitud lunar sideral"""
        nakshatra_size = 13.333333  # 13°20'
        nakshatra_number = int(moon_longitude / nakshatra_size)
        
        nakshatra_names = [
            'Aśvinī', 'Bharaṇī', 'Kṛttikā', 'Rohiṇī', 'Mṛgaśirā', 'Ārdrā', 'Punarvasu',
            'Puṣya', 'Āśleṣā', 'Maghā', 'Pūrva Phalgunī', 'Uttara Phalgunī', 'Hastā',
            'Citrā', 'Svātī', 'Viśākhā', 'Anurādhā', 'Jyeṣṭhā', 'Mūla', 'Pūrva Āṣāḍhā',
            'Uttara Āṣāḍhā', 'Śravaṇa', 'Dhaniṣṭhā', 'Śatabhiṣā', 'Pūrva Bhādrapadā',
            'Uttara Bhādrapadā', 'Revatī'
        ]
        
        return {
            'number': nakshatra_number + 1,
            'name': nakshatra_names[nakshatra_number],
            'longitude': moon_longitude
        }
    
    def _calculate_yoga(self, sun_longitude: float, moon_longitude: float) -> Dict[str, Any]:
        """Calcular Yoga usando suma de longitudes siderales"""
        yoga_longitude = (sun_longitude + moon_longitude) % 360
        yoga_size = 13.333333  # 13°20'
        yoga_number = int(yoga_longitude / yoga_size)
        
        yoga_names = [
            'Viṣkumbha', 'Prīti', 'Āyuṣmān', 'Saubhāgya', 'Śobhana', 'Atigaṇḍa',
            'Sukarmā', 'Dhṛti', 'Śūla', 'Gaṇḍa', 'Vṛddhi', 'Dhruva', 'Vyāghāta',
            'Harṣaṇa', 'Vajra', 'Siddha', 'Vyatipāta', 'Variyāna', 'Parigha',
            'Śiva', 'Siddhi', 'Sādhya', 'Śubha', 'Śukla', 'Brahma', 'Aindra', 'Vaidhṛti'
        ]
        
        return {
            'number': yoga_number + 1,
            'name': yoga_names[yoga_number],
            'longitude': yoga_longitude
        }
    
    def _calculate_karana(self, tithi: Dict[str, Any]) -> Dict[str, Any]:
        """Calcular Karana basado en Tithi"""
        karana_number = ((tithi['number'] - 1) % 11) + 1
        
        karana_names = [
            'Bava', 'Bālava', 'Kaulava', 'Taitila', 'Gara', 'Vaṇija', 'Viṣṭi',
            'Śakuni', 'Catuṣpada', 'Nāga', 'Kiṁstughna'
        ]
        
        return {
            'number': karana_number,
            'name': karana_names[karana_number - 1]
        }
    
    def _calculate_vara(self, sunrise_time: str) -> Dict[str, Any]:
        """Calcular Vara basado en hora del amanecer"""
        from datetime import datetime
        import pytz
        
        # Parsear hora del amanecer
        time_parts = sunrise_time.split(':')
        hours, minutes, seconds = int(time_parts[0]), int(time_parts[1]), int(time_parts[2])
        
        # Crear fecha con hora del amanecer
        sunrise_datetime = datetime.now().replace(hour=hours, minute=minutes, second=seconds)
        vara_number = sunrise_datetime.weekday()
        
        vara_names = [
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
        ]
        
        return {
            'number': vara_number,
            'name': vara_names[vara_number]
        }
