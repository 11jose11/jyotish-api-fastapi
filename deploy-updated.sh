#!/bin/bash

# Script de despliegue actualizado para Jyotish API en Google Cloud Run
# Incluye las correcciones de endpoints y configuración optimizada

set -e

echo "🚀 Iniciando despliegue actualizado de Jyotish API en Google Cloud Run..."

# Configuración del proyecto
PROJECT_ID="jyotish-api-fastapi"
REGION="us-central1"
SERVICE_NAME="jyotish-api"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Verificar que estamos en el proyecto correcto
echo "📋 Verificando proyecto actual..."
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "none")

if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
    echo "🔄 Cambiando al proyecto $PROJECT_ID..."
    gcloud config set project $PROJECT_ID
else
    echo "✅ Ya estamos en el proyecto correcto: $PROJECT_ID"
fi

# Habilitar APIs necesarias
echo "🔧 Habilitando APIs necesarias..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Construir la imagen Docker
echo "🐳 Construyendo imagen Docker..."
gcloud builds submit --tag $IMAGE_NAME --project $PROJECT_ID

# Verificar que la imagen se construyó correctamente
echo "🔍 Verificando imagen construida..."
gcloud container images list-tags $IMAGE_NAME --limit=1

# Desplegar en Cloud Run
echo "🚀 Desplegando en Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --project $PROJECT_ID \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --min-instances 0 \
    --concurrency 80 \
    --timeout 300 \
    --set-env-vars="ENVIRONMENT=production" \
    --set-env-vars="ALLOWED_ORIGIN=https://jyotish-content-manager.vercel.app" \
    --set-env-vars="ADDITIONAL_ORIGINS=https://jyotish-content-manager.vercel.app" \
    --set-env-vars="REQUIRE_API_KEY=false" \
    --set-env-vars="LOG_LEVEL=INFO" \
    --set-env-vars="API_VERSION=0.2.1" \
    --set-env-vars="ENABLE_CACHING=true" \
    --set-env-vars="ENABLE_METRICS=true" \
    --set-env-vars="CORS_MAX_AGE=86400" \
    --set-env-vars="RATE_LIMIT_REQUESTS_PER_MINUTE=100" \
    --set-env-vars="RATE_LIMIT_BURST=20" \
    --set-env-vars="CIRCUIT_BREAKER_FAILURE_THRESHOLD=5" \
    --set-env-vars="CIRCUIT_BREAKER_TIMEOUT=30"

# Obtener la URL del servicio
echo "🔗 Obteniendo URL del servicio..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)")

echo "✅ Despliegue completado exitosamente!"
echo "🌐 URL del servicio: $SERVICE_URL"
echo "📊 Panel de control: https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME"

# Verificar el estado del servicio
echo "🔍 Verificando estado del servicio..."
gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.conditions[0].status)"

# Mostrar logs recientes
echo "📝 Mostrando logs recientes..."
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" --limit=10 --format="table(timestamp,severity,textPayload)"

# Información adicional
echo ""
echo "📋 Información del despliegue:"
echo "   - Proyecto: $PROJECT_ID"
echo "   - Región: $REGION"
echo "   - Servicio: $SERVICE_NAME"
echo "   - Imagen: $IMAGE_NAME"
echo "   - Memoria: 2Gi"
echo "   - CPU: 2"
echo "   - Máx. instancias: 10"
echo "   - Timeout: 300s"
echo "   - Concurrencia: 80"

echo ""
echo "🔧 Endpoints corregidos:"
echo "   - ✅ GET /v1/places/autocomplete - Places autocomplete"
echo "   - ✅ GET /v1/motion/speeds - Motion speeds (campo 'speed' corregido)"
echo "   - ✅ GET /v1/motion/states - Motion states"
echo "   - ✅ GET /v1/chesta-bala/calculate - Chesta Bala calculations"

echo ""
echo "🧪 Para probar los endpoints:"
echo "   curl '$SERVICE_URL/health'"
echo "   curl '$SERVICE_URL/v1/places/autocomplete?query=London'"
echo "   curl '$SERVICE_URL/v1/motion/speeds?start=2024-01-15&end=2024-01-16&place_id=ChIJN1t_tDeuEmsRUsoyG83frY4&planets=Mars,Venus'"

echo ""
echo "🎯 Próximos pasos:"
echo "   1. Verificar que todos los endpoints funcionen correctamente"
echo "   2. Probar la funcionalidad de Chest Bala en el frontend"
echo "   3. Monitorear el rendimiento y logs del servicio"
echo "   4. Configurar alertas si es necesario"

echo ""
echo "🏁 ¡Despliegue completado! La API está lista para usar."
