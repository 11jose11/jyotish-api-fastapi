"""Chesta Bala router for directional strength calculations."""

from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from app.services.chesta_bala import chesta_bala_service
from app.util.logging import get_logger, RequestLogger

logger = get_logger("chesta_bala_router")

router = APIRouter(prefix="/v1/chesta-bala", tags=["Chesta Bala"])


class ChestaBalaRequest(BaseModel):
    """Request model for Chesta Bala calculation."""
    date: str
    time: str = "12:00:00"
    latitude: float
    longitude: float
    planets: Optional[List[str]] = None


class ChestaBalaResponse(BaseModel):
    """Response model for Chesta Bala calculation."""
    date: str
    latitude: float
    longitude: float
    planets: dict
    summary: Optional[dict] = None


@router.get("/calculate")
async def calculate_chesta_bala(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    time: str = Query("12:00:00", description="Time in HH:MM:SS format"),
    latitude: float = Query(..., description="Latitude in decimal degrees"),
    longitude: float = Query(..., description="Longitude in decimal degrees"),
    planets: Optional[str] = Query(None, description="Comma-separated list of planets"),
    include_summary: bool = Query(True, description="Include summary analysis")
):
    """Calculate Chesta Bala (Directional Strength) for planets."""
    with RequestLogger("chesta_bala.calculate") as req_log:
        try:
            # Parse date and time
            dt_str = f"{date}T{time}"
            dt = datetime.fromisoformat(dt_str)
            
            # Validate coordinates
            if not (-90 <= latitude <= 90):
                raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
            if not (-180 <= longitude <= 180):
                raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
            
            # Parse planets list
            planet_list = None
            if planets:
                planet_list = [p.strip() for p in planets.split(",")]
            
            # Calculate Chesta Bala
            chesta_data = chesta_bala_service.calculate_chesta_bala(
                dt, latitude, longitude, planet_list
            )
            
            # Add summary if requested
            if include_summary:
                summary = chesta_bala_service.get_chesta_summary(chesta_data)
                chesta_data['summary'] = summary
            
            req_log.success()
            return chesta_data
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date/time format: {e}")
        except Exception as e:
            logger.error(f"Chesta Bala calculation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/monthly")
async def get_monthly_chesta_analysis(
    year: int = Query(..., description="Year (e.g., 2024)"),
    month: int = Query(..., description="Month (1-12)"),
    latitude: float = Query(..., description="Latitude in decimal degrees"),
    longitude: float = Query(..., description="Longitude in decimal degrees"),
    planets: Optional[str] = Query(None, description="Comma-separated list of planets")
):
    """Get monthly Chesta Bala analysis with motion changes."""
    with RequestLogger("chesta_bala.monthly") as req_log:
        try:
            # Validate inputs
            if not (1 <= month <= 12):
                raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
            if not (-90 <= latitude <= 90):
                raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
            if not (-180 <= longitude <= 180):
                raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
            
            # Parse planets list
            planet_list = None
            if planets:
                planet_list = [p.strip() for p in planets.split(",")]
            
            # Get monthly analysis
            result = chesta_bala_service.get_monthly_chesta_analysis(
                year, month, latitude, longitude, planet_list
            )
            
            req_log.success()
            return result
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid input: {e}")
        except Exception as e:
            logger.error(f"Monthly Chesta Bala analysis failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/daily")
async def get_daily_chesta_analysis(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    time: str = Query("12:00:00", description="Time in HH:MM:SS format"),
    latitude: float = Query(..., description="Latitude in decimal degrees"),
    longitude: float = Query(..., description="Longitude in decimal degrees"),
    planets: Optional[str] = Query(None, description="Comma-separated list of planets")
):
    """Get detailed daily Chesta Bala analysis."""
    with RequestLogger("chesta_bala.daily") as req_log:
        try:
            # Parse date and time
            dt_str = f"{date}T{time}"
            dt = datetime.fromisoformat(dt_str)
            
            # Validate coordinates
            if not (-90 <= latitude <= 90):
                raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
            if not (-180 <= longitude <= 180):
                raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
            
            # Parse planets list
            planet_list = None
            if planets:
                planet_list = [p.strip() for p in planets.split(",")]
            
            # Get daily analysis
            result = chesta_bala_service.get_daily_chesta_analysis(
                dt, latitude, longitude, planet_list
            )
            
            req_log.success()
            return result
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date/time format: {e}")
        except Exception as e:
            logger.error(f"Daily Chesta Bala analysis failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/planets")
async def get_chesta_bala_planets(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    time: str = Query("12:00:00", description="Time in HH:MM:SS format"),
    latitude: float = Query(..., description="Latitude in decimal degrees"),
    longitude: float = Query(..., description="Longitude in decimal degrees"),
    planet: str = Query(..., description="Planet name (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Rahu, Ketu)")
):
    """Calculate Chesta Bala for a specific planet."""
    with RequestLogger("chesta_bala.planet") as req_log:
        try:
            # Parse date and time
            dt_str = f"{date}T{time}"
            dt = datetime.fromisoformat(dt_str)
            
            # Validate coordinates
            if not (-90 <= latitude <= 90):
                raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
            if not (-180 <= longitude <= 180):
                raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
            
            # Validate planet
            valid_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Rahu', 'Ketu']
            if planet not in valid_planets:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid planet. Must be one of: {', '.join(valid_planets)}"
                )
            
            # Calculate Chesta Bala for specific planet
            chesta_data = chesta_bala_service.calculate_chesta_bala(
                dt, latitude, longitude, [planet]
            )
            
            planet_data = chesta_data.get('planets', {}).get(planet, {})
            if not planet_data:
                raise HTTPException(status_code=500, detail=f"Could not calculate Chesta Bala for {planet}")
            
            result = {
                'date': date,
                'time': time,
                'latitude': latitude,
                'longitude': longitude,
                'planet': planet,
                'data': planet_data
            }
            
            req_log.success()
            return result
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date/time format: {e}")
        except Exception as e:
            logger.error(f"Chesta Bala calculation for {planet} failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_chesta_bala_summary(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    time: str = Query("12:00:00", description="Time in HH:MM:SS format"),
    latitude: float = Query(..., description="Latitude in decimal degrees"),
    longitude: float = Query(..., description="Longitude in decimal degrees"),
    planets: Optional[str] = Query(None, description="Comma-separated list of planets")
):
    """Get summary analysis of Chesta Bala for all planets."""
    with RequestLogger("chesta_bala.summary") as req_log:
        try:
            # Parse date and time
            dt_str = f"{date}T{time}"
            dt = datetime.fromisoformat(dt_str)
            
            # Validate coordinates
            if not (-90 <= latitude <= 90):
                raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
            if not (-180 <= longitude <= 180):
                raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
            
            # Parse planets list
            planet_list = None
            if planets:
                planet_list = [p.strip() for p in planets.split(",")]
            
            # Calculate Chesta Bala
            chesta_data = chesta_bala_service.calculate_chesta_bala(
                dt, latitude, longitude, planet_list
            )
            
            # Get summary
            summary = chesta_bala_service.get_chesta_summary(chesta_data)
            
            result = {
                'date': date,
                'time': time,
                'latitude': latitude,
                'longitude': longitude,
                'summary': summary
            }
            
            req_log.success()
            return result
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date/time format: {e}")
        except Exception as e:
            logger.error(f"Chesta Bala summary calculation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/comparison")
async def compare_chesta_bala(
    date1: str = Query(..., description="First date in YYYY-MM-DD format"),
    time1: str = Query("12:00:00", description="First time in HH:MM:SS format"),
    date2: str = Query(..., description="Second date in YYYY-MM-DD format"),
    time2: str = Query("12:00:00", description="Second time in HH:MM:SS format"),
    latitude: float = Query(..., description="Latitude in decimal degrees"),
    longitude: float = Query(..., description="Longitude in decimal degrees"),
    planets: Optional[str] = Query(None, description="Comma-separated list of planets")
):
    """Compare Chesta Bala between two dates."""
    with RequestLogger("chesta_bala.comparison") as req_log:
        try:
            # Parse dates and times
            dt1_str = f"{date1}T{time1}"
            dt2_str = f"{date2}T{time2}"
            dt1 = datetime.fromisoformat(dt1_str)
            dt2 = datetime.fromisoformat(dt2_str)
            
            # Validate coordinates
            if not (-90 <= latitude <= 90):
                raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
            if not (-180 <= longitude <= 180):
                raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
            
            # Parse planets list
            planet_list = None
            if planets:
                planet_list = [p.strip() for p in planets.split(",")]
            
            # Calculate Chesta Bala for both dates
            chesta_data1 = chesta_bala_service.calculate_chesta_bala(
                dt1, latitude, longitude, planet_list
            )
            chesta_data2 = chesta_bala_service.calculate_chesta_bala(
                dt2, latitude, longitude, planet_list
            )
            
            # Compare results
            comparison = {
                'date1': date1,
                'time1': time1,
                'date2': date2,
                'time2': time2,
                'latitude': latitude,
                'longitude': longitude,
                'comparison': {}
            }
            
            planets_data1 = chesta_data1.get('planets', {})
            planets_data2 = chesta_data2.get('planets', {})
            
            for planet_name in planets_data1.keys():
                if planet_name in planets_data2:
                    data1 = planets_data1[planet_name]
                    data2 = planets_data2[planet_name]
                    
                    comparison['comparison'][planet_name] = {
                        'date1': {
                            'chesta_score': data1.get('chesta_score', 0),
                            'strength_level': data1.get('strength_level', 'Unknown'),
                            'speed': data1.get('speed', 0)
                        },
                        'date2': {
                            'chesta_score': data2.get('chesta_score', 0),
                            'strength_level': data2.get('strength_level', 'Unknown'),
                            'speed': data2.get('speed', 0)
                        },
                        'change': {
                            'score_change': data2.get('chesta_score', 0) - data1.get('chesta_score', 0),
                            'speed_change': data2.get('speed', 0) - data1.get('speed', 0),
                            'improvement': data2.get('chesta_score', 0) > data1.get('chesta_score', 0)
                        }
                    }
            
            req_log.success()
            return comparison
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date/time format: {e}")
        except Exception as e:
            logger.error(f"Chesta Bala comparison failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_chesta_bala_info():
    """Get information about Chesta Bala calculations based on classical Vedic texts."""
    return {
        "name": "Cheṣṭā Bala (Directional Strength)",
        "description": "Cheṣṭā Bala measures the directional strength of planets based on their apparent motion according to classical Vedic astrology",
        "calculation_method": "Based on classical motion states and ṣaṣṭyāṁśa values from Vedic texts",
        "motion_states": {
            "Vakra": {
                "sanskrit": "वक्र",
                "description": "Retrógrado",
                "chesta_bala": 60,
                "english": "Retrograde"
            },
            "Anuvakra": {
                "sanskrit": "अनुवक्र",
                "description": "Directo después de retrógrado",
                "chesta_bala": 30,
                "english": "Direct after retrograde"
            },
            "Manda": {
                "sanskrit": "मन्द",
                "description": "Directo pero lento",
                "chesta_bala": 15,
                "english": "Direct but slow"
            },
            "Mandatara": {
                "sanskrit": "मन्दतर",
                "description": "Más lento que lo normal",
                "chesta_bala": 7.5,
                "english": "Slower than normal"
            },
            "Sama": {
                "sanskrit": "सम",
                "description": "Movimiento medio, regular",
                "chesta_bala": 30,
                "english": "Medium, regular motion"
            },
            "Chara": {
                "sanskrit": "चर",
                "description": "Movimiento rápido",
                "chesta_bala": 30,
                "english": "Fast motion"
            },
            "Atichara": {
                "sanskrit": "अतिचर",
                "description": "Muy rápido",
                "chesta_bala": 45,
                "english": "Very fast"
            },
            "Kutilaka": {
                "sanskrit": "कुटिलक",
                "description": "Movimiento estacionario/curvo",
                "chesta_bala": 15,
                "english": "Stationary/curved motion"
            },
            "Vakragati": {
                "sanskrit": "वक्रगति",
                "description": "Retrógrado extremo o giro forzado",
                "chesta_bala": 60,
                "english": "Extreme retrograde"
            }
        },
        "scoring_system": {
            "5": "Excelente (45-60 ṣaṣṭyāṁśa)",
            "4": "Buena (30-44 ṣaṣṭyāṁśa)",
            "3": "Promedio (15-29 ṣaṣṭyāṁśa)",
            "2": "Débil (7.5-14 ṣaṣṭyāṁśa)",
            "1": "Muy Débil (0-7 ṣaṣṭyāṁśa)"
        },
        "planets_supported": [
            "Sun", "Moon", "Mercury", "Venus", "Mars", 
            "Jupiter", "Saturn", "Rahu", "Ketu"
        ],
        "ayanamsa": "True Citra Paksha",
        "data_source": "Swiss Ephemeris with classical Vedic calculations",
        "classical_reference": "Based on Ṣaṣṭyāṁśa system from classical Vedic texts",
        "endpoints": {
            "/calculate": "Calculate Chesta Bala for all planets",
            "/planets": "Calculate Chesta Bala for specific planet",
            "/summary": "Get summary analysis with classical notes",
            "/comparison": "Compare Chesta Bala between dates"
        }
    }
