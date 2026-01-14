"""Authentication dependencies for API routes."""

from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.db_models import User
from app.services.auth_service import get_current_user as auth_get_current_user

# OAuth2 Bearer token security
security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    access_token: Optional[str] = Cookie(None, alias="access_token"),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.

    Supports both Authorization header and access_token cookie.
    """
    token = None

    if credentials:
        token = credentials.credentials
    elif access_token:
        token = access_token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = await auth_get_current_user(token, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

async def get_current_provisioned_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current user and ensure they are provisioned.
    """
    if not current_user.is_provisioned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not provisioned"
        )
    return current_user

def require_role(required_role: str):
    """
    Create a dependency that requires a specific role.

    Usage: user: User = Depends(require_role("lawyer"))
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.value != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}"
            )
        return current_user
    return role_checker

def require_lawyer_status(required_status: str):
    """
    Create a dependency that requires a specific lawyer status.

    Usage: user: User = Depends(require_lawyer_status("approved"))
    """
    async def status_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.lawyer_status.value != required_status:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Lawyer status requirement not met. Required: {required_status}"
            )
        return current_user
    return status_checker