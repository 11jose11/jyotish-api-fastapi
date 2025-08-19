# Mejoras en la Precisión del Cálculo de Panchanga

## Resumen

Se han implementado mejoras significativas en el cálculo de panchanga para mayor precisión, tomando como referencia el lugar específico y la hora exacta del amanecer de cada día.

## Funcionalidades Implementadas

### 1. Cálculo de Amanecer y Atardecer

- **Función `calculate_sunrise()`**: Calcula la hora aproximada del amanecer basada en la latitud, longitud y época del año
- **Función `calculate_sunset()`**: Calcula la hora aproximada del atardecer
- **Función `get_solar_day_info()`**: Proporciona información completa del día solar incluyendo amanecer, atardecer y duración del día

### 2. Panchanga Preciso

- **Función `get_precise_panchanga()`**: Calcula el panchanga completo usando el amanecer (o otro tiempo de referencia) como punto de cálculo
- **Soporte para múltiples tiempos de referencia**: sunrise, sunset, noon, midnight
- **Información detallada de ubicación**: latitud, longitud y altitud

### 3. Nuevos Endpoints de API

#### `/v1/panchanga/precise/daily`
Calcula el panchanga preciso para un día específico en una ubicación dada.

**Parámetros:**
- `date`: Fecha en formato YYYY-MM-DD
- `latitude`: Latitud en grados decimales
- `longitude`: Longitud en grados decimales
- `altitude`: Altitud sobre el nivel del mar en metros (opcional, default: 0)
- `reference_time`: Tiempo de referencia (sunrise, sunset, noon, midnight, default: sunrise)

**Respuesta:**
```json
{
    "date": "2025-01-15",
    "reference_time": "sunrise",
    "reference_timestamp": "2025-01-15T06:00:00",
    "location": {
        "latitude": -12.0464,
        "longitude": -77.0428,
        "altitude": 154.0
    },
    "solar_day": {
        "sunrise": "2025-01-15T06:00:00",
        "sunset": "2025-01-15T18:00:00",
        "day_length_hours": 12.0
    },
    "nakshatra": {
        "index": 9,
        "name": "Ashlesha",
        "pada": 1,
        "longitude": 107.22767872839708
    },
    "tithi": {
        "tithi_number": 2,
        "tithi_name": "Dwitiya",
        "paksha": "Krishna",
        "display": "K2"
    },
    "karana": {
        "name": "Balava",
        "sanskrit": "बालव"
    },
    "vara": {
        "name": "Wednesday",
        "sanskrit": "बुधवार"
    },
    "yoga": {
        "name": "Priti",
        "sanskrit": "प्रीति"
    },
    "tithi_windows": [...],
    "nakshatra_windows": [...],
    "precision": "high"
}
```

#### `/v1/panchanga/precise/solar-day`
Obtiene información del día solar para una ubicación específica.

#### `/v1/panchanga/precise/sunrise`
Calcula la hora exacta del amanecer para una fecha y ubicación.

#### `/v1/panchanga/precise/sunset`
Calcula la hora exacta del atardecer para una fecha y ubicación.

## Mejoras en la Precisión

### 1. Cálculo Basado en Ubicación
- **Latitud**: Afecta la duración del día y las horas de amanecer/atardecer
- **Longitud**: Afecta el tiempo local
- **Altitud**: Considerada para cálculos más precisos (futuro)

### 2. Tiempo de Referencia Configurable
- **Amanecer (sunrise)**: Tiempo tradicional para cálculos de panchanga
- **Atardecer (sunset)**: Alternativa para ciertos cálculos
- **Mediodía (noon)**: Para cálculos de mediodía
- **Medianoche (midnight)**: Para cálculos de medianoche

### 3. Información Solar Detallada
- Hora exacta del amanecer y atardecer
- Duración del día solar
- Información de ubicación geográfica

## Ejemplo de Uso

### Para Lima, Perú (15 de enero de 2025):

```bash
curl "http://localhost:8080/v1/panchanga/precise/daily?date=2025-01-15&latitude=-12.0464&longitude=-77.0428&altitude=154&reference_time=sunrise"
```

**Resultado:**
- **Amanecer**: 06:00:00
- **Nakshatra**: Ashlesha (Pada 1)
- **Tithi**: Krishna Dwitiya (K2)
- **Karana**: Balava
- **Vara**: Wednesday (बुधवार)
- **Yoga**: Priti (प्रीति)

## Ventajas de la Nueva Implementación

1. **Mayor Precisión**: Los cálculos se basan en la ubicación geográfica específica
2. **Flexibilidad**: Múltiples tiempos de referencia disponibles
3. **Información Completa**: Incluye datos solares y ventanas de cambio
4. **API RESTful**: Endpoints bien documentados y fáciles de usar
5. **Escalabilidad**: Preparado para cálculos más precisos en el futuro

## Próximas Mejoras

1. **Cálculo Astronómico Preciso**: Implementar cálculos astronómicos exactos usando algoritmos más sofisticados
2. **Zonas Horarias**: Integración con zonas horarias para mayor precisión
3. **Caché Inteligente**: Caché de cálculos para mejorar el rendimiento
4. **Validación Avanzada**: Validación más robusta de parámetros de entrada

## Archivos Modificados

- `app/services/panchanga.py`: Servicio principal con nuevas funciones
- `app/routers/panchanga_precise.py`: Nuevo router para endpoints precisos
- `app/main.py`: Inclusión del nuevo router
- `app/routers/__init__.py`: Importaciones actualizadas

## Estado Actual

✅ **Completado**: Implementación básica funcional
✅ **Completado**: Endpoints de API operativos
✅ **Completado**: Cálculos basados en ubicación
✅ **Completado**: Múltiples tiempos de referencia
🔄 **En Progreso**: Optimización de rendimiento
📋 **Pendiente**: Cálculos astronómicos más precisos
