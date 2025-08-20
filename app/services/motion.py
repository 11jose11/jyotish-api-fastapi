"""Motion states service for planetary movement classification."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.services.swe import swe_service
from app.util.logging import get_logger

logger = get_logger("motion")

# Motion state classifications
MOTION_STATES = {
    "vakri": "retrograde",
    "vikala": "very slow",
    "kutila": "stationary",
    "anuvakri": "post-retrograde slow",
    "mandatara": "very slow",
    "manda": "slow",
    "sama": "normal",
    "sighra": "fast",
    "atisighra": "very fast"
}

# Baseline speeds for each planet (degrees per day)
BASELINE_SPEEDS = {
    "Sun": 1.0,
    "Moon": 13.2,
    "Mercury": 1.4,
    "Venus": 1.2,
    "Mars": 0.5,
    "Jupiter": 0.08,
    "Saturn": 0.03,
    "Rahu": 0.05,
    "Ketu": 0.05
}

# Planet names in Sanskrit and Spanish
PLANET_NAMES = {
    "Sun": {"sanskrit": "Sūrya", "spanish": "Sol"},
    "Moon": {"sanskrit": "Chandra", "spanish": "Luna"},
    "Mercury": {"sanskrit": "Budha", "spanish": "Mercurio"},
    "Venus": {"sanskrit": "Śukra", "spanish": "Venus"},
    "Mars": {"sanskrit": "Maṅgala", "spanish": "Marte"},
    "Jupiter": {"sanskrit": "Guru", "spanish": "Júpiter"},
    "Saturn": {"sanskrit": "Śani", "spanish": "Saturno"},
    "Rahu": {"sanskrit": "Rāhu", "spanish": "Rahu"},
    "Ketu": {"sanskrit": "Ketu", "spanish": "Ketu"}
}


class MotionService:
    """Service for analyzing planetary motion states."""
    
    def __init__(self):
        self.swe_service = swe_service
    
    def classify_motion_state(self, planet: str, speed: float) -> str:
        """Classify motion state based on speed relative to baseline."""
        baseline = BASELINE_SPEEDS.get(planet, 1.0)
        
        if speed < 0:
            return "vakri"  # retrograde
        
        speed_ratio = speed / baseline
        
        if speed_ratio < 0.03:
            return "vikala"
        elif speed_ratio < 0.1:
            return "mandatara"
        elif speed_ratio < 0.6:
            return "manda"
        elif speed_ratio < 1.4:
            return "sama"
        elif speed_ratio < 2.0:
            return "sighra"
        else:
            return "atisighra"
    
    def get_planet_speeds(
        self,
        start: datetime,
        end: datetime,
        place_id: str,
        planets: List[str]
    ) -> Dict:
        """Get current planetary speeds for the given date range."""
        try:
            # Simplified place info (UTC for now)
            place_info = {"timezone": {"timeZoneId": "UTC"}}
            
            # Calculate speeds for the middle of the date range
            mid_date = start + (end - start) / 2
            
            # Calculate planetary positions
            planet_data = self.swe_service.calculate_planets(mid_date, planets)
            
            speeds = []
            for planet in planets:
                if planet in planet_data:
                    data = planet_data[planet]
                    motion_state = self.classify_motion_state(planet, data["speedDegPerDay"])
                    
                    planet_names = PLANET_NAMES.get(planet, {"sanskrit": planet, "spanish": planet})
                    
                    speeds.append({
                        "planet": planet,
                        "name_sanskrit": planet_names["sanskrit"],
                        "name_spanish": planet_names["spanish"],
                        "speed_deg_per_day": data["speedDegPerDay"],
                        "motion_state": motion_state,
                        "is_retrograde": data["retrograde"]
                    })
            
            return {
                "start": start.isoformat(),
                "end": end.isoformat(),
                "place_id": place_id,
                "planets": speeds
            }
            
        except Exception as e:
            logger.error(f"Error calculating planet speeds: {e}")
            raise
    
    def detect_retrograde_events(
        self, 
        planet: str, 
        start_dt: datetime, 
        end_dt: datetime,
        step_minutes: int = 60
    ) -> List[Dict]:
        """Detect retrograde begin/end events for a planet."""
        events = []
        current_dt = start_dt
        
        # Track previous state
        prev_retrograde = None
        
        while current_dt <= end_dt:
            try:
                planet_data = self.swe_service.calculate_planets(current_dt, [planet])
                if planet not in planet_data:
                    continue
                
                current_retrograde = planet_data[planet]["retrograde"]
                
                # Detect state change
                if prev_retrograde is not None and prev_retrograde != current_retrograde:
                    event_type = "retro_end" if prev_retrograde else "retro_begin"
                    events.append({
                        "planet": planet,
                        "event": event_type,
                        "timestamp": current_dt.isoformat(),
                        "exact": True  # Will be refined with binary search
                    })
                
                prev_retrograde = current_retrograde
                current_dt += timedelta(minutes=step_minutes)
                
            except Exception as e:
                logger.error(f"Error calculating motion for {planet}: {e}")
                current_dt += timedelta(minutes=step_minutes)
        
        return events
    
    def get_motion_states(
        self,
        start: datetime,
        end: datetime,
        step_minutes: int = 60,
        mode: str = "classic",
        planets: Optional[List[str]] = None
    ) -> Dict:
        """Get motion states for planets over time period."""
        if planets is None:
            planets = list(BASELINE_SPEEDS.keys())
        
        results = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "step_minutes": step_minutes,
            "mode": mode,
            "planets": {},
            "events": []
        }
        
        current_dt = start
        
        for planet in planets:
            results["planets"][planet] = []
        
        while current_dt <= end:
            try:
                planet_data = self.swe_service.calculate_planets(current_dt, planets)
                
                for planet in planets:
                    if planet in planet_data:
                        data = planet_data[planet]
                        motion_state = self.classify_motion_state(planet, data["speedDegPerDay"])
                        
                        results["planets"][planet].append({
                            "timestamp": current_dt.isoformat(),
                            "longitude": data["lon"],
                            "speed": data["speedDegPerDay"],
                            "retrograde": data["retrograde"],
                            "motion_state": motion_state
                        })
                
                current_dt += timedelta(minutes=step_minutes)
                
            except Exception as e:
                logger.error(f"Error calculating motion states: {e}")
                current_dt += timedelta(minutes=step_minutes)
        
        # Detect events
        for planet in planets:
            events = self.detect_retrograde_events(planet, start, end, step_minutes)
            results["events"].extend(events)
        
        return results
    
    def find_stationary_points(
        self,
        planet: str,
        start_dt: datetime,
        end_dt: datetime,
        precision_minutes: int = 2
    ) -> List[Dict]:
        """Find exact stationary points using binary search."""
        events = []
        current_dt = start_dt
        
        while current_dt < end_dt:
            # Check for direction change in this interval
            next_dt = current_dt + timedelta(hours=1)
            if next_dt > end_dt:
                break
            
            try:
                start_data = self.swe_service.calculate_planets(current_dt, [planet])
                end_data = self.swe_service.calculate_planets(next_dt, [planet])
                
                if planet not in start_data or planet not in end_data:
                    current_dt = next_dt
                    continue
                
                start_speed = start_data[planet]["speedDegPerDay"]
                end_speed = end_data[planet]["speedDegPerDay"]
                
                # Check if speed changed sign (crossed zero)
                if (start_speed < 0 and end_speed > 0) or (start_speed > 0 and end_speed < 0):
                    # Binary search for exact stationary point
                    stationary_dt = self._binary_search_stationary(
                        planet, current_dt, next_dt, precision_minutes
                    )
                    
                    if stationary_dt:
                        events.append({
                            "planet": planet,
                            "event": "station_exact",
                            "timestamp": stationary_dt.isoformat(),
                            "longitude": self.swe_service.calculate_planets(stationary_dt, [planet])[planet]["lon"]
                        })
                
                current_dt = next_dt
                
            except Exception as e:
                logger.error(f"Error finding stationary points for {planet}: {e}")
                current_dt = next_dt
        
        return events
    
    def _binary_search_stationary(
        self,
        planet: str,
        start_dt: datetime,
        end_dt: datetime,
        precision_minutes: int
    ) -> Optional[datetime]:
        """Binary search for exact stationary point."""
        while (end_dt - start_dt).total_seconds() > precision_minutes * 60:
            mid_dt = start_dt + (end_dt - start_dt) / 2
            
            try:
                start_data = self.swe_service.calculate_planets(start_dt, [planet])
                mid_data = self.swe_service.calculate_planets(mid_dt, [planet])
                
                if planet not in start_data or planet not in mid_data:
                    return None
                
                start_speed = start_data[planet]["speedDegPerDay"]
                mid_speed = mid_data[planet]["speedDegPerDay"]
                
                # Determine which half contains the zero crossing
                if (start_speed < 0 and mid_speed > 0) or (start_speed > 0 and mid_speed < 0):
                    end_dt = mid_dt
                else:
                    start_dt = mid_dt
                    
            except Exception:
                return None
        
        return start_dt


# Global service instance
motion_service = MotionService()
