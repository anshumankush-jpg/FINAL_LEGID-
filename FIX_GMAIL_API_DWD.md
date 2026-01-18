# 🔧 Fix Gmail API Domain-Wide Delegation

**Current Status:** Domain-wide delegation configured ✅  
**Issue:** "Precondition check failed" error ❌  
**Workspace Email:** anshuman.kush@predictivetechlabs.com ✅

---

## ✅ What You Need to Do (3 More Steps):

### Step 1: Enable Gmail API in GCP Console

1. Go to: https://console.cloud.google.com/apis/library/gmail.googleapis.com?project=auth-login-page-481522
2. Click "**ENABLE**"
3. Wait 30 seconds for activation

**Or via command line:**
```bash
gcloud auth login
gcloud services enable gmail.googleapis.com --project=auth-login-page-481522
```

---

### Step 2: Verify Domain-Wide Delegation Settings

Go to Google Workspace Admin Console:

1. Go to: https://admin.google.com
2. Navigate to: **Security** → **Access and data control** → **API Controls**
3. Scroll to: **Domain-wide delegation**
4. Find your service account: `108041415752282433237`
5. Verify the settings:

**Client ID:** `108041415752282433237`

**OAuth Scopes (should have):**
```
https://www.googleapis.com/auth/gmail.send
https://www.googleapis.com/auth/gmail.compose
```

6. If missing scopes, click "Edit" and add them

---

### Step 3: Verify the User Email Exists

The impersonation email must:
- ✅ Be a real Google Workspace user
- ✅ Exist in your Workspace
- ✅ Have Gmail enabled

**Check:**
1. Go to: https://admin.google.com/ac/users
2. Search for: **anshuman.kush@predictivetechlabs.com**
3. Verify the user exists
4. Verify Gmail is enabled for this user

**If the user doesn't exist:**
- Create it in Workspace admin
- Or use a different existing Workspace user email

---

## 🔍 Current Error Diagnosis

**Error:** "Precondition check failed"

**This means:**
- ❌ Gmail API is not enabled in GCP project
- OR ❌ The delegate user doesn't exist
- OR ❌ The delegate user doesn't have Gmail enabled
- OR ❌ Scopes not properly authorized

---

## ✅ Quick Checklist

Run through this checklist:

- [ ] Gmail API enabled in project `auth-login-page-481522`
- [ ] Domain-wide delegation configured with Client ID: `108041415752282433237`
- [ ] Scopes include: `https://www.googleapis.com/auth/gmail.send`
- [ ] User `anshuman.kush@predictivetechlabs.com` exists in Workspace
- [ ] Gmail is enabled for that user
- [ ] Service account JSON file is correct

---

## 🎯 After Fixing

Once Gmail API is enabled and delegation is complete:

### Test Welcome Email:
```powershell
# Register new user
Invoke-RestMethod -Uri "http://localhost:8000/api/auth/v2/register" -Method Post -Body (@{email="newuser@test.com"; password="Test123!"; name="Test"} | ConvertTo-Json) -ContentType "application/json"

# Check achintpalsingh94@gmail.com for welcome email!
```

### Test Password Reset:
```powershell
# Request reset
Invoke-RestMethod -Uri "http://localhost:8000/api/auth/v2/forgot-password" -Method Post -Body (@{email="achintpalsingh94@gmail.com"} | ConvertTo-Json) -ContentType "application/json"

# Check achintpalsingh94@gmail.com for reset email!
```

---

## 💡 Alternative: Skip the Complex Setup

If Gmail API is too complex, **I've already prepared SendGrid** which:
- ✅ Works immediately (no Workspace needed)
- ✅ FREE (100 emails/day)
- ✅ 2-minute setup
- ✅ Just need API key

Your choice! Let me know what you prefer.

---

**Next: Enable Gmail API in your GCP project!**
