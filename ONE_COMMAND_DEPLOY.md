# 🚀 ONE-COMMAND DEPLOYMENT TO CLOUD RUN

## Method 1: Google Cloud Shell (RECOMMENDED - No Setup Required!)

### Step 1: Open Google Cloud Shell
1. Go to: https://console.cloud.google.com/
2. Click the **Cloud Shell** icon (>_) in the top-right corner
3. Wait for the terminal to load

### Step 2: Upload Your Code
In Cloud Shell, click the **3 dots menu** → **Upload** → Upload the entire `production_level` folder
OR clone from GitHub:
```bash
git clone YOUR_GITHUB_REPO_URL
cd YOUR_REPO_NAME
```

### Step 3: Run This ONE Command
```bash
chmod +x cloud-shell-deploy.sh && ./cloud-shell-deploy.sh
```

**That's it!** ✅ The script will:
- Enable all required APIs
- Create secrets (will prompt for your OpenAI API key)
- Grant permissions
- Build backend Docker image
- Deploy backend to Cloud Run
- Build frontend Docker image  
- Deploy frontend to Cloud Run
- Give you the live URLs!

**Time: 10-15 minutes** ⏱️

---

## Method 2: Windows PowerShell (Local Deployment)

### Prerequisites
```powershell
# Install Google Cloud SDK from:
# https://cloud.google.com/sdk/docs/install

# Verify installation
gcloud --version
```

### One-Line Deploy
```powershell
cd C:\Users\anshu\Downloads\production_level
gcloud auth login
.\deploy-to-cloud-run.ps1
```

---

## Method 3: Direct gcloud Build Submit (Fastest After Setup)

### First Time Setup (One Time Only)
```bash
# 1. Set project
gcloud config set project YOUR_PROJECT_ID

# 2. Enable APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com secretmanager.googleapis.com

# 3. Create OpenAI secret
echo "sk-your-openai-key" | gcloud secrets create OPENAI_API_KEY --data-file=-

# 4. Grant permissions
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)")
gcloud projects add-iam-policy-binding $(gcloud config get-value project) --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" --role="roles/secretmanager.secretAccessor"
gcloud projects add-iam-policy-binding $(gcloud config get-value project) --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" --role="roles/run.admin"
gcloud projects add-iam-policy-binding $(gcloud config get-value project) --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" --role="roles/iam.serviceAccountUser"
```

### Deploy (Every Time)
```bash
gcloud builds submit --config=cloudbuild.yaml
```

---

## Copy-Paste Complete Setup (All in One)

```bash
# ============================================
# COMPLETE DEPLOYMENT - COPY ALL OF THIS
# ============================================

# Set your project ID
export PROJECT_ID="your-project-id-here"
gcloud config set project $PROJECT_ID

# Enable APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  secretmanager.googleapis.com \
  containerregistry.googleapis.com

# Create OpenAI secret (replace sk-xxx with your key)
echo "sk-your-openai-api-key" | gcloud secrets create OPENAI_API_KEY --data-file=-

# Create JWT secret
echo "$(openssl rand -base64 64)" | gcloud secrets create JWT_SECRET_KEY --data-file=-

# Grant permissions
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/storage.admin"

# Build and deploy!
gcloud builds submit --config=cloudbuild.yaml

# Get your URLs
echo ""
echo "Backend URL:"
gcloud run services describe legal-bot-backend --region=us-central1 --format='value(status.url)'
echo ""
echo "Frontend URL:"
gcloud run services describe legal-bot-frontend --region=us-central1 --format='value(status.url)'
```

---

## Super Quick Deploy (If Already Set Up)

```bash
# Just build and deploy
gcloud builds submit --config=cloudbuild.yaml

# Or individual services
gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/legal-bot-backend:latest backend/
gcloud run deploy legal-bot-backend --image gcr.io/$(gcloud config get-value project)/legal-bot-backend:latest --region=us-central1
```

---

## Troubleshooting

### "Permission denied"
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### "API not enabled"
```bash
gcloud services enable cloudbuild.googleapis.com run.googleapis.com
```

### "Secret not found"
```bash
echo "your-openai-key" | gcloud secrets create OPENAI_API_KEY --data-file=-
```

### View build logs
```bash
gcloud builds log --stream $(gcloud builds list --limit=1 --format='value(id)')
```

### Check service status
```bash
gcloud run services list --region=us-central1
```

---

## Cost Estimate

- **Cloud Run**: Free tier includes 2 million requests/month
- **Cloud Build**: 120 free build-minutes/day
- **Container Registry**: ~$0.026/GB/month
- **Estimated cost**: $0-5/month for low-medium traffic

---

## What You Get

✅ Backend API running on Cloud Run (auto-scaling)  
✅ Frontend app running on Cloud Run (auto-scaling)  
✅ HTTPS enabled automatically  
✅ Custom domain support (optional)  
✅ Automatic TLS certificates  
✅ Zero-downtime deployments  
✅ Automatic health checks  
✅ Pay only for what you use  

🎉 **Your app is now live and production-ready!**
