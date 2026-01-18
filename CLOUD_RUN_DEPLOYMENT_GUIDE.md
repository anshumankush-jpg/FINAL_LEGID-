# 🚀 LEGID - Cloud Run Deployment Guide

## Complete End-to-End Deployment from GitHub to Cloud Run

---

## 📋 Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud SDK** installed ([Download](https://cloud.google.com/sdk/docs/install))
3. **Git** installed
4. **Project ID** from Google Cloud Console

---

## 🔧 Quick Setup (One-Time)

### Step 1: Install Google Cloud SDK

**Windows (PowerShell as Admin):**
```powershell
# Download and run installer
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:TEMP\GoogleCloudSDKInstaller.exe")
& "$env:TEMP\GoogleCloudSDKInstaller.exe"
```

**Mac/Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### Step 2: Create GCP Project

```bash
# Create new project
gcloud projects create legid-production --name="LEGID Production"

# Set as default
gcloud config set project legid-production

# Enable billing (required for Cloud Run)
# Go to: https://console.cloud.google.com/billing
```

### Step 3: Create Required Secrets

```bash
# Enable Secret Manager
gcloud services enable secretmanager.googleapis.com

# Create secrets (replace with your actual values)
echo -n "your-openai-api-key" | gcloud secrets create OPENAI_API_KEY --data-file=-
echo -n "your-jwt-secret-key" | gcloud secrets create JWT_SECRET_KEY --data-file=-
echo -n "your-google-client-id" | gcloud secrets create GOOGLE_CLIENT_ID --data-file=-
echo -n "your-google-client-secret" | gcloud secrets create GOOGLE_CLIENT_SECRET --data-file=-

# Optional: Microsoft OAuth
echo -n "your-microsoft-client-id" | gcloud secrets create MICROSOFT_CLIENT_ID --data-file=-
echo -n "your-microsoft-client-secret" | gcloud secrets create MICROSOFT_CLIENT_SECRET --data-file=-
```

---

## 🚀 Deployment Methods

### Method 1: One-Command Deployment (Recommended)

**Windows PowerShell:**
```powershell
cd C:\Users\anshu\Downloads\production_level
.\DEPLOY_TO_CLOUD_RUN.ps1
```

**Mac/Linux:**
```bash
cd /path/to/production_level
chmod +x deploy-to-cloud-run.sh
./deploy-to-cloud-run.sh
```

---

### Method 2: GitHub Trigger (Automatic on Push)

#### Set up Cloud Build Trigger:

```bash
# 1. Connect GitHub repository
gcloud builds triggers create github \
  --name="legid-deploy" \
  --repo-name="FINAL_LEGID-" \
  --repo-owner="anshumankush-jpg" \
  --branch-pattern="^main$" \
  --build-config="cloudbuild.yaml"

# 2. Grant permissions
PROJECT_NUMBER=$(gcloud projects describe legid-production --format="value(projectNumber)")
gcloud projects add-iam-policy-binding legid-production \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding legid-production \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud iam service-accounts add-iam-policy-binding \
  ${PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

Now every push to `main` branch will auto-deploy!

---

### Method 3: Manual Cloud Build

```bash
# Navigate to project
cd production_level

# Submit build to Cloud Build
gcloud builds submit --config=cloudbuild.yaml
```

---

### Method 4: Step-by-Step Manual Deployment

#### Deploy Backend:

```bash
# Navigate to backend
cd backend

# Build and push image
gcloud builds submit --tag gcr.io/legid-production/legid-backend

# Deploy to Cloud Run
gcloud run deploy legid-backend \
  --image gcr.io/legid-production/legid-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --min-instances 1 \
  --max-instances 10 \
  --set-secrets="OPENAI_API_KEY=OPENAI_API_KEY:latest,JWT_SECRET_KEY=JWT_SECRET_KEY:latest"

# Get Backend URL
BACKEND_URL=$(gcloud run services describe legid-backend --region us-central1 --format "value(status.url)")
echo "Backend URL: $BACKEND_URL"
```

#### Deploy Frontend:

```bash
# Navigate to frontend
cd ../frontend

# Build and push image
gcloud builds submit --tag gcr.io/legid-production/legid-frontend

# Deploy to Cloud Run
gcloud run deploy legid-frontend \
  --image gcr.io/legid-production/legid-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --set-env-vars="API_URL=$BACKEND_URL"

# Get Frontend URL
FRONTEND_URL=$(gcloud run services describe legid-frontend --region us-central1 --format "value(status.url)")
echo "Frontend URL: $FRONTEND_URL"
```

---

## ⚙️ Post-Deployment Configuration

### 1. Update OAuth Redirect URIs

**Google Cloud Console:**
- Go to: https://console.cloud.google.com/apis/credentials
- Edit your OAuth 2.0 Client
- Add redirect URI: `https://YOUR-BACKEND-URL/api/auth/google/callback`

**Azure Portal (for Microsoft):**
- Go to: https://portal.azure.com
- Navigate to App registrations → Your App
- Add redirect URI: `https://YOUR-BACKEND-URL/api/auth/microsoft/callback`

### 2. Configure Environment Variables

```bash
gcloud run services update legid-backend \
  --region us-central1 \
  --set-env-vars="ENVIRONMENT=production,LOG_LEVEL=INFO,LLM_PROVIDER=openai"
```

### 3. Set Up Custom Domain (Optional)

```bash
# Map custom domain
gcloud beta run domain-mappings create \
  --service legid-frontend \
  --domain legid.yourdomain.com \
  --region us-central1
```

---

## 📊 Monitoring & Logs

### View Logs:
```bash
# Backend logs
gcloud run services logs read legid-backend --region us-central1 --limit 100

# Frontend logs
gcloud run services logs read legid-frontend --region us-central1 --limit 100
```

### Monitor in Console:
- **Cloud Run:** https://console.cloud.google.com/run
- **Cloud Build:** https://console.cloud.google.com/cloud-build/builds
- **Logs:** https://console.cloud.google.com/logs

---

## 💰 Cost Estimation

| Service | Specs | Est. Monthly Cost |
|---------|-------|-------------------|
| Backend (Cloud Run) | 2 vCPU, 2GB RAM, min 1 instance | ~$30-50 |
| Frontend (Cloud Run) | 1 vCPU, 512MB RAM, min 0 | ~$5-15 |
| Container Registry | Storage | ~$1-5 |
| Cloud Build | Build minutes | ~$0-10 |
| **Total** | | **~$40-80/month** |

*Costs vary based on traffic. Free tier includes 2M requests/month.*

---

## 🔧 Troubleshooting

### Common Issues:

**1. Build Failed - Dockerfile not found:**
```bash
# Make sure you're in the right directory
ls backend/Dockerfile
ls frontend/Dockerfile
```

**2. Secrets not found:**
```bash
# List secrets
gcloud secrets list

# Create missing secret
echo -n "value" | gcloud secrets create SECRET_NAME --data-file=-
```

**3. Permission denied:**
```bash
# Grant Cloud Build permissions
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)")
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"
```

**4. Cold start issues:**
```bash
# Set minimum instances
gcloud run services update legid-backend --min-instances 1 --region us-central1
```

---

## ✅ Deployment Checklist

- [ ] GCP Project created with billing enabled
- [ ] Google Cloud SDK installed and authenticated
- [ ] Required APIs enabled
- [ ] Secrets created in Secret Manager
- [ ] Backend deployed successfully
- [ ] Frontend deployed successfully
- [ ] OAuth redirect URIs updated
- [ ] Environment variables configured
- [ ] Custom domain set up (optional)
- [ ] Monitoring configured

---

## 📞 Support

- **GitHub Issues:** https://github.com/anshumankush-jpg/FINAL_LEGID-/issues
- **Cloud Run Docs:** https://cloud.google.com/run/docs
- **Cloud Build Docs:** https://cloud.google.com/build/docs

---

**Built with ❤️ by the LEGID Team**
