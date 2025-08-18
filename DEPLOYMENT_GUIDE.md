# 🚀 Guía de Despliegue - Jyotiṣa API

## 📋 Prerrequisitos

### Software Requerido
- **Python 3.11+**
- **Redis** (opcional, para caché)
- **Docker** (opcional, para containerización)

### APIs Externas
- **Google Maps API** (para búsqueda de lugares)

## 🚀 Despliegue Local

### 1. Instalación Rápida

```bash
# Clonar repositorio
git clone <repository-url>
cd API-Jyotish

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp env.example .env
# Editar .env con tu Google Maps API key

# Ejecutar servidor
python run.py
```

### 2. Configuración de Variables de Entorno

```bash
# .env
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
REDIS_URL=redis://localhost:6379/0
ENABLE_ASYNC=true
ENABLE_CACHING=true
ENABLE_METRICS=true
```

## 🐳 Despliegue con Docker

### 1. Construir Imagen

```bash
# Construir imagen
docker build -t jyotish-api .

# Ejecutar contenedor
docker run -d \
  -p 8080:8080 \
  -e GOOGLE_MAPS_API_KEY=your_key \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  --name jyotish-api \
  jyotish-api
```

### 2. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - GOOGLE_MAPS_API_KEY=${GOOGLE_MAPS_API_KEY}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

```bash
docker-compose up -d
```

## ☁️ Despliegue en la Nube

### Google Cloud Run

```bash
# Configurar proyecto
gcloud config set project YOUR_PROJECT_ID

# Construir y desplegar
gcloud run deploy jyotish-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_MAPS_API_KEY=your_key \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10
```

### Vercel

```bash
# Instalar Vercel CLI
npm i -g vercel

# Desplegar
vercel --prod
```

### Railway

```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Desplegar
railway login
railway init
railway up
```

## 📊 Monitoreo y Métricas

### Endpoints de Monitoreo

- **Health Check**: `GET /health/healthz`
- **Readiness**: `GET /health/readyz`
- **Métricas**: `GET /metrics`
- **Performance**: `GET /v2/ephemeris/performance`

### Configurar Prometheus

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'jyotish-api'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Configurar Grafana

1. **Importar Dashboard**: Usar el dashboard de FastAPI
2. **Configurar Datasource**: Apuntar a Prometheus
3. **Alertas**: Configurar alertas para:
   - High error rate
   - High response time
   - Circuit breaker open

## 🔧 Configuración de Producción

### Variables de Entorno Recomendadas

```bash
# Performance
ENABLE_ASYNC=true
ENABLE_CACHING=true
ENABLE_METRICS=true
MAX_CONCURRENT_REQUESTS=100
BATCH_SIZE_LIMIT=50

# Cache
REDIS_URL=redis://your-redis-host:6379/0
EPHEMERIS_CACHE_TTL=300
PLACE_CACHE_TTL=3600
PANCHANGA_CACHE_TTL=600

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_BURST=10

# Security
API_KEY=your_api_key
REQUIRE_API_KEY=true
```

### Configuración de Redis

```bash
# Instalar Redis
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Configurar Redis
redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

## 🧪 Testing

### Ejecutar Tests

```bash
# Tests unitarios
python -m pytest tests/ -v

# Tests de performance
python -m pytest tests/test_performance.py -v

# Benchmark
python benchmark.py

# Coverage
python -m pytest tests/ --cov=app --cov-report=html
```

### Health Checks

```bash
# Verificar estado del sistema
curl http://localhost:8080/health/healthz

# Verificar readiness
curl http://localhost:8080/health/readyz

# Ver métricas
curl http://localhost:8080/metrics
```

## 🔍 Troubleshooting

### Problemas Comunes

#### Error: "Swiss Ephemeris not initialized"
```bash
# Verificar instalación
pip install pyswisseph

# Verificar archivos de ephemeris
ls /usr/share/ephemeris/
```

#### Error: "Redis connection failed"
```bash
# Verificar Redis
redis-cli ping

# Verificar URL
echo $REDIS_URL
```

#### Error: "Google Maps API key required"
```bash
# Verificar variable de entorno
echo $GOOGLE_MAPS_API_KEY

# Configurar en producción
gcloud run services update jyotish-api \
  --set-env-vars GOOGLE_MAPS_API_KEY=your_key
```

#### Performance Issues
```bash
# Ver métricas de performance
curl http://localhost:8080/v2/ephemeris/performance

# Limpiar caches
curl -X POST http://localhost:8080/v2/ephemeris/clear-cache
```

## 📚 Recursos Adicionales

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Swiss Ephemeris](https://www.astro.com/swisseph/)
- [Redis Documentation](https://redis.io/documentation)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Google Cloud Run](https://cloud.google.com/run/docs)

## 🆘 Soporte

- **Issues**: Abrir issue en GitHub
- **Documentación**: Ver `/docs` en la API
- **Logs**: Verificar logs del servidor
- **Métricas**: Monitorear `/metrics` endpoint
