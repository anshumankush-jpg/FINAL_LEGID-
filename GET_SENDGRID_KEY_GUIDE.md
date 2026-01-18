# 📧 How to Get SendGrid API Key - Complete Guide

**Note:** SendGrid API keys CANNOT be obtained via GCP CLI. You must get them from SendGrid's dashboard. Here's the complete automated process:

---

## 🎯 Method 1: Via SendGrid Website (2 Minutes)

### Step 1: Sign Up
1. Go to: https://signup.sendgrid.com/
2. Fill in:
   - **Email:** achintpalsingh94@gmail.com (or any email)
   - **Password:** (create a strong password)
   - **Company:** Predictive Tech Labs
   - **Website:** https://predictivetechlabs.com (optional)
3. Click "**Create Account**"

### Step 2: Verify Email
1. Check your email inbox
2. Click the verification link
3. Complete email verification

### Step 3: Complete Onboarding
1. SendGrid will ask some questions:
   - **Role:** Developer
   - **Use case:** Transactional emails
   - **Monthly volume:** Less than 1,000
2. Skip sender verification (for now)

### Step 4: Create API Key
1. After login, go to: **Settings** → **API Keys**
   - Direct URL: https://app.sendgrid.com/settings/api_keys
2. Click "**Create API Key**"
3. Settings:
   - **Name:** `LEGID-Production-Emails`
   - **API Key Permissions:** **Full Access** (or just **Mail Send** for security)
4. Click "**Create & View**"
5. **COPY THE KEY IMMEDIATELY!**
   - Starts with `SG.`
   - Example: `SG.aBcD123...`
   - ⚠️ You can only see this ONCE!

---

## 🤖 Method 2: Automated with GCP CLI (After Getting Key)

Once you have the SendGrid API key, run this to configure everything:

```bash
# 1. Set variables
export PROJECT_ID="auth-login-page-481522"
export SENDGRID_KEY="SG.your-actual-key-here"

# 2. Enable APIs
gcloud services enable secretmanager.googleapis.com --project=$PROJECT_ID

# 3. Store in Secret Manager
echo -n "$SENDGRID_KEY" | gcloud secrets create SENDGRID_API_KEY \
  --data-file=- \
  --project=$PROJECT_ID \
  --replication-policy="automatic"

# 4. Grant access to Cloud Run
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

gcloud secrets add-iam-policy-binding SENDGRID_API_KEY \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=$PROJECT_ID

# 5. Verify
gcloud secrets describe SENDGRID_API_KEY --project=$PROJECT_ID

# 6. List versions
gcloud secrets versions list SENDGRID_API_KEY --project=$PROJECT_ID

# 7. Access the secret (to verify)
gcloud secrets versions access latest --secret=SENDGRID_API_KEY --project=$PROJECT_ID
```

---

## 📝 PowerShell Version (Windows)

```powershell
# Complete setup in PowerShell
$PROJECT_ID = "auth-login-page-481522"
$SENDGRID_KEY = Read-Host "Enter your SendGrid API key (SG.xxx)"

# Validate key
if (-not $SENDGRID_KEY.StartsWith("SG.")) {
    Write-Host "ERROR: Invalid SendGrid key!" -ForegroundColor Red
    exit 1
}

# Enable API
gcloud services enable secretmanager.googleapis.com --project=$PROJECT_ID

# Store secret
$SENDGRID_KEY | gcloud secrets create SENDGRID_API_KEY `
    --data-file=- `
    --project=$PROJECT_ID `
    --replication-policy="automatic"

# If secret exists, update it
if ($LASTEXITCODE -ne 0) {
    $SENDGRID_KEY | gcloud secrets versions add SENDGRID_API_KEY `
        --data-file=- `
        --project=$PROJECT_ID
}

# Grant access
$PROJECT_NUMBER = (gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

gcloud secrets add-iam-policy-binding SENDGRID_API_KEY `
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" `
    --role="roles/secretmanager.secretAccessor" `
    --project=$PROJECT_ID

Write-Host "`n[SUCCESS] SendGrid configured in GCP!" -ForegroundColor Green
```

---

## 🔐 Verify Setup via CLI

```bash
# Check secret exists
gcloud secrets describe SENDGRID_API_KEY --project=auth-login-page-481522

# View IAM policy
gcloud secrets get-iam-policy SENDGRID_API_KEY --project=auth-login-page-481522

# List all secrets
gcloud secrets list --project=auth-login-page-481522

# Access the key (for testing)
gcloud secrets versions access latest \
  --secret=SENDGRID_API_KEY \
  --project=auth-login-page-481522
```

---

## 🚀 Deploy to Cloud Run with SendGrid

```bash
# Update Cloud Run service to use the secret
gcloud run services update legal-bot-backend \
  --update-secrets=SENDGRID_API_KEY=SENDGRID_API_KEY:latest \
  --region=us-central1 \
  --project=auth-login-page-481522

# Or deploy fresh
gcloud run deploy legal-bot-backend \
  --image=gcr.io/auth-login-page-481522/legal-bot-backend:latest \
  --region=us-central1 \
  --set-secrets=SENDGRID_API_KEY=SENDGRID_API_KEY:latest \
  --set-env-vars=EMAIL_PROVIDER=sendgrid \
  --project=auth-login-page-481522
```

---

## ✅ What the Complete Setup Does

**Automated via CLI:**
- ✅ Enable Secret Manager API
- ✅ Store SendGrid key in Secret Manager
- ✅ Grant Cloud Run access
- ✅ Configure IAM policies
- ✅ Update environment variables
- ✅ Deploy with secrets

**Manual (2 minutes):**
- Get SendGrid API key from https://sendgrid.com
- Paste it when script asks

---

## 🎯 Quick Start

**Just run my script:**
```powershell
.\setup_sendgrid_complete.ps1
```

**It will:**
1. Open SendGrid signup for you
2. Wait for you to paste API key
3. Automatically configure GCP
4. Update backend code
5. Restart server
6. Test emails
7. Done!

---

**The script is ready! Just run it and follow the prompts!** 🚀
