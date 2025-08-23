#!/bin/bash

# Jyotiṣa API Cloud Run Deployment Script
# This script deploys the Jyotiṣa API to Google Cloud Run

set -e

# Configuration
PROJECT_ID="jyotish-api-fastapi"  # Your actual project ID
REGION="us-central1"
SERVICE_NAME="jyotish-api"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Jyotiṣa API Cloud Run Deployment${NC}"
echo "=================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Google Cloud SDK not found. Please install it first.${NC}"
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install it first.${NC}"
    exit 1
fi

# Set project
echo -e "${YELLOW}📋 Setting project to: $PROJECT_ID${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and push Docker image
echo -e "${YELLOW}🐳 Building Docker image...${NC}"
docker build -t $IMAGE_NAME .

echo -e "${YELLOW}📤 Pushing image to Container Registry...${NC}"
docker push $IMAGE_NAME

# Deploy to Cloud Run
echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --timeout 300 \
    --concurrency 80 \
    --set-env-vars PYTHONUNBUFFERED=1,PYTHONDONTWRITEBYTECODE=1 \
    --update-env-vars CORS_ORIGINS="https://your-frontend-domain.com,http://localhost:3000,http://localhost:5173"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo "=================================="
echo -e "${BLUE}🌐 Service URL:${NC} $SERVICE_URL"
echo -e "${BLUE}📖 API Documentation:${NC} $SERVICE_URL/docs"
echo -e "${BLUE}🔍 Health Check:${NC} $SERVICE_URL/health"
echo -e "${BLUE}ℹ️  API Info:${NC} $SERVICE_URL/info"

# Test the deployment
echo -e "${YELLOW}🧪 Testing deployment...${NC}"
sleep 10

if curl -f "$SERVICE_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
else
    echo -e "${RED}❌ Health check failed!${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Jyotiṣa API is now live on Google Cloud Run!${NC}"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Update your frontend to use the new URL: $SERVICE_URL"
echo "2. Test the API endpoints"
echo "3. Configure custom domain if needed"
echo "4. Set up monitoring and alerts"
