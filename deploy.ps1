# Complete GCP Cloud Run Deployment Script for Windows
# Run: .\deploy.ps1

$ErrorActionPreference = "Stop"

# Configuration
$PROJECT_ID = if ($env:GCP_PROJECT_ID) { $env:GCP_PROJECT_ID } else { Read-Host "Enter GCP Project ID" }
$REGION = "us-central1"
$BACKEND_SERVICE = "legal-bot-backend"
$FRONTEND_SERVICE = "legal-bot-frontend"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Legal AI - Cloud Run Deployment" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Project: $PROJECT_ID"
Write-Host "Region:  $REGION"
Write-Host "============================================" -ForegroundColor Cyan

# Check gcloud
try {
    gcloud --version | Out-Null
} catch {
    Write-Host "ERROR: gcloud CLI not installed" -ForegroundColor Red
    Write-Host "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
}

# Set project
Write-Host "`nStep 1: Setting up GCP project..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID

# Enable APIs
Write-Host "`nStep 2: Enabling required APIs..." -ForegroundColor Yellow
gcloud services enable `
    cloudbuild.googleapis.com `
    run.googleapis.com `
    containerregistry.googleapis.com `
    secretmanager.googleapis.com `
    bigquery.googleapis.com

# Create secrets
Write-Host "`nStep 3: Setting up secrets..." -ForegroundColor Yellow
Write-Host "Enter your API keys (or press Enter to skip if already set):"

$OPENAI_KEY = Read-Host "OpenAI API Key" -AsSecureString
if ($OPENAI_KEY.Length -gt 0) {
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($OPENAI_KEY)
    $OPENAI_KEY_PLAIN = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    $OPENAI_KEY_PLAIN | gcloud secrets create OPENAI_API_KEY --data-file=- 2>$null
    if ($LASTEXITCODE -ne 0) {
        $OPENAI_KEY_PLAIN | gcloud secrets versions add OPENAI_API_KEY --data-file=-
    }
}

$GOOGLE_ID = Read-Host "Google OAuth Client ID"
if ($GOOGLE_ID) {
    $GOOGLE_ID | gcloud secrets create GOOGLE_CLIENT_ID --data-file=- 2>$null
    if ($LASTEXITCODE -ne 0) {
        $GOOGLE_ID | gcloud secrets versions add GOOGLE_CLIENT_ID --data-file=-
    }
}

$GOOGLE_SECRET = Read-Host "Google OAuth Client Secret" -AsSecureString
if ($GOOGLE_SECRET.Length -gt 0) {
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($GOOGLE_SECRET)
    $GOOGLE_SECRET_PLAIN = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    $GOOGLE_SECRET_PLAIN | gcloud secrets create GOOGLE_CLIENT_SECRET --data-file=- 2>$null
    if ($LASTEXITCODE -ne 0) {
        $GOOGLE_SECRET_PLAIN | gcloud secrets versions add GOOGLE_CLIENT_SECRET --data-file=-
    }
}

$MS_ID = Read-Host "Microsoft OAuth Client ID (optional)"
if ($MS_ID) {
    $MS_ID | gcloud secrets create MICROSOFT_CLIENT_ID --data-file=- 2>$null
    if ($LASTEXITCODE -ne 0) {
        $MS_ID | gcloud secrets versions add MICROSOFT_CLIENT_ID --data-file=-
    }
}

$MS_SECRET = Read-Host "Microsoft OAuth Client Secret (optional)" -AsSecureString
if ($MS_SECRET.Length -gt 0) {
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($MS_SECRET)
    $MS_SECRET_PLAIN = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    $MS_SECRET_PLAIN | gcloud secrets create MICROSOFT_CLIENT_SECRET --data-file=- 2>$null
    if ($LASTEXITCODE -ne 0) {
        $MS_SECRET_PLAIN | gcloud secrets versions add MICROSOFT_CLIENT_SECRET --data-file=-
    }
}

# Generate JWT secret
$JWT_SECRET = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object {[char]$_})
$JWT_SECRET | gcloud secrets create JWT_SECRET_KEY --data-file=- 2>$null
if ($LASTEXITCODE -ne 0) {
    $JWT_SECRET | gcloud secrets versions add JWT_SECRET_KEY --data-file=-
}

# Grant secret access
Write-Host "`nStep 4: Granting secret access..." -ForegroundColor Yellow
$PROJECT_NUMBER = (gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding OPENAI_API_KEY `
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" `
    --role="roles/secretmanager.secretAccessor" 2>$null

# Deploy
Write-Host "`nStep 5: Starting Cloud Build deployment..." -ForegroundColor Yellow
Write-Host "This may take 10-15 minutes..." -ForegroundColor Yellow
gcloud builds submit --config=cloudbuild.yaml .

Write-Host "`n============================================" -ForegroundColor Green
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green

# Get URLs
$BACKEND_URL = gcloud run services describe $BACKEND_SERVICE --region=$REGION --format='value(status.url)' 2>$null
$FRONTEND_URL = gcloud run services describe $FRONTEND_SERVICE --region=$REGION --format='value(status.url)' 2>$null

Write-Host "`nYour application URLs:"
Write-Host "  Frontend: $FRONTEND_URL" -ForegroundColor Cyan
Write-Host "  Backend:  $BACKEND_URL" -ForegroundColor Cyan
Write-Host "  API Docs: $BACKEND_URL/docs" -ForegroundColor Cyan
Write-Host "`nIMPORTANT: Update your OAuth redirect URIs:" -ForegroundColor Yellow
Write-Host "  Google:    $BACKEND_URL/api/auth/google/callback" -ForegroundColor Yellow
Write-Host "  Microsoft: $BACKEND_URL/api/auth/microsoft/callback" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Green
