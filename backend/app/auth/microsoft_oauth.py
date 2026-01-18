"""Microsoft OAuth 2.0 authentication handler."""
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import httpx
import jwt
from fastapi import HTTPException, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class MicrosoftUserInfo(BaseModel):
    """Microsoft user information model."""
    id: str  # Microsoft user ID
    email: str
    displayName: Optional[str] = None
    givenName: Optional[str] = None
    surname: Optional[str] = None
    userPrincipalName: Optional[str] = None
    mail: Optional[str] = None
    jobTitle: Optional[str] = None


class MicrosoftOAuthHandler:
    """Handles Microsoft OAuth 2.0 authentication flow."""
    
    def __init__(self):
        """Initialize Microsoft OAuth handler with credentials from environment."""
        self.client_id = os.getenv("MICROSOFT_CLIENT_ID", "")
        self.client_secret = os.getenv("MICROSOFT_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("MICROSOFT_REDIRECT_URI", "http://localhost:8000/api/auth/microsoft/callback")
        self.tenant_id = os.getenv("MICROSOFT_TENANT_ID", "common")  # 'common' for multi-tenant
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-this-in-production")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_expiration = int(os.getenv("JWT_EXPIRATION_MINUTES", "1440"))
        
        # Microsoft OAuth endpoints
        self.auth_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize"
        self.token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        self.graph_url = "https://graph.microsoft.com/v1.0/me"
        
        if self.client_id and self.client_secret:
            logger.info(f"Microsoft OAuth initialized with redirect URI: {self.redirect_uri}")
        else:
            logger.warning("Microsoft OAuth credentials not configured")
    
    def is_configured(self) -> bool:
        """Check if Microsoft OAuth is properly configured."""
        return bool(self.client_id and self.client_secret)
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Generate Microsoft OAuth authorization URL.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL to redirect user to
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile User.Read",
            "response_mode": "query",
        }
        
        if state:
            params["state"] = state
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        auth_url = f"{self.auth_url}?{query_string}"
        
        logger.info(f"Generated Microsoft authorization URL with state: {state}")
        return auth_url
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from Microsoft
            
        Returns:
            Token response containing access_token, refresh_token, etc.
        """
        logger.info("Exchanging Microsoft authorization code for access token")
        
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
            "scope": "openid email profile User.Read",
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url, 
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                token_data = response.json()
                
                logger.info("Successfully exchanged code for Microsoft token")
                return token_data
        except httpx.HTTPError as e:
            logger.error(f"Error exchanging code for Microsoft token: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange authorization code: {str(e)}"
            )
    
    async def get_user_info(self, access_token: str) -> MicrosoftUserInfo:
        """
        Get user information from Microsoft Graph API using access token.
        
        Args:
            access_token: Microsoft access token
            
        Returns:
            User information from Microsoft
        """
        logger.info("Fetching user info from Microsoft Graph")
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.graph_url, headers=headers)
                response.raise_for_status()
                user_data = response.json()
                
                # Map Microsoft Graph response to our model
                # Microsoft Graph uses 'mail' or 'userPrincipalName' for email
                email = user_data.get('mail') or user_data.get('userPrincipalName', '')
                
                user_info = MicrosoftUserInfo(
                    id=user_data.get('id', ''),
                    email=email,
                    displayName=user_data.get('displayName'),
                    givenName=user_data.get('givenName'),
                    surname=user_data.get('surname'),
                    userPrincipalName=user_data.get('userPrincipalName'),
                    mail=user_data.get('mail'),
                    jobTitle=user_data.get('jobTitle')
                )
                
                logger.info(f"Successfully fetched Microsoft user info for: {user_info.email}")
                return user_info
        except httpx.HTTPError as e:
            logger.error(f"Error fetching Microsoft user info: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to fetch user information: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error parsing Microsoft user info: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to parse user information: {str(e)}"
            )
    
    def create_jwt_token(self, user_info: MicrosoftUserInfo) -> str:
        """
        Create JWT token for authenticated user.
        
        Args:
            user_info: Microsoft user information
            
        Returns:
            JWT token string
        """
        logger.info(f"Creating JWT token for Microsoft user: {user_info.email}")
        
        payload = {
            "sub": user_info.id,  # Microsoft user ID
            "email": user_info.email,
            "name": user_info.displayName,
            "given_name": user_info.givenName,
            "family_name": user_info.surname,
            "email_verified": True,  # Microsoft accounts are verified
            "auth_provider": "microsoft",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=self.jwt_expiration),
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        logger.info(f"JWT token created successfully for Microsoft user {user_info.email}")
        return token
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            logger.info(f"JWT token verified for user: {payload.get('email')}")
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid JWT token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )


# Singleton instance
_microsoft_oauth_handler: Optional[MicrosoftOAuthHandler] = None


def get_microsoft_oauth_handler() -> MicrosoftOAuthHandler:
    """Get or create singleton MicrosoftOAuthHandler instance."""
    global _microsoft_oauth_handler
    if _microsoft_oauth_handler is None:
        _microsoft_oauth_handler = MicrosoftOAuthHandler()
    return _microsoft_oauth_handler
