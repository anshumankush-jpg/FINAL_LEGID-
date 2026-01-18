# 🚀 Complete Guide: Deploy LEGID to Google Cloud Run from GitHub

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **GitHub Repository**: https://github.com/anshumankush-jpg/FINAL_LEGID-
3. **Google Cloud SDK** installed (gcloud CLI)

---

## Step 1: Initial GCP Setup (One-Time)

### 1.1 Install Google Cloud SDK

**Windows:**
```powershell
# Download and install from:
# https://cloud.google.com/sdk/docs/install

# Or use PowerShell:
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe
```

### 1.2 Authenticate and Configure

```bash
# Login to Google Cloud
gcloud auth login

# Set your project (replace with your project ID)
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable bigquery.googleapis.com
```

---

## Step 2: Create GCP Project Configuration

### 2.1 Set Environment Variables

```bash
# Set these variables (replace with your values)
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"
export BACKEND_SERVICE="legid-backend"
export FRONTEND_SERVICE="legid-frontend"

# For Windows PowerShell:
$env:PROJECT_ID="your-gcp-project-id"
$env:REGION="us-central1"
$env:BACKEND_SERVICE="legid-backend"
$env:FRONTEND_SERVICE="legid-frontend"
```

### 2.2 Create Secret Manager Secrets

```bash
# Create secrets for sensitive data
echo -n "your-openai-api-key" | gcloud secrets create OPENAI_API_KEY --data-file=-
echo -n "your-jwt-secret-key" | gcloud secrets create JWT_SECRET_KEY --data-file=-
echo -n "your-google-client-id" | gcloud secrets create GOOGLE_CLIENT_ID --data-file=-
echo -n "your-google-client-secret" | gcloud secrets create GOOGLE_CLIENT_SECRET --data-file=-
echo -n "your-microsoft-client-id" | gcloud secrets create MICROSOFT_CLIENT_ID --data-file=-
echo -n "your-microsoft-client-secret" | gcloud secrets create MICROSOFT_CLIENT_SECRET --data-file=-

# For Windows PowerShell:
"your-openai-api-key" | gcloud secrets create OPENAI_API_KEY --data-file=-
"your-jwt-secret-key" | gcloud secrets create JWT_SECRET_KEY --data-file=-
```

---

## Step 3: Connect GitHub to Cloud Build

### 3.1 Link GitHub Repository

```bash
# Navigate to Cloud Build in GCP Console
# Or use CLI to connect repository:
gcloud alpha builds connections create github github-connection \
  --region=$REGION

# Create repository connection
gcloud alpha builds repositories create legid-repo \
  --remote-uri=https://github.com/anshumankush-jpg/FINAL_LEGID-.git \
  --connection=github-connection \
  --region=$REGION
```

**OR use the Console:**
1. Go to: https://console.cloud.google.com/cloud-build/triggers
2. Click "Connect Repository"
3. Select "GitHub" → Authenticate
4. Select: `anshumankush-jpg/FINAL_LEGID-`

---

## Step 4: Deploy Using Cloud Build

### 4.1 Deploy Backend

```bash
# Submit build from GitHub
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=_SERVICE_NAME=$BACKEND_SERVICE,_REGION=$REGION \
  https://github.com/anshumankush-jpg/FINAL_LEGID-.git

# Or deploy from local directory
cd C:\Users\anshu\Downloads\production_level
gcloud builds submit --config cloudbuild.yaml
```

### 4.2 Deploy Frontend

```bash
# Deploy frontend separately
gcloud builds submit \
  --config=cloudbuild-frontend.yaml \
  --substitutions=_SERVICE_NAME=$FRONTEND_SERVICE,_REGION=$REGION
```

---

## Step 5: Configure Cloud Run Services

### 5.1 Update Backend Service

```bash
# Deploy backend with secrets
gcloud run deploy $BACKEND_SERVICE \
  --image=gcr.io/$PROJECT_ID/legid-backend:latest \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --min-instances=0 \
  --max-instances=10 \
  --timeout=300 \
  --set-secrets="OPENAI_API_KEY=OPENAI_API_KEY:latest,JWT_SECRET_KEY=JWT_SECRET_KEY:latest,GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID:latest,GOOGLE_CLIENT_SECRET=GOOGLE_CLIENT_SECRET:latest,MICROSOFT_CLIENT_ID=MICROSOFT_CLIENT_ID:latest,MICROSOFT_CLIENT_SECRET=MICROSOFT_CLIENT_SECRET:latest" \
  --set-env-vars="LLM_PROVIDER=openai,ENVIRONMENT=production,LOG_LEVEL=INFO"
```

### 5.2 Update Frontend Service

```bash
# Get backend URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region=$REGION --format='value(status.url)')

# Deploy frontend with backend URL
gcloud run deploy $FRONTEND_SERVICE \
  --image=gcr.io/$PROJECT_ID/legid-frontend:latest \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=5 \
  --set-env-vars="VITE_API_URL=$BACKEND_URL,VITE_ENVIRONMENT=production"
```

---

## Step 6: Set Up Cloud Build Triggers (Auto-Deploy)

### 6.1 Create Trigger for Backend

```bash
gcloud builds triggers create github \
  --name="deploy-backend-on-push" \
  --repo-name=FINAL_LEGID- \
  --repo-owner=anshumankush-jpg \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml \
  --include-logs-with-status
```

### 6.2 Create Trigger for Frontend

```bash
gcloud builds triggers create github \
  --name="deploy-frontend-on-push" \
  --repo-name=FINAL_LEGID- \
  --repo-owner=anshumankush-jpg \
  --branch-pattern="^main$" \
  --build-config=cloudbuild-frontend.yaml \
  --include-logs-with-status
```

---

## Step 7: Configure Custom Domain (Optional)

### 7.1 Map Custom Domain

```bash
# Add domain mapping
gcloud run domain-mappings create \
  --service=$FRONTEND_SERVICE \
  --domain=www.yourdomain.com \
  --region=$REGION

gcloud run domain-mappings create \
  --service=$BACKEND_SERVICE \
  --domain=api.yourdomain.com \
  --region=$REGION
```

### 7.2 Update DNS Records

Add the DNS records shown in the output to your domain provider.

---

## Step 8: Verify Deployment

### 8.1 Get Service URLs

```bash
# Get frontend URL
gcloud run services describe $FRONTEND_SERVICE \
  --region=$REGION \
  --format='value(status.url)'

# Get backend URL
gcloud run services describe $BACKEND_SERVICE \
  --region=$REGION \
  --format='value(status.url)'
```

### 8.2 Test Deployment

```bash
# Test backend health
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region=$REGION --format='value(status.url)')
curl $BACKEND_URL/health

# Test frontend
FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --region=$REGION --format='value(status.url)')
echo "Visit: $FRONTEND_URL"
```

---

## Step 9: Monitor and Logs

### 9.1 View Logs

```bash
# Backend logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$BACKEND_SERVICE" \
  --limit=50 \
  --format=json

# Frontend logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$FRONTEND_SERVICE" \
  --limit=50 \
  --format=json
```

### 9.2 View Metrics

Visit: https://console.cloud.google.com/run

---

## Step 10: Update OAuth Redirect URIs

### 10.1 Google OAuth Console

1. Go to: https://console.cloud.google.com/apis/credentials
2. Update **Authorized redirect URIs**:
   - Add: `https://YOUR-BACKEND-URL/api/auth/google/callback`

### 10.2 Microsoft Azure Portal

1. Go to: https://portal.azure.com
2. Navigate to **Azure Active Directory** → **App registrations**
3. Update **Redirect URIs**:
   - Add: `https://YOUR-BACKEND-URL/api/auth/microsoft/callback`

---

## Troubleshooting

### Common Issues

**1. Build Fails**
```bash
# Check build logs
gcloud builds list --limit=5
gcloud builds log BUILD_ID
```

**2. Service Won't Start**
```bash
# Check service logs
gcloud run services logs read $BACKEND_SERVICE --region=$REGION
```

**3. Secret Access Denied**
```bash
# Grant Cloud Run access to secrets
gcloud secrets add-iam-policy-binding OPENAI_API_KEY \
  --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

**4. CORS Issues**
- Update `backend/app/main.py` CORS origins to include Cloud Run URLs

---

## Cost Optimization

### Free Tier Limits
- **Cloud Run**: 2 million requests/month free
- **Cloud Build**: 120 build-minutes/day free
- **Container Registry**: 0.5 GB storage free

### Optimization Tips
```bash
# Set min instances to 0 (cold starts but cost-effective)
gcloud run services update $BACKEND_SERVICE \
  --min-instances=0 \
  --region=$REGION

# Reduce memory if possible
gcloud run services update $BACKEND_SERVICE \
  --memory=1Gi \
  --region=$REGION
```

---

## Next Steps

1. ✅ Set up monitoring alerts
2. ✅ Configure Cloud CDN for frontend
3. ✅ Set up Cloud Armor for DDoS protection
4. ✅ Enable Cloud SQL for production database
5. ✅ Set up CI/CD pipeline with tests

---

## Quick Reference Commands

```bash
# Redeploy backend
gcloud builds submit --config cloudbuild.yaml

# Redeploy frontend
gcloud builds submit --config cloudbuild-frontend.yaml

# View service URLs
gcloud run services list --region=$REGION

# Delete services (cleanup)
gcloud run services delete $BACKEND_SERVICE --region=$REGION
gcloud run services delete $FRONTEND_SERVICE --region=$REGION
```

---

**🎉 Your LEGID application is now deployed to Google Cloud Run!**

**Support**: For issues, check logs or contact GCP support.
