#!/bin/bash

# Script de despliegue para Google Cloud Run
# Jyotiṣa API

set -e

# Configuración
PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"us-central1"}
SERVICE_NAME="jyotish-api"
IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

echo "🚀 Desplegando Jyotiṣa API en Google Cloud Run"
echo "================================================"
echo "Proyecto: $PROJECT_ID"
echo "Región: $REGION"
echo "Servicio: $SERVICE_NAME"
echo "Imagen: $IMAGE_TAG"
echo ""

# Verificar que gcloud esté instalado
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI no está instalado"
    echo "Instala gcloud desde: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Verificar que estemos autenticados
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Error: No estás autenticado en gcloud"
    echo "Ejecuta: gcloud auth login"
    exit 1
fi

# Verificar que el proyecto existe
if ! gcloud projects describe "$PROJECT_ID" > /dev/null 2>&1; then
    echo "❌ Error: El proyecto $PROJECT_ID no existe o no tienes acceso"
    exit 1
fi

echo "✅ Configuración verificada"
echo ""

# Construir la imagen
echo "🔨 Construyendo imagen Docker..."
gcloud builds submit --tag "$IMAGE_TAG" --project "$PROJECT_ID"

if [ $? -ne 0 ]; then
    echo "❌ Error construyendo la imagen"
    exit 1
fi

echo "✅ Imagen construida exitosamente"
echo ""

# Desplegar en Cloud Run
echo "🚀 Desplegando en Google Cloud Run..."

gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_TAG" \
    --region "$REGION" \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --min-instances 0 \
    --timeout 300 \
    --concurrency 80 \
    --project "$PROJECT_ID"

if [ $? -ne 0 ]; then
    echo "❌ Error desplegando el servicio"
    exit 1
fi

echo ""
echo "✅ ¡Despliegue completado exitosamente!"
echo ""
echo "📋 Información del servicio:"
echo "   URL: https://$SERVICE_NAME-$REGION-$PROJECT_ID.a.run.app"
echo "   Documentación: https://$SERVICE_NAME-$REGION-$PROJECT_ID.a.run.app/docs"
echo "   Health Check: https://$SERVICE_NAME-$REGION-$PROJECT_ID.a.run.app/health/healthz"
echo ""
echo "🔧 Para configurar variables de entorno:"
echo "   gcloud run services update $SERVICE_NAME \\"
echo "     --region $REGION \\"
echo "     --set-env-vars GOOGLE_MAPS_API_KEY=your_api_key \\"
echo "     --project $PROJECT_ID"
echo ""
echo "📊 Para ver logs:"
echo "   gcloud logs tail --service=$SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
