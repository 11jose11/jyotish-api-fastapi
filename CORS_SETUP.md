# 🌐 Configuración CORS Mejorada para FastAPI

## 📋 Resumen

Esta configuración CORS mejorada está diseñada específicamente para trabajar con tu frontend en Vercel (`https://jyotish-content-manager.vercel.app`) y proporciona:

- ✅ **Configuración robusta** para Google Cloud Run
- ✅ **Variables de entorno** flexibles
- ✅ **Manejo de errores** específico para CORS
- ✅ **Soporte completo** para preflight OPTIONS
- ✅ **Headers personalizados** según tus requerimientos

---

## 🔧 Configuración

### 1. Variables de Entorno

#### **Producción (Google Cloud Run)**
```bash
# Configuración principal
ENVIRONMENT=production
ALLOWED_ORIGIN=https://jyotish-content-manager.vercel.app

# Dominios adicionales (opcional)
ADDITIONAL_ORIGINS=https://staging-frontend.vercel.app,https://admin-frontend.vercel.app

# Otras configuraciones
GOOGLE_MAPS_API_KEY=your_api_key_here
```

#### **Desarrollo Local**
```bash
# Archivo .env
ENVIRONMENT=development
ALLOWED_ORIGIN=http://localhost:3000
ADDITIONAL_ORIGINS=http://localhost:3001,http://localhost:5173
```

### 2. Headers CORS Configurados

```python
# Headers permitidos
"Content-Type"
"Authorization" 
"x-client-info"
"apikey"
"X-API-Key"
"X-Requested-With"
"X-Request-Id"
"Origin"
"Access-Control-Request-Method"
"Access-Control-Request-Headers"

# Métodos permitidos
"GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"
```

---

## 🚀 Ejemplos de Uso

### 1. Frontend JavaScript (Vercel)

```javascript
// Ejemplo de fetch desde tu frontend de Vercel
const API_BASE = 'https://jyotish-api-ndcfqrjivq-uc.a.run.app';

// Función para hacer requests a la API
async function fetchFromAPI(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  
  const defaultOptions = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'x-client-info': 'jyotish-frontend-v1.0.0',
      // Agregar API key si es necesario
      // 'apikey': 'your-api-key-here'
    },
    credentials: 'include', // Para cookies si las usas
  };

  const finalOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers
    }
  };

  try {
    const response = await fetch(url, finalOptions);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

// Ejemplos de uso
async function getYogas() {
  return await fetchFromAPI('/v1/panchanga/yogas/detect?date=2025-01-15&latitude=43.2965&longitude=5.3698');
}

async function getPanchanga() {
  return await fetchFromAPI('/v1/panchanga/precise/daily?date=2025-01-15&latitude=43.2965&longitude=5.3698');
}

async function getChestaBala() {
  return await fetchFromAPI('/v1/chesta-bala/calculate?date=2025-01-15&latitude=43.2965&longitude=5.3698');
}

// POST request example
async function detectYogasPost(data) {
  return await fetchFromAPI('/v1/panchanga/yogas/detect', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}
```

### 2. React Hook Personalizado

```javascript
// hooks/useJyotishAPI.js
import { useState, useCallback } from 'react';

const API_BASE = 'https://jyotish-api-ndcfqrjivq-uc.a.run.app';

export function useJyotishAPI() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const apiRequest = useCallback(async (endpoint, options = {}) => {
    setLoading(true);
    setError(null);

    try {
      const url = `${API_BASE}${endpoint}`;
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          'x-client-info': 'jyotish-frontend-v1.0.0',
        },
        ...options
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    apiRequest
  };
}

// Uso en componentes
function YogasComponent() {
  const { loading, error, apiRequest } = useJyotishAPI();
  const [yogas, setYogas] = useState(null);

  const fetchYogas = async () => {
    try {
      const data = await apiRequest('/v1/panchanga/yogas/detect?date=2025-01-15&latitude=43.2965&longitude=5.3698');
      setYogas(data);
    } catch (err) {
      console.error('Failed to fetch yogas:', err);
    }
  };

  return (
    <div>
      <button onClick={fetchYogas} disabled={loading}>
        {loading ? 'Loading...' : 'Get Yogas'}
      </button>
      {error && <p>Error: {error}</p>}
      {yogas && <pre>{JSON.stringify(yogas, null, 2)}</pre>}
    </div>
  );
}
```

---

## 🧪 Testing

### 1. Endpoint de Prueba CORS

```bash
# Probar configuración CORS
curl -H "Origin: https://jyotish-content-manager.vercel.app" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://jyotish-api-ndcfqrjivq-uc.a.run.app/cors-test
```

### 2. Verificar Headers de Respuesta

```bash
# Verificar headers CORS en respuesta
curl -I -H "Origin: https://jyotish-content-manager.vercel.app" \
     https://jyotish-api-ndcfqrjivq-uc.a.run.app/health
```

### 3. Test desde Frontend

```javascript
// Test simple desde el navegador
fetch('https://jyotish-api-ndcfqrjivq-uc.a.run.app/cors-test', {
  headers: {
    'Content-Type': 'application/json',
    'x-client-info': 'test-frontend'
  }
})
.then(response => response.json())
.then(data => console.log('CORS Test:', data))
.catch(error => console.error('CORS Error:', error));
```

---

## 🔒 Manejo de Errores

### 1. Error de Origen No Permitido

Si un dominio no autorizado hace una petición, recibirás:

```json
{
  "error": true,
  "message": "CORS origin not allowed",
  "allowed_origins": ["<hidden>"],
  "requested_origin": "https://unauthorized-domain.com"
}
```

### 2. Logs de Error

Los errores CORS se registran en los logs:

```
WARNING: CORS origin not allowed: https://unauthorized-domain.com
```

---

## 📝 Agregar Nuevos Dominios

### 1. Para un Dominio Adicional

```bash
# En Google Cloud Run
ADDITIONAL_ORIGINS=https://new-frontend.vercel.app,https://admin-panel.vercel.app
```

### 2. Para Múltiples Dominios

```bash
# Separar por comas
ADDITIONAL_ORIGINS=https://frontend1.vercel.app,https://frontend2.vercel.app,https://staging.vercel.app
```

### 3. En el Código (si necesitas lógica más compleja)

```python
# En app/config.py, modificar el método cors_origins
@property
def cors_origins(self) -> List[str]:
    origins = [
        self.allowed_origin,
        "https://jyotish-api-ndcfqrjivq-uc.a.run.app",
    ]
    
    # Agregar dominios adicionales
    if self.additional_origins:
        additional = [origin.strip() for origin in self.additional_origins.split(",")]
        origins.extend(additional)
    
    # Agregar dominios específicos si es necesario
    if self.environment == "staging":
        origins.append("https://staging-frontend.vercel.app")
    
    return origins
```

---

## 🚀 Despliegue

### 1. Google Cloud Run

```bash
# Variables de entorno en Cloud Run
ENVIRONMENT=production
ALLOWED_ORIGIN=https://jyotish-content-manager.vercel.app
ADDITIONAL_ORIGINS=https://staging-frontend.vercel.app
GOOGLE_MAPS_API_KEY=your_api_key_here
```

### 2. Verificación Post-Despliegue

```bash
# Verificar que CORS funciona
curl -H "Origin: https://jyotish-content-manager.vercel.app" \
     https://jyotish-api-ndcfqrjivq-uc.a.run.app/cors-test

# Verificar que dominios no autorizados son rechazados
curl -H "Origin: https://unauthorized-domain.com" \
     https://jyotish-api-ndcfqrjivq-uc.a.run.app/cors-test
```

---

## ✅ Checklist de Verificación

- [ ] Variables de entorno configuradas en Google Cloud Run
- [ ] `ALLOWED_ORIGIN` apunta a tu frontend de Vercel
- [ ] Endpoint `/cors-test` responde correctamente
- [ ] Frontend puede hacer requests sin errores CORS
- [ ] Dominios no autorizados reciben error 403
- [ ] Headers CORS están presentes en las respuestas
- [ ] Preflight OPTIONS funciona correctamente

---

## 🆘 Troubleshooting

### Error: "CORS origin not allowed"
- Verificar que `ALLOWED_ORIGIN` está configurado correctamente
- Verificar que el dominio del frontend coincide exactamente
- Revisar logs de la API para más detalles

### Error: "No 'Access-Control-Allow-Origin' header"
- Verificar que el middleware CORS está activo
- Verificar que el endpoint responde correctamente
- Probar con el endpoint `/cors-test`

### Error: "Method not allowed"
- Verificar que el método HTTP está en `cors_allow_methods`
- Verificar que el endpoint soporta el método solicitado
