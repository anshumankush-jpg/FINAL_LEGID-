# Quick Deploy to Cloud Run - One Command
# Run: .\quick-deploy.ps1

Write-Host "🚀 Quick Deploy to Cloud Run" -ForegroundColor Cyan

# Ensure we're authenticated
$project = gcloud config get-value project 2>$null
if ([string]::IsNullOrEmpty($project)) {
    Write-Host "Please authenticate first:" -ForegroundColor Yellow
    Write-Host "  gcloud auth login" -ForegroundColor White
    Write-Host "  gcloud config set project YOUR_PROJECT_ID" -ForegroundColor White
    exit 1
}

Write-Host "Project: $project" -ForegroundColor Green

# Add and commit changes
git add -A
git commit -m "Deploy $(Get-Date -Format 'yyyy-MM-dd HH:mm')" --allow-empty

# Push to trigger Cloud Build
git push origin main

Write-Host "`n✅ Pushed to Git! Cloud Build will start automatically." -ForegroundColor Green
Write-Host "`nWatch progress: https://console.cloud.google.com/cloud-build/builds?project=$project" -ForegroundColor Cyan
