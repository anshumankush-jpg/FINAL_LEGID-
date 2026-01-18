#!/bin/bash

# ============================================================================
# LEGID - Automated Deployment to Google Cloud Run (Bash version)
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ID="${1:-}"
REGION="${2:-us-central1}"
BACKEND_SERVICE="legid-backend"
FRONTEND_SERVICE="legid-frontend"

echo -e "${CYAN}============================================================================${NC}"
echo -e "${CYAN}🚀 LEGID Cloud Run Deployment Script${NC}"
echo -e "${CYAN}============================================================================${NC}\n"

if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}Usage: $0 <PROJECT_ID> [REGION]${NC}"
    echo -e "${YELLOW}Example: $0 my-project-id us-central1${NC}\n"
    read -p "Enter your GCP Project ID: " PROJECT_ID
fi

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Backend Service: $BACKEND_SERVICE"
echo "  Frontend Service: $FRONTEND_SERVICE"
echo ""

# ============================================================================
# Check Prerequisites
# ============================================================================

check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ Google Cloud SDK not installed!${NC}"
        echo -e "${YELLOW}   Download from: https://cloud.google.com/sdk/docs/install${NC}"
        exit 1
    fi
}

# ============================================================================
# Enable APIs
# ============================================================================

enable_apis() {
    echo -e "\n${CYAN}📡 Enabling required GCP APIs...${NC}"
    
    apis=(
        "cloudbuild.googleapis.com"
        "run.googleapis.com"
        "containerregistry.googleapis.com"
        "artifactregistry.googleapis.com"
        "secretmanager.googleapis.com"
        "bigquery.googleapis.com"
    )
    
    for api in "${apis[@]}"; do
        echo "  Enabling $api..."
        gcloud services enable "$api" --project="$PROJECT_ID" 2>&1 | grep -v "already enabled" || true
    done
    
    echo -e "${GREEN}✅ APIs enabled successfully!${NC}"
}

# ============================================================================
# Create Secrets
# ============================================================================

create_secrets() {
    echo -e "\n${CYAN}🔐 Setting up Secret Manager...${NC}"
    
    # Function to create or update secret
    create_secret() {
        local secret_name=$1
        local prompt=$2
        local auto_generate=$3
        
        # Check if secret exists
        if gcloud secrets describe "$secret_name" --project="$PROJECT_ID" &> /dev/null; then
            echo -e "  ${YELLOW}⏭️  Secret $secret_name already exists, skipping...${NC}"
            return
        fi
        
        local value
        if [ "$auto_generate" = "true" ]; then
            read -p "$prompt (press Enter for auto-generated): " value
            if [ -z "$value" ]; then
                value=$(openssl rand -base64 32)
                echo "  Generated: ${value:0:20}..."
            fi
        else
            read -sp "$prompt: " value
            echo ""
        fi
        
        if [ -n "$value" ]; then
            echo "  Creating secret: $secret_name..."
            echo -n "$value" | gcloud secrets create "$secret_name" --data-file=- --project="$PROJECT_ID" 2>&1 | grep -v "Created secret" || true
            echo -e "  ${GREEN}✅ Secret $secret_name created${NC}"
        fi
    }
    
    # Required secrets
    create_secret "OPENAI_API_KEY" "Enter your OpenAI API Key" "false"
    create_secret "JWT_SECRET_KEY" "Enter JWT Secret" "true"
    
    # Optional secrets
    echo -e "\n${YELLOW}Optional OAuth secrets (press Enter to skip):${NC}"
    create_secret "GOOGLE_CLIENT_ID" "Enter Google OAuth Client ID" "false"
    create_secret "GOOGLE_CLIENT_SECRET" "Enter Google OAuth Client Secret" "false"
    create_secret "MICROSOFT_CLIENT_ID" "Enter Microsoft OAuth Client ID" "false"
    create_secret "MICROSOFT_CLIENT_SECRET" "Enter Microsoft OAuth Client Secret" "false"
}

# ============================================================================
# Deploy Backend
# ============================================================================

deploy_backend() {
    echo -e "\n${CYAN}🔨 Building and Deploying Backend...${NC}"
    
    # Build using Cloud Build
    echo "  Building container..."
    gcloud builds submit --config cloudbuild-backend.yaml --project="$PROJECT_ID"
    
    # Get backend URL
    BACKEND_URL=$(gcloud run services describe "$BACKEND_SERVICE" --region="$REGION" --format='value(status.url)' --project="$PROJECT_ID" 2>/dev/null || echo "")
    
    if [ -n "$BACKEND_URL" ]; then
        echo -e "\n${GREEN}✅ Backend deployed successfully!${NC}"
        echo -e "   ${CYAN}URL: $BACKEND_URL${NC}"
    else
        echo -e "${RED}❌ Backend deployment failed!${NC}"
        exit 1
    fi
}

# ============================================================================
# Deploy Frontend
# ============================================================================

deploy_frontend() {
    echo -e "\n${CYAN}🔨 Building and Deploying Frontend...${NC}"
    
    # Get backend URL
    BACKEND_URL=$(gcloud run services describe "$BACKEND_SERVICE" --region="$REGION" --format='value(status.url)' --project="$PROJECT_ID" 2>/dev/null || echo "")
    
    if [ -z "$BACKEND_URL" ]; then
        echo -e "${YELLOW}⚠️  Backend not found. Please deploy backend first.${NC}"
        read -p "Enter Backend URL manually (or press Enter to skip): " BACKEND_URL
        if [ -z "$BACKEND_URL" ]; then
            echo -e "${RED}❌ Cannot deploy frontend without backend URL${NC}"
            return
        fi
    fi
    
    echo "  Using Backend URL: $BACKEND_URL"
    
    # Build using Cloud Build
    echo "  Building container..."
    gcloud builds submit --config cloudbuild-frontend.yaml \
        --substitutions=_BACKEND_URL="$BACKEND_URL" \
        --project="$PROJECT_ID"
    
    # Get frontend URL
    FRONTEND_URL=$(gcloud run services describe "$FRONTEND_SERVICE" --region="$REGION" --format='value(status.url)' --project="$PROJECT_ID" 2>/dev/null || echo "")
    
    if [ -n "$FRONTEND_URL" ]; then
        echo -e "\n${GREEN}✅ Frontend deployed successfully!${NC}"
        echo -e "   ${CYAN}URL: $FRONTEND_URL${NC}"
    else
        echo -e "${RED}❌ Frontend deployment failed!${NC}"
        exit 1
    fi
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    # Check prerequisites
    check_gcloud
    
    # Set project
    echo -e "\n${CYAN}🔧 Setting GCP project...${NC}"
    gcloud config set project "$PROJECT_ID"
    
    # Enable APIs
    enable_apis
    
    # Create secrets
    read -p "Do you want to create/update secrets? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_secrets
    fi
    
    # Deploy backend
    read -p "Deploy backend? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        deploy_backend
    fi
    
    # Deploy frontend
    read -p "Deploy frontend? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        deploy_frontend
    fi
    
    # Final summary
    echo -e "\n${CYAN}============================================================================${NC}"
    echo -e "${GREEN}🎉 Deployment Complete!${NC}"
    echo -e "${CYAN}============================================================================${NC}"
    
    BACKEND_URL=$(gcloud run services describe "$BACKEND_SERVICE" --region="$REGION" --format='value(status.url)' --project="$PROJECT_ID" 2>/dev/null || echo "")
    FRONTEND_URL=$(gcloud run services describe "$FRONTEND_SERVICE" --region="$REGION" --format='value(status.url)' --project="$PROJECT_ID" 2>/dev/null || echo "")
    
    if [ -n "$BACKEND_URL" ]; then
        echo -e "\n${YELLOW}📡 Backend Service:${NC}"
        echo -e "   ${CYAN}URL: $BACKEND_URL${NC}"
        echo "   Health: $BACKEND_URL/health"
    fi
    
    if [ -n "$FRONTEND_URL" ]; then
        echo -e "\n${YELLOW}🌐 Frontend Service:${NC}"
        echo -e "   ${CYAN}URL: $FRONTEND_URL${NC}"
    fi
    
    echo -e "\n${YELLOW}⚠️  Next Steps:${NC}"
    echo "   1. Update OAuth redirect URIs with Cloud Run URLs"
    echo "   2. Test the deployment"
    echo "   3. Set up Cloud Build triggers for auto-deploy"
    echo ""
}

# Run main function
main
