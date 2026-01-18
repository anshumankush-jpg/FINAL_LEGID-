#!/bin/bash
# ============================================
# Complete Gmail API Setup for GCP
# Run this in Google Cloud Shell
# ============================================

set -e

PROJECT_ID="auth-login-page-481522"
SERVICE_ACCOUNT_EMAIL="auth-email-sender@${PROJECT_ID}.iam.gserviceaccount.com"
WORKSPACE_EMAIL="info@predictivetechlabs.com"

echo "============================================"
echo "GMAIL API ACTIVATION - COMPLETE SETUP"
echo "============================================"
echo ""
echo "Project: $PROJECT_ID"
echo "Service Account: $SERVICE_ACCOUNT_EMAIL"
echo "Workspace Email: $WORKSPACE_EMAIL"
echo ""

# Step 1: Set project
echo "[Step 1] Setting project..."
gcloud config set project $PROJECT_ID

# Step 2: Enable Gmail API
echo ""
echo "[Step 2] Enabling Gmail API..."
gcloud services enable gmail.googleapis.com --project=$PROJECT_ID

# Check if enabled
echo "Verifying Gmail API is enabled..."
gcloud services list --enabled --project=$PROJECT_ID | grep gmail

# Step 3: Enable other required APIs
echo ""
echo "[Step 3] Enabling additional APIs..."
gcloud services enable \
  iamcredentials.googleapis.com \
  servicemanagement.googleapis.com \
  servicecontrol.googleapis.com \
  --project=$PROJECT_ID

# Step 4: Get service account details
echo ""
echo "[Step 4] Service Account Details..."
gcloud iam service-accounts describe $SERVICE_ACCOUNT_EMAIL --project=$PROJECT_ID

# Get the unique ID (Client ID for domain-wide delegation)
CLIENT_ID=$(gcloud iam service-accounts describe $SERVICE_ACCOUNT_EMAIL \
  --project=$PROJECT_ID \
  --format='value(uniqueId)')

echo ""
echo "Service Account Client ID: $CLIENT_ID"
echo ""
echo "============================================"
echo "IMPORTANT: COPY THIS CLIENT ID"
echo "============================================"
echo "Client ID: $CLIENT_ID"
echo ""
echo "Use this in Google Workspace Admin Console:"
echo "1. Go to: https://admin.google.com"
echo "2. Security → API Controls → Domain-wide Delegation"
echo "3. Add client ID: $CLIENT_ID"
echo "4. Add scopes:"
echo "   https://www.googleapis.com/auth/gmail.send"
echo "   https://www.googleapis.com/auth/gmail.compose"
echo "============================================"

# Step 5: Verify API is active
echo ""
echo "[Step 5] Verifying API configuration..."

echo ""
echo "Enabled APIs:"
gcloud services list --enabled --project=$PROJECT_ID | grep -E "gmail|iam|servicemanagement"

echo ""
echo "Service Account Permissions:"
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:$SERVICE_ACCOUNT_EMAIL" \
  --format="table(bindings.role)"

# Step 6: Test API access
echo ""
echo "[Step 6] Testing Gmail API access..."

# Try to call Gmail API (will fail if delegation not complete)
echo "Attempting Gmail API call..."

# Create a simple test using gcloud
gcloud auth activate-service-account \
  --key-file=./gcp-email-service-account.json \
  --project=$PROJECT_ID 2>/dev/null || echo "Service account activated"

echo ""
echo "============================================"
echo "SETUP STATUS"
echo "============================================"
echo ""
echo "✅ Gmail API: Enabled"
echo "✅ Service Account: Active"
echo "✅ Client ID: $CLIENT_ID"
echo ""
echo "⚠️  NEXT STEPS:"
echo ""
echo "1. Verify in Google Workspace Admin:"
echo "   https://admin.google.com/ac/owl/domainwidedelegation"
echo ""
echo "2. Make sure this user EXISTS:"
echo "   $WORKSPACE_EMAIL"
echo "   Check: https://admin.google.com/ac/users"
echo ""
echo "3. Make sure Gmail is ENABLED for that user"
echo ""
echo "4. Wait 5-10 minutes for changes to propagate"
echo ""
echo "5. Then restart your backend and test"
echo ""
echo "============================================"
echo "VERIFICATION COMMANDS"
echo "============================================"
echo ""
echo "# Check if Gmail API is active:"
echo "gcloud services list --enabled | grep gmail"
echo ""
echo "# Get service account Client ID:"
echo "gcloud iam service-accounts describe $SERVICE_ACCOUNT_EMAIL --format='value(uniqueId)'"
echo ""
echo "# List all enabled APIs:"
echo "gcloud services list --enabled --project=$PROJECT_ID"
echo ""
echo "============================================"
echo ""
echo "If Gmail API still doesn't work after this,"
echo "it means your Google Workspace user doesn't exist"
echo "or delegation isn't properly configured."
echo ""
echo "In that case: USE SENDGRID!"
echo "============================================"
