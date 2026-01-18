#!/bin/bash
# ============================================================================
# LEGID - Complete Cloud Run Deployment Script (Linux/Mac)
# Deploys Backend and Frontend from GitHub to Google Cloud Run
# ============================================================================

set -e

# Configuration - UPDATE THESE VALUES
PROJECT_ID="legid-project"
REGION="us-central1"
BACKEND_SERVICE="legid-backend"
FRONTEND_SERVICE="legid-frontend"

echo "============================================"
echo "  LEGID - Cloud Run Deployment"
echo "============================================"
echo ""

# Step 1: Check if gcloud is installed
echo "[1/8] Checking Google Cloud SDK..."
if ! command -v gcloud &> /dev/null; then
    echo "✗ Google Cloud SDK not found. Please install it from:"
    echo "  https://cloud.google.com/sdk/docs/install"
    exit 1
fi
echo "✓ Google Cloud SDK is installed"

# Step 2: Authenticate with GCP
echo ""
echo "[2/8] Authenticating with Google Cloud..."
gcloud auth login --brief
echo "✓ Authenticated successfully"

# Step 3: Set the project
echo ""
echo "[3/8] Setting GCP Project to: $PROJECT_ID"
gcloud config set project $PROJECT_ID
echo "✓ Project set to $PROJECT_ID"

# Step 4: Enable required APIs
echo ""
echo "[4/8] Enabling required GCP APIs..."
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
gcloud services enable artifactregistry.googleapis.com --quiet
gcloud services enable secretmanager.googleapis.com --quiet
echo "✓ All APIs enabled"

# Step 5: Build and Deploy Backend
echo ""
echo "[5/8] Building and Deploying Backend..."
echo "  This may take 5-10 minutes..."

cd backend

# Build the container
gcloud builds submit --tag gcr.io/$PROJECT_ID/$BACKEND_SERVICE

# Deploy to Cloud Run
gcloud run deploy $BACKEND_SERVICE \
    --image gcr.io/$PROJECT_ID/$BACKEND_SERVICE \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --set-env-vars "ENVIRONMENT=production" \
    --set-env-vars "LOG_LEVEL=INFO" \
    --min-instances 1 \
    --max-instances 10

# Get backend URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --platform managed --region $REGION --format "value(status.url)")
echo "✓ Backend deployed: $BACKEND_URL"

cd ..

# Step 6: Build and Deploy Frontend
echo ""
echo "[6/8] Building and Deploying Frontend..."
echo "  This may take 5-10 minutes..."

cd frontend

# Update frontend to use production backend URL
cat > src/environments/environment.prod.ts << EOF
export const environment = {
  production: true,
  apiUrl: '$BACKEND_URL'
};
EOF

# Build the container
gcloud builds submit --tag gcr.io/$PROJECT_ID/$FRONTEND_SERVICE

# Deploy to Cloud Run
gcloud run deploy $FRONTEND_SERVICE \
    --image gcr.io/$PROJECT_ID/$FRONTEND_SERVICE \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --timeout 60 \
    --min-instances 0 \
    --max-instances 5

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --platform managed --region $REGION --format "value(status.url)")
echo "✓ Frontend deployed: $FRONTEND_URL"

cd ..

# Step 7: Summary
echo ""
echo "============================================"
echo "  DEPLOYMENT COMPLETE!"
echo "============================================"
echo ""
echo "Your LEGID application is now live:"
echo ""
echo "  Frontend:  $FRONTEND_URL"
echo "  Backend:   $BACKEND_URL"
echo "  API Docs:  $BACKEND_URL/docs"
echo ""
echo "============================================"
echo ""
echo "NEXT STEPS:"
echo "1. Set environment variables in Cloud Run console"
echo "2. Update OAuth redirect URIs in Google/Microsoft console"
echo "3. Configure custom domain (optional)"
echo ""
