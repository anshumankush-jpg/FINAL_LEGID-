# 🚀 How to Deploy LEGID to Google Cloud Run

## ✅ **ALL CODE PUSHED TO GITHUB**

Your complete LEGID application is now in your repository:
**https://github.com/anshumankush-jpg/FINAL_LEGID-**

---

## 📦 **3 Ways to Deploy**

### **Option 1: Automatic One-Command Deploy (Easiest)** ⭐

#### Windows (PowerShell):
```powershell
.\deploy-to-cloudrun.ps1 -ProjectId "your-gcp-project-id" -DeployAll
```

#### Linux/Mac (Bash):
```bash
chmod +x deploy-to-cloudrun.sh
./deploy-to-cloudrun.sh your-gcp-project-id
```

**That's it!** The script will:
- ✅ Enable all required GCP APIs
- ✅ Create secrets in Secret Manager
- ✅ Build Docker containers
- ✅ Deploy backend to Cloud Run
- ✅ Deploy frontend to Cloud Run
- ✅ Give you the live URLs

---

### **Option 2: Deploy from GCP Console (No CLI needed)**

1. **Go to Cloud Build**:
   https://console.cloud.google.com/cloud-build/triggers

2. **Connect your GitHub repo**:
   - Click "Connect Repository"
   - Select GitHub → `anshumankush-jpg/FINAL_LEGID-`

3. **Create Build Trigger**:
   - Name: `deploy-legid`
   - Source: `main` branch
   - Build config: `cloudbuild-backend.yaml`
   - Click "Create"

4. **Run the trigger** → Wait for deployment ✅

---

### **Option 3: Manual Deploy (Full Control)**

#### Step 1: Install Google Cloud SDK
```bash
# Windows: Download from
https://cloud.google.com/sdk/docs/install

# Mac:
brew install google-cloud-sdk

# Linux:
curl https://sdk.cloud.google.com | bash
```

#### Step 2: Authenticate
```bash
gcloud auth login
gcloud config set project YOUR-PROJECT-ID
```

#### Step 3: Enable APIs
```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com \
  secretmanager.googleapis.com
```

#### Step 4: Create Secrets
```bash
# OpenAI API Key (Required)
echo -n "sk-your-openai-key" | gcloud secrets create OPENAI_API_KEY --data-file=-

# JWT Secret (Required)
echo -n "your-jwt-secret" | gcloud secrets create JWT_SECRET_KEY --data-file=-

# Google OAuth (Optional)
echo -n "your-google-client-id" | gcloud secrets create GOOGLE_CLIENT_ID --data-file=-
echo -n "your-google-client-secret" | gcloud secrets create GOOGLE_CLIENT_SECRET --data-file=-

# Microsoft OAuth (Optional)
echo -n "your-microsoft-client-id" | gcloud secrets create MICROSOFT_CLIENT_ID --data-file=-
echo -n "your-microsoft-client-secret" | gcloud secrets create MICROSOFT_CLIENT_SECRET --data-file=-
```

#### Step 5: Deploy Backend
```bash
cd C:\Users\anshu\Downloads\production_level
gcloud builds submit --config cloudbuild-backend.yaml
```

#### Step 6: Deploy Frontend
```bash
# Get backend URL first
BACKEND_URL=$(gcloud run services describe legid-backend --region=us-central1 --format='value(status.url)')

# Deploy frontend
gcloud builds submit --config cloudbuild-frontend.yaml --substitutions=_BACKEND_URL=$BACKEND_URL
```

---

## 📊 **Deployment Files Created**

All deployment files are now in your GitHub repo:

| File | Purpose |
|------|---------|
| `deploy-to-cloudrun.ps1` | Windows PowerShell deployment script |
| `deploy-to-cloudrun.sh` | Linux/Mac bash deployment script |
| `cloudbuild-backend.yaml` | Backend Cloud Build configuration |
| `cloudbuild-frontend.yaml` | Frontend Cloud Build configuration |
| `DEPLOY_TO_CLOUD_RUN_COMPLETE.md` | Complete deployment guide |
| `QUICK_DEPLOY_CLOUDRUN.md` | Quick start guide |

---

## 🔑 **After Deployment**

### 1. Get Your URLs
```bash
# Backend URL
gcloud run services describe legid-backend --region=us-central1 --format='value(status.url)'

# Frontend URL
gcloud run services describe legid-frontend --region=us-central1 --format='value(status.url)'
```

### 2. Update OAuth Redirect URIs

#### Google OAuth:
1. Go to: https://console.cloud.google.com/apis/credentials
2. Edit OAuth 2.0 Client
3. Add: `https://YOUR-BACKEND-URL/api/auth/google/callback`

#### Microsoft OAuth:
1. Go to: https://portal.azure.com
2. Azure AD → App registrations
3. Add: `https://YOUR-BACKEND-URL/api/auth/microsoft/callback`

### 3. Test Deployment
```bash
# Test backend
curl https://YOUR-BACKEND-URL/health

# Open frontend
https://YOUR-FRONTEND-URL
```

---

## 💰 **Cost Estimate**

### Free Tier:
- **Cloud Run**: 2 million requests/month
- **Cloud Build**: 120 build-minutes/day
- **Storage**: 0.5 GB free

### With Normal Usage:
- **Light** (< 10k requests/day): **$0-5/month**
- **Medium** (100k requests/day): **$20-50/month**
- **Heavy** (1M requests/day): **$200-500/month**

---

## 🔧 **Troubleshooting**

### Build Fails?
```bash
# Check logs
gcloud builds list
gcloud builds log BUILD_ID
```

### Service Won't Start?
```bash
# Check service logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50
```

### Secret Access Denied?
```bash
# Grant access
PROJECT_NUMBER=$(gcloud projects describe YOUR-PROJECT-ID --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding OPENAI_API_KEY \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## 🎯 **Quick Start Commands**

```powershell
# Windows - Deploy Everything
.\deploy-to-cloudrun.ps1 -ProjectId "your-project-id" -DeployAll

# Or step by step:
.\deploy-to-cloudrun.ps1 -ProjectId "your-project-id" -SetupOnly
.\deploy-to-cloudrun.ps1 -ProjectId "your-project-id" -DeployBackend
.\deploy-to-cloudrun.ps1 -ProjectId "your-project-id" -DeployFrontend
```

```bash
# Linux/Mac - Deploy Everything
./deploy-to-cloudrun.sh your-project-id

# Or use Cloud Build directly
gcloud builds submit --config cloudbuild-backend.yaml
```

---

## 📚 **Documentation**

- **Complete Guide**: `DEPLOY_TO_CLOUD_RUN_COMPLETE.md`
- **Quick Start**: `QUICK_DEPLOY_CLOUDRUN.md`
- **GitHub Repo**: https://github.com/anshumankush-jpg/FINAL_LEGID-

---

## ✅ **What's Deployed**

- ✅ **Backend API** (FastAPI + Python)
  - Microsoft OAuth login
  - Google OAuth login
  - BigQuery logging
  - Email services (Gmail/SendGrid)
  - Case citations
  - Document generation
  - Vector search (FAISS)

- ✅ **Frontend** (Angular/React)
  - Modern dark theme
  - Chat interface
  - Document upload
  - Voice chat
  - Password reset

---

## 🎉 **You're Ready to Deploy!**

**Choose your method above and get your LEGID app live in 5-10 minutes!**

**Support**: If you have issues, check the logs or create an issue on GitHub.
