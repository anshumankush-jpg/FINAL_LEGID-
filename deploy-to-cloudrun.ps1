# ============================================================================
# LEGID - Automated Deployment to Google Cloud Run
# ============================================================================

param(
    [string]$ProjectId = "",
    [string]$Region = "us-central1",
    [switch]$SetupOnly,
    [switch]$DeployBackend,
    [switch]$DeployFrontend,
    [switch]$DeployAll
)

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "🚀 LEGID Cloud Run Deployment Script" -ForegroundColor Cyan
Write-Host "============================================================================`n" -ForegroundColor Cyan

# ============================================================================
# CONFIGURATION
# ============================================================================

if (-not $ProjectId) {
    $ProjectId = Read-Host "Enter your GCP Project ID"
}

$BACKEND_SERVICE = "legid-backend"
$FRONTEND_SERVICE = "legid-frontend"
$REPO_URL = "https://github.com/anshumankush-jpg/FINAL_LEGID-.git"

Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "  Project ID: $ProjectId"
Write-Host "  Region: $Region"
Write-Host "  Backend Service: $BACKEND_SERVICE"
Write-Host "  Frontend Service: $FRONTEND_SERVICE"
Write-Host ""

# ============================================================================
# FUNCTION: Check if gcloud is installed
# ============================================================================

function Test-GCloudInstalled {
    try {
        $null = gcloud --version
        return $true
    } catch {
        Write-Host "❌ Google Cloud SDK not installed!" -ForegroundColor Red
        Write-Host "   Download from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
        return $false
    }
}

# ============================================================================
# FUNCTION: Enable required APIs
# ============================================================================

function Enable-GCPAPIs {
    Write-Host "`n📡 Enabling required GCP APIs..." -ForegroundColor Cyan
    
    $apis = @(
        "cloudbuild.googleapis.com",
        "run.googleapis.com",
        "containerregistry.googleapis.com",
        "artifactregistry.googleapis.com",
        "secretmanager.googleapis.com",
        "bigquery.googleapis.com"
    )
    
    foreach ($api in $apis) {
        Write-Host "  Enabling $api..." -ForegroundColor Gray
        gcloud services enable $api --project=$ProjectId 2>&1 | Out-Null
    }
    
    Write-Host "✅ APIs enabled successfully!" -ForegroundColor Green
}

# ============================================================================
# FUNCTION: Create secrets in Secret Manager
# ============================================================================

function Set-Secrets {
    Write-Host "`n🔐 Setting up Secret Manager..." -ForegroundColor Cyan
    
    # Check if secrets already exist
    $secrets = @{
        "OPENAI_API_KEY" = "Enter your OpenAI API Key"
        "JWT_SECRET_KEY" = "Enter JWT Secret (press Enter for auto-generated)"
        "GOOGLE_CLIENT_ID" = "Enter Google OAuth Client ID (optional)"
        "GOOGLE_CLIENT_SECRET" = "Enter Google OAuth Client Secret (optional)"
        "MICROSOFT_CLIENT_ID" = "Enter Microsoft OAuth Client ID (optional)"
        "MICROSOFT_CLIENT_SECRET" = "Enter Microsoft OAuth Client Secret (optional)"
    }
    
    foreach ($secretName in $secrets.Keys) {
        $exists = gcloud secrets describe $secretName --project=$ProjectId 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ⏭️  Secret $secretName already exists, skipping..." -ForegroundColor Yellow
            continue
        }
        
        $prompt = $secrets[$secretName]
        
        if ($secretName -eq "JWT_SECRET_KEY") {
            $value = Read-Host $prompt
            if (-not $value) {
                $value = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes([guid]::NewGuid().ToString() + [guid]::NewGuid().ToString()))
                Write-Host "  Generated: $($value.Substring(0, 20))..." -ForegroundColor Gray
            }
        } elseif ($secretName -like "*CLIENT_ID" -or $secretName -like "*CLIENT_SECRET") {
            $value = Read-Host "$prompt (or press Enter to skip)"
            if (-not $value) {
                Write-Host "  ⏭️  Skipping $secretName" -ForegroundColor Gray
                continue
            }
        } else {
            $value = Read-Host $prompt
        }
        
        if ($value) {
            Write-Host "  Creating secret: $secretName..." -ForegroundColor Gray
            $value | gcloud secrets create $secretName --data-file=- --project=$ProjectId 2>&1 | Out-Null
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  ✅ Secret $secretName created" -ForegroundColor Green
            } else {
                Write-Host "  ⚠️  Failed to create $secretName" -ForegroundColor Red
            }
        }
    }
}

# ============================================================================
# FUNCTION: Deploy Backend to Cloud Run
# ============================================================================

function Deploy-Backend {
    Write-Host "`n🔨 Building and Deploying Backend..." -ForegroundColor Cyan
    
    # Build using Cloud Build
    Write-Host "  Building container..." -ForegroundColor Gray
    gcloud builds submit --config cloudbuild-backend.yaml --project=$ProjectId
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Backend build failed!" -ForegroundColor Red
        return
    }
    
    # Deploy to Cloud Run
    Write-Host "`n  Deploying to Cloud Run..." -ForegroundColor Gray
    gcloud run deploy $BACKEND_SERVICE `
        --image="gcr.io/$ProjectId/legid-backend:latest" `
        --platform=managed `
        --region=$Region `
        --allow-unauthenticated `
        --memory=2Gi `
        --cpu=2 `
        --min-instances=0 `
        --max-instances=10 `
        --timeout=300 `
        --set-secrets="OPENAI_API_KEY=OPENAI_API_KEY:latest,JWT_SECRET_KEY=JWT_SECRET_KEY:latest,GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID:latest,GOOGLE_CLIENT_SECRET=GOOGLE_CLIENT_SECRET:latest,MICROSOFT_CLIENT_ID=MICROSOFT_CLIENT_ID:latest,MICROSOFT_CLIENT_SECRET=MICROSOFT_CLIENT_SECRET:latest" `
        --set-env-vars="LLM_PROVIDER=openai,ENVIRONMENT=production,LOG_LEVEL=INFO" `
        --project=$ProjectId
    
    if ($LASTEXITCODE -eq 0) {
        $backendUrl = gcloud run services describe $BACKEND_SERVICE --region=$Region --format="value(status.url)" --project=$ProjectId
        Write-Host "`n✅ Backend deployed successfully!" -ForegroundColor Green
        Write-Host "   URL: $backendUrl" -ForegroundColor Cyan
        return $backendUrl
    } else {
        Write-Host "❌ Backend deployment failed!" -ForegroundColor Red
    }
}

# ============================================================================
# FUNCTION: Deploy Frontend to Cloud Run
# ============================================================================

function Deploy-Frontend {
    param([string]$BackendUrl)
    
    Write-Host "`n🔨 Building and Deploying Frontend..." -ForegroundColor Cyan
    
    if (-not $BackendUrl) {
        $BackendUrl = gcloud run services describe $BACKEND_SERVICE --region=$Region --format="value(status.url)" --project=$ProjectId 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "⚠️  Backend not found. Please deploy backend first." -ForegroundColor Yellow
            $BackendUrl = Read-Host "Enter Backend URL manually (or press Enter to skip)"
            if (-not $BackendUrl) {
                Write-Host "❌ Cannot deploy frontend without backend URL" -ForegroundColor Red
                return
            }
        }
    }
    
    Write-Host "  Using Backend URL: $BackendUrl" -ForegroundColor Gray
    
    # Build using Cloud Build
    Write-Host "  Building container..." -ForegroundColor Gray
    gcloud builds submit --config cloudbuild-frontend.yaml `
        --substitutions=_BACKEND_URL=$BackendUrl `
        --project=$ProjectId
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Frontend build failed!" -ForegroundColor Red
        return
    }
    
    # Deploy to Cloud Run
    Write-Host "`n  Deploying to Cloud Run..." -ForegroundColor Gray
    gcloud run deploy $FRONTEND_SERVICE `
        --image="gcr.io/$ProjectId/legid-frontend:latest" `
        --platform=managed `
        --region=$Region `
        --allow-unauthenticated `
        --memory=512Mi `
        --cpu=1 `
        --min-instances=0 `
        --max-instances=5 `
        --set-env-vars="VITE_API_URL=$BackendUrl,VITE_ENVIRONMENT=production" `
        --project=$ProjectId
    
    if ($LASTEXITCODE -eq 0) {
        $frontendUrl = gcloud run services describe $FRONTEND_SERVICE --region=$Region --format="value(status.url)" --project=$ProjectId
        Write-Host "`n✅ Frontend deployed successfully!" -ForegroundColor Green
        Write-Host "   URL: $frontendUrl" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Frontend deployment failed!" -ForegroundColor Red
    }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

# Check prerequisites
if (-not (Test-GCloudInstalled)) {
    exit 1
}

# Set project
Write-Host "`n🔧 Setting GCP project..." -ForegroundColor Cyan
gcloud config set project $ProjectId

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to set project. Make sure you're authenticated." -ForegroundColor Red
    Write-Host "   Run: gcloud auth login" -ForegroundColor Yellow
    exit 1
}

# Enable APIs
Enable-GCPAPIs

# Setup secrets
if ($SetupOnly -or $DeployAll) {
    Set-Secrets
}

if ($SetupOnly) {
    Write-Host "`n✅ Setup completed! Run with -DeployAll to deploy services." -ForegroundColor Green
    exit 0
}

# Deploy services
$backendUrl = $null

if ($DeployBackend -or $DeployAll) {
    $backendUrl = Deploy-Backend
}

if ($DeployFrontend -or $DeployAll) {
    Deploy-Frontend -BackendUrl $backendUrl
}

# Final summary
Write-Host "`n============================================================================" -ForegroundColor Cyan
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Cyan

if ($DeployBackend -or $DeployAll) {
    $backendUrl = gcloud run services describe $BACKEND_SERVICE --region=$Region --format="value(status.url)" --project=$ProjectId 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n📡 Backend Service:" -ForegroundColor Yellow
        Write-Host "   URL: $backendUrl" -ForegroundColor Cyan
        Write-Host "   Health: $backendUrl/health" -ForegroundColor Gray
    }
}

if ($DeployFrontend -or $DeployAll) {
    $frontendUrl = gcloud run services describe $FRONTEND_SERVICE --region=$Region --format="value(status.url)" --project=$ProjectId 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n🌐 Frontend Service:" -ForegroundColor Yellow
        Write-Host "   URL: $frontendUrl" -ForegroundColor Cyan
    }
}

Write-Host "`n⚠️  Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Update OAuth redirect URIs with Cloud Run URLs" -ForegroundColor Gray
Write-Host "   2. Test the deployment" -ForegroundColor Gray
Write-Host "   3. Set up Cloud Build triggers for auto-deploy" -ForegroundColor Gray
Write-Host ""
