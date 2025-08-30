"""Chesta Bala (Directional Strength) calculation service based on classical Vedic astrology."""

import swisseph as swe
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import math

from app.util.logging import get_logger

logger = get_logger("chesta_bala")


class ChestaBalaService:
    """Service for calculating Chesta Bala (Directional Strength) of planets based on classical texts."""
    
    def __init__(self):
        # Set Swiss Ephemeris to True Citra Paksha ayanamsa
        swe.set_sid_mode(swe.SIDM_TRUE_CITRA)
        
        # Planet mapping
        self.planets = {
            'Sun': swe.SUN,
            'Moon': swe.MOON,
            'Mercury': swe.MERCURY,
            'Venus': swe.VENUS,
            'Mars': swe.MARS,
            'Jupiter': swe.JUPITER,
            'Saturn': swe.SATURN,
            'Rahu': swe.MEAN_NODE,  # Mean Node (Rahu)
            'Ketu': None  # Ketu is opposite to Rahu
        }
        
        # Classical Chesta Bala motion states and their ṣaṣṭyāṁśa values
        self.motion_states = {
            'Vakra': {
                'sanskrit': 'वक्र',
                'description': 'Retrógrado',
                'chesta_bala': 60,
                'english': 'Retrograde',
                'speed_threshold': -0.01  # Negative speed indicates retrograde
            },
            'Anuvakra': {
                'sanskrit': 'अनुवक्र',
                'description': 'Directo después de retrógrado',
                'chesta_bala': 30,
                'english': 'Direct after retrograde',
                'speed_threshold': 0.01
            },
            'Manda': {
                'sanskrit': 'मन्द',
                'description': 'Directo pero lento',
                'chesta_bala': 15,
                'english': 'Direct but slow',
                'speed_threshold': 0.3
            },
            'Mandatara': {
                'sanskrit': 'मन्दतर',
                'description': 'Más lento que lo normal',
                'chesta_bala': 7.5,
                'english': 'Slower than normal',
                'speed_threshold': 0.5
            },
            'Sama': {
                'sanskrit': 'सम',
                'description': 'Movimiento medio, regular',
                'chesta_bala': 30,
                'english': 'Medium, regular motion',
                'speed_threshold': 1.0
            },
            'Chara': {
                'sanskrit': 'चर',
                'description': 'Movimiento rápido',
                'chesta_bala': 30,
                'english': 'Fast motion',
                'speed_threshold': 2.0
            },
            'Atichara': {
                'sanskrit': 'अतिचर',
                'description': 'Muy rápido',
                'chesta_bala': 45,
                'english': 'Very fast',
                'speed_threshold': 5.0
            },
            'Kutilaka': {
                'sanskrit': 'कुटिलक',
                'description': 'Movimiento estacionario/curvo (planeta casi detenido, cambiando dirección)',
                'chesta_bala': 15,
                'english': 'Stationary/curved motion (planet almost stopped, changing direction)',
                'speed_threshold': 0.05
            },
            'Vakragati': {
                'sanskrit': 'वक्रगति',
                'description': 'Retrógrado extremo o giro forzado',
                'chesta_bala': 60,
                'english': 'Extreme retrograde or forced turn',
                'speed_threshold': -0.5
            }
        }
        
        # Planet-specific speed ranges for motion state determination
        self.planet_speed_ranges = {
            'Sun': {'normal_min': 0.95, 'normal_max': 1.05, 'fast': 1.1, 'slow': 0.9},
            'Moon': {'normal_min': 12.0, 'normal_max': 15.0, 'fast': 16.0, 'slow': 10.0},
            'Mercury': {'normal_min': 0.8, 'normal_max': 1.5, 'fast': 2.0, 'slow': 0.5},
            'Venus': {'normal_min': 0.8, 'normal_max': 1.3, 'fast': 1.8, 'slow': 0.5},
            'Mars': {'normal_min': 0.4, 'normal_max': 0.8, 'fast': 1.2, 'slow': 0.2},
            'Jupiter': {'normal_min': 0.05, 'normal_max': 0.15, 'fast': 0.3, 'slow': 0.02},
            'Saturn': {'normal_min': 0.03, 'normal_max': 0.12, 'fast': 0.2, 'slow': 0.01},
            'Rahu': {'normal_min': 0.05, 'normal_max': 0.08, 'fast': 0.12, 'slow': 0.03},
            'Ketu': {'normal_min': 0.05, 'normal_max': 0.08, 'fast': 0.12, 'slow': 0.03}
        }
    
    def calculate_chesta_bala(
        self, 
        date: datetime, 
        latitude: float, 
        longitude: float,
        planets: Optional[List[str]] = None
    ) -> Dict:
        """
        Calculate Chesta Bala for all planets.
        
        Args:
            date: Date and time for calculation
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            planets: List of planets to calculate (default: all)
            
        Returns:
            Dictionary with Chesta Bala calculations
        """
        try:
            if planets is None:
                planets = list(self.planets.keys())
            
            # Convert date to Julian Day
            jd = self._datetime_to_jd(date)
            
            results = {
                'date': date.isoformat(),
                'latitude': latitude,
                'longitude': longitude,
                'planets': {}
            }
            
            for planet_name in planets:
                if planet_name not in self.planets:
                    continue
                    
                planet_data = self._calculate_planet_chesta_bala(
                    planet_name, jd, latitude, longitude
                )
                results['planets'][planet_name] = planet_data
            
            return results
            
        except Exception as e:
            logger.error(f"Error calculating Chesta Bala: {e}")
            raise
    
    def _calculate_planet_chesta_bala(
        self, 
        planet_name: str, 
        jd: float, 
        latitude: float, 
        longitude: float
    ) -> Dict:
        """Calculate Chesta Bala for a specific planet using classical methods."""
        try:
            planet_info = self.planets[planet_name]
            planet_id = planet_info['id']
            
            if planet_name == 'Ketu':
                # Ketu is opposite to Rahu
                rahu_data = self._calculate_planet_chesta_bala('Rahu', jd, latitude, longitude)
                ketu_data = rahu_data.copy()
                ketu_data['longitude'] = (rahu_data['longitude'] + 180) % 360
                ketu_data['speed'] = rahu_data['speed']
                ketu_data['motion_state'] = rahu_data['motion_state']
                ketu_data['chesta_bala'] = rahu_data['chesta_bala']
                ketu_data['chesta_score'] = rahu_data['chesta_score']
                ketu_data['strength_level'] = rahu_data['strength_level']
                return ketu_data
            
            # Get current position and speed using Swiss Ephemeris
            position = swe.calc_ut(jd, planet_id)[0]
            longitude = position[0]
            
            # Calculate speed and determine if retrograde
            speed_data = self._calculate_planet_speed_detailed(planet_id, jd)
            speed = speed_data['speed']
            is_retrograde = speed_data['is_retrograde']
            
            # Determine classical motion state
            motion_state_info = self._determine_classical_motion_state(planet_name, speed, is_retrograde)
            
            # Get Chesta Bala value from classical texts
            chesta_bala = motion_state_info['chesta_bala']
            chesta_score = self._calculate_chesta_score_classical(chesta_bala)
            strength_level = self._get_strength_level_classical(chesta_bala)
            
            # Return the exact structure requested in the prompt
            return {
                'graha': planet_info['sanskrit'],
                'graha_es': planet_info['español'],
                'chesta_avasta': motion_state_info['sanskrit'],
                'chesta_es': motion_state_info['español'],
                'velocidad_grados_por_dia': round(speed, 2),
                'categoria': motion_state_info['sanskrit'],
                'puntuaje_shastiamsa': chesta_bala,
                # Additional information for compatibility
                'longitude': longitude,
                'speed': abs(speed),
                'is_retrograde': is_retrograde,
                'motion_state': motion_state_info['sanskrit'],
                'motion_state_sanskrit': motion_state_info['sanskrit'],
                'motion_state_description': motion_state_info['description'],
                'chesta_bala': chesta_bala,
                'chesta_score': chesta_score,
                'strength_level': strength_level,
                'description': self._get_chesta_description_classical(planet_name, motion_state_info),
                'classical_reference': f"Śaṣṭiāṁśa: {chesta_bala}/60"
            }
            
        except Exception as e:
            logger.error(f"Error calculating Chesta Bala for {planet_name}: {e}")
            return {
                'error': str(e),
                'graha': self.planets.get(planet_name, {}).get('sanskrit', planet_name),
                'graha_es': self.planets.get(planet_name, {}).get('español', planet_name),
                'chesta_avasta': 'अज्ञात',
                'chesta_es': 'Desconocido',
                'velocidad_grados_por_dia': 0,
                'categoria': 'अज्ञात',
                'puntuaje_shastiamsa': 0,
                'longitude': 0,
                'speed': 0,
                'is_retrograde': False,
                'motion_state': 'unknown',
                'motion_state_sanskrit': 'अज्ञात',
                'motion_state_description': 'Estado desconocido',
                'chesta_bala': 0,
                'chesta_score': 0,
                'strength_level': 'unknown'
            }
    
    def _calculate_planet_speed_detailed(self, planet_id: int, jd: float) -> Dict:
        """Calculate planet's speed and determine if retrograde using Swiss Ephemeris."""
        try:
            # Calculate position at current time
            pos1 = swe.calc_ut(jd, planet_id)[0]
            
            # Calculate position 1 day later
            pos2 = swe.calc_ut(jd + 1, planet_id)[0]
            
            # Calculate speed (can be negative for retrograde motion)
            speed = pos2[0] - pos1[0]
            
            # Handle longitude wrap-around
            if speed > 180:
                speed = speed - 360
            elif speed < -180:
                speed = speed + 360
            
            # Determine if retrograde
            is_retrograde = speed < 0
            
            return {
                'speed': speed,
                'is_retrograde': is_retrograde,
                'absolute_speed': abs(speed)
            }
            
        except Exception as e:
            logger.error(f"Error calculating planet speed: {e}")
            return {
                'speed': 0.0,
                'is_retrograde': False,
                'absolute_speed': 0.0
            }
    
    def _determine_classical_motion_state(self, planet_name: str, speed: float, is_retrograde: bool) -> Dict:
        """Determine the classical motion state of a planet based on Vedic texts."""
        try:
            abs_speed = abs(speed)
            
            # Check for retrograde states first
            if is_retrograde:
                if abs_speed > 0.5:
                    return self.motion_states['Vakragati']  # Extreme retrograde
                else:
                    return self.motion_states['Vakra']  # Normal retrograde
            
            # Check for stationary/curved motion (Kutilaka)
            if abs_speed < 0.05:
                return self.motion_states['Kutilaka']
            
            # Get planet-specific speed ranges
            ranges = self.planet_speed_ranges.get(planet_name, {})
            normal_min = ranges.get('normal_min', 0.5)
            normal_max = ranges.get('normal_max', 1.5)
            fast_threshold = ranges.get('fast', 2.0)
            slow_threshold = ranges.get('slow', 0.3)
            
            # Determine motion state based on speed
            if abs_speed > fast_threshold:
                return self.motion_states['Atichara']  # Very fast
            elif abs_speed > normal_max:
                return self.motion_states['Chara']  # Fast
            elif abs_speed < slow_threshold:
                return self.motion_states['Mandatara']  # Very slow
            elif abs_speed < normal_min:
                return self.motion_states['Manda']  # Slow
            else:
                return self.motion_states['Sama']  # Normal/regular
                
        except Exception as e:
            logger.error(f"Error determining motion state for {planet_name}: {e}")
            return self.motion_states['Sama']  # Default to normal motion
    
    def _calculate_chesta_score_classical(self, chesta_bala: float) -> int:
        """Calculate Chesta Bala score based on classical ṣaṣṭyāṁśa values."""
        # Convert ṣaṣṭyāṁśa (0-60) to score (1-5)
        if chesta_bala >= 45:
            return 5  # Excellent (Atichara, Vakra, Vakragati)
        elif chesta_bala >= 30:
            return 4  # Good (Sama, Chara, Anuvakra)
        elif chesta_bala >= 15:
            return 3  # Average (Manda, Kutilaka)
        elif chesta_bala >= 7.5:
            return 2  # Poor (Mandatara)
        else:
            return 1  # Very Poor
    
    def _get_strength_level_classical(self, chesta_bala: float) -> str:
        """Get strength level description based on classical values."""
        if chesta_bala >= 45:
            return 'Excelente'
        elif chesta_bala >= 30:
            return 'Buena'
        elif chesta_bala >= 15:
            return 'Promedio'
        elif chesta_bala >= 7.5:
            return 'Débil'
        else:
            return 'Muy Débil'
    
    def _get_chesta_description_classical(self, planet_name: str, motion_state_info: Dict) -> str:
        """Get classical description of Chesta Bala for a planet."""
        state = motion_state_info['state']
        description = motion_state_info['description']
        chesta_bala = motion_state_info['chesta_bala']
        
        return f"{planet_name} está en estado {state} ({description}). Cheṣṭā Bala: {chesta_bala}/60 ṣaṣṭyāṁśa."
    
    def _datetime_to_jd(self, dt: datetime) -> float:
        """Convert datetime to Julian Day Number."""
        if dt.tzinfo is not None:
            dt = dt.astimezone().replace(tzinfo=None)
        
        return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0 + dt.second/3600.0)
    
    def get_chesta_summary(self, chesta_data: Dict) -> Dict:
        """Generate a summary of Chesta Bala calculations using classical methods."""
        try:
            planets = chesta_data.get('planets', {})
            
            # Calculate averages
            total_chesta_bala = 0
            planet_count = 0
            strong_planets = []
            weak_planets = []
            retrograde_planets = []
            motion_states_summary = {}
            
            for planet_name, data in planets.items():
                if 'chesta_bala' in data:
                    chesta_bala = data['chesta_bala']
                    total_chesta_bala += chesta_bala
                    planet_count += 1
                    
                    # Track motion states
                    motion_state = data.get('motion_state', 'Unknown')
                    if motion_state not in motion_states_summary:
                        motion_states_summary[motion_state] = []
                    motion_states_summary[motion_state].append(planet_name)
                    
                    # Track retrograde planets
                    if data.get('is_retrograde', False):
                        retrograde_planets.append(planet_name)
                    
                    # Categorize by strength
                    if chesta_bala >= 30:
                        strong_planets.append(planet_name)
                    elif chesta_bala <= 15:
                        weak_planets.append(planet_name)
            
            average_chesta_bala = total_chesta_bala / planet_count if planet_count > 0 else 0
            
            return {
                'date': chesta_data.get('date'),
                'average_chesta_bala': round(average_chesta_bala, 2),
                'strong_planets': strong_planets,
                'weak_planets': weak_planets,
                'retrograde_planets': retrograde_planets,
                'motion_states_summary': motion_states_summary,
                'overall_assessment': self._get_overall_assessment_classical(average_chesta_bala),
                'recommendations': self._get_chesta_recommendations_classical(strong_planets, weak_planets, retrograde_planets),
                'classical_notes': self._get_classical_notes(motion_states_summary, retrograde_planets)
            }
            
        except Exception as e:
            logger.error(f"Error generating Chesta summary: {e}")
            return {'error': str(e)}
    
    def _get_overall_assessment_classical(self, average_chesta_bala: float) -> str:
        """Get overall assessment based on classical Chesta Bala values."""
        if average_chesta_bala >= 45:
            return "Excelente - Los planetas tienen fuerza direccional máxima según los textos clásicos"
        elif average_chesta_bala >= 30:
            return "Buena - La mayoría de planetas tienen fuerza direccional favorable"
        elif average_chesta_bala >= 15:
            return "Promedio - Fuerza direccional mixta según los ṣaṣṭyāṁśa"
        else:
            return "Débil - Los planetas tienen fuerza direccional limitada"
    
    def _get_chesta_recommendations_classical(self, strong_planets: List[str], weak_planets: List[str], retrograde_planets: List[str]) -> List[str]:
        """Get recommendations based on classical Chesta Bala analysis."""
        recommendations = []
        
        if strong_planets:
            recommendations.append(f"Planetas fuertes (Cheṣṭā Bala ≥30): {', '.join(strong_planets)} - Aprovecha su energía direccional")
        
        if weak_planets:
            recommendations.append(f"Planetas débiles (Cheṣṭā Bala ≤15): {', '.join(weak_planets)} - Considera remedios astrológicos")
        
        if retrograde_planets:
            recommendations.append(f"Planetas retrógrados: {', '.join(retrograde_planets)} - Período de introspección y revisión")
        
        if len(strong_planets) > len(weak_planets):
            recommendations.append("Período favorable para actividades importantes según los textos védicos")
        elif len(weak_planets) > len(strong_planets):
            recommendations.append("Período que requiere más cuidado y paciencia según la astrología clásica")
        
        return recommendations
    
    def _get_classical_notes(self, motion_states_summary: Dict, retrograde_planets: List[str]) -> List[str]:
        """Get classical astrological notes based on motion states."""
        notes = []
        
        # Notes about retrograde planets
        if retrograde_planets:
            notes.append(f"Planetas retrógrados: {', '.join(retrograde_planets)} - Según los textos clásicos, los planetas retrógrados tienen Cheṣṭā Bala de 60 ṣaṣṭyāṁśa")
        
        # Notes about motion states
        for state, planets in motion_states_summary.items():
            if state == 'Vakra':
                notes.append(f"Estado Vakra (retrógrado): {', '.join(planets)} - Máxima fuerza direccional")
            elif state == 'Atichara':
                notes.append(f"Estado Atichara (muy rápido): {', '.join(planets)} - Fuerza direccional muy alta")
            elif state == 'Kutilaka':
                notes.append(f"Estado Kutilaka (estacionario): {', '.join(planets)} - Cambio de dirección")
        
        return notes


# Create service instance
chesta_bala_service = ChestaBalaService()
