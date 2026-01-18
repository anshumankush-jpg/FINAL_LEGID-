# Complete Cloud Run Deployment Guide 🚀

## End-to-End: Git → Cloud Run

This guide will push your current codebase to Google Cloud Run via Git/GitHub.

---

## Prerequisites Checklist

- [ ] Google Cloud SDK installed (`gcloud --version`)
- [ ] Git installed (`git --version`)
- [ ] GitHub account (or GitLab/Bitbucket)
- [ ] GCP Project with billing enabled

---

## Quick Deploy (5 Minutes)

### Option 1: Using PowerShell Script (Recommended)

```powershell
.\deploy-to-cloud-run.ps1
```

### Option 2: Using Cloud Shell Script

```bash
./deploy-cloud-shell.sh
```

---

## Manual Step-by-Step Deployment

### Step 1: Authenticate with GCP

```powershell
# Login to Google Cloud
gcloud auth login

# Set your project (replace with your project ID)
gcloud config set project YOUR_PROJECT_ID
```

### Step 2: Enable Required APIs

```powershell
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### Step 3: Create Secrets in Secret Manager

```powershell
# Create OPENAI_API_KEY secret
echo "your-openai-api-key" | gcloud secrets create OPENAI_API_KEY --data-file=-

# Create JWT_SECRET_KEY secret
echo "your-jwt-secret-key" | gcloud secrets create JWT_SECRET_KEY --data-file=-

# Create GOOGLE_CLIENT_ID secret (for OAuth)
echo "your-google-client-id" | gcloud secrets create GOOGLE_CLIENT_ID --data-file=-

# Create GOOGLE_CLIENT_SECRET secret (for OAuth)
echo "your-google-client-secret" | gcloud secrets create GOOGLE_CLIENT_SECRET --data-file=-
```

### Step 4: Grant Cloud Build Permissions

```powershell
# Get project number
$PROJECT_ID = gcloud config get-value project
$PROJECT_NUMBER = gcloud projects describe $PROJECT_ID --format="value(projectNumber)"

# Grant Secret Manager access
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" `
    --role="roles/secretmanager.secretAccessor"

# Grant Cloud Run Admin
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" `
    --role="roles/run.admin"

# Grant IAM Service Account User
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" `
    --role="roles/iam.serviceAccountUser"
```

### Step 5: Push to GitHub

```powershell
# Initialize Git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Deploy to Cloud Run"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push to main branch
git push -u origin main
```

### Step 6: Connect GitHub to Cloud Build

1. Go to: https://console.cloud.google.com/cloud-build/triggers
2. Click **"Connect Repository"**
3. Select **"GitHub"** 
4. Authorize Google Cloud Build
5. Select your repository
6. Click **"Connect"**

### Step 7: Create Build Trigger

```powershell
gcloud builds triggers create github `
    --name="deploy-legal-bot" `
    --repo-name="YOUR_REPO_NAME" `
    --repo-owner="YOUR_GITHUB_USERNAME" `
    --branch-pattern="^main$" `
    --build-config="cloudbuild.yaml"
```

### Step 8: Trigger Deployment

```powershell
# Push any change to trigger build
git commit --allow-empty -m "Trigger Cloud Run deployment"
git push origin main
```

---

## Watch Deployment Progress

```powershell
# Watch build logs
gcloud builds log --stream $(gcloud builds list --limit=1 --format='value(id)')

# Or view in Console:
# https://console.cloud.google.com/cloud-build/builds
```

---

## Get Deployment URLs

```powershell
# Get Backend URL
gcloud run services describe legal-bot-backend --region=us-central1 --format='value(status.url)'

# Get Frontend URL
gcloud run services describe legal-bot-frontend --region=us-central1 --format='value(status.url)'
```

---

## Troubleshooting

### Build Failed?
```powershell
# View recent build logs
gcloud builds list --limit=5
gcloud builds log BUILD_ID
```

### Secrets Not Found?
```powershell
# List secrets
gcloud secrets list

# Verify secret exists
gcloud secrets versions access latest --secret="OPENAI_API_KEY"
```

### Permission Denied?
```powershell
# Re-run IAM commands from Step 4
```

---

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| OPENAI_API_KEY | OpenAI API key | ✅ Yes |
| JWT_SECRET_KEY | JWT signing secret | ✅ Yes |
| GOOGLE_CLIENT_ID | OAuth client ID | Optional |
| GOOGLE_CLIENT_SECRET | OAuth client secret | Optional |
| GOOGLE_CLOUD_PROJECT | Auto-set by Cloud Run | Auto |

---

## Cost Estimate

- **Cloud Run**: Pay per use (~$0.00002400/vCPU-second)
- **Container Registry**: ~$0.026/GB/month
- **Cloud Build**: 120 free build-minutes/day

**Estimated**: $0-10/month for low traffic

