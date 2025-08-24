# 🌟 Jyotiṣa API - Endpoints Completos

## 📍 **URL Base de la API**
```
https://jyotish-api-ndcfqrjivq-uc.a.run.app
```

## 🔑 **Configuración de Autenticación**
```javascript
// Headers requeridos para todas las peticiones
const headers = {
  'X-API-Key': 'tu_api_key_aqui',
  'Content-Type': 'application/json',
  'Accept': 'application/json'
};
```

---

## 🏥 **Endpoints de Salud y Información**

### 1. **Health Check**
```http
GET /health/healthz
```
**Respuesta:**
```json
{
  "status": "ok"
}
```

### 2. **Readiness Check**
```http
GET /health/readyz
```
**Respuesta:**
```json
{
  "status": "ready",
  "swiss_ephemeris": "initialized",
  "timestamp": "2025-01-19T10:30:00Z"
}
```

### 3. **Información de la API**
```http
GET /info
```
**Respuesta:**
```json
{
  "name": "Jyotiṣa API",
  "version": "0.2.0",
  "description": "Vedic astrology API with Swiss Ephemeris",
  "ayanamsa": {
    "type": "True Citra Paksha",
    "description": "All calculations use True Citra Paksha ayanamsa",
    "current_value_2024": "24°11'14\"",
    "swiss_ephemeris_mode": "SIDM_TRUE_CITRA"
  },
  "features": [
    "Precise panchanga calculations",
    "Accurate sunrise/sunset times",
    "Planetary positions in nakshatras",
    "High-precision astronomical calculations"
  ],
  "cors": {
    "enabled": true,
    "origins_count": 12,
    "credentials_allowed": true,
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
  }
}
```

### 4. **Documentación Swagger**
```http
GET /docs
```

### 5. **Documentación ReDoc**
```http
GET /redoc
```

---

## 🌙 **Endpoints de Panchanga Precisa**

### 6. **Panchanga Diario**
```http
GET /v1/panchanga/precise/daily
```
**Parámetros:**
- `date` (string, requerido): Fecha en formato YYYY-MM-DD
- `latitude` (float, requerido): Latitud en grados decimales
- `longitude` (float, requerido): Longitud en grados decimales
- `altitude` (float, opcional): Altitud en metros (default: 0.0)
- `reference_time` (string, opcional): "sunrise", "sunset", "noon", "midnight" (default: "sunrise")

**Ejemplo:**
```http
GET /v1/panchanga/precise/daily?date=2024-12-19&latitude=43.2965&longitude=5.3698&reference_time=sunrise
```

**Respuesta:**
```json
{
  "date": "2024-12-19",
  "reference_time": "08:05:56",
  "sunrise_time": "05:00:00",
  "sunset_time": "17:00:00",
  "panchanga": {
    "tithi": {
      "number": 4,
      "paksha": "Krishna",
      "display": "K4",
      "name": "Chaturthi",
      "elongation": 234.5,
      "percentage_remaining": 45.2
    },
    "vara": {
      "number": 4,
      "name": "Thursday",
      "ruler": "Jupiter"
    },
    "nakshatra": {
      "number": 12,
      "name": "Uttara Phalguni",
      "ruler": "Sun",
      "percentage_remaining": 67.8
    },
    "yoga": {
      "number": 15,
      "name": "Siddha",
      "percentage_remaining": 23.4
    },
    "karana": {
      "number": 7,
      "name": "Bava",
      "percentage_remaining": 89.1
    }
  }
}
```

### 7. **Información de Ayanamsa**
```http
GET /v1/panchanga/precise/ayanamsa
```
**Parámetros:**
- `date` (string, requerido): Fecha en formato YYYY-MM-DD
- `time` (string, opcional): Hora en formato HH:MM:SS (default: "12:00:00")

**Ejemplo:**
```http
GET /v1/panchanga/precise/ayanamsa?date=2024-12-19&time=12:00:00
```

---

## 🌟 **Endpoints de Efemérides**

### 8. **Efemérides Generales**
```http
GET /v1/ephemeris/
```
**Parámetros:**
- `when_utc` (string, opcional): Timestamp ISO-8601 en UTC
- `when_local` (string, opcional): Timestamp ISO-8601 sin timezone
- `place_id` (string, opcional): Google Place ID para conversión de tiempo local
- `planets` (string, opcional): Lista de planetas separados por coma (default: "Sun,Moon,Mercury,Venus,Mars,Jupiter,Saturn,Rahu,Ketu")

**Ejemplo:**
```http
GET /v1/ephemeris/?when_utc=2024-12-19T12:00:00Z&planets=Sun,Moon,Mercury
```

### 9. **Posiciones Planetarias**
```http
GET /v1/ephemeris/planets
```
**Parámetros:**
- `when_utc` (string, opcional): Timestamp ISO-8601 en UTC
- `planets` (string, opcional): Lista de planetas separados por coma

**Ejemplo:**
```http
GET /v1/ephemeris/planets?when_utc=2024-12-19T12:00:00Z&planets=Sun,Moon,Mercury,Venus,Mars
```

**Respuesta:**
```json
{
  "timestamp": "2024-12-19T12:00:00Z",
  "planets": {
    "Sun": {
      "longitude": 267.123,
      "latitude": 0.0,
      "distance": 0.983,
      "rasi": {
        "name": "Sagittarius",
        "number": 9
      },
      "nakshatra": {
        "name": "Purva Ashadha",
        "number": 20,
        "pada": 3
      }
    },
    "Moon": {
      "longitude": 45.678,
      "latitude": 2.345,
      "distance": 60.123,
      "rasi": {
        "name": "Taurus",
        "number": 2
      },
      "nakshatra": {
        "name": "Rohini",
        "number": 4,
        "pada": 2
      }
    }
  },
  "precision": "high"
}
```

### 10. **Estadísticas de Cache**
```http
GET /v1/ephemeris/cache-stats
```

---

## 📅 **Endpoints de Calendario**

### 11. **Calendario Mensual**
```http
GET /v1/calendar/month
```
**Parámetros:**
- `year` (int, requerido): Año
- `month` (int, requerido): Mes (1-12)
- `place_id` (string, requerido): Google Place ID
- `anchor` (string, opcional): "sunrise", "midnight", "noon", "custom" (default: "sunrise")
- `custom_time` (string, opcional): Hora personalizada en formato HH:MM
- `format` (string, opcional): "compact" o "detailed" (default: "compact")
- `planets` (string, opcional): Lista de planetas separados por coma
- `units` (string, opcional): "decimal", "dms", o "both" (default: "both")

**Ejemplo:**
```http
GET /v1/calendar/month?year=2024&month=12&place_id=ChIJN1t_tDeuEmsRUsoyG83frY4&anchor=sunrise&planets=Sun,Moon,Mercury,Venus,Mars
```

---

## 🧘 **Endpoints de Yogas**

### 12. **Detección de Yogas**
```http
GET /v1/panchanga/yogas/detect
```
**Parámetros:**
- `date` (string, requerido): Fecha en formato YYYY-MM-DD
- `latitude` (float, requerido): Latitud en grados decimales
- `longitude` (float, requerido): Longitud en grados decimales
- `altitude` (float, opcional): Altitud en metros (default: 0.0)

**Ejemplo:**
```http
GET /v1/panchanga/yogas/detect?date=2024-12-19&latitude=43.2965&longitude=5.3698
```

**Respuesta:**
```json
{
  "date": "2024-12-19",
  "location": {
    "latitude": 43.2965,
    "longitude": 5.3698
  },
  "panchanga": {
    "vara": "Thursday",
    "tithi": {
      "tithi_number": 5,
      "tithi_name": "Panchami",
      "paksha": "Krishna",
      "paksha_short": "K",
      "display": "K5"
    },
    "nakshatra": {
      "nakshatra_number": 12,
      "nakshatra_name": "Uttara Phalguni",
      "ruler": "Sun"
    }
  },
  "yogas": [
    {
      "name": "Guru Pushya",
      "name_sanskrit": "गुरु पुष्य",
      "type": "beneficial",
      "description": "Jupiter in Pushya nakshatra",
      "priority": 1,
      "color": "green"
    }
  ]
}
```

---

## 🌊 **Endpoints de Movimiento Planetario**

### 13. **Estados de Movimiento**
```http
GET /v1/motion/states
```
**Parámetros:**
- `start` (string, requerido): Tiempo de inicio en formato ISO-8601
- `end` (string, requerido): Tiempo de fin en formato ISO-8601
- `tzname` (string, opcional): Nombre de timezone (default: "UTC")
- `step_minutes` (int, opcional): Intervalo de paso en minutos (default: 60)
- `mode` (string, opcional): "classic" o "adaptive" (default: "classic")
- `planets` (string, opcional): Lista de planetas separados por coma (default: "Mars,Venus")

**Ejemplo:**
```http
GET /v1/motion/states?start=2024-12-19T00:00:00&end=2024-12-20T00:00:00&planets=Sun,Moon&step_minutes=60
```

### 14. **Velocidades Planetarias**
```http
GET /v1/motion/speeds
```
**Parámetros:**
- `start` (string, requerido): Fecha de inicio en formato YYYY-MM-DD
- `end` (string, requerido): Fecha de fin en formato YYYY-MM-DD
- `place_id` (string, requerido): Google Place ID
- `planets` (string, opcional): Lista de planetas separados por coma

**Ejemplo:**
```http
GET /v1/motion/speeds?start=2024-12-19&end=2024-12-20&place_id=ChIJN1t_tDeuEmsRUsoyG83frY4&planets=Sun,Moon,Mercury,Venus,Mars
```

---

## 📊 **Endpoints de Métricas y Monitoreo**

### 15. **Métricas de la Aplicación**
```http
GET /metrics
```

### 16. **Estado del Circuit Breaker**
```http
GET /circuit-breaker/status
```

---

## 🔧 **Configuración para Frontend**

### **Variables de Entorno (Frontend)**
```javascript
// src/.env.local
NEXT_PUBLIC_API_URL=https://jyotish-api-ndcfqrjivq-uc.a.run.app
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=AIzaSyCI239BEMuN0jk49prWfDngFwpe4pYcvAg
```

### **Configuración de API Client**
```javascript
// src/lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://jyotish-api-ndcfqrjivq-uc.a.run.app';

const API_ENDPOINTS = {
  health: '/health/healthz',
  info: '/info',
  panchanga: {
    daily: '/v1/panchanga/precise/daily',
    ayanamsa: '/v1/panchanga/precise/ayanamsa'
  },
  ephemeris: {
    general: '/v1/ephemeris/',
    planets: '/v1/ephemeris/planets',
    cacheStats: '/v1/ephemeris/cache-stats'
  },
  calendar: {
    month: '/v1/calendar/month'
  },
  yogas: {
    detect: '/v1/panchanga/yogas/detect'
  },
  motion: {
    states: '/v1/motion/states',
    speeds: '/v1/motion/speeds'
  }
};

// Función para hacer peticiones a la API
async function apiRequest(endpoint, params = {}) {
  const url = new URL(`${API_BASE_URL}${endpoint}`);
  
  // Agregar parámetros de query
  Object.keys(params).forEach(key => {
    if (params[key] !== undefined && params[key] !== null) {
      url.searchParams.append(key, params[key]);
    }
  });
  
  const response = await fetch(url, {
    headers: {
      'X-API-Key': process.env.NEXT_PUBLIC_API_KEY || 'your_api_key',
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
}
```

### **Ejemplos de Uso en React/Next.js**
```javascript
// Hook para obtener panchanga diario
export function useDailyPanchanga(date, latitude, longitude) {
  return useQuery({
    queryKey: ['panchanga', date, latitude, longitude],
    queryFn: () => apiRequest(API_ENDPOINTS.panchanga.daily, {
      date,
      latitude,
      longitude,
      reference_time: 'sunrise'
    }),
    enabled: !!(date && latitude && longitude)
  });
}

// Hook para obtener yogas
export function useYogas(date, latitude, longitude) {
  return useQuery({
    queryKey: ['yogas', date, latitude, longitude],
    queryFn: () => apiRequest(API_ENDPOINTS.yogas.detect, {
      date,
      latitude,
      longitude
    }),
    enabled: !!(date && latitude && longitude)
  });
}

// Hook para obtener posiciones planetarias
export function usePlanetPositions(timestamp, planets = 'Sun,Moon,Mercury,Venus,Mars') {
  return useQuery({
    queryKey: ['planets', timestamp, planets],
    queryFn: () => apiRequest(API_ENDPOINTS.ephemeris.planets, {
      when_utc: timestamp,
      planets
    }),
    enabled: !!timestamp
  });
}
```

---

## 🌐 **Configuración de CORS**

### **Headers de CORS Configurados:**
- ✅ `Access-Control-Allow-Origin`: Configurado para múltiples dominios
- ✅ `Access-Control-Allow-Methods`: GET, POST, PUT, DELETE, OPTIONS, PATCH
- ✅ `Access-Control-Allow-Headers`: Headers completos incluidos
- ✅ `Access-Control-Allow-Credentials`: true
- ✅ `Access-Control-Max-Age`: 86400 segundos

### **Dominios Permitidos:**
- `http://localhost:3000` (desarrollo)
- `https://localhost:3000` (desarrollo HTTPS)
- `https://jyotish-api-ndcfqrjivq-uc.a.run.app` (API)
- `https://jyotish-frontend-ndcfqrjivq-uc.a.run.app` (Frontend)
- `https://*.vercel.app` (Vercel)
- `https://*.netlify.app` (Netlify)
- `https://*.run.app` (Cloud Run)

---

## 📝 **Notas Importantes**

### **Formato de Fechas:**
- **YYYY-MM-DD**: Para fechas (ej: "2024-12-19")
- **ISO-8601**: Para timestamps (ej: "2024-12-19T12:00:00Z")
- **HH:MM:SS**: Para horas (ej: "12:00:00")

### **Coordenadas:**
- **Latitud**: -90 a +90 grados decimales
- **Longitud**: -180 a +180 grados decimales
- **Altitud**: En metros sobre el nivel del mar

### **Planetas Soportados:**
- `Sun`, `Moon`, `Mercury`, `Venus`, `Mars`, `Jupiter`, `Saturn`, `Rahu`, `Ketu`

### **Ayanamsa:**
- **Tipo**: True Citra Paksha
- **Valor 2024**: 24°11'14"
- **Modo Swiss Ephemeris**: SIDM_TRUE_CITRA

---

## 🚀 **URLs de Despliegue**

### **API (Backend):**
```
https://jyotish-api-ndcfqrjivq-uc.a.run.app
```

### **Frontend (Next.js):**
```
https://jyotish-frontend-ndcfqrjivq-uc.a.run.app
```

### **Documentación:**
```
https://jyotish-api-ndcfqrjivq-uc.a.run.app/docs
https://jyotish-api-ndcfqrjivq-uc.a.run.app/redoc
```

---

**📅 Fecha de Actualización**: 2025-01-19  
**🔧 Versión API**: 0.2.0  
**✅ Estado**: Todos los endpoints funcionando y verificados
