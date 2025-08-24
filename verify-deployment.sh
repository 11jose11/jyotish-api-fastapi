#!/bin/bash

# Jyotiṣa API & Frontend Deployment Verification Script
# This script verifies all endpoints and configurations for deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
API_BASE_URL="https://jyotish-api-ndcfqrjivq-uc.a.run.app"
FRONTEND_URL="http://localhost:3000"  # Update this for production
GOOGLE_MAPS_API_KEY="${GOOGLE_MAPS_API_KEY:-}"

echo -e "${BLUE}🔍 Jyotiṣa API & Frontend Deployment Verification${NC}"
echo "=================================================="
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to test API endpoint
test_api_endpoint() {
    local endpoint=$1
    local description=$2
    local method=${3:-GET}
    local data=${4:-}
    
    echo -e "${YELLOW}Testing: ${description}${NC}"
    echo -e "  Endpoint: ${CYAN}${method} ${endpoint}${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "%{http_code}" -o /tmp/response.json "${endpoint}")
    else
        response=$(curl -s -w "%{http_code}" -o /tmp/response.json -X "${method}" -H "Content-Type: application/json" -d "${data}" "${endpoint}")
    fi
    
    http_code="${response: -3}"
    
    if [ "$http_code" -eq 200 ]; then
        echo -e "  ${GREEN}✅ Success (${http_code})${NC}"
        if [ -s /tmp/response.json ]; then
            echo -e "  ${CYAN}Response preview:${NC}"
            head -c 200 /tmp/response.json | cat
            echo ""
        fi
    else
        echo -e "  ${RED}❌ Failed (${http_code})${NC}"
        if [ -s /tmp/response.json ]; then
            echo -e "  ${RED}Error response:${NC}"
            cat /tmp/response.json
            echo ""
        fi
    fi
    echo ""
}

# Function to check environment variables
check_env_var() {
    local var_name=$1
    local var_value=$2
    local required=${3:-false}
    
    if [ -n "$var_value" ]; then
        echo -e "  ${GREEN}✅ ${var_name} is set${NC}"
        if [ "$required" = "true" ]; then
            echo -e "    Value: ${CYAN}${var_value:0:20}...${NC}"
        fi
    else
        if [ "$required" = "true" ]; then
            echo -e "  ${RED}❌ ${var_name} is NOT set (REQUIRED)${NC}"
            return 1
        else
            echo -e "  ${YELLOW}⚠️  ${var_name} is NOT set (optional)${NC}"
        fi
    fi
}

# Function to check file exists
check_file() {
    local file_path=$1
    local description=$2
    
    if [ -f "$file_path" ]; then
        echo -e "  ${GREEN}✅ ${description} exists${NC}"
    else
        echo -e "  ${RED}❌ ${description} missing: ${file_path}${NC}"
        return 1
    fi
}

# Function to check directory exists
check_directory() {
    local dir_path=$1
    local description=$2
    
    if [ -d "$dir_path" ]; then
        echo -e "  ${GREEN}✅ ${description} exists${NC}"
    else
        echo -e "  ${RED}❌ ${description} missing: ${dir_path}${NC}"
        return 1
    fi
}

# Function to check Python dependencies
check_python_deps() {
    echo -e "${BLUE}🐍 Checking Python dependencies...${NC}"
    
    if command_exists python3; then
        echo -e "  ${GREEN}✅ Python 3 is installed${NC}"
        
        if [ -f "requirements.txt" ]; then
            echo -e "  ${GREEN}✅ requirements.txt exists${NC}"
            
            # Check if key packages are available
            python3 -c "import fastapi" 2>/dev/null && echo -e "  ${GREEN}✅ FastAPI is available${NC}" || echo -e "  ${RED}❌ FastAPI is missing${NC}"
            python3 -c "import swisseph" 2>/dev/null && echo -e "  ${GREEN}✅ Swiss Ephemeris is available${NC}" || echo -e "  ${RED}❌ Swiss Ephemeris is missing${NC}"
            python3 -c "import pydantic" 2>/dev/null && echo -e "  ${GREEN}✅ Pydantic is available${NC}" || echo -e "  ${RED}❌ Pydantic is missing${NC}"
        else
            echo -e "  ${RED}❌ requirements.txt missing${NC}"
        fi
    else
        echo -e "  ${RED}❌ Python 3 is not installed${NC}"
    fi
    echo ""
}

# Function to check Node.js dependencies
check_node_deps() {
    echo -e "${BLUE}📦 Checking Node.js dependencies...${NC}"
    
    if command_exists node; then
        echo -e "  ${GREEN}✅ Node.js is installed${NC}"
        echo -e "    Version: ${CYAN}$(node --version)${NC}"
        
        if command_exists npm; then
            echo -e "  ${GREEN}✅ npm is installed${NC}"
            echo -e "    Version: ${CYAN}$(npm --version)${NC}"
        else
            echo -e "  ${RED}❌ npm is not installed${NC}"
        fi
        
        if [ -f "src/package.json" ]; then
            echo -e "  ${GREEN}✅ Frontend package.json exists${NC}"
            
            # Check if node_modules exists
            if [ -d "src/node_modules" ]; then
                echo -e "  ${GREEN}✅ node_modules exists${NC}"
            else
                echo -e "  ${YELLOW}⚠️  node_modules missing - run 'npm install' in src/ directory${NC}"
            fi
        else
            echo -e "  ${RED}❌ Frontend package.json missing${NC}"
        fi
    else
        echo -e "  ${RED}❌ Node.js is not installed${NC}"
    fi
    echo ""
}

# Function to check Docker configuration
check_docker_config() {
    echo -e "${BLUE}🐳 Checking Docker configuration...${NC}"
    
    if command_exists docker; then
        echo -e "  ${GREEN}✅ Docker is installed${NC}"
        echo -e "    Version: ${CYAN}$(docker --version)${NC}"
        
        if [ -f "Dockerfile" ]; then
            echo -e "  ${GREEN}✅ Dockerfile exists${NC}"
        else
            echo -e "  ${RED}❌ Dockerfile missing${NC}"
        fi
        
        if [ -f ".dockerignore" ]; then
            echo -e "  ${GREEN}✅ .dockerignore exists${NC}"
        else
            echo -e "  ${YELLOW}⚠️  .dockerignore missing${NC}"
        fi
    else
        echo -e "  ${RED}❌ Docker is not installed${NC}"
    fi
    echo ""
}

# Function to check API structure
check_api_structure() {
    echo -e "${BLUE}🏗️  Checking API structure...${NC}"
    
    check_directory "app" "API application directory"
    check_directory "app/routers" "API routers directory"
    check_directory "app/services" "API services directory"
    check_directory "app/middleware" "API middleware directory"
    check_directory "app/models" "API models directory"
    check_directory "app/util" "API utilities directory"
    check_directory "rules" "Rules directory"
    
    check_file "app/main.py" "Main FastAPI application"
    check_file "app/config.py" "API configuration"
    check_file "requirements.txt" "Python requirements"
    check_file "pyproject.toml" "Python project configuration"
    
    # Check key router files
    check_file "app/routers/health.py" "Health router"
    check_file "app/routers/panchanga_precise.py" "Panchanga router"
    check_file "app/routers/ephemeris.py" "Ephemeris router"
    check_file "app/routers/yogas.py" "Yogas router"
    check_file "app/routers/motion.py" "Motion router"
    
    # Check key service files
    check_file "app/services/swe.py" "Swiss Ephemeris service"
    check_file "app/services/panchanga_precise.py" "Panchanga service"
    check_file "app/services/yogas.py" "Yogas service"
    
    echo ""
}

# Function to check frontend structure
check_frontend_structure() {
    echo -e "${BLUE}🎨 Checking frontend structure...${NC}"
    
    check_directory "src" "Frontend source directory"
    check_directory "src/app" "Next.js app directory"
    check_directory "src/components" "React components directory"
    check_directory "src/hooks" "React hooks directory"
    check_directory "src/lib" "Frontend utilities directory"
    check_directory "src/types" "TypeScript types directory"
    
    check_file "src/app/page.tsx" "Home page"
    check_file "src/app/calendario/page.tsx" "Calendar page"
    check_file "src/app/layout.tsx" "Root layout"
    check_file "src/hooks/use-calendar.ts" "Calendar hooks"
    check_file "src/lib/api.ts" "API client"
    check_file "src/types/api.ts" "API types"
    check_file "src/lib/yogas-special.json" "Yogas definitions"
    
    echo ""
}

# Function to check environment variables
check_environment() {
    echo -e "${BLUE}🔧 Checking environment variables...${NC}"
    
    # Load .env file if it exists
    if [ -f ".env" ]; then
        echo -e "  ${GREEN}✅ .env file exists${NC}"
        source .env
    else
        echo -e "  ${YELLOW}⚠️  .env file missing - using system environment${NC}"
    fi
    
    # Check API environment variables
    check_env_var "GOOGLE_MAPS_API_KEY" "$GOOGLE_MAPS_API_KEY" "true"
    check_env_var "API_KEY" "$API_KEY" "false"
    check_env_var "SWISS_EPHE_PATH" "$SWISS_EPHE_PATH" "false"
    
    # Check frontend environment variables
    check_env_var "NEXT_PUBLIC_API_URL" "$NEXT_PUBLIC_API_URL" "false"
    check_env_var "NEXT_PUBLIC_GOOGLE_MAPS_API_KEY" "$NEXT_PUBLIC_GOOGLE_MAPS_API_KEY" "false"
    
    echo ""
}

# Function to test API endpoints
test_api_endpoints() {
    echo -e "${BLUE}🌐 Testing API endpoints...${NC}"
    
    # Test basic endpoints
    test_api_endpoint "${API_BASE_URL}/health" "Health check"
    test_api_endpoint "${API_BASE_URL}/info" "API information"
    test_api_endpoint "${API_BASE_URL}/docs" "API documentation"
    
    # Test panchanga endpoints
    test_api_endpoint "${API_BASE_URL}/v1/panchanga/precise/daily?date=2024-12-19&latitude=43.2965&longitude=5.3698" "Daily panchanga (Marseille)"
    test_api_endpoint "${API_BASE_URL}/v1/panchanga/precise/ayanamsa" "Ayanamsa information"
    
    # Test ephemeris endpoints
    test_api_endpoint "${API_BASE_URL}/v1/ephemeris/planets?year=2024&month=12&place_id=test&anchor=sunrise&units=both&planets=Sun,Moon" "Planetary positions"
    
    # Test yogas endpoints
    test_api_endpoint "${API_BASE_URL}/v1/panchanga/yogas/detect?date=2024-12-19&latitude=43.2965&longitude=5.3698" "Yogas detection"
    
    # Test motion endpoints
    test_api_endpoint "${API_BASE_URL}/v1/motion/states?start=2024-12-19&end=2024-12-20&place_id=test&planets=Sun,Moon" "Motion states"
    
    echo ""
}

# Function to check CORS configuration
check_cors_config() {
    echo -e "${BLUE}🔒 Checking CORS configuration...${NC}"
    
    # Test CORS preflight
    echo -e "${YELLOW}Testing CORS preflight request...${NC}"
    cors_response=$(curl -s -I -X OPTIONS -H "Origin: ${FRONTEND_URL}" -H "Access-Control-Request-Method: GET" "${API_BASE_URL}/health" 2>/dev/null | grep -i "access-control" || echo "No CORS headers")
    
    if echo "$cors_response" | grep -q "Access-Control-Allow-Origin"; then
        echo -e "  ${GREEN}✅ CORS is properly configured${NC}"
        echo -e "    ${CYAN}CORS Headers:${NC}"
        echo "$cors_response" | sed 's/^/      /'
    else
        echo -e "  ${RED}❌ CORS headers not found${NC}"
    fi
    
    echo ""
}

# Function to check API configuration
check_api_config() {
    echo -e "${BLUE}⚙️  Checking API configuration...${NC}"
    
    # Check if API config has proper CORS settings
    if grep -q "cors_origins" app/config.py; then
        echo -e "  ${GREEN}✅ CORS origins configured in config.py${NC}"
    else
        echo -e "  ${RED}❌ CORS origins not found in config.py${NC}"
    fi
    
    # Check if main.py includes CORS middleware
    if grep -q "CORSMiddleware" app/main.py; then
        echo -e "  ${GREEN}✅ CORS middleware configured in main.py${NC}"
    else
        echo -e "  ${RED}❌ CORS middleware not found in main.py${NC}"
    fi
    
    # Check if all routers are included
    if grep -q "include_router" app/main.py; then
        echo -e "  ${GREEN}✅ Routers are included in main.py${NC}"
    else
        echo -e "  ${RED}❌ Routers not found in main.py${NC}"
    fi
    
    echo ""
}

# Function to check frontend API integration
check_frontend_integration() {
    echo -e "${BLUE}🔗 Checking frontend API integration...${NC}"
    
    # Check if API base URL is configured
    if grep -q "API_BASE_URL" src/lib/api.ts; then
        echo -e "  ${GREEN}✅ API base URL configured in api.ts${NC}"
        api_url=$(grep "API_BASE_URL" src/lib/api.ts | head -1)
        echo -e "    ${CYAN}${api_url}${NC}"
    else
        echo -e "  ${RED}❌ API base URL not found in api.ts${NC}"
    fi
    
    # Check if all endpoints are defined
    if grep -q "API_ENDPOINTS" src/lib/api.ts; then
        echo -e "  ${GREEN}✅ API endpoints defined in api.ts${NC}"
    else
        echo -e "  ${RED}❌ API endpoints not found in api.ts${NC}"
    fi
    
    # Check if types are properly defined
    if [ -f "src/types/api.ts" ]; then
        echo -e "  ${GREEN}✅ API types defined${NC}"
    else
        echo -e "  ${RED}❌ API types missing${NC}"
    fi
    
    echo ""
}

# Function to check deployment scripts
check_deployment_scripts() {
    echo -e "${BLUE}🚀 Checking deployment scripts...${NC}"
    
    check_file "deploy-full.sh" "Full deployment script"
    check_file "Dockerfile" "Docker configuration"
    check_file ".dockerignore" "Docker ignore file"
    
    # Check if deployment script is executable
    if [ -x "deploy-full.sh" ]; then
        echo -e "  ${GREEN}✅ Deployment script is executable${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Deployment script is not executable${NC}"
        echo -e "    Run: ${CYAN}chmod +x deploy-full.sh${NC}"
    fi
    
    echo ""
}

# Function to run all checks
run_all_checks() {
    echo -e "${PURPLE}🔍 Starting comprehensive deployment verification...${NC}"
    echo "=================================================="
    echo ""
    
    # Check system dependencies
    check_python_deps
    check_node_deps
    check_docker_config
    
    # Check project structure
    check_api_structure
    check_frontend_structure
    
    # Check configuration
    check_environment
    check_api_config
    check_frontend_integration
    check_deployment_scripts
    
    # Test API endpoints
    test_api_endpoints
    check_cors_config
    
    echo -e "${GREEN}✅ All checks completed!${NC}"
    echo ""
}

# Function to provide deployment recommendations
provide_recommendations() {
    echo -e "${PURPLE}📋 Deployment Recommendations${NC}"
    echo "=================================="
    echo ""
    
    echo -e "${BLUE}1. Environment Setup:${NC}"
    echo "   - Create .env file with required variables"
    echo "   - Set GOOGLE_MAPS_API_KEY for location services"
    echo "   - Configure NEXT_PUBLIC_API_URL for frontend"
    echo ""
    
    echo -e "${BLUE}2. API Deployment:${NC}"
    echo "   - Run: ${CYAN}./deploy-full.sh${NC}"
    echo "   - Verify API is accessible at: ${CYAN}${API_BASE_URL}${NC}"
    echo "   - Test all endpoints are working"
    echo ""
    
    echo -e "${BLUE}3. Frontend Deployment:${NC}"
    echo "   - Install dependencies: ${CYAN}cd src && npm install${NC}"
    echo "   - Build for production: ${CYAN}npm run build${NC}"
    echo "   - Deploy to Vercel/Netlify or your preferred platform"
    echo ""
    
    echo -e "${BLUE}4. Post-Deployment:${NC}"
    echo "   - Update frontend API URL to production endpoint"
    echo "   - Test CORS configuration"
    echo "   - Monitor API performance and logs"
    echo "   - Set up monitoring and alerts"
    echo ""
    
    echo -e "${BLUE}5. Security:${NC}"
    echo "   - Ensure API key is properly configured"
    echo "   - Review CORS origins for production"
    echo "   - Enable rate limiting if needed"
    echo ""
}

# Main execution
main() {
    case "${1:-all}" in
        "api")
            echo -e "${BLUE}🔍 API-only verification...${NC}"
            check_python_deps
            check_api_structure
            check_environment
            check_api_config
            test_api_endpoints
            check_cors_config
            ;;
        "frontend")
            echo -e "${BLUE}🔍 Frontend-only verification...${NC}"
            check_node_deps
            check_frontend_structure
            check_frontend_integration
            ;;
        "deployment")
            echo -e "${BLUE}🔍 Deployment verification...${NC}"
            check_docker_config
            check_deployment_scripts
            check_environment
            ;;
        "all"|*)
            run_all_checks
            provide_recommendations
            ;;
    esac
}

# Run main function
main "$@"
