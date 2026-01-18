# 🚀 DEPLOY TO CLOUD RUN NOW

## Quick Start (3 Commands)

### 1. Open PowerShell and Navigate to Project
```powershell
cd C:\Users\anshu\Downloads\production_level
```

### 2. Login to Google Cloud
```powershell
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 3. Run the Deployment Script
```powershell
.\deploy-to-cloud-run.ps1
```

---

## OR: Manual Step-by-Step (Copy-Paste Commands)

### Step 1: Authenticate
```powershell
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Step 2: Enable APIs
```powershell
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com secretmanager.googleapis.com
```

### Step 3: Create OpenAI Secret
```powershell
# Replace sk-xxx with your actual OpenAI key
echo "sk-xxx" | gcloud secrets create OPENAI_API_KEY --data-file=-
```

### Step 4: Grant Permissions
```powershell
$PROJECT_ID = gcloud config get-value project
$PROJECT_NUMBER = gcloud projects describe $PROJECT_ID --format="value(projectNumber)"

gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" --role="roles/secretmanager.secretAccessor"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" --role="roles/run.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" --role="roles/iam.serviceAccountUser"
```

### Step 5: Push to GitHub
```powershell
git add -A
git commit -m "Deploy to Cloud Run"
git push origin main
```

### Step 6: Submit Build
```powershell
gcloud builds submit --config=cloudbuild.yaml
```

---

## After Deployment

### Get Your URLs
```powershell
# Backend API
gcloud run services describe legal-bot-backend --region=us-central1 --format="value(status.url)"

# Frontend App  
gcloud run services describe legal-bot-frontend --region=us-central1 --format="value(status.url)"
```

### Watch Build Logs
```powershell
gcloud builds log --stream $(gcloud builds list --limit=1 --format="value(id)")
```

---

## Files Created for Deployment

| File | Purpose |
|------|---------|
| `cloudbuild.yaml` | Cloud Build configuration |
| `backend/Dockerfile` | Backend container image |
| `frontend/Dockerfile` | Frontend container image |
| `deploy-to-cloud-run.ps1` | PowerShell deployment script |
| `deploy-cloud-run.sh` | Bash deployment script |
| `quick-deploy.ps1` | Quick one-command deploy |

---

## Troubleshooting

### "Permission denied"
```powershell
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### "Secret not found"
```powershell
gcloud secrets list
# If OPENAI_API_KEY is missing:
echo "your-key" | gcloud secrets create OPENAI_API_KEY --data-file=-
```

### "Build failed"
```powershell
gcloud builds list --limit=1
gcloud builds log BUILD_ID
```

### Check Service Status
```powershell
gcloud run services list --region=us-central1
```
