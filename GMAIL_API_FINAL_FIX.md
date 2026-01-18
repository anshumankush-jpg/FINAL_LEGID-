# 🔧 Gmail API - Final Configuration Steps

**Status:** Gmail API enabled ✅  
**Issue:** "Precondition check failed" ❌  
**Cause:** Missing one final step in Google Workspace

---

## ⚠️ Current Error

```
Gmail API error: <HttpError 400 "Precondition check failed">
```

This means: The user **anshuman.kush@predictivetechlabs.com** is not properly configured.

---

## ✅ Final Steps Needed

### Step 1: Verify the User Exists in Workspace

1. Go to: https://admin.google.com/u/0/ac/users
2. Search for: **anshuman.kush@predictivetechlabs.com**
3. **Does this user exist?**
   - If **NO** → Create the user OR use a different existing user
   - If **YES** → Continue to Step 2

### Step 2: Enable Gmail for This User

1. Click on the user: **anshuman.kush@predictivetechlabs.com**
2. Go to: **Apps** section
3. Find: **Gmail**
4. Make sure Gmail is **ON** (enabled)

### Step 3: Wait for Propagation

After making changes:
- Wait **5-10 minutes** for Google to propagate changes
- Domain-wide delegation can take time to activate

### Step 4: Verify Domain-Wide Delegation Again

1. Go to: https://admin.google.com
2. Navigate: **Security** → **Access and data control** → **API Controls**
3. Click: **Manage Domain-Wide Delegation**
4. Find: Client ID `108041415752282433237`
5. **Verify it shows:**
   ```
   Client ID: 108041415752282433237
   Scopes: https://www.googleapis.com/auth/gmail.send
   ```

---

## 🎯 Alternative: Use a Different User

If **anshuman.kush@predictivetechlabs.com** doesn't exist, tell me:
- What Workspace user email DOES exist?
- Example: admin@predictivetechlabs.com
- Example: support@predictivetechlabs.com

I'll update the code to use that instead!

---

## ⚡ Or: Use SendGrid (Much Simpler!)

Since Gmail API is complex, you could:
1. Get SendGrid API key (2 minutes)
2. I'll integrate it
3. Emails work immediately!

**SendGrid setup:**
- Go to: https://sendgrid.com
- Sign up (free)
- Get API key
- Done!

---

## 🔍 Quick Check

**Answer these:**

1. **Does anshuman.kush@predictivetechlabs.com exist in your Workspace?**
   - YES → I'll wait for propagation (5-10 min)
   - NO → Tell me which Workspace email to use instead

2. **Or skip Gmail API complexity?**
   - Get SendGrid API key (free, 2 minutes)
   - Much simpler than Gmail API

---

**What would you like to do?**
