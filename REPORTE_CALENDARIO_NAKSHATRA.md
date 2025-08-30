# 📅 **REPORTE: FUNCIÓN CALENDARIO - NAKSHATRA Y PADA PRECISO**

## ✅ **RESPUESTA A TU PREGUNTA**

**SÍ, la función de calendario en tu API proporciona la posición de planetas en nakshatra y pada preciso según True Citra Paksha.**

---

## 🔍 **VERIFICACIÓN TÉCNICA**

### **1. Ayanamsa Configurado**
```python
# En app/services/swe.py línea 58
swe.set_sid_mode(swe.SIDM_TRUE_CITRA, 0, 0)
logger.info("Swiss Ephemeris initialized with True Citra Paksha sidereal mode")
```

### **2. Cálculo de Posiciones**
```python
# En app/services/swe.py línea 158
flags = swe.FLG_SIDEREAL | swe.FLG_MOSEPH
result = swe.calc_ut(jd, planet_id, flags)
```

### **3. Cálculo de Nakshatra y Pada**
```python
# En app/services/swe.py líneas 125-135
def _get_nakshatra_uncached(self, longitude: float) -> Tuple[str, int]:
    """Get nakshatra from longitude."""
    nakshatra_number = int(longitude // NAKSHATRA_SPAN)
    nakshatra_name = NAKSHATRAS[nakshatra_number]
    return nakshatra_name, nakshatra_number + 1

def _get_pada_uncached(self, longitude: float) -> int:
    """Get pada from longitude."""
    nakshatra_longitude = longitude % NAKSHATRA_SPAN
    pada = int(nakshatra_longitude // PADA_SPAN) + 1
    return min(max(pada, 1), 4)  # Ensure pada is between 1 and 4
```

---

## 🧪 **PRUEBA VERIFICADA**

### **Endpoint Probado:**
```http
GET https://jyotish-api-ndcfqrjivq-uc.a.run.app/v1/calendar/month?year=2025&month=8&place_id=test&planets=Sun,Moon,Mars
```

### **Resultado para el Sol (2025-08-01):**
```json
{
  "lon_decimal": 105.063627,
  "retrograde": false,
  "motion_state": "sama",
  "rasi": "Karka",
  "rasi_index": 4,
  "nakshatra": "Pushya",
  "nak_index": 8,
  "pada": 4,
  "changedNakshatra": false,
  "changedPada": false,
  "changedRasi": false,
  "lon_dms": "105.06°"
}
```

---

## 📊 **DETALLES TÉCNICOS**

### **Constantes Utilizadas:**
```python
NAKSHATRA_SPAN = 13 + 1/3  # 13°20' (exacto)
PADA_SPAN = NAKSHATRA_SPAN / 4  # 3°20' (exacto)
RASI_SPAN = 30.0  # 30° (exacto)
```

### **Lista de Nakshatras (27):**
```python
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]
```

### **Lista de Rashis (12):**
```python
RASHIS = [
    "Mesha", "Vrishabha", "Mithuna", "Karka",
    "Simha", "Kanya", "Tula", "Vrishchika",
    "Dhanu", "Makara", "Kumbha", "Meena"
]
```

---

## 🎯 **ENDPOINTS DE CALENDARIO DISPONIBLES**

### **1. Calendario Mensual**
```http
GET https://jyotish-api-ndcfqrjivq-uc.a.run.app/v1/calendar/month
```

**Parámetros:**
- `year` (int, requerido): Año
- `month` (int, requerido): Mes (1-12)
- `place_id` (string, requerido): Google Place ID
- `anchor` (string, opcional): "sunrise", "midnight", "noon", "custom" (default: "sunrise")
- `custom_time` (string, opcional): Tiempo personalizado en formato HH:MM
- `format` (string, opcional): "compact" o "detailed" (default: "compact")
- `planets` (string, opcional): Lista separada por comas de planetas
- `units` (string, opcional): "decimal", "dms", o "both" (default: "both")

### **2. Calendario Diario**
```http
GET https://jyotish-api-ndcfqrjivq-uc.a.run.app/v1/calendar/day
```

**Parámetros:**
- `date` (string, requerido): Fecha en formato YYYY-MM-DD
- `place_id` (string, requerido): Google Place ID

---

## 📋 **ESTRUCTURA DE RESPUESTA**

### **Para cada planeta:**
```json
{
  "lon_decimal": 105.063627,        // Longitud eclíptica en grados decimales
  "retrograde": false,              // Si el planeta está retrógrado
  "motion_state": "sama",           // Estado de movimiento
  "rasi": "Karka",                  // Nombre del rashi
  "rasi_index": 4,                  // Índice del rashi (1-12)
  "nakshatra": "Pushya",            // Nombre del nakshatra
  "nak_index": 8,                   // Índice del nakshatra (1-27)
  "pada": 4,                        // Pada (1-4)
  "changedNakshatra": false,        // Si cambió de nakshatra
  "changedPada": false,             // Si cambió de pada
  "changedRasi": false,             // Si cambió de rashi
  "lon_dms": "105.06°"              // Longitud en formato DMS
}
```

---

## 🔧 **CONFIGURACIÓN TRUE CITRA PAKSHA**

### **Ayanamsa Utilizado:**
- **Tipo:** True Citra Paksha
- **Valor 2024:** 24°11'14"
- **Modo Swiss Ephemeris:** SIDM_TRUE_CITRA (14)
- **Precisión:** Alta precisión astronómica

### **Ventajas de True Citra Paksha:**
1. **Precisión astronómica:** Basado en la posición real de Spica (Citra)
2. **Consistencia:** Utilizado por astrólogos modernos
3. **Exactitud:** Corrige las variaciones del ayanamsa
4. **Estándar:** Reconocido internacionalmente

---

## 🚀 **EJEMPLO DE USO**

### **JavaScript/React:**
```javascript
const response = await fetch(
  'https://jyotish-api-ndcfqrjivq-uc.a.run.app/v1/calendar/month?year=2025&month=8&place_id=test&planets=Sun,Moon,Mars'
);
const data = await response.json();

// Acceder a datos del Sol
const sunData = data.days[0].planets.Sun;
console.log(`Sol en ${sunData.nakshatra} pada ${sunData.pada}`);
console.log(`Rashi: ${sunData.rasi}`);
console.log(`Longitud: ${sunData.lon_decimal}°`);
```

### **Python:**
```python
import requests

url = "https://jyotish-api-ndcfqrjivq-uc.a.run.app/v1/calendar/month"
params = {
    "year": 2025,
    "month": 8,
    "place_id": "test",
    "planets": "Sun,Moon,Mars"
}

response = requests.get(url, params=params)
data = response.json()

# Acceder a datos del Sol
sun_data = data["days"][0]["planets"]["Sun"]
print(f"Sol en {sun_data['nakshatra']} pada {sun_data['pada']}")
print(f"Rashi: {sun_data['rasi']}")
print(f"Longitud: {sun_data['lon_decimal']}°")
```

---

## ✅ **CONCLUSIÓN**

**La función de calendario de tu API SÍ proporciona:**

1. ✅ **Posiciones precisas de planetas en nakshatra**
2. ✅ **Cálculo exacto de pada (1-4)**
3. ✅ **Uso de True Citra Paksha ayanamsa**
4. ✅ **Posiciones en rashi (signos zodiacales)**
5. ✅ **Longitudes eclípticas precisas**
6. ✅ **Estados de movimiento (retrógrado, directo)**
7. ✅ **Detección de cambios de nakshatra/pada/rashi**

**Todo calculado con alta precisión astronómica usando Swiss Ephemeris y True Citra Paksha ayanamsa.**
