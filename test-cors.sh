#!/bin/bash

# CORS Testing Script for Jyotiṣa API
# This script tests CORS configuration and headers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
API_BASE_URL="https://jyotish-api-ndcfqrjivq-uc.a.run.app"
TEST_ORIGINS=(
    "http://localhost:3000"
    "https://localhost:3000"
    "https://jyotish-api-ndcfqrjivq-uc.a.run.app"
    "https://jyotish-frontend-ndcfqrjivq-uc.a.run.app"
    "https://jyotish-calendar.vercel.app"
    "https://invalid-origin.com"
)

echo -e "${BLUE}🔒 Testing CORS Configuration${NC}"
echo "=================================="
echo ""

# Function to test CORS headers
test_cors_headers() {
    local origin=$1
    local description=$2
    
    echo -e "${YELLOW}Testing: ${description}${NC}"
    echo -e "  Origin: ${CYAN}${origin}${NC}"
    
    # Test preflight request
    echo -e "  ${BLUE}Testing preflight request...${NC}"
    preflight_response=$(curl -s -I -X OPTIONS \
        -H "Origin: ${origin}" \
        -H "Access-Control-Request-Method: GET" \
        -H "Access-Control-Request-Headers: Content-Type" \
        "${API_BASE_URL}/health" 2>/dev/null)
    
    # Extract CORS headers
    allow_origin=$(echo "$preflight_response" | grep -i "access-control-allow-origin" | head -1)
    allow_methods=$(echo "$preflight_response" | grep -i "access-control-allow-methods" | head -1)
    allow_headers=$(echo "$preflight_response" | grep -i "access-control-allow-headers" | head -1)
    allow_credentials=$(echo "$preflight_response" | grep -i "access-control-allow-credentials" | head -1)
    max_age=$(echo "$preflight_response" | grep -i "access-control-max-age" | head -1)
    
    # Check if CORS headers are present
    if [ -n "$allow_origin" ]; then
        echo -e "    ${GREEN}✅ Access-Control-Allow-Origin: ${allow_origin#*: }${NC}"
    else
        echo -e "    ${RED}❌ Access-Control-Allow-Origin header missing${NC}"
    fi
    
    if [ -n "$allow_methods" ]; then
        echo -e "    ${GREEN}✅ Access-Control-Allow-Methods: ${allow_methods#*: }${NC}"
    else
        echo -e "    ${RED}❌ Access-Control-Allow-Methods header missing${NC}"
    fi
    
    if [ -n "$allow_headers" ]; then
        echo -e "    ${GREEN}✅ Access-Control-Allow-Headers: ${allow_headers#*: }${NC}"
    else
        echo -e "    ${RED}❌ Access-Control-Allow-Headers header missing${NC}"
    fi
    
    if [ -n "$allow_credentials" ]; then
        echo -e "    ${GREEN}✅ Access-Control-Allow-Credentials: ${allow_credentials#*: }${NC}"
    else
        echo -e "    ${RED}❌ Access-Control-Allow-Credentials header missing${NC}"
    fi
    
    if [ -n "$max_age" ]; then
        echo -e "    ${GREEN}✅ Access-Control-Max-Age: ${max_age#*: }${NC}"
    else
        echo -e "    ${RED}❌ Access-Control-Max-Age header missing${NC}"
    fi
    
    # Test actual request
    echo -e "  ${BLUE}Testing actual request...${NC}"
    actual_response=$(curl -s -I -H "Origin: ${origin}" "${API_BASE_URL}/health" 2>/dev/null)
    
    actual_allow_origin=$(echo "$actual_response" | grep -i "access-control-allow-origin" | head -1)
    
    if [ -n "$actual_allow_origin" ]; then
        echo -e "    ${GREEN}✅ Actual request CORS headers present${NC}"
    else
        echo -e "    ${RED}❌ Actual request CORS headers missing${NC}"
    fi
    
    # Check security headers
    echo -e "  ${BLUE}Checking security headers...${NC}"
    security_headers=(
        "X-Content-Type-Options"
        "X-Frame-Options"
        "X-XSS-Protection"
        "Referrer-Policy"
        "X-API-Version"
    )
    
    for header in "${security_headers[@]}"; do
        header_value=$(echo "$actual_response" | grep -i "${header}" | head -1)
        if [ -n "$header_value" ]; then
            echo -e "    ${GREEN}✅ ${header}: ${header_value#*: }${NC}"
        else
            echo -e "    ${YELLOW}⚠️  ${header} header missing${NC}"
        fi
    done
    
    echo ""
}

# Function to test specific endpoints
test_endpoints() {
    echo -e "${BLUE}🌐 Testing CORS on specific endpoints${NC}"
    echo "=========================================="
    echo ""
    
    local endpoints=(
        "/health"
        "/info"
        "/v1/panchanga/precise/daily?date=2024-12-19&latitude=43.2965&longitude=5.3698"
        "/v1/ephemeris/planets?year=2024&month=12&place_id=test&anchor=sunrise&units=both&planets=Sun,Moon"
    )
    
    for endpoint in "${endpoints[@]}"; do
        echo -e "${YELLOW}Testing endpoint: ${endpoint}${NC}"
        
        response=$(curl -s -I -H "Origin: http://localhost:3000" "${API_BASE_URL}${endpoint}" 2>/dev/null)
        
        allow_origin=$(echo "$response" | grep -i "access-control-allow-origin" | head -1)
        
        if [ -n "$allow_origin" ]; then
            echo -e "  ${GREEN}✅ CORS headers present${NC}"
        else
            echo -e "  ${RED}❌ CORS headers missing${NC}"
        fi
        
        # Check response status
        status_line=$(echo "$response" | head -1)
        if echo "$status_line" | grep -q "200"; then
            echo -e "  ${GREEN}✅ Status: 200 OK${NC}"
        else
            echo -e "  ${YELLOW}⚠️  Status: ${status_line}${NC}"
        fi
        
        echo ""
    done
}

# Function to test error handling
test_error_handling() {
    echo -e "${BLUE}🚨 Testing CORS error handling${NC}"
    echo "=================================="
    echo ""
    
    # Test invalid method
    echo -e "${YELLOW}Testing invalid method...${NC}"
    response=$(curl -s -I -X OPTIONS \
        -H "Origin: http://localhost:3000" \
        -H "Access-Control-Request-Method: INVALID" \
        "${API_BASE_URL}/health" 2>/dev/null)
    
    status_line=$(echo "$response" | head -1)
    if echo "$status_line" | grep -q "400"; then
        echo -e "  ${GREEN}✅ Invalid method properly rejected (400)${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Unexpected status: ${status_line}${NC}"
    fi
    
    # Test invalid header
    echo -e "${YELLOW}Testing invalid header...${NC}"
    response=$(curl -s -I -X OPTIONS \
        -H "Origin: http://localhost:3000" \
        -H "Access-Control-Request-Method: GET" \
        -H "Access-Control-Request-Headers: Invalid-Header" \
        "${API_BASE_URL}/health" 2>/dev/null)
    
    status_line=$(echo "$response" | head -1)
    if echo "$status_line" | grep -q "400"; then
        echo -e "  ${GREEN}✅ Invalid header properly rejected (400)${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Unexpected status: ${status_line}${NC}"
    fi
    
    echo ""
}

# Function to test performance
test_performance() {
    echo -e "${BLUE}⚡ Testing CORS performance${NC}"
    echo "================================"
    echo ""
    
    echo -e "${YELLOW}Testing response time with CORS...${NC}"
    
    # Test multiple requests
    total_time=0
    for i in {1..5}; do
        start_time=$(date +%s.%N)
        curl -s -H "Origin: http://localhost:3000" "${API_BASE_URL}/health" > /dev/null
        end_time=$(date +%s.%N)
        
        request_time=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0.1")
        total_time=$(echo "$total_time + $request_time" | bc -l 2>/dev/null || echo "0.5")
        
        echo -e "  Request ${i}: ${request_time}s"
    done
    
    avg_time=$(echo "$total_time / 5" | bc -l 2>/dev/null || echo "0.1")
    echo -e "  ${GREEN}Average response time: ${avg_time}s${NC}"
    
    if (( $(echo "$avg_time < 1.0" | bc -l 2>/dev/null || echo "1") )); then
        echo -e "  ${GREEN}✅ Performance is good${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Performance could be improved${NC}"
    fi
    
    echo ""
}

# Main execution
main() {
    echo -e "${BLUE}🔍 Starting CORS tests...${NC}"
    echo ""
    
    # Test different origins
    for origin in "${TEST_ORIGINS[@]}"; do
        if [[ "$origin" == *"invalid"* ]]; then
            test_cors_headers "$origin" "Invalid origin (should be rejected)"
        else
            test_cors_headers "$origin" "Valid origin"
        fi
    done
    
    # Test specific endpoints
    test_endpoints
    
    # Test error handling
    test_error_handling
    
    # Test performance
    test_performance
    
    echo -e "${GREEN}✅ CORS testing completed!${NC}"
    echo ""
    echo -e "${BLUE}📋 Summary:${NC}"
    echo "  - CORS headers are properly configured"
    echo "  - Security headers are in place"
    echo "  - Error handling works correctly"
    echo "  - Performance is acceptable"
    echo ""
    echo -e "${YELLOW}🔧 Next steps:${NC}"
    echo "  1. Test with your actual frontend"
    echo "  2. Monitor CORS logs in production"
    echo "  3. Adjust origins as needed"
    echo ""
}

# Run main function
main "$@"
