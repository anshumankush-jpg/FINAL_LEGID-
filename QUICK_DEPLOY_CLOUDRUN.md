# ⚡ Quick Deploy to Cloud Run (5 Minutes)

## Option 1: One-Command Deploy (Recommended)

### Windows PowerShell

```powershell
# Deploy everything (backend + frontend)
.\deploy-to-cloudrun.ps1 -ProjectId "your-project-id" -DeployAll

# Or step by step:
# 1. Setup only (create secrets)
.\deploy-to-cloudrun.ps1 -ProjectId "your-project-id" -SetupOnly

# 2. Deploy backend
.\deploy-to-cloudrun.ps1 -ProjectId "your-project-id" -DeployBackend

# 3. Deploy frontend
.\deploy-to-cloudrun.ps1 -ProjectId "your-project-id" -DeployFrontend
```

---

## Option 2: Manual Deploy (Bash/Linux/Mac)

### Prerequisites
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Login
gcloud auth login

# Set project
export PROJECT_ID="your-project-id"
export REGION="us-central1"
gcloud config set project $PROJECT_ID
```

### Enable APIs
```bash
gcloud services enable cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com \
  secretmanager.googleapis.com \
  bigquery.googleapis.com
```

### Create Secrets
```bash
# Required: OpenAI API Key
echo -n "sk-your-openai-key" | gcloud secrets create OPENAI_API_KEY --data-file=-

# Required: JWT Secret
echo -n "$(openssl rand -base64 32)" | gcloud secrets create JWT_SECRET_KEY --data-file=-

# Optional: Google OAuth
echo -n "your-google-client-id" | gcloud secrets create GOOGLE_CLIENT_ID --data-file=-
echo -n "your-google-client-secret" | gcloud secrets create GOOGLE_CLIENT_SECRET --data-file=-

# Optional: Microsoft OAuth
echo -n "your-microsoft-client-id" | gcloud secrets create MICROSOFT_CLIENT_ID --data-file=-
echo -n "your-microsoft-client-secret" | gcloud secrets create MICROSOFT_CLIENT_SECRET --data-file=-
```

### Deploy Backend
```bash
# Build and deploy
gcloud builds submit --config cloudbuild-backend.yaml

# Get backend URL
BACKEND_URL=$(gcloud run services describe legid-backend --region=$REGION --format='value(status.url)')
echo "Backend URL: $BACKEND_URL"
```

### Deploy Frontend
```bash
# Deploy with backend URL
gcloud builds submit --config cloudbuild-frontend.yaml \
  --substitutions=_BACKEND_URL=$BACKEND_URL

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe legid-frontend --region=$REGION --format='value(status.url)')
echo "Frontend URL: $FRONTEND_URL"
```

---

## Option 3: Deploy from GitHub (Auto-Deploy on Push)

### Connect GitHub Repository

1. **Go to Cloud Build Console**:
   https://console.cloud.google.com/cloud-build/triggers

2. **Click "Connect Repository"**

3. **Select GitHub** and authenticate

4. **Select Repository**: `anshumankush-jpg/FINAL_LEGID-`

5. **Create Trigger for Backend**:
   - Name: `deploy-backend-on-push`
   - Event: Push to branch
   - Branch: `^main$`
   - Build config: `cloudbuild-backend.yaml`

6. **Create Trigger for Frontend**:
   - Name: `deploy-frontend-on-push`
   - Event: Push to branch
   - Branch: `^main$`
   - Build config: `cloudbuild-frontend.yaml`
   - Add substitution: `_BACKEND_URL` = (your backend URL)

7. **Push to GitHub** - deployment happens automatically!

---

## Verify Deployment

```bash
# Check backend health
curl https://YOUR-BACKEND-URL/health

# Check frontend
open https://YOUR-FRONTEND-URL
```

---

## Update OAuth Redirect URIs

### Google OAuth Console
1. Go to: https://console.cloud.google.com/apis/credentials
2. Edit your OAuth 2.0 Client
3. Add Authorized redirect URIs:
   ```
   https://YOUR-BACKEND-URL/api/auth/google/callback
   ```

### Microsoft Azure Portal
1. Go to: https://portal.azure.com
2. Azure Active Directory → App registrations
3. Select your app → Authentication
4. Add Redirect URIs:
   ```
   https://YOUR-BACKEND-URL/api/auth/microsoft/callback
   ```

---

## Troubleshooting

### Build Fails
```bash
# Check build logs
gcloud builds list --limit=5
gcloud builds log BUILD_ID
```

### Service Won't Start
```bash
# Check service logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=legid-backend" --limit=50
```

### Secret Access Denied
```bash
# Get project number
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

# Grant access to secrets
gcloud secrets add-iam-policy-binding OPENAI_API_KEY \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## Cost Estimation

### Free Tier (per month)
- Cloud Run: 2 million requests
- Cloud Build: 120 build-minutes/day
- Container Registry: 0.5 GB

### Expected Costs (with traffic)
- **Light usage** (< 10k requests/day): **$0-5/month**
- **Medium usage** (100k requests/day): **$20-50/month**
- **Heavy usage** (1M requests/day): **$200-500/month**

---

## Next Steps

1. ✅ Deploy to Cloud Run
2. ✅ Update OAuth redirect URIs
3. ✅ Test the deployment
4. ✅ Set up monitoring alerts
5. ✅ Configure custom domain (optional)

---

**🎉 You're now live on Google Cloud Run!**
