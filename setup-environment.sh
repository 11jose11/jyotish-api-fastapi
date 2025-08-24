#!/bin/bash

# Jyotiṣa API & Frontend Environment Setup Script
# This script helps configure environment variables and Google Maps API key

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🔧 Jyotiṣa Environment Setup${NC}"
echo "=================================="
echo ""

# Function to check if .env file exists
check_env_file() {
    if [ -f ".env" ]; then
        echo -e "${GREEN}✅ .env file exists${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  .env file not found${NC}"
        return 1
    fi
}

# Function to create .env file
create_env_file() {
    echo -e "${BLUE}📝 Creating .env file...${NC}"
    
    cat > .env << 'EOF'
# Jyotiṣa API Environment Variables
# Copy this file to .env and fill in your values

# Google APIs (Required)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# API Authentication (Optional)
API_KEY=your_api_key_here
REQUIRE_API_KEY=false

# Swiss Ephemeris Configuration
SWISS_EPHE_PATH=/path/to/swiss/ephemeris/files
NODE_MODE=true
AYANAMSA_MODE=lahiri
SIDEREAL_MODE=1

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001","https://your-frontend-domain.com"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET","POST","PUT","DELETE","OPTIONS","PATCH"]
CORS_ALLOW_HEADERS=["Accept","Accept-Language","Content-Language","Content-Type","Authorization","X-API-Key","X-Requested-With","X-Request-Id","Origin","Access-Control-Request-Method","Access-Control-Request-Headers"]
CORS_EXPOSE_HEADERS=["X-Request-Id","X-Total-Count","X-Page-Count"]
CORS_MAX_AGE=86400

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379

# Application Settings
LOG_LEVEL=INFO
CACHE_TTL=600
API_VERSION=0.2.0

# HTTP Client Settings
HTTP_TIMEOUT=5
HTTP_CONNECT_TIMEOUT=3
HTTP_MAX_RETRIES=2

# Circuit Breaker Settings
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=30

# Performance Settings
ENABLE_ASYNC=true
ENABLE_CACHING=true
ENABLE_METRICS=true
MAX_CONCURRENT_REQUESTS=100
BATCH_SIZE_LIMIT=50

# Cache Settings
EPHEMERIS_CACHE_TTL=300
PLACE_CACHE_TTL=3600
PANCHANGA_CACHE_TTL=600

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_BURST=10

# Testing Settings
ENABLE_TEST_MODE=false
EOF

    echo -e "${GREEN}✅ .env file created${NC}"
    echo ""
}

# Function to guide user through Google Maps API setup
setup_google_maps_api() {
    echo -e "${BLUE}🗺️  Google Maps API Setup${NC}"
    echo "=============================="
    echo ""
    
    echo -e "${YELLOW}📋 To get a Google Maps API key, follow these steps:${NC}"
    echo ""
    echo "1. Go to the Google Cloud Console:"
    echo -e "   ${CYAN}https://console.cloud.google.com/${NC}"
    echo ""
    echo "2. Create a new project or select an existing one"
    echo ""
    echo "3. Enable the following APIs:"
    echo "   - Maps JavaScript API"
    echo "   - Places API"
    echo "   - Geocoding API"
    echo "   - Time Zone API"
    echo ""
    echo "4. Create credentials:"
    echo "   - Go to 'APIs & Services' > 'Credentials'"
    echo "   - Click 'Create Credentials' > 'API Key'"
    echo "   - Copy the generated API key"
    echo ""
    echo "5. Restrict the API key (recommended):"
    echo "   - Click on the API key to edit it"
    echo "   - Under 'Application restrictions', select 'HTTP referrers'"
    echo "   - Add your domain(s) to the allowed referrers"
    echo "   - Under 'API restrictions', select 'Restrict key'"
    echo "   - Select the APIs you enabled in step 3"
    echo ""
    
    read -p "Do you have a Google Maps API key? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your Google Maps API key: " api_key
        
        if [ -n "$api_key" ]; then
            # Update .env file with the API key
            if [ -f ".env" ]; then
                # Use sed to replace the placeholder with the actual API key
                if [[ "$OSTYPE" == "darwin"* ]]; then
                    # macOS
                    sed -i '' "s/GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here/GOOGLE_MAPS_API_KEY=$api_key/" .env
                else
                    # Linux
                    sed -i "s/GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here/GOOGLE_MAPS_API_KEY=$api_key/" .env
                fi
                
                echo -e "${GREEN}✅ Google Maps API key updated in .env file${NC}"
                
                # Also set it as environment variable for current session
                export GOOGLE_MAPS_API_KEY="$api_key"
                echo -e "${GREEN}✅ Google Maps API key set for current session${NC}"
            else
                echo -e "${RED}❌ .env file not found. Please run this script again.${NC}"
                exit 1
            fi
        else
            echo -e "${RED}❌ API key cannot be empty${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠️  Please get a Google Maps API key and run this script again${NC}"
        echo ""
        echo -e "${BLUE}🔗 Quick links:${NC}"
        echo "Google Cloud Console: https://console.cloud.google.com/"
        echo "Google Maps Platform: https://developers.google.com/maps"
        echo ""
        exit 1
    fi
    
    echo ""
}

# Function to setup frontend environment
setup_frontend_env() {
    echo -e "${BLUE}🎨 Frontend Environment Setup${NC}"
    echo "================================="
    echo ""
    
    # Check if src directory exists
    if [ ! -d "src" ]; then
        echo -e "${RED}❌ src directory not found${NC}"
        return 1
    fi
    
    # Create frontend .env.local file
    echo -e "${YELLOW}📝 Creating frontend .env.local file...${NC}"
    
    # Get API key from .env file
    if [ -f ".env" ]; then
        api_key=$(grep "GOOGLE_MAPS_API_KEY=" .env | cut -d'=' -f2)
        if [ "$api_key" = "your_google_maps_api_key_here" ]; then
            api_key="your_google_maps_api_key_here"
        fi
    else
        api_key="your_google_maps_api_key_here"
    fi
    
    cat > src/.env.local << EOF
# Jyotiṣa Calendar Frontend Environment Variables
# Copy this file to .env.local and fill in your values

# API Configuration
NEXT_PUBLIC_API_URL=https://jyotish-api-ndcfqrjivq-uc.a.run.app

# Google Maps API (Required for location search)
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=$api_key

# Development Configuration
NODE_ENV=development

# Optional: Custom API endpoints for development
# NEXT_PUBLIC_API_URL=http://localhost:8080

# Optional: Analytics (if needed in the future)
# NEXT_PUBLIC_GA_ID=your_google_analytics_id
# NEXT_PUBLIC_GTM_ID=your_google_tag_manager_id
EOF

    echo -e "${GREEN}✅ Frontend .env.local file created${NC}"
    echo ""
}

# Function to test API key
test_api_key() {
    echo -e "${BLUE}🧪 Testing Google Maps API key...${NC}"
    
    if [ -z "$GOOGLE_MAPS_API_KEY" ]; then
        echo -e "${RED}❌ Google Maps API key not set${NC}"
        return 1
    fi
    
    # Test the API key with a simple geocoding request
    echo -e "${YELLOW}Testing API key with geocoding request...${NC}"
    
    test_url="https://maps.googleapis.com/maps/api/geocode/json?address=Paris&key=$GOOGLE_MAPS_API_KEY"
    response=$(curl -s "$test_url")
    
    if echo "$response" | grep -q '"status" : "OK"'; then
        echo -e "${GREEN}✅ Google Maps API key is working!${NC}"
        return 0
    elif echo "$response" | grep -q '"status" : "REQUEST_DENIED"'; then
        echo -e "${RED}❌ Google Maps API key is invalid or restricted${NC}"
        echo -e "${YELLOW}Please check your API key and restrictions${NC}"
        return 1
    else
        echo -e "${YELLOW}⚠️  Could not verify API key. Please test manually.${NC}"
        return 1
    fi
}

# Function to display next steps
display_next_steps() {
    echo -e "${GREEN}✅ Environment setup completed!${NC}"
    echo ""
    echo -e "${BLUE}📋 Next steps:${NC}"
    echo "1. Test the API:"
    echo -e "   ${CYAN}./verify-deployment.sh api${NC}"
    echo ""
    echo "2. Deploy the API:"
    echo -e "   ${CYAN}./deploy-full.sh${NC}"
    echo ""
    echo "3. Deploy the frontend:"
    echo -e "   ${CYAN}./deploy-full.sh frontend${NC}"
    echo ""
    echo "4. Or deploy everything at once:"
    echo -e "   ${CYAN}./deploy-full.sh all${NC}"
    echo ""
    echo -e "${YELLOW}🔧 Configuration files created:${NC}"
    echo "   - .env (API environment variables)"
    echo "   - src/.env.local (Frontend environment variables)"
    echo ""
    echo -e "${YELLOW}⚠️  Important:${NC}"
    echo "   - Keep your API keys secure"
    echo "   - Don't commit .env files to version control"
    echo "   - Set up proper API key restrictions in Google Cloud Console"
    echo ""
}

# Main execution
main() {
    echo -e "${BLUE}🔍 Checking current environment...${NC}"
    
    # Check if .env file exists
    if ! check_env_file; then
        create_env_file
    fi
    
    # Setup Google Maps API
    setup_google_maps_api
    
    # Setup frontend environment
    setup_frontend_env
    
    # Test API key
    if test_api_key; then
        echo -e "${GREEN}✅ API key test passed!${NC}"
    else
        echo -e "${YELLOW}⚠️  API key test failed. Please check your configuration.${NC}"
    fi
    
    echo ""
    display_next_steps
}

# Run main function
main "$@"
