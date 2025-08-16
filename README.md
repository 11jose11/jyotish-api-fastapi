# Jyotiṣa API

Una API completa de Jyotiṣa (astrología védica) construida con Python, FastAPI y Swiss Ephemeris, integrada con Google Places API y Google Time Zone API para resolver ubicaciones y zonas horarias históricas.

## ✅ Estado del Proyecto

**API completamente funcional y lista para producción**

- ✅ Swiss Ephemeris funcionando en modo sideral Lahiri
- ✅ Todos los endpoints implementados y probados
- ✅ Dockerizado y listo para Google Cloud Run
- ✅ Logging JSON y observabilidad
- ✅ Tests unitarios incluidos
- ✅ Documentación completa

## Características

- **Swiss Ephemeris con modo sideral Lahiri**: Cálculos precisos de posiciones planetarias
- **Google Places API**: Autocompletado y resolución de lugares
- **Google Time Zone API**: Soporte para zonas horarias históricas incluyendo DST
- **Cálculos de Pañchāṅga**: Tithi, Nakṣatra, Rāśi, etc.
- **Estados de movimiento planetario**: Clasificación de cheṣṭā (vakri, manda, sighra, etc.)
- **Detección de Yogas**: Combinaciones positivas y negativas según reglas tradicionales
- **Calendarios mensuales y diarios**: Con ventanas exactas de cambios
- **Observabilidad**: Logging JSON, métricas, health checks
- **Dockerizado**: Listo para Google Cloud Run

## Tecnologías

- **Python 3.11**
- **FastAPI** - Framework web moderno y rápido
- **Swiss Ephemeris** - Biblioteca de efemérides astronómicas
- **Google APIs** - Places y Time Zone
- **Pydantic** - Validación de datos
- **Docker** - Containerización

## Instalación Local

### Requisitos

- Python 3.11+
- Google Maps API Key (opcional para desarrollo)

### Configuración local

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd jyotish-api
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación**
```bash
python run.py
```

La API estará disponible en: http://localhost:8080
Documentación: http://localhost:8080/docs

## Despliegue en Google Cloud Run

### Opción 1: Despliegue Automático (Recomendado)

```bash
# 1. Configurar gcloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 2. Ejecutar script de despliegue
./deploy.sh YOUR_PROJECT_ID us-central1
```

### Opción 2: Despliegue Manual

```bash
# 1. Construir y subir imagen
gcloud builds submit --tag gcr.io/$PROJECT_ID/jyotish-api:latest

# 2. Desplegar servicio
gcloud run deploy jyotish-api \
  --image gcr.io/$PROJECT_ID/jyotish-api:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1
```

### Opción 3: Despliegue con Cloud Build

```bash
# Configurar trigger en Cloud Build
gcloud builds submit --config cloudbuild.yaml
```

### Configurar Variables de Entorno

```bash
# Configurar Google Maps API Key
gcloud run services update jyotish-api \
  --region us-central1 \
  --set-env-vars GOOGLE_MAPS_API_KEY=your_api_key
```

## Endpoints de la API

### Health Checks

```bash
# Health check básico
curl https://your-service-url/health/healthz

# Readiness check
curl https://your-service-url/health/readyz
```

### Efemérides

```bash
# Cálculo con timestamp UTC
curl "https://your-service-url/v1/ephemeris?when_utc=2024-01-15T12:00:00Z"

# Cálculo con tiempo local y place_id
curl "https://your-service-url/v1/ephemeris?when_local=2024-01-15T12:00:00&place_id=ChIJD7fiBh9u5kcRYJSMaMOCCwQ"
```

### Calendario

```bash
# Calendario mensual
curl "https://your-service-url/v1/calendar/month?year=2024&month=8&place_id=ChIJD7fiBh9u5kcRYJSMaMOCCwQ"

# Calendario diario
curl "https://your-service-url/v1/calendar/day?date=2024-08-15&place_id=ChIJD7fiBh9u5kcRYJSMaMOCCwQ"
```

### Estados de Movimiento

```bash
# Estados de movimiento planetario
curl "https://your-service-url/v1/motion/states?start=2024-08-01T00:00:00&end=2024-08-31T23:59:59&planets=Mars,Venus"
```

### Yogas

```bash
# Detectar yogas
curl -X POST "https://your-service-url/v1/panchanga/yogas/detect" \
  -H "Content-Type: application/json" \
  -d '{
    "start": "2024-08-01",
    "end": "2024-08-31",
    "place_id": "ChIJD7fiBh9u5kcRYJSMaMOCCwQ",
    "granularity": "day",
    "includeNotes": true
  }'
```

## Documentación de la API

La documentación interactiva está disponible en:
- **Swagger UI**: https://your-service-url/docs
- **ReDoc**: https://your-service-url/redoc

## Estructura del Proyecto

```
jyotish-api/
├── app/
│   ├── main.py              # Aplicación principal FastAPI
│   ├── config.py            # Configuración y settings
│   ├── util/
│   │   └── logging.py       # Configuración de logging JSON
│   ├── services/
│   │   ├── swe.py           # Wrapper Swiss Ephemeris
│   │   ├── places.py        # Google Places API
│   │   ├── timezone.py      # Google Time Zone API
│   │   ├── motion.py        # Estados de movimiento
│   │   ├── panchanga.py     # Cálculos de pañchāṅga
│   │   └── yogas.py         # Detección de yogas
│   └── routers/
│       ├── health.py        # Health checks
│       ├── places.py        # Endpoints de lugares
│       ├── ephemeris.py     # Efemérides
│       ├── calendar.py      # Calendarios
│       ├── motion.py        # Movimiento planetario
│       └── yogas.py         # Yogas
├── rules/
│   └── panchanga_rules.json # Reglas de yogas
├── tests/                   # Tests unitarios
├── requirements.txt         # Dependencias Python
├── Dockerfile              # Configuración Docker
├── deploy.sh               # Script de despliegue
├── cloudbuild.yaml         # Configuración Cloud Build
└── README.md               # Este archivo
```

## Algoritmos Implementados

### Cálculos Básicos

- **Rāśi**: `rasi_index = floor(lon/30) + 1`
- **Nakṣatra**: `nak_index = floor(lon/13°20') + 1`
- **Pāda**: `pada = floor((lon % 13°20')/(3°20')) + 1`
- **Tithi**: `tithi = floor((λ_moon - λ_sun) % 360 / 12°) + 1`

### Estados de Movimiento

- **Vakri**: Movimiento retrógrado (v < 0)
- **Vikala**: Muy lento (|v| < 3% del baseline)
- **Manda**: Lento (0.6 < v/baseline < 1.4)
- **Sama**: Normal (1.4 < v/baseline < 2.0)
- **Sighra**: Rápido (v/baseline > 2.0)

### Yogas Detectados

**Positivos:**
- Amṛta Siddhi (Vāra + Nakṣatra)
- Sarvārtha Siddhi
- Siddha
- Ravi Yoga (offset Sol-Luna)
- Guru Puṣya (Jueves + Puṣya)
- Ravi Puṣya (Sol + Puṣya)

**Negativos:**
- Dagdha, Visha, Hutasana, Krakacha, Samvartaka
- Asubha (Tithi + Nakṣatra)
- Vināsa (combinación triple)
- Panchaka (clasificación por día)

## Tests

```bash
# Ejecutar tests
pytest

# Tests con coverage
pytest --cov=app tests/
```

## Desarrollo

### Formateo de código

```bash
# Formatear con black
black app/

# Linting con ruff
ruff check app/
```

## Monitoreo y Logs

```bash
# Ver logs en tiempo real
gcloud logs tail --service=jyotish-api --region=us-central1

# Ver métricas
gcloud run services describe jyotish-api --region=us-central1
```

## Troubleshooting

### Problemas Comunes

1. **Error de Swiss Ephemeris**: Verificar que pyswisseph esté instalado correctamente
2. **Error de Google API**: Verificar que GOOGLE_MAPS_API_KEY esté configurado
3. **Error de memoria**: Aumentar --memory a 2Gi si es necesario
4. **Timeout**: Aumentar --timeout si los cálculos son lentos

### Logs de Debug

```bash
# Ver logs detallados
gcloud logs read --service=jyotish-api --limit=50 --format="table(timestamp,severity,textPayload)"
```

## Contribuir

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Soporte

Para soporte y preguntas:
- Abrir un issue en GitHub
- Consultar la documentación de la API en `/docs`
- Revisar los logs de la aplicación

## Roadmap

- [x] API básica funcional
- [x] Swiss Ephemeris integrado
- [x] Google APIs integradas
- [x] Docker y Cloud Run
- [ ] Soporte para Redis/MemoryStore
- [ ] Más algoritmos de cálculo de salida del sol
- [ ] API para cálculos de horóscopo
- [ ] Soporte para múltiples sistemas de coordenadas
- [ ] Cache distribuido
- [ ] Métricas Prometheus
- [ ] Tests de integración
- [ ] Cliente Python oficial
