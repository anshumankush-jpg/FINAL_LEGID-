# 📧 Enable Real Gmail Email Sending

**Service Account:** auth-email-sender@auth-login-page-481522.iam.gserviceaccount.com  
**JSON Key:** ✅ Already configured in `gcp-email-service-account.json`

---

## 🚨 Current Issue

**Problem:** Gmail API with service accounts requires **domain-wide delegation** OR a verified sending domain.

**Your service account CAN:**
- ✅ Access BigQuery
- ✅ Use most GCP services

**But CANNOT (yet):**
- ❌ Send emails via Gmail API (requires Google Workspace + delegation)

---

## ✅ Solution: Use SendGrid (Recommended - Easiest!)

SendGrid is FREE for 100 emails/day and takes 5 minutes to set up.

### Step 1: Get SendGrid API Key

1. Go to: https://sendgrid.com
2. Sign up (free account)
3. Verify your email
4. Go to: Settings → API Keys
5. Create API Key
6. Copy the key

### Step 2: Install SendGrid

```powershell
cd backend
pip install sendgrid
```

### Step 3: Add to .env

```env
SENDGRID_API_KEY=SG.your-api-key-here
EMAIL_FROM=noreply@weknowrights.ca
```

### Step 4: Update Code

I'll create the SendGrid implementation for you!

---

## 🔄 Alternative Solutions

### Option 1: SendGrid (RECOMMENDED)
- ✅ Free tier: 100 emails/day
- ✅ Setup time: 5 minutes
- ✅ No domain verification needed for testing
- ✅ Easy integration

### Option 2: AWS SES
- ✅ Very cheap ($0.10 per 1000 emails)
- ⚠️ Requires AWS account
- ⚠️ Domain verification required

### Option 3: Gmail API with Domain-Wide Delegation
- ⚠️ Requires Google Workspace (paid)
- ⚠️ Requires admin access
- ⚠️ Complex setup

### Option 4: SMTP (Gmail/Outlook)
- ⚠️ Less secure (app passwords)
- ⚠️ Rate limited
- ⚠️ May trigger spam filters

---

## 💡 Quick Fix for Testing

**For now, the system shows the reset link in:**
1. Browser console (F12)
2. Backend logs
3. API response (debug mode)

**This is actually BETTER for testing** because:
- ✅ You can test immediately
- ✅ No email delays
- ✅ No spam folder issues
- ✅ Works offline

---

## 🚀 Want Me to Set Up SendGrid for You?

Just say "yes" and I'll:
1. Create SendGrid email service
2. Update the forgot password endpoint
3. Add HTML email templates
4. Test email sending

**You just need to:**
- Sign up at sendgrid.com
- Get your API key
- Give it to me

---

## 📝 Current Status

**Email Service:** ✅ Configured (Gmail API)  
**Service Account:** ✅ Loaded  
**Actually Sending:** ❌ Needs domain delegation OR SendGrid  
**Workaround:** ✅ Reset link shown in console/logs  

**For production, use SendGrid - it's the easiest solution!**
