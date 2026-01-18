# 🚀 GCP Cloud Run Deployment Guide

Complete deployment guide for Legal AI Application on Google Cloud Platform.

## 📋 Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed ([Download](https://cloud.google.com/sdk/docs/install))
3. **Docker** (optional, for local testing)
4. **API Keys Ready**:
   - OpenAI API Key
   - Google OAuth Client ID & Secret
   - Microsoft OAuth Client ID & Secret (optional)

## 🎯 Quick Deploy (Windows)

```powershell
# 1. Set your GCP project ID
$env:GCP_PROJECT_ID = "your-project-id"

# 2. Run the deployment script
.\deploy.ps1
```

The script will:
- ✅ Enable required GCP APIs
- ✅ Create/update secrets in Secret Manager
- ✅ Build Docker images
- ✅ Deploy to Cloud Run
- ✅ Output your application URLs

## 📝 Manual Deployment Steps

### Step 1: Set Up GCP Project

```bash
# Authenticate
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    secretmanager.googleapis.com \
    bigquery.googleapis.com
```

### Step 2: Create Secrets

```bash
# OpenAI API Key
echo -n "sk-..." | gcloud secrets create OPENAI_API_KEY --data-file=-

# Google OAuth
echo -n "your-google-client-id" | gcloud secrets create GOOGLE_CLIENT_ID --data-file=-
echo -n "your-google-secret" | gcloud secrets create GOOGLE_CLIENT_SECRET --data-file=-

# Microsoft OAuth (optional)
echo -n "your-ms-client-id" | gcloud secrets create MICROSOFT_CLIENT_ID --data-file=-
echo -n "your-ms-secret" | gcloud secrets create MICROSOFT_CLIENT_SECRET --data-file=-

# JWT Secret (auto-generated random string)
openssl rand -hex 32 | gcloud secrets create JWT_SECRET_KEY --data-file=-
```

### Step 3: Grant Secret Access

```bash
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format='value(projectNumber)')

gcloud secrets add-iam-policy-binding OPENAI_API_KEY \
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### Step 4: Deploy

```bash
# Deploy using Cloud Build
gcloud builds submit --config=cloudbuild.yaml .
```

## 🔧 Configuration

### Backend Configuration

- **Memory**: 4Gi (configurable in `cloudbuild.yaml`)
- **CPU**: 2 vCPU
- **Port**: 8000
- **Timeout**: 300 seconds
- **Max Instances**: 10
- **Min Instances**: 0 (scales to zero)

### Frontend Configuration

- **Memory**: 512Mi
- **CPU**: 1 vCPU
- **Port**: 80
- **Timeout**: 300 seconds
- **Max Instances**: 10

## 🔐 OAuth Setup After Deployment

After deployment, update your OAuth redirect URIs:

### Google Cloud Console
1. Go to [APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials)
2. Edit your OAuth 2.0 Client ID
3. Add authorized redirect URI:
   ```
   https://legal-bot-backend-XXXXX-uc.a.run.app/api/auth/google/callback
   ```

### Azure Portal
1. Go to [App Registrations](https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade)
2. Select your app → Authentication
3. Add redirect URI:
   ```
   https://legal-bot-backend-XXXXX-uc.a.run.app/api/auth/microsoft/callback
   ```

## 📊 Monitoring

### View Logs

```bash
# Backend logs
gcloud run services logs read legal-bot-backend --region=us-central1

# Frontend logs
gcloud run services logs read legal-bot-frontend --region=us-central1
```

### Check Service Status

```bash
# Backend
gcloud run services describe legal-bot-backend --region=us-central1

# Frontend
gcloud run services describe legal-bot-frontend --region=us-central1
```

## 🔄 Update Deployment

To update your deployment:

```bash
# Just push new code and trigger build
gcloud builds submit --config=cloudbuild.yaml .
```

Or use the deployment script again:
```powershell
.\deploy.ps1
```

## 🐛 Troubleshooting

### Build Fails

1. **Check Cloud Build logs**:
   ```bash
   gcloud builds list --limit=1
   gcloud builds log [BUILD_ID]
   ```

2. **Common issues**:
   - Missing secrets → Create them in Secret Manager
   - API not enabled → Run `gcloud services enable [API_NAME]`
   - Quota exceeded → Check Cloud Run quotas

### Service Won't Start

1. **Check service logs**:
   ```bash
   gcloud run services logs read legal-bot-backend --region=us-central1 --limit=50
   ```

2. **Common issues**:
   - Missing environment variables → Check secrets are set
   - Port mismatch → Ensure backend uses PORT env var
   - Health check failing → Check `/health` endpoint

### Cold Start Issues

- Increase `min-instances` to 1 (costs more but eliminates cold starts)
- Optimize Docker image size
- Use Cloud CDN for static assets

## 💰 Cost Estimation

**Free Tier** (first 2 million requests/month):
- Cloud Run: Free
- Cloud Build: 120 build-minutes/day free
- Container Registry: 0.5 GB storage free

**After Free Tier**:
- Cloud Run: ~$0.40 per million requests
- Cloud Build: ~$0.003 per build-minute
- Storage: ~$0.026 per GB/month

## 📚 Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)

## ✅ Deployment Checklist

- [ ] GCP project created and billing enabled
- [ ] gcloud CLI installed and authenticated
- [ ] All API keys collected (OpenAI, Google, Microsoft)
- [ ] Secrets created in Secret Manager
- [ ] OAuth redirect URIs updated after deployment
- [ ] Health checks passing (`/health` endpoint)
- [ ] Frontend can connect to backend API
- [ ] BigQuery logging working (check tables)

---

**Need Help?** Check the logs or review the Cloud Build history in GCP Console.
