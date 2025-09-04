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
        
        # Planet names in Sanskrit and Spanish
        self.planet_names = {
            'Sun': {'sanskrit': 'सूर्य', 'español': 'Sol'},
            'Moon': {'sanskrit': 'चन्द्र', 'español': 'Luna'},
            'Mercury': {'sanskrit': 'बुध', 'español': 'Mercurio'},
            'Venus': {'sanskrit': 'शुक्र', 'español': 'Venus'},
            'Mars': {'sanskrit': 'मङ्गल', 'español': 'Marte'},
            'Jupiter': {'sanskrit': 'गुरु', 'español': 'Júpiter'},
            'Saturn': {'sanskrit': 'शनि', 'español': 'Saturno'},
            'Rahu': {'sanskrit': 'राहु', 'español': 'Rahu'},
            'Ketu': {'sanskrit': 'केतु', 'español': 'Ketu'}
        }
        
        # Classical Chesta Bala motion states and their ṣaṣṭyāṁśa values
        self.motion_states = {
            'Vakra': {
                'sanskrit': 'वक्र',
                'transliteration': 'vakra',
                'description': 'Retrógrado',
                'chesta_bala': 60,
                'english': 'Retrograde',
                'speed_threshold': -0.01  # Negative speed indicates retrograde
            },
            'Anuvakra': {
                'sanskrit': 'अनुवक्र',
                'transliteration': 'anuvakra',
                'description': 'Directo después de retrogradación',
                'chesta_bala': 30,
                'english': 'Direct after retrograde',
                'speed_threshold': 0.01
            },
            'Vikala': {
                'sanskrit': 'विकल',
                'transliteration': 'vikala',
                'description': 'Estacionario (sin movimiento)',
                'chesta_bala': 15,
                'english': 'Stationary (no movement)',
                'speed_threshold': 0.05
            },
            'Mandatara': {
                'sanskrit': 'मन्दतर',
                'transliteration': 'mandatara',
                'description': 'Muy lento',
                'chesta_bala': 15,
                'english': 'Very slow',
                'speed_threshold': 0.3
            },
            'Manda': {
                'sanskrit': 'मन्द',
                'transliteration': 'manda',
                'description': 'Lento',
                'chesta_bala': 30,
                'english': 'Slow',
                'speed_threshold': 0.6
            },
            'Sama': {
                'sanskrit': 'साम',
                'transliteration': 'sama',
                'description': 'Movimiento medio',
                'chesta_bala': 30,
                'english': 'Medium motion',
                'speed_threshold': 1.4
            },
            'Chara': {
                'sanskrit': 'चरा',
                'transliteration': 'chara',
                'description': 'Rápido',
                'chesta_bala': 30,
                'english': 'Fast',
                'speed_threshold': 2.0
            },
            'Sighra': {
                'sanskrit': 'शीघ्र',
                'transliteration': 'sighra',
                'description': 'Rápido',
                'chesta_bala': 30,
                'english': 'Fast',
                'speed_threshold': 2.0
            },
            'Atichara': {
                'sanskrit': 'अतिचरा',
                'transliteration': 'atichara',
                'description': 'Muy rápido',
                'chesta_bala': 45,
                'english': 'Very fast',
                'speed_threshold': 3.0
            },
            'Sighratara': {
                'sanskrit': 'शीघ्रतर',
                'transliteration': 'sighratara',
                'description': 'Muy rápido',
                'chesta_bala': 45,
                'english': 'Very fast',
                'speed_threshold': 3.0
            },
            'Kutilaka': {
                'sanskrit': 'कुटिलक',
                'transliteration': 'kutilaka',
                'description': 'Movimiento irregular, zigzagueante',
                'chesta_bala': 37.5,  # Valor promedio entre 30-45
                'english': 'Irregular, zigzag motion',
                'speed_threshold': 0.1
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
            planet_id = self.planets[planet_name]
            
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
            
            # Get planet names
            planet_names = self.planet_names.get(planet_name, {'sanskrit': planet_name, 'español': planet_name})
            
            # Return the exact structure requested in the prompt
            return {
                'graha': planet_names['sanskrit'],
                'graha_es': planet_names['español'],
                'chesta_avasta': motion_state_info['sanskrit'],
                'chesta_avasta_transliteration': motion_state_info['transliteration'],
                'chesta_es': motion_state_info['description'],
                'velocidad_grados_por_dia': round(speed, 2),
                'categoria': motion_state_info['sanskrit'],
                'categoria_transliteration': motion_state_info['transliteration'],
                'puntuaje_shastiamsa': chesta_bala,
                # Additional information for compatibility
                'longitude': longitude,
                'speed': abs(speed),
                'is_retrograde': is_retrograde,
                'motion_state': motion_state_info['sanskrit'],
                'motion_state_sanskrit': motion_state_info['sanskrit'],
                'motion_state_transliteration': motion_state_info['transliteration'],
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
                'chesta_avasta_transliteration': 'ajñāta',
                'chesta_es': 'Desconocido',
                'velocidad_grados_por_dia': 0,
                'categoria': 'अज्ञात',
                'categoria_transliteration': 'ajñāta',
                'puntuaje_shastiamsa': 0,
                'longitude': 0,
                'speed': 0,
                'is_retrograde': False,
                'motion_state': 'unknown',
                'motion_state_sanskrit': 'अज्ञात',
                'motion_state_transliteration': 'ajñāta',
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
                return self.motion_states['Vakra']  # Retrograde
            
            # Check for stationary motion (Vikala)
            if abs_speed < 0.05:
                return self.motion_states['Vikala']
            
            # Check for irregular motion (Kutilaka) - very small speed variations
            if 0.05 <= abs_speed < 0.1:
                return self.motion_states['Kutilaka']
            
            # Get planet-specific speed ranges
            ranges = self.planet_speed_ranges.get(planet_name, {})
            normal_min = ranges.get('normal_min', 0.5)
            normal_max = ranges.get('normal_max', 1.5)
            fast_threshold = ranges.get('fast', 2.0)
            slow_threshold = ranges.get('slow', 0.3)
            
            # Determine motion state based on speed
            if abs_speed >= 3.0:
                return self.motion_states['Atichara']  # Very fast
            elif abs_speed >= 2.0:
                return self.motion_states['Sighra']  # Fast
            elif abs_speed >= normal_max:
                return self.motion_states['Chara']  # Fast
            elif abs_speed <= slow_threshold:
                return self.motion_states['Mandatara']  # Very slow
            elif abs_speed <= normal_min:
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
        state = motion_state_info.get('transliteration', 'unknown')
        description = motion_state_info.get('description', 'unknown')
        chesta_bala = motion_state_info.get('chesta_bala', 0)
        
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
    
    def get_monthly_chesta_analysis(
        self, 
        year: int, 
        month: int, 
        latitude: float, 
        longitude: float,
        planets: Optional[List[str]] = None
    ) -> Dict:
        """Get monthly Chesta Bala analysis with motion changes."""
        try:
            if planets is None:
                planets = list(self.planets.keys())
            
            # Get first and last day of month
            from calendar import monthrange
            first_day = datetime(year, month, 1)
            last_day_num = monthrange(year, month)[1]
            last_day = datetime(year, month, last_day_num)
            
            # Calculate for each day of the month
            daily_data = {}
            motion_changes = []
            previous_states = {}
            
            current_date = first_day
            while current_date <= last_day:
                date_str = current_date.strftime('%Y-%m-%d')
                jd = self._datetime_to_jd(current_date)
                
                daily_planets = {}
                for planet_name in planets:
                    if planet_name not in self.planets:
                        continue
                    
                    planet_data = self._calculate_planet_chesta_bala(
                        planet_name, jd, latitude, longitude
                    )
                    daily_planets[planet_name] = planet_data
                    
                    # Check for motion state changes
                    current_state = planet_data.get('motion_state_transliteration', 'unknown')
                    if planet_name in previous_states:
                        prev_state = previous_states[planet_name]
                        if current_state != prev_state:
                            motion_changes.append({
                                'date': date_str,
                                'planet': planet_name,
                                'from_state': prev_state,
                                'to_state': current_state,
                                'from_sanskrit': self._get_sanskrit_for_transliteration(prev_state),
                                'to_sanskrit': self._get_sanskrit_for_transliteration(current_state),
                                'chesta_bala_change': planet_data.get('chesta_bala', 0) - self._get_chesta_bala_for_state(prev_state)
                            })
                    
                    previous_states[planet_name] = current_state
                
                daily_data[date_str] = {
                    'date': date_str,
                    'planets': daily_planets
                }
                
                current_date += timedelta(days=1)
            
            # Generate summary
            summary = self._generate_monthly_summary(daily_data, motion_changes)
            
            return {
                'year': year,
                'month': month,
                'latitude': latitude,
                'longitude': longitude,
                'daily_data': daily_data,
                'motion_changes': motion_changes,
                'summary': summary
            }
            
        except Exception as e:
            logger.error(f"Error in monthly Chesta analysis: {e}")
            raise
    
    def get_daily_chesta_analysis(
        self, 
        date: datetime, 
        latitude: float, 
        longitude: float,
        planets: Optional[List[str]] = None
    ) -> Dict:
        """Get detailed daily Chesta Bala analysis."""
        try:
            if planets is None:
                planets = list(self.planets.keys())
            
            jd = self._datetime_to_jd(date)
            
            planets_data = {}
            for planet_name in planets:
                if planet_name not in self.planets:
                    continue
                
                planet_data = self._calculate_planet_chesta_bala(
                    planet_name, jd, latitude, longitude
                )
                planets_data[planet_name] = planet_data
            
            # Generate daily summary
            summary = self._generate_daily_summary(planets_data)
            
            return {
                'date': date.isoformat(),
                'latitude': latitude,
                'longitude': longitude,
                'planets': planets_data,
                'summary': summary
            }
            
        except Exception as e:
            logger.error(f"Error in daily Chesta analysis: {e}")
            raise
    
    def _get_sanskrit_for_transliteration(self, transliteration: str) -> str:
        """Get Sanskrit name for transliteration."""
        for state_name, state_data in self.motion_states.items():
            if state_data['transliteration'] == transliteration:
                return state_data['sanskrit']
        return transliteration
    
    def _get_chesta_bala_for_state(self, transliteration: str) -> float:
        """Get Chesta Bala value for transliteration."""
        for state_name, state_data in self.motion_states.items():
            if state_data['transliteration'] == transliteration:
                return state_data['chesta_bala']
        return 0.0
    
    def _generate_monthly_summary(self, daily_data: Dict, motion_changes: List[Dict]) -> Dict:
        """Generate monthly summary of Chesta Bala analysis."""
        try:
            # Count motion changes by planet
            changes_by_planet = {}
            for change in motion_changes:
                planet = change['planet']
                if planet not in changes_by_planet:
                    changes_by_planet[planet] = []
                changes_by_planet[planet].append(change)
            
            # Calculate average Chesta Bala for each planet
            planet_averages = {}
            for date_str, day_data in daily_data.items():
                for planet_name, planet_data in day_data['planets'].items():
                    if planet_name not in planet_averages:
                        planet_averages[planet_name] = []
                    planet_averages[planet_name].append(planet_data.get('chesta_bala', 0))
            
            # Calculate averages
            for planet_name in planet_averages:
                values = planet_averages[planet_name]
                planet_averages[planet_name] = sum(values) / len(values) if values else 0
            
            return {
                'total_motion_changes': len(motion_changes),
                'changes_by_planet': changes_by_planet,
                'planet_averages': planet_averages,
                'most_active_planet': max(changes_by_planet.keys(), key=lambda k: len(changes_by_planet[k])) if changes_by_planet else None,
                'average_chesta_bala': sum(planet_averages.values()) / len(planet_averages) if planet_averages else 0
            }
            
        except Exception as e:
            logger.error(f"Error generating monthly summary: {e}")
            return {'error': str(e)}
    
    def _generate_daily_summary(self, planets_data: Dict) -> Dict:
        """Generate daily summary of Chesta Bala analysis."""
        try:
            total_chesta_bala = 0
            planet_count = 0
            strong_planets = []
            weak_planets = []
            retrograde_planets = []
            motion_states = {}
            
            for planet_name, planet_data in planets_data.items():
                chesta_bala = planet_data.get('chesta_bala', 0)
                total_chesta_bala += chesta_bala
                planet_count += 1
                
                # Categorize by strength
                if chesta_bala >= 45:
                    strong_planets.append(planet_name)
                elif chesta_bala <= 15:
                    weak_planets.append(planet_name)
                
                # Track retrograde planets
                if planet_data.get('is_retrograde', False):
                    retrograde_planets.append(planet_name)
                
                # Track motion states
                motion_state = planet_data.get('motion_state_transliteration', 'unknown')
                if motion_state not in motion_states:
                    motion_states[motion_state] = []
                motion_states[motion_state].append(planet_name)
            
            average_chesta_bala = total_chesta_bala / planet_count if planet_count > 0 else 0
            
            return {
                'average_chesta_bala': round(average_chesta_bala, 2),
                'strong_planets': strong_planets,
                'weak_planets': weak_planets,
                'retrograde_planets': retrograde_planets,
                'motion_states': motion_states,
                'overall_assessment': self._get_overall_assessment_classical(average_chesta_bala)
            }
            
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
            return {'error': str(e)}


# Create service instance
chesta_bala_service = ChestaBalaService()
