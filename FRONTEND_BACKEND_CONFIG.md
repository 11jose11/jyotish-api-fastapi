# 🌟 Configuración Completa Frontend + Backend - Jyotiṣa API

## 🚀 **URLs Principales**

### **API (Backend) - FastAPI**
```
🌐 https://jyotish-api-ndcfqrjivq-uc.a.run.app
```

### **Frontend (Next.js) - Desplegado**
```
🌐 https://jyotish-frontend-ndcfqrjivq-uc.a.run.app
```

### **Documentación Interactiva**
```
📚 https://jyotish-api-ndcfqrjivq-uc.a.run.app/docs
📖 https://jyotish-api-ndcfqrjivq-uc.a.run.app/redoc
```

---

## 🔧 **Configuración del Frontend**

### **1. Variables de Entorno (src/.env.local)**
```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://jyotish-api-ndcfqrjivq-uc.a.run.app

# Google Maps API (Required for location search)
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=AIzaSyCI239BEMuN0jk49prWfDngFwpe4pYcvAg

# Development Configuration
NODE_ENV=development
```

### **2. Configuración de API Client (src/lib/api.ts)**
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://jyotish-api-ndcfqrjivq-uc.a.run.app';

export const API_ENDPOINTS = {
  // Health & Info
  health: '/health/healthz',
  info: '/info',
  
  // Panchanga
  panchanga: {
    daily: '/v1/panchanga/precise/daily',
    ayanamsa: '/v1/panchanga/precise/ayanamsa'
  },
  
  // Ephemeris
  ephemeris: {
    general: '/v1/ephemeris/',
    planets: '/v1/ephemeris/planets',
    cacheStats: '/v1/ephemeris/cache-stats'
  },
  
  // Calendar
  calendar: {
    month: '/v1/calendar/month'
  },
  
  // Yogas
  yogas: {
    detect: '/v1/panchanga/yogas/detect'
  },
  
  // Motion
  motion: {
    states: '/v1/motion/states',
    speeds: '/v1/motion/speeds'
  }
};

// Función para hacer peticiones a la API
export async function apiRequest(endpoint: string, params: Record<string, any> = {}) {
  const url = new URL(`${API_BASE_URL}${endpoint}`);
  
  // Agregar parámetros de query
  Object.keys(params).forEach(key => {
    if (params[key] !== undefined && params[key] !== null) {
      url.searchParams.append(key, params[key]);
    }
  });
  
  const response = await fetch(url, {
    headers: {
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

### **3. Hooks de React Query (src/hooks/use-calendar.ts)**
```typescript
import { useQuery } from '@tanstack/react-query';
import { apiRequest, API_ENDPOINTS } from '../lib/api';

// Hook para obtener panchanga diario
export function useDailyPanchanga(date: string, latitude: number, longitude: number) {
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
export function useYogas(date: string, latitude: number, longitude: number) {
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
export function usePlanetPositions(timestamp: string, planets: string = 'Sun,Moon,Mercury,Venus,Mars') {
  return useQuery({
    queryKey: ['planets', timestamp, planets],
    queryFn: () => apiRequest(API_ENDPOINTS.ephemeris.planets, {
      when_utc: timestamp,
      planets
    }),
    enabled: !!timestamp
  });
}

// Hook para obtener calendario mensual
export function useMonthlyCalendar(year: number, month: number, placeId: string) {
  return useQuery({
    queryKey: ['calendar', year, month, placeId],
    queryFn: () => apiRequest(API_ENDPOINTS.calendar.month, {
      year,
      month,
      place_id: placeId,
      anchor: 'sunrise',
      planets: 'Sun,Moon,Mercury,Venus,Mars,Jupiter,Saturn,Rahu,Ketu'
    }),
    enabled: !!(year && month && placeId)
  });
}

// Hook para obtener velocidades planetarias
export function usePlanetSpeeds(startDate: string, endDate: string, placeId: string) {
  return useQuery({
    queryKey: ['speeds', startDate, endDate, placeId],
    queryFn: () => apiRequest(API_ENDPOINTS.motion.speeds, {
      start: startDate,
      end: endDate,
      place_id: placeId,
      planets: 'Sun,Moon,Mercury,Venus,Mars,Jupiter,Saturn,Rahu,Ketu'
    }),
    enabled: !!(startDate && endDate && placeId)
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

## 📋 **Endpoints Principales Verificados**

### **🏥 Salud y Información**
```http
GET /health/healthz          ✅ Funcionando
GET /info                    ✅ Funcionando
GET /docs                    ✅ Funcionando
```

### **🌙 Panchanga Precisa**
```http
GET /v1/panchanga/precise/daily     ✅ Funcionando
GET /v1/panchanga/precise/ayanamsa  ✅ Funcionando
```

### **🌟 Efemérides**
```http
GET /v1/ephemeris/planets    ✅ Funcionando
GET /v1/ephemeris/           ✅ Funcionando
```

### **🧘 Yogas**
```http
GET /v1/panchanga/yogas/detect  ✅ Funcionando
```

### **📅 Calendario**
```http
GET /v1/calendar/month       ✅ Funcionando
```

### **🌊 Movimiento Planetario**
```http
GET /v1/motion/states        ✅ Funcionando
GET /v1/motion/speeds        ✅ Funcionando
```

---

## 🎯 **Ejemplos de Uso en Componentes React**

### **Componente de Panchanga Diario**
```tsx
import { useDailyPanchanga } from '../hooks/use-calendar';

export function DailyPanchanga({ date, latitude, longitude }: {
  date: string;
  latitude: number;
  longitude: number;
}) {
  const { data, isLoading, error } = useDailyPanchanga(date, latitude, longitude);
  
  if (isLoading) return <div>Cargando panchanga...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return (
    <div>
      <h2>Panchanga para {data.date}</h2>
      <div>
        <p>Tithi: {data.panchanga.tithi.name} ({data.panchanga.tithi.display})</p>
        <p>Vara: {data.panchanga.vara.name}</p>
        <p>Nakshatra: {data.panchanga.nakshatra.name}</p>
        <p>Yoga: {data.panchanga.yoga.name}</p>
        <p>Karana: {data.panchanga.karana.name}</p>
      </div>
    </div>
  );
}
```

### **Componente de Yogas**
```tsx
import { useYogas } from '../hooks/use-calendar';

export function YogasList({ date, latitude, longitude }: {
  date: string;
  latitude: number;
  longitude: number;
}) {
  const { data, isLoading, error } = useYogas(date, latitude, longitude);
  
  if (isLoading) return <div>Cargando yogas...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return (
    <div>
      <h2>Yogas para {data.date}</h2>
      {data.yogas.length > 0 ? (
        <ul>
          {data.yogas.map((yoga, index) => (
            <li key={index} style={{ color: yoga.color }}>
              {yoga.name} ({yoga.name_sanskrit}) - {yoga.description}
            </li>
          ))}
        </ul>
      ) : (
        <p>No se detectaron yogas especiales para esta fecha.</p>
      )}
    </div>
  );
}
```

### **Componente de Posiciones Planetarias**
```tsx
import { usePlanetPositions } from '../hooks/use-calendar';

export function PlanetPositions({ timestamp, planets }: {
  timestamp: string;
  planets?: string;
}) {
  const { data, isLoading, error } = usePlanetPositions(timestamp, planets);
  
  if (isLoading) return <div>Cargando posiciones planetarias...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return (
    <div>
      <h2>Posiciones Planetarias</h2>
      <p>Timestamp: {data.timestamp}</p>
      {Object.entries(data.planets).map(([planet, info]: [string, any]) => (
        <div key={planet}>
          <h3>{planet}</h3>
          <p>Rashi: {info.rasi.name} ({info.rasi.number})</p>
          <p>Nakshatra: {info.nakshatra.name} (Pada {info.nakshatra.pada})</p>
          <p>Longitud: {info.longitude.toFixed(2)}°</p>
        </div>
      ))}
    </div>
  );
}
```

---

## 🔑 **Configuración de Google Maps API**

### **Clave de API Configurada:**
```
AIzaSyCI239BEMuN0jk49prWfDngFwpe4pYcvAg
```

### **APIs Habilitadas:**
- ✅ Places API
- ✅ Geocoding API
- ✅ Maps JavaScript API

### **Uso en el Frontend:**
```typescript
// src/lib/places.ts
export async function searchPlaces(query: string) {
  const response = await fetch(
    `https://maps.googleapis.com/maps/api/place/textsearch/json?query=${encodeURIComponent(query)}&key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}`
  );
  
  if (!response.ok) {
    throw new Error('Error searching places');
  }
  
  return response.json();
}

export async function getPlaceDetails(placeId: string) {
  const response = await fetch(
    `https://maps.googleapis.com/maps/api/place/details/json?place_id=${placeId}&fields=geometry,formatted_address&key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}`
  );
  
  if (!response.ok) {
    throw new Error('Error getting place details');
  }
  
  return response.json();
}
```

---

## 🚀 **Scripts de Despliegue**

### **Despliegue Completo (API + Frontend)**
```bash
./deploy-full.sh
```

### **Verificación de Despliegue**
```bash
./verify-deployment.sh
```

### **Configuración de Entorno**
```bash
./setup-environment.sh
```

---

## 📊 **Monitoreo y Métricas**

### **Endpoints de Monitoreo:**
```http
GET /metrics                    # Métricas de la aplicación
GET /circuit-breaker/status     # Estado del circuit breaker
GET /health/readyz              # Verificación de readiness
```

### **Headers de Respuesta:**
- `X-API-Version`: 0.2.0
- `X-Response-Time`: Tiempo de procesamiento
- `X-Request-Id`: ID único de la petición

---

## ✅ **Estado de Verificación**

### **✅ API Backend:**
- ✅ Desplegado en Google Cloud Run
- ✅ CORS configurado correctamente
- ✅ Todos los endpoints funcionando
- ✅ Autenticación configurada
- ✅ Logging y monitoreo activo

### **✅ Frontend:**
- ✅ Configuración de Next.js completa
- ✅ Variables de entorno configuradas
- ✅ Hooks de React Query implementados
- ✅ Google Maps API configurada
- ✅ CORS compatible

### **✅ Integración:**
- ✅ Comunicación API-Frontend funcionando
- ✅ Headers de seguridad implementados
- ✅ Manejo de errores configurado
- ✅ Cache y optimización activos

---

## 🎯 **Próximos Pasos**

1. **✅ Configuración completada**
2. **✅ Endpoints verificados**
3. **✅ CORS optimizado**
4. **🔄 Probar integración completa**
5. **🔄 Monitorear en producción**
6. **🔄 Optimizar performance**

---

**📅 Fecha de Configuración**: 2025-01-19  
**🔧 Versión**: 0.2.0  
**✅ Estado**: Listo para producción
