"""
Authentication Routes V2 - Email/Password Authentication
Simple JWT-based authentication without external dependencies
"""
import secrets
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
import jwt
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth/v2", tags=["authentication-v2"])

# In-memory user store (for demo - in production use a database)
_users_db: Dict[str, dict] = {}

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "legid-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


# Request/Response Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: Optional[str] = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class GoogleLoginRequest(BaseModel):
    credential: str  # Google ID token


def hash_password(password: str) -> str:
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed


def create_access_token(user_data: dict) -> str:
    """Create JWT access token"""
    payload = {
        "sub": user_data.get("email"),
        "name": user_data.get("name"),
        "user_id": user_data.get("id"),
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register a new user with email and password"""
    try:
        email = request.email.lower()
        
        # Check if user already exists
        if email in _users_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user_id = f"user_{secrets.token_urlsafe(8)}"
        user = {
            "id": user_id,
            "email": email,
            "name": request.name or email.split("@")[0],
            "password_hash": hash_password(request.password),
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Store user
        _users_db[email] = user
        
        # Create access token
        access_token = create_access_token(user)
        
        logger.info(f"User registered: {email}")
        
        # Send welcome email via Gmail API
        try:
            from app.services.gmail_email_service import get_gmail_service
            gmail_service = get_gmail_service()
            email_sent = gmail_service.send_welcome_email(
                to_email=email,
                user_name=user.get("name")
            )
            
            if email_sent:
                logger.info(f"[SUCCESS] Welcome email sent to {email} via Gmail API")
            else:
                logger.info(f"[INFO] Welcome email not sent - Gmail API not configured (emails shown in logs)")
        except Exception as e:
            logger.error(f"[ERROR] Welcome email error: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return AuthResponse(
            access_token=access_token,
            user={
                "id": user_id,
                "email": email,
                "name": user["name"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Email/password login"""
    try:
        email = request.email.lower()
        
        # Check if user exists
        user = _users_db.get(email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(request.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create access token
        access_token = create_access_token(user)
        
        logger.info(f"User logged in: {email}")
        
        return AuthResponse(
            access_token=access_token,
            user={
                "id": user["id"],
                "email": email,
                "name": user["name"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me")
async def get_current_user(token: str):
    """Get current user from token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {
            "email": payload.get("sub"),
            "name": payload.get("name"),
            "user_id": payload.get("user_id")
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


@router.post("/logout")
async def logout():
    """Logout endpoint (stateless JWT - just returns success)"""
    return {"message": "Logged out successfully"}


# Password reset tokens (in-memory, for production use Redis or database)
_reset_tokens: Dict[str, dict] = {}


@router.post("/forgot-password")
async def forgot_password(request: dict):
    """Request password reset email"""
    try:
        email = request.get("email", "").lower()
        
        # Check if user exists
        user = _users_db.get(email)
        
        if not user:
            # Don't reveal if email exists or not (security best practice)
            return {"message": "If the email exists, a password reset link has been sent"}
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        
        # Store reset token with expiration (15 minutes)
        _reset_tokens[reset_token] = {
            "email": email,
            "expires_at": datetime.utcnow() + timedelta(minutes=15)
        }
        
        # Generate reset link
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:4200")
        reset_link = f"{frontend_url}/reset-password?token={reset_token}"
        
        logger.info(f"Password reset requested for {email}")
        
        # Send email using Gmail API
        email_sent = False
        try:
            from app.services.gmail_email_service import get_gmail_service
            gmail_service = get_gmail_service()
            email_sent = gmail_service.send_password_reset_email(
                to_email=email,
                reset_link=reset_link,
                user_name=user.get("name")
            )
            
            if email_sent:
                logger.info(f"[SUCCESS] Password reset email sent to {email}")
            else:
                logger.warning(f"[WARN] Email not sent (Gmail API issue), but reset link is available")
        except Exception as e:
            logger.warning(f"[WARN] Email service error: {e}")
        
        # Log the reset link (always, for testing)
        logger.info("=" * 80)
        logger.info(f"PASSWORD RESET LINK FOR: {email}")
        logger.info(f"Link: {reset_link}")
        logger.info(f"Email Sent: {'Yes' if email_sent else 'No (check logs above)'}")
        logger.info("=" * 80)
        
        # Always return success message (don't reveal if email exists)
        return {
            "message": "If the email exists, a password reset link has been sent" + (" (check your email)" if email_sent else " (check console/logs for link)"),
            "reset_link": reset_link if os.getenv("DEBUG", "true").lower() == "true" else None,
            "email_sent": email_sent
        }
        
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed"
        )


@router.post("/reset-password")
async def reset_password(request: dict):
    """Reset password using token"""
    try:
        token = request.get("token")
        new_password = request.get("new_password")
        
        if not token or not new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token and new password are required"
            )
        
        # Validate token
        reset_data = _reset_tokens.get(token)
        
        if not reset_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Check if token expired
        if datetime.utcnow() > reset_data["expires_at"]:
            del _reset_tokens[token]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )
        
        # Get user
        email = reset_data["email"]
        user = _users_db.get(email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password
        user["password_hash"] = hash_password(new_password)
        
        # Delete used token
        del _reset_tokens[token]
        
        logger.info(f"Password reset successful for {email}")
        
        return {"message": "Password reset successful"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )