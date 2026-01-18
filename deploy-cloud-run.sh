#!/bin/bash
# =========================================================
# COMPLETE CLOUD RUN DEPLOYMENT SCRIPT (Bash/Linux/Cloud Shell)
# Pushes current codebase from Git to Google Cloud Run
# =========================================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
REGION="${REGION:-us-central1}"
GIT_REMOTE="${GIT_REMOTE:-origin}"
BRANCH="${BRANCH:-main}"

echo -e "${CYAN}"
echo "========================================================="
echo "   CLOUD RUN DEPLOYMENT SCRIPT"
echo "   Deploy Legal Bot to Google Cloud Run"
echo "========================================================="
echo -e "${NC}"

# =========================================================
# STEP 1: Check Prerequisites
# =========================================================
echo -e "${YELLOW}[1/10] Checking prerequisites...${NC}"

if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}ERROR: Google Cloud SDK not found!${NC}"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi
echo -e "${GREEN}  ✓ Google Cloud SDK installed${NC}"

if ! command -v git &> /dev/null; then
    echo -e "${RED}ERROR: Git not found!${NC}"
    exit 1
fi
echo -e "${GREEN}  ✓ Git installed${NC}"

# =========================================================
# STEP 2: Authenticate and Set Project
# =========================================================
echo -e "${YELLOW}\n[2/10] Setting up GCP project...${NC}"

PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo -n "Enter your GCP Project ID: "
    read PROJECT_ID
fi

echo -e "${CYAN}  Using project: $PROJECT_ID${NC}"
gcloud config set project "$PROJECT_ID"

PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)" 2>/dev/null)
if [ -z "$PROJECT_NUMBER" ]; then
    echo -e "${RED}ERROR: Could not get project number. Are you authenticated?${NC}"
    echo "Run: gcloud auth login"
    exit 1
fi
echo -e "${GREEN}  ✓ Project configured (Number: $PROJECT_NUMBER)${NC}"

# =========================================================
# STEP 3: Enable Required APIs
# =========================================================
echo -e "${YELLOW}\n[3/10] Enabling required APIs...${NC}"

APIS=(
    "cloudbuild.googleapis.com"
    "run.googleapis.com"
    "containerregistry.googleapis.com"
    "secretmanager.googleapis.com"
    "artifactregistry.googleapis.com"
)

for api in "${APIS[@]}"; do
    echo "  Enabling $api..."
    gcloud services enable "$api" --quiet 2>/dev/null
done
echo -e "${GREEN}  ✓ All APIs enabled${NC}"

# =========================================================
# STEP 4: Setup Secrets
# =========================================================
echo -e "${YELLOW}\n[4/10] Setting up secrets...${NC}"

# Check OPENAI_API_KEY
if ! gcloud secrets describe OPENAI_API_KEY &>/dev/null; then
    echo -e "${YELLOW}  OPENAI_API_KEY secret not found.${NC}"
    echo -n "  Enter your OpenAI API Key (or press Enter to skip): "
    read -r OPENAI_KEY
    if [ -n "$OPENAI_KEY" ]; then
        echo -n "$OPENAI_KEY" | gcloud secrets create OPENAI_API_KEY --data-file=- 2>/dev/null
        echo -e "${GREEN}  ✓ OPENAI_API_KEY secret created${NC}"
    fi
else
    echo -e "${GREEN}  ✓ OPENAI_API_KEY secret exists${NC}"
fi

# Check JWT_SECRET_KEY
if ! gcloud secrets describe JWT_SECRET_KEY &>/dev/null; then
    JWT_SECRET=$(openssl rand -base64 48)
    echo -n "$JWT_SECRET" | gcloud secrets create JWT_SECRET_KEY --data-file=- 2>/dev/null
    echo -e "${GREEN}  ✓ JWT_SECRET_KEY secret created (auto-generated)${NC}"
else
    echo -e "${GREEN}  ✓ JWT_SECRET_KEY secret exists${NC}"
fi

# =========================================================
# STEP 5: Grant IAM Permissions
# =========================================================
echo -e "${YELLOW}\n[5/10] Granting Cloud Build permissions...${NC}"

SERVICE_ACCOUNT="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

ROLES=(
    "roles/secretmanager.secretAccessor"
    "roles/run.admin"
    "roles/iam.serviceAccountUser"
    "roles/storage.admin"
)

for role in "${ROLES[@]}"; do
    echo "  Granting $role..."
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="$role" --quiet 2>/dev/null || true
done
echo -e "${GREEN}  ✓ IAM permissions granted${NC}"

# =========================================================
# STEP 6: Initialize Git Repository
# =========================================================
echo -e "${YELLOW}\n[6/10] Setting up Git repository...${NC}"

if [ ! -d ".git" ]; then
    git init
    echo -e "${GREEN}  ✓ Git repository initialized${NC}"
else
    echo -e "${GREEN}  ✓ Git repository exists${NC}"
fi

REMOTE_URL=$(git remote get-url "$GIT_REMOTE" 2>/dev/null || echo "")
if [ -z "$REMOTE_URL" ]; then
    echo -e "${YELLOW}  No remote '$GIT_REMOTE' found.${NC}"
    echo -n "  Enter your GitHub repository URL (e.g., https://github.com/user/repo.git): "
    read -r REPO_URL
    if [ -n "$REPO_URL" ]; then
        git remote add "$GIT_REMOTE" "$REPO_URL"
        echo -e "${GREEN}  ✓ Remote added: $REPO_URL${NC}"
    fi
else
    echo -e "${GREEN}  ✓ Remote configured: $REMOTE_URL${NC}"
fi

# =========================================================
# STEP 7: Create .gcloudignore
# =========================================================
echo -e "${YELLOW}\n[7/10] Creating .gcloudignore...${NC}"

if [ ! -f ".gcloudignore" ]; then
cat > .gcloudignore << 'EOF'
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
EOF
    echo -e "${GREEN}  ✓ .gcloudignore created${NC}"
else
    echo -e "${GREEN}  ✓ .gcloudignore exists${NC}"
fi

# =========================================================
# STEP 8: Commit and Push to Git
# =========================================================
echo -e "${YELLOW}\n[8/10] Committing and pushing to Git...${NC}"

git add -A

if [ -n "$(git status --porcelain)" ]; then
    COMMIT_MSG="Deploy to Cloud Run - $(date '+%Y-%m-%d %H:%M:%S')"
    git commit -m "$COMMIT_MSG"
    echo -e "${GREEN}  ✓ Changes committed${NC}"
else
    git commit --allow-empty -m "Trigger Cloud Run deployment - $(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "${GREEN}  ✓ Empty commit created (no changes)${NC}"
fi

REMOTE_URL=$(git remote get-url "$GIT_REMOTE" 2>/dev/null || echo "")
if [ -n "$REMOTE_URL" ]; then
    echo "  Pushing to $GIT_REMOTE/$BRANCH..."
    git push -u "$GIT_REMOTE" "$BRANCH" 2>&1 || true
    echo -e "${GREEN}  ✓ Pushed to Git${NC}"
else
    echo -e "${YELLOW}  WARNING: No remote configured. Please push manually.${NC}"
fi

# =========================================================
# STEP 9: Cloud Build Trigger Info
# =========================================================
echo -e "${YELLOW}\n[9/10] Setting up Cloud Build trigger...${NC}"

TRIGGER_EXISTS=$(gcloud builds triggers list --format="value(name)" 2>/dev/null | grep -w "deploy-legal-bot" || echo "")

if [ -z "$TRIGGER_EXISTS" ]; then
    echo -e "${YELLOW}  Cloud Build trigger not found.${NC}"
    echo ""
    echo -e "${CYAN}  MANUAL STEP REQUIRED:${NC}"
    echo "  1. Go to: https://console.cloud.google.com/cloud-build/triggers?project=$PROJECT_ID"
    echo "  2. Click 'Connect Repository'"
    echo "  3. Select GitHub and authorize"
    echo "  4. Select your repository"
    echo "  5. Create a trigger with:"
    echo "     - Name: deploy-legal-bot"
    echo "     - Event: Push to branch"
    echo "     - Branch: ^main\$"
    echo "     - Config: cloudbuild.yaml"
else
    echo -e "${GREEN}  ✓ Cloud Build trigger exists${NC}"
fi

# =========================================================
# STEP 10: Trigger Manual Build
# =========================================================
echo -e "${YELLOW}\n[10/10] Triggering Cloud Build...${NC}"

echo ""
echo -n "Would you like to trigger a manual build now? (y/n): "
read -r TRIGGER_BUILD

if [ "$TRIGGER_BUILD" = "y" ] || [ "$TRIGGER_BUILD" = "Y" ]; then
    echo "  Starting Cloud Build..."
    
    if gcloud builds submit --config=cloudbuild.yaml --async 2>&1; then
        echo -e "${GREEN}  ✓ Build submitted successfully!${NC}"
        echo ""
        echo -e "${CYAN}  Watch build progress:${NC}"
        echo "  gcloud builds log --stream \$(gcloud builds list --limit=1 --format='value(id)')"
        echo ""
        echo -e "${CYAN}  Or view in Console:${NC}"
        echo "  https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
    else
        echo -e "${YELLOW}  Build submission failed. Check the error above.${NC}"
    fi
else
    echo "  Skipped manual build."
fi

# =========================================================
# SUMMARY
# =========================================================
echo ""
echo -e "${GREEN}"
echo "========================================================="
echo "   DEPLOYMENT SETUP COMPLETE!"
echo "========================================================="
echo -e "${NC}"

cat << EOF

NEXT STEPS:
-----------
1. If you haven't connected your GitHub repo to Cloud Build:
   - Visit: https://console.cloud.google.com/cloud-build/triggers?project=$PROJECT_ID
   - Click "Connect Repository" and follow the prompts

2. Create a build trigger (if not done):
   - Name: deploy-legal-bot
   - Branch: main
   - Config: cloudbuild.yaml

3. Push any change to trigger deployment:
   git push origin main

4. View build progress:
   https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID

AFTER DEPLOYMENT:
-----------------
Get your app URLs:

EOF

echo -e "${YELLOW}# Backend API:${NC}"
echo -e "${CYAN}gcloud run services describe legal-bot-backend --region=$REGION --format='value(status.url)'${NC}"
echo ""
echo -e "${YELLOW}# Frontend App:${NC}"
echo -e "${CYAN}gcloud run services describe legal-bot-frontend --region=$REGION --format='value(status.url)'${NC}"
echo ""
echo "========================================================="
echo ""
