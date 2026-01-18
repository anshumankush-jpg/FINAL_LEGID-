# ============================================================================
# LEGID - Complete Cloud Run Deployment Script
# Deploys Backend and Frontend from GitHub to Google Cloud Run
# ============================================================================

# Configuration - UPDATE THESE VALUES
$PROJECT_ID = "legid-project"  # Your GCP Project ID
$REGION = "us-central1"        # Cloud Run region
$BACKEND_SERVICE = "legid-backend"
$FRONTEND_SERVICE = "legid-frontend"
$REPO_URL = "https://github.com/anshumankush-jpg/FINAL_LEGID-.git"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  LEGID - Cloud Run Deployment" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if gcloud is installed
Write-Host "[1/8] Checking Google Cloud SDK..." -ForegroundColor Yellow
try {
    $gcloudVersion = gcloud --version 2>$null
    Write-Host "✓ Google Cloud SDK is installed" -ForegroundColor Green
} catch {
    Write-Host "✗ Google Cloud SDK not found. Please install it from:" -ForegroundColor Red
    Write-Host "  https://cloud.google.com/sdk/docs/install" -ForegroundColor White
    exit 1
}

# Step 2: Authenticate with GCP
Write-Host ""
Write-Host "[2/8] Authenticating with Google Cloud..." -ForegroundColor Yellow
gcloud auth login --brief 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Authentication failed" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Authenticated successfully" -ForegroundColor Green

# Step 3: Set the project
Write-Host ""
Write-Host "[3/8] Setting GCP Project to: $PROJECT_ID" -ForegroundColor Yellow
gcloud config set project $PROJECT_ID
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to set project. Make sure the project exists." -ForegroundColor Red
    exit 1
}
Write-Host "✓ Project set to $PROJECT_ID" -ForegroundColor Green

# Step 4: Enable required APIs
Write-Host ""
Write-Host "[4/8] Enabling required GCP APIs..." -ForegroundColor Yellow
$apis = @(
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "containerregistry.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com"
)
foreach ($api in $apis) {
    Write-Host "  Enabling $api..." -ForegroundColor Gray
    gcloud services enable $api --quiet 2>$null
}
Write-Host "✓ All APIs enabled" -ForegroundColor Green

# Step 5: Build and Deploy Backend
Write-Host ""
Write-Host "[5/8] Building and Deploying Backend..." -ForegroundColor Yellow
Write-Host "  This may take 5-10 minutes..." -ForegroundColor Gray

Set-Location -Path "backend"

# Build the container
gcloud builds submit --tag gcr.io/$PROJECT_ID/$BACKEND_SERVICE

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Backend build failed" -ForegroundColor Red
    Set-Location -Path ".."
    exit 1
}

# Deploy to Cloud Run
gcloud run deploy $BACKEND_SERVICE `
    --image gcr.io/$PROJECT_ID/$BACKEND_SERVICE `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --memory 2Gi `
    --cpu 2 `
    --timeout 300 `
    --set-env-vars "ENVIRONMENT=production" `
    --set-env-vars "LOG_LEVEL=INFO" `
    --min-instances 1 `
    --max-instances 10

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Backend deployment failed" -ForegroundColor Red
    Set-Location -Path ".."
    exit 1
}

# Get backend URL
$BACKEND_URL = gcloud run services describe $BACKEND_SERVICE --platform managed --region $REGION --format "value(status.url)"
Write-Host "✓ Backend deployed: $BACKEND_URL" -ForegroundColor Green

Set-Location -Path ".."

# Step 6: Build and Deploy Frontend
Write-Host ""
Write-Host "[6/8] Building and Deploying Frontend..." -ForegroundColor Yellow
Write-Host "  This may take 5-10 minutes..." -ForegroundColor Gray

Set-Location -Path "frontend"

# Update frontend to use production backend URL
$envFile = "src/environments/environment.prod.ts"
$envContent = @"
export const environment = {
  production: true,
  apiUrl: '$BACKEND_URL'
};
"@
Set-Content -Path $envFile -Value $envContent

# Build the container
gcloud builds submit --tag gcr.io/$PROJECT_ID/$FRONTEND_SERVICE

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Frontend build failed" -ForegroundColor Red
    Set-Location -Path ".."
    exit 1
}

# Deploy to Cloud Run
gcloud run deploy $FRONTEND_SERVICE `
    --image gcr.io/$PROJECT_ID/$FRONTEND_SERVICE `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --memory 512Mi `
    --cpu 1 `
    --timeout 60 `
    --min-instances 0 `
    --max-instances 5

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Frontend deployment failed" -ForegroundColor Red
    Set-Location -Path ".."
    exit 1
}

# Get frontend URL
$FRONTEND_URL = gcloud run services describe $FRONTEND_SERVICE --platform managed --region $REGION --format "value(status.url)"
Write-Host "✓ Frontend deployed: $FRONTEND_URL" -ForegroundColor Green

Set-Location -Path ".."

# Step 7: Configure Secrets (Optional)
Write-Host ""
Write-Host "[7/8] Setting up secrets..." -ForegroundColor Yellow
Write-Host "  Note: You need to set secrets manually in Cloud Console or via gcloud" -ForegroundColor Gray
Write-Host "  Required secrets:" -ForegroundColor Gray
Write-Host "    - OPENAI_API_KEY" -ForegroundColor White
Write-Host "    - JWT_SECRET_KEY" -ForegroundColor White
Write-Host "    - GOOGLE_CLIENT_ID" -ForegroundColor White
Write-Host "    - GOOGLE_CLIENT_SECRET" -ForegroundColor White
Write-Host "    - MICROSOFT_CLIENT_ID (optional)" -ForegroundColor White
Write-Host "    - MICROSOFT_CLIENT_SECRET (optional)" -ForegroundColor White

# Step 8: Summary
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your LEGID application is now live:" -ForegroundColor White
Write-Host ""
Write-Host "  Frontend:  $FRONTEND_URL" -ForegroundColor Green
Write-Host "  Backend:   $BACKEND_URL" -ForegroundColor Green
Write-Host "  API Docs:  $BACKEND_URL/docs" -ForegroundColor Green
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Set environment variables in Cloud Run console" -ForegroundColor White
Write-Host "2. Update OAuth redirect URIs in Google/Microsoft console" -ForegroundColor White
Write-Host "3. Configure custom domain (optional)" -ForegroundColor White
Write-Host ""
