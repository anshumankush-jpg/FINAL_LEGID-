export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000',  // Backend API URL
  showEvaluation: true,  // Set to false in production
  
  // OAuth Configuration (client IDs only - secrets stay on backend)
  googleClientId: '',  // Set your Google OAuth client ID
  microsoftClientId: '',  // Set your Microsoft OAuth client ID
  
  // Feature flags
  enableMultiAccount: false,
  enableLawyerVerification: true
  
  // Note: API keys should NEVER be in the frontend
  // All API calls go through the backend which handles authentication
};

