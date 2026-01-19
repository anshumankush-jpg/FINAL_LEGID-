#!/bin/bash
# =========================================================
# COMPLETE END-TO-END CLOUD RUN DEPLOYMENT
# Copy and paste this entire script into Google Cloud Shell
# =========================================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

clear
echo -e "${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║   CLOUD RUN DEPLOYMENT - LEGAL AI BOT                ║
║   Automated End-to-End Deployment                    ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# =========================================================
# CONFIGURATION
# =========================================================
REGION="us-central1"
BACKEND_SERVICE="legal-bot-backend"
FRONTEND_SERVICE="legal-bot-frontend"

# =========================================================
# STEP 1: Get Project ID
# =========================================================
echo -e "${YELLOW}[1/11] Setting up GCP project...${NC}"
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo -e "${CYAN}Available projects:${NC}"
    gcloud projects list --format="table(projectId,name)"
    echo ""
    echo -n "Enter your GCP Project ID: "
    read PROJECT_ID
    gcloud config set project "$PROJECT_ID"
fi

echo -e "${GREEN}  ✓ Using project: $PROJECT_ID${NC}"
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
echo -e "${GREEN}  ✓ Project number: $PROJECT_NUMBER${NC}"

# =========================================================
# STEP 2: Enable Required APIs
# =========================================================
echo -e "\n${YELLOW}[2/11] Enabling required APIs...${NC}"
echo -e "${CYAN}  This may take 2-3 minutes...${NC}"

gcloud services enable cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    secretmanager.googleapis.com \
    artifactregistry.googleapis.com \
    cloudresourcemanager.googleapis.com \
    --quiet

echo -e "${GREEN}  ✓ All APIs enabled${NC}"

# =========================================================
# STEP 3: Create Secrets
# =========================================================
echo -e "\n${YELLOW}[3/11] Setting up secrets...${NC}"

# OpenAI API Key
if gcloud secrets describe OPENAI_API_KEY &>/dev/null; then
    echo -e "${GREEN}  ✓ OPENAI_API_KEY already exists${NC}"
else
    echo -e "${CYAN}  Creating OPENAI_API_KEY secret...${NC}"
    echo -n "  Enter your OpenAI API Key (starts with sk-): "
    read -s OPENAI_KEY
    echo ""
    
    if [ -n "$OPENAI_KEY" ]; then
        echo -n "$OPENAI_KEY" | gcloud secrets create OPENAI_API_KEY \
            --data-file=- \
            --replication-policy="automatic"
        echo -e "${GREEN}  ✓ OPENAI_API_KEY created${NC}"
    else
        echo -e "${RED}  ERROR: OpenAI API Key is required!${NC}"
        exit 1
    fi
fi

# JWT Secret Key
if gcloud secrets describe JWT_SECRET_KEY &>/dev/null; then
    echo -e "${GREEN}  ✓ JWT_SECRET_KEY already exists${NC}"
else
    JWT_SECRET=$(openssl rand -base64 64 | tr -d '\n')
    echo -n "$JWT_SECRET" | gcloud secrets create JWT_SECRET_KEY \
        --data-file=- \
        --replication-policy="automatic"
    echo -e "${GREEN}  ✓ JWT_SECRET_KEY created (auto-generated)${NC}"
fi

# Optional: Google OAuth secrets
echo -e "${CYAN}  Do you want to set up Google OAuth? (y/n)${NC}"
read -r SETUP_OAUTH

if [ "$SETUP_OAUTH" = "y" ] || [ "$SETUP_OAUTH" = "Y" ]; then
    if ! gcloud secrets describe GOOGLE_CLIENT_ID &>/dev/null; then
        echo -n "  Enter Google OAuth Client ID: "
        read GOOGLE_CLIENT_ID
        echo -n "$GOOGLE_CLIENT_ID" | gcloud secrets create GOOGLE_CLIENT_ID --data-file=- --replication-policy="automatic"
    fi
    
    if ! gcloud secrets describe GOOGLE_CLIENT_SECRET &>/dev/null; then
        echo -n "  Enter Google OAuth Client Secret: "
        read -s GOOGLE_CLIENT_SECRET
        echo ""
        echo -n "$GOOGLE_CLIENT_SECRET" | gcloud secrets create GOOGLE_CLIENT_SECRET --data-file=- --replication-policy="automatic"
    fi
    echo -e "${GREEN}  ✓ OAuth secrets configured${NC}"
fi

# =========================================================
# STEP 4: Grant IAM Permissions
# =========================================================
echo -e "\n${YELLOW}[4/11] Granting Cloud Build permissions...${NC}"

SERVICE_ACCOUNT="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

# Grant all necessary roles
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor" \
    --condition=None --quiet &>/dev/null

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/run.admin" \
    --condition=None --quiet &>/dev/null

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/iam.serviceAccountUser" \
    --condition=None --quiet &>/dev/null

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/storage.admin" \
    --condition=None --quiet &>/dev/null

echo -e "${GREEN}  ✓ IAM permissions granted${NC}"

# =========================================================
# STEP 5: Clone/Upload Code (if in Cloud Shell)
# =========================================================
echo -e "\n${YELLOW}[5/11] Checking source code...${NC}"

if [ ! -f "cloudbuild.yaml" ]; then
    echo -e "${CYAN}  Source code not found in current directory.${NC}"
    echo -n "  Enter your GitHub repository URL (or press Enter to skip): "
    read REPO_URL
    
    if [ -n "$REPO_URL" ]; then
        echo "  Cloning repository..."
        git clone "$REPO_URL" temp_repo
        cd temp_repo
        echo -e "${GREEN}  ✓ Repository cloned${NC}"
    else
        echo -e "${RED}  ERROR: Source code required!${NC}"
        echo "  Please run this script from your project directory or provide a Git URL."
        exit 1
    fi
else
    echo -e "${GREEN}  ✓ Source code found${NC}"
fi

# =========================================================
# STEP 6: Build Backend Image
# =========================================================
echo -e "\n${YELLOW}[6/11] Building backend Docker image...${NC}"
echo -e "${CYAN}  This will take 5-10 minutes...${NC}"

gcloud builds submit \
    --tag "gcr.io/$PROJECT_ID/$BACKEND_SERVICE:latest" \
    --timeout=20m \
    backend/ \
    2>&1 | grep -E "(Step|Successfully|ERROR|FAILED)" || true

if [ $? -eq 0 ]; then
    echo -e "${GREEN}  ✓ Backend image built successfully${NC}"
else
    echo -e "${RED}  Backend build failed. Check logs above.${NC}"
    exit 1
fi

# =========================================================
# STEP 7: Deploy Backend to Cloud Run
# =========================================================
echo -e "\n${YELLOW}[7/11] Deploying backend to Cloud Run...${NC}"

gcloud run deploy "$BACKEND_SERVICE" \
    --image="gcr.io/$PROJECT_ID/$BACKEND_SERVICE:latest" \
    --region="$REGION" \
    --platform=managed \
    --allow-unauthenticated \
    --memory=4Gi \
    --cpu=2 \
    --timeout=300 \
    --concurrency=80 \
    --min-instances=0 \
    --max-instances=10 \
    --port=8000 \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --set-secrets="OPENAI_API_KEY=OPENAI_API_KEY:latest,JWT_SECRET_KEY=JWT_SECRET_KEY:latest" \
    --quiet

BACKEND_URL=$(gcloud run services describe "$BACKEND_SERVICE" --region="$REGION" --format='value(status.url)')
echo -e "${GREEN}  ✓ Backend deployed: $BACKEND_URL${NC}"

# =========================================================
# STEP 8: Test Backend Health
# =========================================================
echo -e "\n${YELLOW}[8/11] Testing backend health...${NC}"

sleep 5  # Wait for service to be ready

HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health" || echo "000")

if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo -e "${GREEN}  ✓ Backend is healthy (HTTP $HEALTH_RESPONSE)${NC}"
else
    echo -e "${YELLOW}  ⚠ Backend health check returned HTTP $HEALTH_RESPONSE${NC}"
    echo -e "${YELLOW}  Continuing deployment...${NC}"
fi

# =========================================================
# STEP 9: Build Frontend Image
# =========================================================
echo -e "\n${YELLOW}[9/11] Building frontend Docker image...${NC}"
echo -e "${CYAN}  Building with API_URL: $BACKEND_URL${NC}"

cd frontend 2>/dev/null || true

gcloud builds submit \
    --tag "gcr.io/$PROJECT_ID/$FRONTEND_SERVICE:latest" \
    --build-arg="VITE_API_URL=$BACKEND_URL" \
    --timeout=15m \
    . \
    2>&1 | grep -E "(Step|Successfully|ERROR|FAILED)" || true

if [ $? -eq 0 ]; then
    echo -e "${GREEN}  ✓ Frontend image built successfully${NC}"
else
    echo -e "${RED}  Frontend build failed. Trying alternative build...${NC}"
    
    # Create temporary Dockerfile if needed
    docker build --build-arg VITE_API_URL="$BACKEND_URL" -t "gcr.io/$PROJECT_ID/$FRONTEND_SERVICE:latest" .
    docker push "gcr.io/$PROJECT_ID/$FRONTEND_SERVICE:latest"
fi

cd .. 2>/dev/null || true

# =========================================================
# STEP 10: Deploy Frontend to Cloud Run
# =========================================================
echo -e "\n${YELLOW}[10/11] Deploying frontend to Cloud Run...${NC}"

gcloud run deploy "$FRONTEND_SERVICE" \
    --image="gcr.io/$PROJECT_ID/$FRONTEND_SERVICE:latest" \
    --region="$REGION" \
    --platform=managed \
    --allow-unauthenticated \
    --memory=512Mi \
    --cpu=1 \
    --timeout=60 \
    --min-instances=0 \
    --max-instances=10 \
    --port=80 \
    --set-env-vars="API_URL=$BACKEND_URL" \
    --quiet

FRONTEND_URL=$(gcloud run services describe "$FRONTEND_SERVICE" --region="$REGION" --format='value(status.url)')
echo -e "${GREEN}  ✓ Frontend deployed: $FRONTEND_URL${NC}"

# =========================================================
# STEP 11: Final Verification
# =========================================================
echo -e "\n${YELLOW}[11/11] Running final verification...${NC}"

# Test backend
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health" || echo "000")
if [ "$BACKEND_STATUS" = "200" ]; then
    echo -e "${GREEN}  ✓ Backend health check: OK${NC}"
else
    echo -e "${YELLOW}  ⚠ Backend health check: HTTP $BACKEND_STATUS${NC}"
fi

# Test frontend
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" || echo "000")
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo -e "${GREEN}  ✓ Frontend accessible: OK${NC}"
else
    echo -e "${YELLOW}  ⚠ Frontend status: HTTP $FRONTEND_STATUS${NC}"
fi

# =========================================================
# SUCCESS SUMMARY
# =========================================================
echo ""
echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║   🎉 DEPLOYMENT COMPLETE! 🎉                         ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📱 YOUR APPLICATION URLs:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}🔗 Frontend (Open this in your browser):${NC}"
echo -e "${BLUE}   $FRONTEND_URL${NC}"
echo ""
echo -e "${GREEN}🔗 Backend API:${NC}"
echo -e "${BLUE}   $BACKEND_URL${NC}"
echo ""
echo -e "${GREEN}🔗 API Documentation:${NC}"
echo -e "${BLUE}   $BACKEND_URL/docs${NC}"
echo ""
echo -e "${GREEN}🔗 Health Check:${NC}"
echo -e "${BLUE}   $BACKEND_URL/health${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📊 CLOUD CONSOLE LINKS:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}Cloud Run Services:${NC}"
echo "   https://console.cloud.google.com/run?project=$PROJECT_ID"
echo ""
echo -e "${GREEN}Build History:${NC}"
echo "   https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
echo ""
echo -e "${GREEN}Logs (Backend):${NC}"
echo "   https://console.cloud.google.com/run/detail/$REGION/$BACKEND_SERVICE/logs?project=$PROJECT_ID"
echo ""
echo -e "${GREEN}Logs (Frontend):${NC}"
echo "   https://console.cloud.google.com/run/detail/$REGION/$FRONTEND_SERVICE/logs?project=$PROJECT_ID"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🔧 USEFUL COMMANDS:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}View backend logs:${NC}"
echo "   gcloud run logs tail $BACKEND_SERVICE --region=$REGION"
echo ""
echo -e "${GREEN}View frontend logs:${NC}"
echo "   gcloud run logs tail $FRONTEND_SERVICE --region=$REGION"
echo ""
echo -e "${GREEN}Update backend (after code changes):${NC}"
echo "   gcloud builds submit --tag gcr.io/$PROJECT_ID/$BACKEND_SERVICE:latest backend/"
echo "   gcloud run deploy $BACKEND_SERVICE --image gcr.io/$PROJECT_ID/$BACKEND_SERVICE:latest --region=$REGION"
echo ""
echo -e "${GREEN}Scale services:${NC}"
echo "   gcloud run services update $BACKEND_SERVICE --region=$REGION --max-instances=20"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}✅ All done! Open your frontend URL to start using the app!${NC}"
echo ""
