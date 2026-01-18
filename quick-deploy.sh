#!/bin/bash
# Quick Deploy to Cloud Run - One Command
# Run: ./quick-deploy.sh

echo "🚀 Quick Deploy to Cloud Run"

# Ensure we're authenticated
PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT" ]; then
    echo "Please authenticate first:"
    echo "  gcloud auth login"
    echo "  gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "Project: $PROJECT"

# Add and commit changes
git add -A
git commit -m "Deploy $(date '+%Y-%m-%d %H:%M')" --allow-empty

# Push to trigger Cloud Build
git push origin main

echo ""
echo "✅ Pushed to Git! Cloud Build will start automatically."
echo "Watch progress: https://console.cloud.google.com/cloud-build/builds?project=$PROJECT"
