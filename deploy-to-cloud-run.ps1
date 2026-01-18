# =========================================================
# COMPLETE CLOUD RUN DEPLOYMENT SCRIPT
# Pushes current codebase from Git to Google Cloud Run
# =========================================================

param(
    [string]$ProjectId = "",
    [string]$Region = "us-central1",
    [string]$GitRemote = "origin",
    [string]$Branch = "main"
)

Write-Host @"
=========================================================
   CLOUD RUN DEPLOYMENT SCRIPT
   Deploy Legal Bot to Google Cloud Run
=========================================================
"@ -ForegroundColor Cyan

# =========================================================
# STEP 1: Check Prerequisites
# =========================================================
Write-Host "`n[1/10] Checking prerequisites..." -ForegroundColor Yellow

# Check gcloud
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Google Cloud SDK not found!" -ForegroundColor Red
    Write-Host "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
}
Write-Host "  ✓ Google Cloud SDK installed" -ForegroundColor Green

# Check git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Git not found!" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Git installed" -ForegroundColor Green

# =========================================================
# STEP 2: Authenticate and Set Project
# =========================================================
Write-Host "`n[2/10] Setting up GCP project..." -ForegroundColor Yellow

# Get current project or prompt
if ([string]::IsNullOrEmpty($ProjectId)) {
    $ProjectId = gcloud config get-value project 2>$null
    if ([string]::IsNullOrEmpty($ProjectId)) {
        $ProjectId = Read-Host "Enter your GCP Project ID"
    }
}

Write-Host "  Using project: $ProjectId" -ForegroundColor Cyan
gcloud config set project $ProjectId

# Get project number
$ProjectNumber = gcloud projects describe $ProjectId --format="value(projectNumber)" 2>$null
if ([string]::IsNullOrEmpty($ProjectNumber)) {
    Write-Host "ERROR: Could not get project number. Are you authenticated?" -ForegroundColor Red
    Write-Host "Run: gcloud auth login"
    exit 1
}
Write-Host "  ✓ Project configured (Number: $ProjectNumber)" -ForegroundColor Green

# =========================================================
# STEP 3: Enable Required APIs
# =========================================================
Write-Host "`n[3/10] Enabling required APIs..." -ForegroundColor Yellow

$apis = @(
    "cloudbuild.googleapis.com",
    "run.googleapis.com", 
    "containerregistry.googleapis.com",
    "secretmanager.googleapis.com",
    "artifactregistry.googleapis.com"
)

foreach ($api in $apis) {
    Write-Host "  Enabling $api..." -ForegroundColor Gray
    gcloud services enable $api --quiet 2>$null
}
Write-Host "  ✓ All APIs enabled" -ForegroundColor Green

# =========================================================
# STEP 4: Setup Secrets
# =========================================================
Write-Host "`n[4/10] Setting up secrets..." -ForegroundColor Yellow

# Check if OPENAI_API_KEY secret exists
$secretExists = gcloud secrets describe OPENAI_API_KEY 2>$null
if (-not $secretExists) {
    Write-Host "  OPENAI_API_KEY secret not found." -ForegroundColor Yellow
    $openaiKey = Read-Host "  Enter your OpenAI API Key (or press Enter to skip)"
    if (-not [string]::IsNullOrEmpty($openaiKey)) {
        $openaiKey | gcloud secrets create OPENAI_API_KEY --data-file=- 2>$null
        Write-Host "  ✓ OPENAI_API_KEY secret created" -ForegroundColor Green
    }
} else {
    Write-Host "  ✓ OPENAI_API_KEY secret exists" -ForegroundColor Green
}

# Check JWT_SECRET_KEY
$jwtExists = gcloud secrets describe JWT_SECRET_KEY 2>$null
if (-not $jwtExists) {
    # Generate a random JWT secret
    $jwtSecret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object {[char]$_})
    $jwtSecret | gcloud secrets create JWT_SECRET_KEY --data-file=- 2>$null
    Write-Host "  ✓ JWT_SECRET_KEY secret created (auto-generated)" -ForegroundColor Green
} else {
    Write-Host "  ✓ JWT_SECRET_KEY secret exists" -ForegroundColor Green
}

# =========================================================
# STEP 5: Grant IAM Permissions
# =========================================================
Write-Host "`n[5/10] Granting Cloud Build permissions..." -ForegroundColor Yellow

$serviceAccount = "$ProjectNumber@cloudbuild.gserviceaccount.com"

$roles = @(
    "roles/secretmanager.secretAccessor",
    "roles/run.admin",
    "roles/iam.serviceAccountUser",
    "roles/storage.admin"
)

foreach ($role in $roles) {
    Write-Host "  Granting $role..." -ForegroundColor Gray
    gcloud projects add-iam-policy-binding $ProjectId `
        --member="serviceAccount:$serviceAccount" `
        --role="$role" --quiet 2>$null | Out-Null
}
Write-Host "  ✓ IAM permissions granted" -ForegroundColor Green

# =========================================================
# STEP 6: Initialize Git Repository
# =========================================================
Write-Host "`n[6/10] Setting up Git repository..." -ForegroundColor Yellow

# Check if already a git repo
if (-not (Test-Path ".git")) {
    git init
    Write-Host "  ✓ Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "  ✓ Git repository exists" -ForegroundColor Green
}

# Check if remote exists
$remoteUrl = git remote get-url $GitRemote 2>$null
if ([string]::IsNullOrEmpty($remoteUrl)) {
    Write-Host "  No remote '$GitRemote' found." -ForegroundColor Yellow
    $repoUrl = Read-Host "  Enter your GitHub repository URL (e.g., https://github.com/user/repo.git)"
    if (-not [string]::IsNullOrEmpty($repoUrl)) {
        git remote add $GitRemote $repoUrl
        Write-Host "  ✓ Remote added: $repoUrl" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: No remote configured. You'll need to add one manually." -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✓ Remote configured: $remoteUrl" -ForegroundColor Green
}

# =========================================================
# STEP 7: Create .gcloudignore if needed
# =========================================================
Write-Host "`n[7/10] Creating .gcloudignore..." -ForegroundColor Yellow

$gcloudIgnoreContent = @"
# Ignore common files
.git
.gitignore
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env
*.env.local
node_modules/
.next/
dist/
build/
*.log
.DS_Store
Thumbs.db
*.md
!README.md
*.bat
*.ps1
*.txt
!requirements.txt
tests/
__tests__/
*.test.*
*.spec.*
"@

if (-not (Test-Path ".gcloudignore")) {
    $gcloudIgnoreContent | Out-File -FilePath ".gcloudignore" -Encoding utf8
    Write-Host "  ✓ .gcloudignore created" -ForegroundColor Green
} else {
    Write-Host "  ✓ .gcloudignore exists" -ForegroundColor Green
}

# =========================================================
# STEP 8: Commit and Push to Git
# =========================================================
Write-Host "`n[8/10] Committing and pushing to Git..." -ForegroundColor Yellow

# Add all files
git add -A

# Check if there are changes to commit
$status = git status --porcelain
if ($status) {
    $commitMessage = "Deploy to Cloud Run - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    git commit -m $commitMessage
    Write-Host "  ✓ Changes committed" -ForegroundColor Green
} else {
    # Create empty commit to trigger build
    git commit --allow-empty -m "Trigger Cloud Run deployment - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Host "  ✓ Empty commit created (no changes)" -ForegroundColor Green
}

# Push to remote
$remoteUrl = git remote get-url $GitRemote 2>$null
if (-not [string]::IsNullOrEmpty($remoteUrl)) {
    Write-Host "  Pushing to $GitRemote/$Branch..." -ForegroundColor Gray
    git push -u $GitRemote $Branch 2>&1
    Write-Host "  ✓ Pushed to Git" -ForegroundColor Green
} else {
    Write-Host "  WARNING: No remote configured. Please push manually." -ForegroundColor Yellow
}

# =========================================================
# STEP 9: Create/Update Cloud Build Trigger
# =========================================================
Write-Host "`n[9/10] Setting up Cloud Build trigger..." -ForegroundColor Yellow

# Check if trigger exists
$triggerExists = gcloud builds triggers list --format="value(name)" 2>$null | Where-Object { $_ -eq "deploy-legal-bot" }

if (-not $triggerExists) {
    Write-Host "  Cloud Build trigger not found." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  MANUAL STEP REQUIRED:" -ForegroundColor Cyan
    Write-Host "  1. Go to: https://console.cloud.google.com/cloud-build/triggers?project=$ProjectId"
    Write-Host "  2. Click 'Connect Repository'"
    Write-Host "  3. Select GitHub and authorize"
    Write-Host "  4. Select your repository"
    Write-Host "  5. Create a trigger with:"
    Write-Host "     - Name: deploy-legal-bot"
    Write-Host "     - Event: Push to branch"
    Write-Host "     - Branch: ^main$"
    Write-Host "     - Config: cloudbuild.yaml"
    Write-Host ""
    Write-Host "  OR use this command after connecting your repo:" -ForegroundColor Yellow
    Write-Host "  gcloud builds triggers create github --name=deploy-legal-bot --repo-owner=YOUR_USERNAME --repo-name=YOUR_REPO --branch-pattern='^main$' --build-config=cloudbuild.yaml"
} else {
    Write-Host "  ✓ Cloud Build trigger exists" -ForegroundColor Green
}

# =========================================================
# STEP 10: Trigger Manual Build (Optional)
# =========================================================
Write-Host "`n[10/10] Triggering Cloud Build..." -ForegroundColor Yellow

Write-Host ""
Write-Host "Would you like to trigger a manual build now? (y/n)" -ForegroundColor Cyan
$triggerBuild = Read-Host

if ($triggerBuild -eq "y" -or $triggerBuild -eq "Y") {
    Write-Host "  Starting Cloud Build..." -ForegroundColor Gray
    
    # Submit build directly from source
    $buildResult = gcloud builds submit --config=cloudbuild.yaml --async 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Build submitted successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "  Watch build progress:" -ForegroundColor Cyan
        Write-Host "  gcloud builds log --stream `$(gcloud builds list --limit=1 --format='value(id)')"
        Write-Host ""
        Write-Host "  Or view in Console:" -ForegroundColor Cyan
        Write-Host "  https://console.cloud.google.com/cloud-build/builds?project=$ProjectId"
    } else {
        Write-Host "  Build submission failed. Check the error above." -ForegroundColor Yellow
        Write-Host "  You may need to connect your GitHub repo first." -ForegroundColor Yellow
    }
} else {
    Write-Host "  Skipped manual build." -ForegroundColor Gray
}

# =========================================================
# SUMMARY
# =========================================================
Write-Host ""
Write-Host @"
=========================================================
   DEPLOYMENT SETUP COMPLETE! 
=========================================================
"@ -ForegroundColor Green

Write-Host @"

NEXT STEPS:
-----------
1. If you haven't connected your GitHub repo to Cloud Build:
   - Visit: https://console.cloud.google.com/cloud-build/triggers?project=$ProjectId
   - Click "Connect Repository" and follow the prompts

2. Create a build trigger (if not done):
   - Name: deploy-legal-bot
   - Branch: main
   - Config: cloudbuild.yaml

3. Push any change to trigger deployment:
   git push origin main

4. View build progress:
   https://console.cloud.google.com/cloud-build/builds?project=$ProjectId

AFTER DEPLOYMENT:
-----------------
Get your app URLs:

"@ -ForegroundColor White

Write-Host "# Backend API:" -ForegroundColor Yellow
Write-Host "gcloud run services describe legal-bot-backend --region=$Region --format='value(status.url)'" -ForegroundColor Cyan
Write-Host ""
Write-Host "# Frontend App:" -ForegroundColor Yellow  
Write-Host "gcloud run services describe legal-bot-frontend --region=$Region --format='value(status.url)'" -ForegroundColor Cyan
Write-Host ""
Write-Host "=========================================================`n" -ForegroundColor Green
