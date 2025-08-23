#!/bin/bash

# Global Cleanup Script for Jyotiṣa API
# Removes obsolete files and optimizes project structure

set -e

echo "🧹 Global Cleanup - Jyotiṣa API"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to remove files/directories
remove_item() {
    local item="$1"
    local description="$2"
    
    if [ -e "$item" ]; then
        echo -e "${YELLOW}Removing: $description${NC}"
        rm -rf "$item"
        echo -e "${GREEN}✅ Removed: $item${NC}"
    else
        echo -e "${BLUE}⏭️  Skipped: $item (not found)${NC}"
    fi
}

# Remove obsolete Docker files
echo -e "\n${BLUE}🐳 Cleaning Docker files...${NC}"
remove_item "Dockerfile.old" "Old Dockerfile"
remove_item "navatara-service/" "Navatara service directory (integrated)"

# Remove obsolete documentation files
echo -e "\n${BLUE}📚 Cleaning documentation...${NC}"
remove_item "FRONTEND_INTEGRATION_NAVATARA.md" "Obsolete Navatara integration guide"
remove_item "API_ROBUSTNESS_FRONTEND_INTEGRATION.md" "Obsolete robustness guide"
remove_item "navatara-service/FRONTEND_INTEGRATION_GUIDE.md" "Obsolete frontend guide"
remove_item "navatara-service/ROBUSTNESS_SUMMARY.md" "Obsolete robustness summary"
remove_item "navatara-service/CLEANUP_REPORT.md" "Obsolete cleanup report"

# Remove obsolete test files
echo -e "\n${BLUE}🧪 Cleaning test files...${NC}"
remove_item "test_ayanamsa_direct.py" "Obsolete ayanamsa test"
remove_item "test_ayanamsa_precision.py" "Obsolete precision test"

# Remove obsolete configuration files
echo -e "\n${BLUE}⚙️ Cleaning configuration files...${NC}"
remove_item "vercel.json" "Obsolete Vercel config"
remove_item "frontend-integration-example.js" "Obsolete frontend example"

# Remove obsolete deployment files
echo -e "\n${BLUE}🚀 Cleaning deployment files...${NC}"
remove_item "cloud-run-config.yaml" "Obsolete Cloud Run config"
remove_item "cloudbuild.yaml" "Obsolete Cloud Build config"

# Remove obsolete documentation
echo -e "\n${BLUE}📖 Cleaning obsolete documentation...${NC}"
remove_item "FRONTEND_ENV_SETUP.md" "Obsolete env setup guide"
remove_item "FRONTEND_INTEGRATION.md" "Obsolete integration guide"
remove_item "CLOUD_RUN_DEPLOYMENT.md" "Obsolete deployment guide"
remove_item "DEPLOYMENT_GUIDE.md" "Obsolete deployment guide"
remove_item "OPTIMIZATION_GUIDE.md" "Obsolete optimization guide"
remove_item "ROBUSTNESS_IMPROVEMENTS.md" "Obsolete robustness guide"
remove_item "PANCHANGA_PRECISION_IMPROVEMENTS.md" "Obsolete panchanga guide"
remove_item "PANCHANGA_YOGAS_FIX.md" "Obsolete yogas guide"
remove_item "PR_SUMMARY.md" "Obsolete PR summary"
remove_item "STATUS.md" "Obsolete status file"
remove_item "AUDIT_SUMMARY.md" "Obsolete audit summary"
remove_item "CLEANUP_SUMMARY.md" "Obsolete cleanup summary"

# Clean Python cache
echo -e "\n${BLUE}🐍 Cleaning Python cache...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Clean temporary files
echo -e "\n${BLUE}🗂️ Cleaning temporary files...${NC}"
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.temp" -delete 2>/dev/null || true
find . -name "*.log" -delete 2>/dev/null || true

# Clean OS generated files
echo -e "\n${BLUE}💻 Cleaning OS files...${NC}"
find . -name ".DS_Store" -delete 2>/dev/null || true
find . -name "Thumbs.db" -delete 2>/dev/null || true

# Clean IDE files
echo -e "\n${BLUE}🔧 Cleaning IDE files...${NC}"
find . -name ".vscode" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".idea" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.swp" -delete 2>/dev/null || true
find . -name "*.swo" -delete 2>/dev/null || true

# Update .gitignore
echo -e "\n${BLUE}📝 Updating .gitignore...${NC}"
cat >> .gitignore << 'EOF'

# Obsolete files
Dockerfile.old
navatara-service/
FRONTEND_INTEGRATION_NAVATARA.md
API_ROBUSTNESS_FRONTEND_INTEGRATION.md
test_ayanamsa_*.py
vercel.json
frontend-integration-example.js
cloud-run-config.yaml
cloudbuild.yaml

# Obsolete documentation
FRONTEND_ENV_SETUP.md
FRONTEND_INTEGRATION.md
CLOUD_RUN_DEPLOYMENT.md
DEPLOYMENT_GUIDE.md
OPTIMIZATION_GUIDE.md
ROBUSTNESS_IMPROVEMENTS.md
PANCHANGA_PRECISION_IMPROVEMENTS.md
PANCHANGA_YOGAS_FIX.md
PR_SUMMARY.md
STATUS.md
AUDIT_SUMMARY.md
CLEANUP_SUMMARY.md
EOF

echo -e "\n${GREEN}✅ Global cleanup completed!${NC}"

# Show current structure
echo -e "\n${BLUE}📁 Current project structure:${NC}"
echo "================================"
find . -type f -name "*.py" -not -path "*/__pycache__/*" | head -20
echo "..."

# Show remaining documentation
echo -e "\n${BLUE}📚 Remaining documentation:${NC}"
echo "================================"
find . -name "*.md" | head -10
echo "..."

echo -e "\n${GREEN}🎉 Jyotiṣa API is now unified and optimized!${NC}"
echo ""
echo "📋 Next steps:"
echo "1. Test the unified API locally"
echo "2. Deploy to Cloud Run"
echo "3. Update frontend integration"
echo "4. Run comprehensive tests"
