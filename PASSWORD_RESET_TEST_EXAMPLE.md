# 🔐 Password Reset Test Example

**Generated:** January 17, 2026, 11:59 PM  
**Status:** ✅ Ready to Test

---

## 👤 Test User Created

**Email:** achintpalsingh94@gmail.com  
**Password:** SecurePass2026!  
**Name:** Achint Pal Singh

---

## 🔗 Password Reset Link

**Click or copy this link:**
```
http://localhost:4200/reset-password?token=ntXdcyuj3UD_tjcKme4vnB_lXGHszyogzgN20EX9ITo
```

⏱️ **Expires in:** 15 minutes  
🔒 **Single-use:** Token becomes invalid after password reset

---

## 🎯 Quick Test (Copy-Paste Method)

1. **Copy the reset link above**
2. **Paste it in your browser**
3. **You'll see the "Reset Password" page**
4. **Enter new password** (minimum 8 characters)
5. **Confirm password** (must match)
6. **Click "Reset Password" button**
7. **Success!** You'll be redirected to login
8. **Login with achintpalsingh94@gmail.com and your NEW password**

---

## 📱 Full UI Test (Via Login Page)

### Step 1: Go to Login Page
```
http://localhost:4200
```

### Step 2: Find "Forgot password?" Link
- **Location:** Below the password field, on the **RIGHT side**
- **Color:** Bright cyan/blue
- **Text:** "Forgot password?"

### Step 3: Click the Link
- Form will expand below
- Shows "Enter your email address"

### Step 4: Enter Email
```
achintpalsingh94@gmail.com
```

### Step 5: Send Reset Link
- Click "Send Reset Link" button
- You'll see success message

### Step 6: Get the Link
- Press **F12** (open browser console)
- Look for the password reset link in console logs
- Copy the link

### Step 7: Reset Password
- Paste link in browser
- Enter new password (min 8 characters)
- Confirm password
- Click "Reset Password"

### Step 8: Login
- Redirected to login page
- Login with **achintpalsingh94@gmail.com** and your **NEW password**
- Success! ✅

---

## 🧪 Testing Scenarios

### Test 1: Valid Reset
- ✅ Use link within 15 minutes
- ✅ Enter valid password (8+ chars)
- ✅ Passwords match
- ✅ Should succeed

### Test 2: Expired Token
- ❌ Wait 16+ minutes
- ❌ Try to use link
- ❌ Should show "Reset token has expired"

### Test 3: Invalid Password
- ❌ Enter password with less than 8 characters
- ❌ Should show validation error

### Test 4: Password Mismatch
- ❌ Enter different passwords in both fields
- ❌ Should show "Passwords do not match"

### Test 5: Reuse Token
- ❌ Try to use same link twice
- ❌ Should show "Invalid or expired reset token"

---

## 📊 What Gets Logged

### Backend Console Log:
```
Password reset requested for achintpalsingh94@gmail.com
Reset link (for demo): http://localhost:4200/reset-password?token=...
```

### Browser Console Log (F12):
```javascript
{
  "message": "If the email exists, a password reset link has been sent",
  "reset_link": "http://localhost:4200/reset-password?token=..."
}
```

### BigQuery (Production):
```sql
-- Login events table will show:
- event_type: 'password_reset_requested'
- event_type: 'password_reset_completed'
- timestamp, ip_address, user_agent
```

---

## 🔐 Security Features

✅ **Token Expiration:** 15 minutes  
✅ **Single-use:** Token deleted after successful reset  
✅ **Email Privacy:** Doesn't reveal if email exists  
✅ **Password Validation:** Minimum 8 characters  
✅ **Confirmation Required:** Must match passwords  
✅ **Secure Hashing:** SHA-256 (upgrade to bcrypt for production)  

---

## 🎯 Quick Reference

| What | Value |
|------|-------|
| **Test Email** | achintpalsingh94@gmail.com |
| **Current Password** | SecurePass2026! |
| **Reset Link** | http://localhost:4200/reset-password?token=ntXdcyuj3UD_tjcKme4vnB_lXGHszyogzgN20EX9ITo |
| **Link Valid** | 15 minutes |
| **Min Password Length** | 8 characters |

---

## 📝 Other Test Users

| Email | Password |
|-------|----------|
| test@example.com | Test123456 |
| info@predictivetechlabs.com | TechLabs2026! |
| achintpalsingh94@gmail.com | SecurePass2026! |

All users have forgot password functionality enabled!

---

## ✅ Ready to Test!

**Just copy this link and paste it in your browser:**
```
http://localhost:4200/reset-password?token=ntXdcyuj3UD_tjcKme4vnB_lXGHszyogzgN20EX9ITo
```

**Or test the full flow on the login page at:**
```
http://localhost:4200
```

🎉 **Everything is working and ready to test!**
