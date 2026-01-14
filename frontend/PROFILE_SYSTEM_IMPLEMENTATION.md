# ChatGPT-Style Profile + Account Menu System

## Implementation Summary

This document describes the complete ChatGPT-style Profile + Account Menu system implemented for LegalAI.

---

## Features Implemented

### A) Profile Menu (Bottom Left Sidebar)

The `SidebarProfileMenuComponent` provides a ChatGPT-style dropdown menu:

- **Profile Header**: Avatar (with initials fallback), display name, username handle
- **Menu Items**:
  - Personalization (theme, font size, response style)
  - Settings (profile edit, privacy, account info)
  - Help (submenu with 6 options)
  - Log out
- **Bottom Account Card**: Avatar, display name, role label

### B) Edit Profile Modal

The `EditProfileModalComponent` provides:

- **Avatar Upload**: Camera icon overlay, file validation (PNG/JPG/WebP, 5MB max)
- **Display Name**: Text input with validation
- **Username**: Unique handle with format validation (3-20 chars, alphanumeric + underscore)
- **Email**: Read-only display
- **Phone**: Optional phone number
- **Address**: Full address fields (line 1, line 2, city, province/state, postal/zip, country)
- **Save/Cancel**: Instant persistence with success feedback

### C) Personalization Page (`/personalization`)

- **Theme**: Dark / Light
- **Font Size**: Small / Medium / Large
- **Response Style**: Concise / Balanced / Detailed
- **Legal Tone**: Neutral / Firm / Very Formal

### D) Settings Page (`/settings`)

- **Profile Section**: Edit profile button
- **Privacy & Cookies**: Toggle switches for analytics/marketing cookies
- **Account Info**: Email, role, lawyer status, member since
- **Danger Zone**: Log out from all devices

### E) Help Pages (`/help`, `/help/:section`)

- Help Center (FAQ)
- Release Notes
- Terms & Policies
- Report Bug (form)
- Keyboard Shortcuts
- Download Apps

### F) Access Control

- **Not Provisioned Page**: Request access form for blocked users
- **Access Denied Page**: Role-based access denial
- **Guards**: `ProvisionedGuard`, `RoleGuard`

---

## Files Created/Modified

### Frontend (Angular)

#### New Services
- `frontend/src/app/services/profile.service.ts` - Profile management service

#### Updated Services
- `frontend/src/app/services/auth.service.ts` - Session, logout, user state management

#### New Components
- `frontend/src/app/pages/help/help.component.ts` - Help pages with tabs
- `frontend/src/app/pages/not-provisioned/not-provisioned.component.ts` - Access request page
- `frontend/src/app/pages/access-denied/access-denied.component.ts` - Access denied page
- `frontend/src/app/pages/static/terms.component.ts` - Terms of Service
- `frontend/src/app/pages/static/privacy.component.ts` - Privacy Policy
- `frontend/src/app/pages/static/cookies.component.ts` - Cookie Policy
- `frontend/src/app/pages/lawyer/lawyer-dashboard.component.ts` - Lawyer dashboard

#### New Guards
- `frontend/src/app/guards/provisioned.guard.ts` - Blocks non-provisioned users
- `frontend/src/app/guards/role.guard.ts` - Role-based access control

#### Updated Routes
- `frontend/src/app/app.routes.ts` - Added all new routes

### Backend (FastAPI)

#### Updated Routes
- `backend/app/api/routes/profile.py` - Added `/api/me`, `/api/logout`, `/api/logout/all`

#### New Documentation
- `backend/docs/bigquery_schema.sql` - Complete BigQuery schema with MERGE upserts

---

## Environment Variables Required

### Frontend (`frontend/src/environments/environment.ts`)

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8001'
};
```

### Backend (`.env`)

```env
# Database
DATABASE_URL=sqlite:///./legalai.db

# OAuth (Google)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:4200/auth/callback/google

# OAuth (Microsoft)
MS_CLIENT_ID=your-microsoft-client-id
MS_CLIENT_SECRET=your-microsoft-client-secret
MS_TENANT=common
MS_REDIRECT_URI=http://localhost:4200/auth/callback/microsoft

# GCS (for avatar uploads)
GCS_BUCKET=legalai-avatars
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# BigQuery (optional, for analytics)
BIGQUERY_PROJECT_ID=your-project-id
BIGQUERY_DATASET=legalai

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

---

## API Endpoints

### Profile & User

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/me` | Get current user + profile |
| GET | `/api/profile` | Get user profile |
| PUT | `/api/profile` | Update user profile |
| POST | `/api/avatar/upload-url` | Get signed URL for avatar upload |
| PUT | `/api/profile/avatar` | Update avatar URL |
| GET | `/api/consent` | Get consent settings |
| PUT | `/api/consent` | Update consent settings |
| POST | `/api/logout` | Logout current session |
| POST | `/api/logout/all` | Logout from all devices |
| POST | `/api/request-access` | Request access (non-provisioned users) |

---

## Local Development Setup

### 1. Start Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8001
```

### 2. Start Frontend (Angular)

```bash
cd frontend
npm install
ng serve --port 4200
```

### 3. Access the App

- Frontend: http://localhost:4200
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

---

## User Flow

1. **Login**: User authenticates via Google/Microsoft/Email
2. **Provisioning Check**: If not provisioned → `/not-provisioned` page
3. **Setup**: First-time users complete setup wizard
4. **Chat**: Main chat interface with sidebar profile menu
5. **Profile Menu**: Click avatar to open dropdown
6. **Edit Profile**: Click profile header to open modal
7. **Settings**: Navigate to settings page for account management
8. **Logout**: Clears session and redirects to login

---

## Role-Based Access

| Role | Access |
|------|--------|
| `client` | Chat, basic features |
| `lawyer` (pending) | Chat, basic features |
| `lawyer` (approved) | Chat, Document Generator, Lawyer Dashboard |
| `employee` | Chat, admin features |
| `employee_admin` | Full admin access |

---

## Security Features

- **Provisioned Users Only**: No auto-signup from OAuth
- **Role Guards**: Protect lawyer-only routes
- **Session Management**: Secure logout from all devices
- **Cookie Consent**: GDPR-compliant consent management
- **Avatar Validation**: File type and size limits

---

## Testing Checklist

- [ ] Profile menu opens on avatar click
- [ ] Edit profile modal opens from menu header
- [ ] Display name and username update persists
- [ ] Avatar upload works with preview
- [ ] Personalization settings save
- [ ] Help pages render correctly
- [ ] Logout clears session and redirects
- [ ] Non-provisioned users see request access page
- [ ] Role guards block unauthorized access
