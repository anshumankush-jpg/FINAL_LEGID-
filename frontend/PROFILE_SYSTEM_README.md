# LEGID Profile + Account Menu System

A complete ChatGPT-style profile and account management system for the LEGID/LegalAI Angular application.

## Features Implemented

### A) Profile Menu (Bottom Left Sidebar)
- **Profile Trigger**: Avatar + name with chevron indicator
- **Profile Header**: Large avatar with camera icon, display name, username handle
- **Menu Items**:
  - Personalization (theme, font size, response style)
  - Settings (profile, privacy, account info)
  - Help (submenu with 6 pages)
  - Log out
- **Account Summary Card**: Avatar + name + role label

### B) Edit Profile Modal
- Large avatar with camera overlay for upload
- Display name input
- Username input with `@` prefix and validation
- Email (read-only)
- Phone number
- Full address fields (line 1, line 2, city, province/state, postal/zip, country)
- Cancel/Save buttons with loading states
- Real-time username availability check

### C) Personalization Page (`/personalization`)
- Theme: Dark / Light
- Font Size: Small / Medium / Large
- Response Style: Concise / Balanced / Detailed
- Legal Tone: Neutral / Firm / Very Formal
- Auto-save with debounce

### D) Settings Page (`/settings`)
- Profile section with edit button
- Privacy & Cookies section with toggles
- Account information (email, role, lawyer status)
- Danger zone: Logout from all devices

### E) Help Pages (`/help/:section`)
- Help Center with FAQ accordion
- Release Notes with version history
- Terms & Policies (Terms, Privacy, Cookies)
- Report Bug form
- Keyboard Shortcuts reference
- Download Apps page

### F) Not Provisioned Page (`/not-provisioned`)
- Informational message for blocked users
- Request Access form
- Success confirmation

## File Structure

```
frontend/src/app/
├── components/
│   ├── sidebar-profile-menu/
│   │   └── sidebar-profile-menu.component.ts
│   └── edit-profile-modal/
│       └── edit-profile-modal.component.ts
├── pages/
│   ├── personalization/
│   │   └── personalization.component.ts
│   ├── settings/
│   │   └── settings.component.ts
│   ├── help/
│   │   └── help.component.ts
│   └── not-provisioned/
│       └── not-provisioned.component.ts
├── services/
│   ├── auth.service.ts
│   └── profile.service.ts
├── guards/
│   ├── auth.guard.ts
│   ├── setup.guard.ts
│   └── provisioned.guard.ts
└── app.routes.ts
```

## Environment Variables

### Frontend (`frontend/src/environments/environment.ts`)

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000',
  
  // OAuth (if using)
  googleClientId: 'YOUR_GOOGLE_CLIENT_ID',
  microsoftClientId: 'YOUR_MICROSOFT_CLIENT_ID',
  
  // Feature flags
  enableMultiAccount: false,
  enableLawyerVerification: true
};
```

### Backend (`.env`)

```env
# API Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
API_BASE_URL=http://localhost:8000

# Database
DATABASE_URL=sqlite:///./data/legalai.db

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# OAuth Providers
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
MICROSOFT_TENANT_ID=common

# Cloud Storage (for avatars)
GCS_BUCKET_NAME=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# BigQuery (optional, for analytics)
BIGQUERY_PROJECT_ID=your-project-id
BIGQUERY_DATASET=legalai

# OpenAI
OPENAI_API_KEY=your-openai-key
```

## API Endpoints

### Profile Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/profile` | Get full user data (user + profile + consent) |
| PUT | `/api/profile` | Update profile fields |
| PUT | `/api/profile/preferences` | Update preferences JSON |
| GET | `/api/profile/check-username/{username}` | Check username availability |
| POST | `/api/profile/avatar/upload-url` | Get signed URL for avatar upload |
| PUT | `/api/profile/avatar/upload/{user_id}/{filename}` | Upload avatar (local dev) |
| GET | `/api/profile/avatar/{user_id}/{filename}` | Serve avatar (local dev) |

### Consent Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/profile/consent` | Get consent settings |
| PUT | `/api/profile/consent` | Update consent settings |

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/session` | Create session (login) |
| GET | `/api/me` | Get current user |
| POST | `/api/logout` | Logout current session |
| POST | `/api/logout/all` | Logout all devices |

### Access Requests

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/profile/request-access` | Submit access request |

## Local Development Setup

### 1. Start Backend

```bash
cd legal-bot/backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Start Frontend (Angular)

```bash
cd frontend
npm install
npm start
# Opens at http://localhost:4200
```

### 3. Test the Flow

1. Navigate to `http://localhost:4200`
2. Login with credentials or OAuth
3. Click profile avatar in bottom-left sidebar
4. Explore menu items:
   - Click header to open Edit Profile modal
   - Navigate to Personalization
   - Navigate to Settings
   - Expand Help submenu

## OAuth Redirect URIs

### Development
- Google: `http://localhost:4200/auth/callback/google`
- Microsoft: `http://localhost:4200/auth/callback/microsoft`

### Production
- Google: `https://app.legid.ai/auth/callback/google`
- Microsoft: `https://app.legid.ai/auth/callback/microsoft`

## Database Schema

See `legal-bot/docs/bigquery_schema.sql` for complete BigQuery schema including:
- `identity_users` - Core user identity
- `user_profiles` - Extended profile data
- `user_consent` - Cookie/data consent
- `conversations` - Chat history
- `messages` - Individual messages
- `access_requests` - Non-provisioned user requests
- `lawyer_applications` - Lawyer verification

## Security Features

1. **LOGIN-ONLY Access**: Users must be pre-provisioned
2. **Role-Based Access Control**: client, lawyer, employee, employee_admin
3. **Lawyer Verification**: Pending/approved/rejected status
4. **Session Management**: JWT with refresh tokens
5. **Consent Tracking**: GDPR/CCPA compliant
6. **Audit Logging**: All actions logged

## Acceptance Criteria

- [x] Clicking avatar opens dropdown menu
- [x] Clicking profile header opens Edit Profile modal
- [x] Display name + username persist after refresh
- [x] Avatar upload with preview
- [x] Personalization settings save and apply
- [x] Help pages exist and route correctly
- [x] Logout fully logs out user
- [x] Not-provisioned users see access request page

## Troubleshooting

### Avatar Upload Fails
- Check GCS credentials or use local storage fallback
- Verify file type (jpg, jpeg, png, webp only)
- Check file size (max 5MB)

### Username Validation
- 3-20 characters
- Letters, numbers, underscore only
- Must be unique (case-insensitive)

### OAuth Login Issues
- Verify redirect URIs match exactly
- Check client ID/secret in environment
- Ensure user email is provisioned

### Session Expired
- Token expires after 60 minutes by default
- Refresh token should auto-renew
- Clear localStorage and re-login if issues persist
