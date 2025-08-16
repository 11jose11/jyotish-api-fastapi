# 🚀 Guía Rápida de Despliegue - Jyotiṣa API

## Despliegue en Google Cloud Run

### Prerrequisitos

1. **Instalar Google Cloud SDK**
   ```bash
   # macOS
   brew install google-cloud-sdk
   
   # Linux
   curl https://sdk.cloud.google.com | bash
   ```

2. **Autenticarse**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Habilitar APIs necesarias**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   ```

### Despliegue Rápido

```bash
# 1. Clonar el repositorio
git clone <your-repo>
cd jyotish-api

# 2. Ejecutar despliegue automático
./deploy.sh YOUR_PROJECT_ID us-central1
```

### Configurar Variables de Entorno

```bash
# Configurar Google Maps API Key
gcloud run services update jyotish-api \
  --region us-central1 \
  --set-env-vars GOOGLE_MAPS_API_KEY=your_api_key
```

### Verificar Despliegue

```bash
# Verificar que el servicio esté funcionando
curl https://jyotish-api-us-central1-YOUR_PROJECT_ID.a.run.app/health/healthz

# Ver logs
gcloud logs tail --service=jyotish-api --region=us-central1
```

## URLs del Servicio

- **API Base**: `https://jyotish-api-us-central1-YOUR_PROJECT_ID.a.run.app`
- **Documentación**: `https://jyotish-api-us-central1-YOUR_PROJECT_ID.a.run.app/docs`
- **Health Check**: `https://jyotish-api-us-central1-YOUR_PROJECT_ID.a.run.app/health/healthz`

## Comandos Útiles

```bash
# Ver información del servicio
gcloud run services describe jyotish-api --region=us-central1

# Ver logs en tiempo real
gcloud logs tail --service=jyotish-api --region=us-central1

# Actualizar configuración
gcloud run services update jyotish-api --region=us-central1 --memory=2Gi

# Eliminar servicio
gcloud run services delete jyotish-api --region=us-central1
```

## Troubleshooting

### Error: "No module named 'fastapi'"
- Verificar que requirements.txt esté incluido en el Dockerfile

### Error: "Google Maps API key required"
- Configurar la variable de entorno GOOGLE_MAPS_API_KEY

### Error: "Swiss Ephemeris not initialized"
- Verificar que pyswisseph esté instalado correctamente

### Error: "Memory limit exceeded"
- Aumentar memoria: `--memory=2Gi`

### Error: "Request timeout"
- Aumentar timeout: `--timeout=600`
