"""Authentication routes for Google and Microsoft OAuth."""
import os
import logging
import secrets
from urllib.parse import urlencode, quote_plus
from fastapi import APIRouter, Query, HTTPException, status, Response, Request
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional

from .google_oauth import get_google_oauth_handler, GoogleUserInfo
from .microsoft_oauth import get_microsoft_oauth_handler, MicrosoftUserInfo
from .bigquery_client import get_bigquery_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


class TokenResponse(BaseModel):
    """Response model for token endpoint."""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserInfoResponse(BaseModel):
    """Response model for user info."""
    email: str
    name: Optional[str]
    picture: Optional[str]
    email_verified: bool


@router.get("/google/login")
async def google_login():
    """
    Initiate Google OAuth login flow.
    
    Redirects user to Google's OAuth consent screen.
    """
    logger.info("Initiating Google OAuth login")
    
    oauth_handler = get_google_oauth_handler()
    
    # Generate random state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # In production, store state in session/redis to validate later
    # For now, we'll skip state validation in the callback
    
    auth_url = oauth_handler.get_authorization_url(state=state)
    logger.info(f"Redirecting to Google OAuth: {auth_url}")
    
    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    state: Optional[str] = Query(None)
):
    """
    Handle Google OAuth callback.
    
    Args:
        code: Authorization code from Google
        error: Error message if OAuth failed
        state: State parameter for CSRF protection
        
    Returns:
        Redirects to frontend with JWT token or error
    """
    logger.info(f"Google OAuth callback received - code present: {bool(code)}, error: {error}")
    
    # Hard-code to 4200 since env vars may not be set correctly
    frontend_url = "http://localhost:4200"
    logger.info(f"Using frontend URL: {frontend_url}")
    
    # Check for OAuth errors
    if error:
        logger.error(f"OAuth error: {error}")
        return RedirectResponse(url=f"{frontend_url}?error={error}")
    
    if not code:
        logger.error("No authorization code received")
        return RedirectResponse(url=f"{frontend_url}?error=no_code")
    
    try:
        oauth_handler = get_google_oauth_handler()
        
        # Exchange code for token
        token_data = await oauth_handler.exchange_code_for_token(code)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token received from Google"
            )
        
        # Get user information
        user_info = await oauth_handler.get_user_info(access_token)
        
        # Create JWT token for our application
        jwt_token = oauth_handler.create_jwt_token(user_info)
        
        # Log to BigQuery
        try:
            bq_client = get_bigquery_client()
            
            # Get IP and user agent for logging
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
            
            # Upsert user identity
            user_id = await bq_client.upsert_identity_user(
                auth_uid=user_info.sub,
                auth_provider="google",
                email=user_info.email,
                role="customer",
                display_name=user_info.name,
                photo_url=user_info.picture,
                is_verified=user_info.email_verified
            )
            
            # Log login event
            await bq_client.log_login_event(
                user_id=user_id or user_info.sub,
                auth_provider="google",
                event_type="login",
                success=True,
                ip_address=ip_address,
                user_agent=user_agent
            )
            logger.info(f"Logged Google login event for user: {user_info.email}")
        except Exception as bq_error:
            logger.warning(f"Failed to log to BigQuery: {bq_error}")
        
        # Redirect to frontend with token (URL encode all parameters)
        # In production, consider using httpOnly cookies instead of URL parameters
        params = {
            'token': jwt_token,
            'email': user_info.email,
            'name': user_info.name or '',
            'picture': user_info.picture or '',
            'provider': 'google'
        }
        redirect_url = f"{frontend_url}?{urlencode(params)}"
        
        logger.info(f"Successfully authenticated user: {user_info.email}")
        logger.info(f"Redirecting to: {frontend_url}?token=...&email={user_info.email}")
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        logger.error(f"Error in OAuth callback: {e}", exc_info=True)
        return RedirectResponse(url=f"{frontend_url}?error=auth_failed")


@router.post("/google/token")
async def google_token_exchange(code: str):
    """
    Exchange Google authorization code for JWT token (alternative to callback).
    
    This endpoint can be used for SPA applications that handle the OAuth
    callback in JavaScript and want to exchange the code for a token via API.
    
    Args:
        code: Authorization code from Google
        
    Returns:
        JWT token and user information
    """
    logger.info("Exchanging Google authorization code for JWT token")
    
    try:
        oauth_handler = get_google_oauth_handler()
        
        # Exchange code for token
        token_data = await oauth_handler.exchange_code_for_token(code)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token received from Google"
            )
        
        # Get user information
        user_info = await oauth_handler.get_user_info(access_token)
        
        # Create JWT token for our application
        jwt_token = oauth_handler.create_jwt_token(user_info)
        
        return TokenResponse(
            access_token=jwt_token,
            user={
                "email": user_info.email,
                "name": user_info.name,
                "picture": user_info.picture,
                "email_verified": user_info.email_verified,
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exchanging token: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to authenticate: {str(e)}"
        )


@router.get("/verify")
async def verify_token(token: str = Query(...)):
    """
    Verify JWT token and return user information.
    
    Args:
        token: JWT token to verify
        
    Returns:
        User information if token is valid
    """
    logger.info("Verifying JWT token")
    
    try:
        oauth_handler = get_google_oauth_handler()
        payload = oauth_handler.verify_jwt_token(token)
        
        return UserInfoResponse(
            email=payload.get("email"),
            name=payload.get("name"),
            picture=payload.get("picture"),
            email_verified=payload.get("email_verified", False),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying token: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


@router.post("/logout")
async def logout():
    """
    Logout endpoint.
    
    In a stateless JWT system, logout is primarily handled client-side
    by removing the token. This endpoint exists for consistency and
    can be extended with token blacklisting if needed.
    """
    logger.info("User logout")
    return {"message": "Successfully logged out"}


@router.get("/config")
async def get_oauth_config():
    """
    Get OAuth configuration for frontend.
    
    Returns client IDs and redirect URIs for frontend to use.
    """
    google_handler = get_google_oauth_handler()
    microsoft_handler = get_microsoft_oauth_handler()
    
    return {
        "google": {
            "client_id": google_handler.client_id,
            "redirect_uri": google_handler.redirect_uri,
            "enabled": bool(google_handler.client_id),
        },
        "microsoft": {
            "client_id": microsoft_handler.client_id,
            "redirect_uri": microsoft_handler.redirect_uri,
            "enabled": microsoft_handler.is_configured(),
        }
    }


# ============================================
# MICROSOFT OAUTH ENDPOINTS
# ============================================

@router.get("/microsoft/login")
async def microsoft_login():
    """
    Initiate Microsoft OAuth login flow.
    
    Redirects user to Microsoft's OAuth consent screen.
    """
    logger.info("Initiating Microsoft OAuth login")
    
    microsoft_handler = get_microsoft_oauth_handler()
    
    if not microsoft_handler.is_configured():
        logger.error("Microsoft OAuth is not configured")
        return JSONResponse(
            status_code=501,
            content={"error": "Microsoft login is not configured. Please set MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET."}
        )
    
    # Generate random state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    auth_url = microsoft_handler.get_authorization_url(state=state)
    logger.info(f"Redirecting to Microsoft OAuth: {auth_url}")
    
    # Return JSON with auth URL for SPA flow (like Google)
    return {"auth_url": auth_url, "state": state}


@router.get("/microsoft/callback")
async def microsoft_callback(
    request: Request,
    code: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None),
    state: Optional[str] = Query(None)
):
    """
    Handle Microsoft OAuth callback.
    
    Args:
        code: Authorization code from Microsoft
        error: Error code if OAuth failed
        error_description: Error description
        state: State parameter for CSRF protection
        
    Returns:
        Redirects to frontend with JWT token or error
    """
    logger.info(f"Microsoft OAuth callback received - code present: {bool(code)}, error: {error}")
    
    frontend_url = "http://localhost:4200"
    
    # Check for OAuth errors
    if error:
        logger.error(f"Microsoft OAuth error: {error} - {error_description}")
        return RedirectResponse(url=f"{frontend_url}?error={error}&error_description={error_description}")
    
    if not code:
        logger.error("No authorization code received from Microsoft")
        return RedirectResponse(url=f"{frontend_url}?error=no_code")
    
    try:
        microsoft_handler = get_microsoft_oauth_handler()
        
        # Exchange code for token
        token_data = await microsoft_handler.exchange_code_for_token(code)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token received from Microsoft"
            )
        
        # Get user information
        user_info = await microsoft_handler.get_user_info(access_token)
        
        # Create JWT token for our application
        jwt_token = microsoft_handler.create_jwt_token(user_info)
        
        # Log to BigQuery
        try:
            bq_client = get_bigquery_client()
            
            # Get IP and user agent for logging
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
            
            # Upsert user identity
            user_id = await bq_client.upsert_identity_user(
                auth_uid=user_info.id,
                auth_provider="microsoft",
                email=user_info.email,
                role="customer",
                display_name=user_info.displayName,
                photo_url=None,  # Microsoft Graph doesn't return photo URL in basic call
                is_verified=True
            )
            
            # Log login event
            await bq_client.log_login_event(
                user_id=user_id or user_info.id,
                auth_provider="microsoft",
                event_type="login",
                success=True,
                ip_address=ip_address,
                user_agent=user_agent
            )
            logger.info(f"Logged Microsoft login event for user: {user_info.email}")
        except Exception as bq_error:
            logger.warning(f"Failed to log to BigQuery: {bq_error}")
        
        # Redirect to frontend with token
        params = {
            'token': jwt_token,
            'email': user_info.email,
            'name': user_info.displayName or '',
            'provider': 'microsoft'
        }
        redirect_url = f"{frontend_url}?{urlencode(params)}"
        
        logger.info(f"Successfully authenticated Microsoft user: {user_info.email}")
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        logger.error(f"Error in Microsoft OAuth callback: {e}", exc_info=True)
        return RedirectResponse(url=f"{frontend_url}?error=auth_failed")


@router.post("/microsoft/token")
async def microsoft_token_exchange(code: str, request: Request):
    """
    Exchange Microsoft authorization code for JWT token (alternative to callback).
    
    This endpoint can be used for SPA applications that handle the OAuth
    callback in JavaScript and want to exchange the code for a token via API.
    """
    logger.info("Exchanging Microsoft authorization code for JWT token")
    
    try:
        microsoft_handler = get_microsoft_oauth_handler()
        
        if not microsoft_handler.is_configured():
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Microsoft OAuth is not configured"
            )
        
        # Exchange code for token
        token_data = await microsoft_handler.exchange_code_for_token(code)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token received from Microsoft"
            )
        
        # Get user information
        user_info = await microsoft_handler.get_user_info(access_token)
        
        # Create JWT token for our application
        jwt_token = microsoft_handler.create_jwt_token(user_info)
        
        # Log to BigQuery
        try:
            bq_client = get_bigquery_client()
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
            
            user_id = await bq_client.upsert_identity_user(
                auth_uid=user_info.id,
                auth_provider="microsoft",
                email=user_info.email,
                role="customer",
                display_name=user_info.displayName,
                is_verified=True
            )
            
            await bq_client.log_login_event(
                user_id=user_id or user_info.id,
                auth_provider="microsoft",
                event_type="login",
                success=True,
                ip_address=ip_address,
                user_agent=user_agent
            )
        except Exception as bq_error:
            logger.warning(f"Failed to log to BigQuery: {bq_error}")
        
        return TokenResponse(
            access_token=jwt_token,
            user={
                "email": user_info.email,
                "name": user_info.displayName,
                "given_name": user_info.givenName,
                "family_name": user_info.surname,
                "email_verified": True,
                "auth_provider": "microsoft"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exchanging Microsoft token: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to authenticate: {str(e)}"
        )
