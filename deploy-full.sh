#!/bin/bash

# Jyotiṣa API & Frontend Complete Deployment Script
# This script deploys both the API and frontend

set -e

# Configuration
PROJECT_ID="jyotish-api-fastapi"
REGION="us-central1"
API_SERVICE_NAME="jyotish-api"
FRONTEND_SERVICE_NAME="jyotish-frontend"
API_IMAGE_NAME="gcr.io/$PROJECT_ID/$API_SERVICE_NAME"
FRONTEND_IMAGE_NAME="gcr.io/$PROJECT_ID/$FRONTEND_SERVICE_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🚀 Jyotiṣa API & Frontend Complete Deployment${NC}"
echo "================================================"
echo ""

# Function to check prerequisites
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
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
    
    # Check if node is installed
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js not found. Please install it first.${NC}"
        exit 1
    fi
    
    # Check if npm is installed
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ npm not found. Please install it first.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All prerequisites are installed${NC}"
    echo ""
}

# Function to set up Google Cloud
setup_google_cloud() {
    echo -e "${BLUE}☁️  Setting up Google Cloud...${NC}"
    
    # Set project
    echo -e "${YELLOW}📋 Setting project to: $PROJECT_ID${NC}"
    gcloud config set project $PROJECT_ID
    
    # Enable required APIs
    echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable run.googleapis.com
    gcloud services enable containerregistry.googleapis.com
    gcloud services enable cloudresourcemanager.googleapis.com
    
    echo -e "${GREEN}✅ Google Cloud setup completed${NC}"
    echo ""
}

# Function to build and deploy API
deploy_api() {
    echo -e "${BLUE}🔧 Building and deploying API...${NC}"
    
    # Build API Docker image
    echo -e "${YELLOW}🐳 Building API Docker image...${NC}"
    docker build --platform linux/amd64 -t $API_IMAGE_NAME .
    
    # Push API image
    echo -e "${YELLOW}📤 Pushing API image to Container Registry...${NC}"
    docker push $API_IMAGE_NAME
    
    # Deploy API to Cloud Run
    echo -e "${YELLOW}🚀 Deploying API to Cloud Run...${NC}"
    gcloud run deploy $API_SERVICE_NAME \
        --image $API_IMAGE_NAME \
        --region $REGION \
        --platform managed \
        --allow-unauthenticated \
        --port 8080 \
        --memory 512Mi \
        --cpu 1 \
        --max-instances 10 \
        --timeout 300 \
        --concurrency 80 \
        --set-env-vars PYTHONUNBUFFERED=1,PYTHONDONTWRITEBYTECODE=1
    
    # Get API service URL
    API_URL=$(gcloud run services describe $API_SERVICE_NAME --region=$REGION --format='value(status.url)')
    
    echo -e "${GREEN}✅ API deployed successfully!${NC}"
    echo -e "${CYAN}🌐 API URL: $API_URL${NC}"
    echo ""
    
    # Store API URL for frontend
    echo $API_URL > .api_url
}

# Function to build and deploy frontend
deploy_frontend() {
    echo -e "${BLUE}🎨 Building and deploying frontend...${NC}"
    
    # Read API URL
    if [ -f .api_url ]; then
        API_URL=$(cat .api_url)
    else
        echo -e "${RED}❌ API URL not found. Please deploy API first.${NC}"
        exit 1
    fi
    
    # Navigate to frontend directory
    cd src
    
    # Install dependencies
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    npm install
    
    # Create environment file for build
    echo -e "${YELLOW}🔧 Creating environment configuration...${NC}"
    cat > .env.local << EOF
NEXT_PUBLIC_API_URL=$API_URL
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=${GOOGLE_MAPS_API_KEY:-your_google_maps_api_key_here}
NODE_ENV=production
EOF
    
    # Build frontend
    echo -e "${YELLOW}🔨 Building frontend for production...${NC}"
    npm run build
    
    # Create Dockerfile for frontend
    echo -e "${YELLOW}🐳 Creating frontend Dockerfile...${NC}"
    cat > Dockerfile << EOF
# Frontend Dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json package-lock.json* ./
RUN npm ci --only=production

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Next.js collects completely anonymous telemetry data about general usage.
# Learn more here: https://nextjs.org/telemetry
# Uncomment the following line in case you want to disable telemetry during the build.
ENV NEXT_TELEMETRY_DISABLED 1

RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
EOF
    
    # Build frontend Docker image
    echo -e "${YELLOW}🐳 Building frontend Docker image...${NC}"
    docker build --platform linux/amd64 -t $FRONTEND_IMAGE_NAME .
    
    # Push frontend image
    echo -e "${YELLOW}📤 Pushing frontend image to Container Registry...${NC}"
    docker push $FRONTEND_IMAGE_NAME
    
    # Deploy frontend to Cloud Run
    echo -e "${YELLOW}🚀 Deploying frontend to Cloud Run...${NC}"
    gcloud run deploy $FRONTEND_SERVICE_NAME \
        --image $FRONTEND_IMAGE_NAME \
        --region $REGION \
        --platform managed \
        --allow-unauthenticated \
        --port 3000 \
        --memory 512Mi \
        --cpu 1 \
        --max-instances 10 \
        --timeout 300 \
        --concurrency 80 \
        --set-env-vars NODE_ENV=production,NEXT_PUBLIC_API_URL=$API_URL
    
    # Get frontend service URL
    FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE_NAME --region=$REGION --format='value(status.url)')
    
    echo -e "${GREEN}✅ Frontend deployed successfully!${NC}"
    echo -e "${CYAN}🌐 Frontend URL: $FRONTEND_URL${NC}"
    echo ""
    
    # Clean up
    rm -f .env.local Dockerfile
    cd ..
}

# Function to test deployment
test_deployment() {
    echo -e "${BLUE}🧪 Testing deployment...${NC}"
    
    # Read URLs
    if [ -f .api_url ]; then
        API_URL=$(cat .api_url)
    else
        echo -e "${RED}❌ API URL not found${NC}"
        return 1
    fi
    
    FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE_NAME --region=$REGION --format='value(status.url)' 2>/dev/null || echo "")
    
    # Test API
    echo -e "${YELLOW}Testing API...${NC}"
    if curl -f "$API_URL/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API health check passed!${NC}"
    else
        echo -e "${RED}❌ API health check failed!${NC}"
    fi
    
    # Test frontend
    if [ -n "$FRONTEND_URL" ]; then
        echo -e "${YELLOW}Testing frontend...${NC}"
        if curl -f "$FRONTEND_URL" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Frontend is accessible!${NC}"
        else
            echo -e "${RED}❌ Frontend is not accessible!${NC}"
        fi
    fi
    
    echo ""
}

# Function to display deployment summary
display_summary() {
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo "================================================"
    echo ""
    
    # Read URLs
    if [ -f .api_url ]; then
        API_URL=$(cat .api_url)
        echo -e "${BLUE}🌐 API URL:${NC} $API_URL"
        echo -e "${BLUE}📖 API Documentation:${NC} $API_URL/docs"
        echo -e "${BLUE}🔍 API Health Check:${NC} $API_URL/health"
        echo -e "${BLUE}ℹ️  API Info:${NC} $API_URL/info"
    fi
    
    FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE_NAME --region=$REGION --format='value(status.url)' 2>/dev/null || echo "")
    if [ -n "$FRONTEND_URL" ]; then
        echo ""
        echo -e "${BLUE}🌐 Frontend URL:${NC} $FRONTEND_URL"
        echo -e "${BLUE}📱 Calendar App:${NC} $FRONTEND_URL/calendario"
    fi
    
    echo ""
    echo -e "${YELLOW}📝 Next steps:${NC}"
    echo "1. Test the application functionality"
    echo "2. Configure custom domains if needed"
    echo "3. Set up monitoring and alerts"
    echo "4. Configure SSL certificates"
    echo "5. Set up CI/CD pipeline for future deployments"
    echo ""
    echo -e "${YELLOW}🔧 Configuration:${NC}"
    echo "1. Update environment variables in Cloud Run"
    echo "2. Configure Google Maps API key"
    echo "3. Set up proper CORS origins"
    echo "4. Configure rate limiting if needed"
    echo ""
}

# Function to clean up
cleanup() {
    echo -e "${BLUE}🧹 Cleaning up...${NC}"
    rm -f .api_url
    echo -e "${GREEN}✅ Cleanup completed${NC}"
    echo ""
}

# Main execution
main() {
    case "${1:-all}" in
        "api")
            echo -e "${BLUE}🔧 API-only deployment...${NC}"
            check_prerequisites
            setup_google_cloud
            deploy_api
            test_deployment
            ;;
        "frontend")
            echo -e "${BLUE}🎨 Frontend-only deployment...${NC}"
            check_prerequisites
            setup_google_cloud
            deploy_frontend
            test_deployment
            ;;
        "all"|*)
            echo -e "${BLUE}🚀 Full deployment (API + Frontend)...${NC}"
            check_prerequisites
            setup_google_cloud
            deploy_api
            deploy_frontend
            test_deployment
            display_summary
            ;;
    esac
    
    cleanup
}

# Handle script interruption
trap cleanup EXIT

# Run main function
main "$@"
