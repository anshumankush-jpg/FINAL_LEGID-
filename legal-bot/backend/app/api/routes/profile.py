"""
Profile API Routes - User profile, preferences, and consent management.
"""
import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.profile_service import (
    ProfileService, ConsentService, ConversationService,
    AccessRequestService, AccountSessionService
)
from app.services.auth_service import get_current_user
from app.models.db_models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/profile", tags=["profile"])


# ============================================
# Pydantic Models
# ============================================

class ProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = None
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    province_state: Optional[str] = None
    postal_zip: Optional[str] = None
    country: Optional[str] = None


class PreferencesUpdateRequest(BaseModel):
    theme: Optional[str] = None  # dark, light, system
    font_size: Optional[str] = None  # small, medium, large
    response_style: Optional[str] = None  # concise, detailed, legal
    auto_read: Optional[bool] = None
    language: Optional[str] = None


class ConsentUpdateRequest(BaseModel):
    analytics: Optional[bool] = None
    marketing: Optional[bool] = None
    functional: Optional[bool] = None


class AccessRequestCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    requested_role: Optional[str] = "client"
    reason: Optional[str] = None
    organization: Optional[str] = None


class ConversationCreate(BaseModel):
    title: Optional[str] = None
    law_type: Optional[str] = None
    jurisdiction_country: Optional[str] = None
    jurisdiction_region: Optional[str] = None


class MessageCreate(BaseModel):
    role: str
    content: str
    attachments: Optional[List[Dict]] = None


# ============================================
# Profile Routes
# ============================================

@router.get("")
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's full profile."""
    try:
        user_data = ProfileService.get_full_user_data(db, current_user.id)
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        return user_data
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to get profile")


@router.put("")
async def update_profile(
    update_data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile."""
    try:
        # Check username availability if changing
        if update_data.username:
            if not ProfileService.check_username_available(db, update_data.username, current_user.id):
                raise HTTPException(status_code=400, detail="Username already taken")
        
        profile = ProfileService.update_profile(
            db, current_user.id,
            update_data.model_dump(exclude_unset=True)
        )
        
        return {
            "success": True,
            "message": "Profile updated",
            "profile": {
                "display_name": profile.display_name,
                "username": profile.username,
                "avatar_url": profile.avatar_url,
                "phone": profile.phone,
                "address": {
                    "line_1": profile.address_line_1,
                    "line_2": profile.address_line_2,
                    "city": profile.city,
                    "province_state": profile.province_state,
                    "postal_zip": profile.postal_zip,
                    "country": profile.country
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")


@router.put("/preferences")
async def update_preferences(
    prefs: PreferencesUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user preferences."""
    try:
        profile = ProfileService.update_preferences(
            db, current_user.id,
            prefs.model_dump(exclude_unset=True)
        )
        
        return {
            "success": True,
            "preferences": profile.preferences_json
        }
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to update preferences")


@router.get("/check-username/{username}")
async def check_username(
    username: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if username is available."""
    available = ProfileService.check_username_available(db, username, current_user.id)
    return {"available": available, "username": username}


@router.post("/avatar/upload-url")
async def get_avatar_upload_url(
    filename: str,
    content_type: str = "image/jpeg",
    current_user: User = Depends(get_current_user)
):
    """Generate signed URL for avatar upload to GCS."""
    try:
        from app.services.gcs_service import GCSService
        gcs_service = GCSService()

        # Validate content type
        allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
        if content_type not in allowed_types:
            raise HTTPException(status_code=400, detail=f"Content type {content_type} not allowed")

        # Validate filename
        if not filename or len(filename) > 100:
            raise HTTPException(status_code=400, detail="Invalid filename")

        # Generate GCS path
        file_extension = filename.split('.')[-1].lower()
        gcs_path = f"avatars/{current_user.id}/avatar.{file_extension}"

        # Generate signed URL
        signed_url = gcs_service.generate_upload_signed_url(gcs_path, content_type)

        return {
            "signed_url": signed_url,
            "file_path": gcs_path,
            "public_url": f"https://storage.googleapis.com/{gcs_service.bucket_name}/{gcs_path}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating avatar upload URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate upload URL")


# ============================================
# Consent Routes
# ============================================

@router.get("/consent")
async def get_consent(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user consent preferences."""
    consent = ConsentService.get_or_create_consent(db, current_user.id)
    return {
        "necessary": consent.necessary,
        "analytics": consent.analytics,
        "marketing": consent.marketing,
        "functional": consent.functional,
        "updated_at": consent.updated_at.isoformat() if consent.updated_at else None
    }


@router.put("/consent")
async def update_consent(
    consent_data: ConsentUpdateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user consent preferences."""
    try:
        # Get IP and user agent for audit
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        consent = ConsentService.update_consent(
            db, current_user.id,
            consent_data.model_dump(exclude_unset=True),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return {
            "success": True,
            "consent": {
                "necessary": consent.necessary,
                "analytics": consent.analytics,
                "marketing": consent.marketing,
                "functional": consent.functional
            }
        }
    except Exception as e:
        logger.error(f"Error updating consent: {e}")
        raise HTTPException(status_code=500, detail="Failed to update consent")


# ============================================
# Conversation Routes
# ============================================

@router.get("/conversations")
async def get_conversations(
    include_archived: bool = False,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's conversations."""
    conversations = ConversationService.get_user_conversations(
        db, current_user.id,
        include_archived=include_archived,
        limit=limit,
        offset=offset
    )
    
    return {
        "conversations": [
            {
                "id": c.id,
                "title": c.title,
                "law_type": c.law_type,
                "jurisdiction_country": c.jurisdiction_country,
                "jurisdiction_region": c.jurisdiction_region,
                "is_archived": c.is_archived,
                "is_pinned": c.is_pinned,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
                "last_message_at": c.last_message_at.isoformat() if c.last_message_at else None
            }
            for c in conversations
        ]
    }


@router.post("/conversations")
async def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new conversation."""
    try:
        conversation = ConversationService.create_conversation(
            db, current_user.id,
            title=data.title,
            law_type=data.law_type,
            jurisdiction_country=data.jurisdiction_country,
            jurisdiction_region=data.jurisdiction_region
        )
        
        return {
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to create conversation")


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages in a conversation."""
    # Verify conversation belongs to user
    from app.models.db_models import Conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = ConversationService.get_conversation_messages(
        db, conversation_id, limit=limit, offset=offset
    )
    
    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "has_attachments": m.has_attachments,
                "attachments": m.attachments_json,
                "feedback": m.feedback,
                "created_at": m.created_at.isoformat() if m.created_at else None
            }
            for m in messages
        ]
    }


@router.post("/conversations/{conversation_id}/messages")
async def add_message(
    conversation_id: str,
    message: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a message to conversation."""
    # Verify conversation belongs to user
    from app.models.db_models import Conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    try:
        msg = ConversationService.add_message(
            db, conversation_id,
            role=message.role,
            content=message.content,
            attachments=message.attachments
        )
        
        return {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Error adding message: {e}")
        raise HTTPException(status_code=500, detail="Failed to add message")


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation."""
    success = ConversationService.delete_conversation(db, conversation_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"success": True, "message": "Conversation deleted"}


@router.put("/conversations/{conversation_id}/archive")
async def archive_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Archive a conversation."""
    success = ConversationService.archive_conversation(db, conversation_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"success": True, "message": "Conversation archived"}


# ============================================
# Access Request Routes (Public + Admin)
# ============================================

@router.post("/request-access", tags=["public"])
async def request_access(
    data: AccessRequestCreate,
    db: Session = Depends(get_db)
):
    """Request access (for non-provisioned users)."""
    try:
        request = AccessRequestService.create_request(
            db,
            email=data.email,
            name=data.name,
            requested_role=data.requested_role,
            reason=data.reason,
            organization=data.organization
        )
        
        return {
            "success": True,
            "message": "Access request submitted. You will be notified when approved.",
            "request_id": request.id
        }
    except Exception as e:
        logger.error(f"Error creating access request: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit request")


# ============================================
# Account Switching Routes
# ============================================

@router.get("/accounts")
async def get_device_accounts(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all accounts on this device."""
    # Get device ID from cookie or header
    device_id = request.cookies.get("device_id") or request.headers.get("X-Device-ID")
    
    if not device_id:
        # Return just current account
        profile = ProfileService.get_or_create_profile(db, current_user.id)
        return {
            "accounts": [{
                "user_id": current_user.id,
                "email": current_user.email,
                "name": current_user.name,
                "role": current_user.role.value if current_user.role else "client",
                "avatar_url": profile.avatar_url,
                "display_name": profile.display_name
            }],
            "current_user_id": current_user.id
        }
    
    accounts = AccountSessionService.get_device_accounts(db, device_id)
    return {
        "accounts": accounts,
        "current_user_id": current_user.id
    }


@router.post("/accounts/add")
async def add_account_to_device(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add current account to device list."""
    device_id = request.cookies.get("device_id") or request.headers.get("X-Device-ID")
    
    if not device_id:
        raise HTTPException(status_code=400, detail="Device ID required")
    
    user_agent = request.headers.get("user-agent", "")
    device_name = "Web Browser"
    if "Mobile" in user_agent:
        device_name = "Mobile Device"
    elif "Windows" in user_agent:
        device_name = "Windows PC"
    elif "Mac" in user_agent:
        device_name = "Mac"
    
    session = AccountSessionService.add_account_to_device(
        db, device_id, current_user.id, device_name
    )
    
    return {
        "success": True,
        "session_id": session.id
    }


@router.delete("/accounts/{user_id}")
async def remove_account_from_device(
    user_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove an account from device."""
    device_id = request.cookies.get("device_id") or request.headers.get("X-Device-ID")
    
    if not device_id:
        raise HTTPException(status_code=400, detail="Device ID required")
    
    success = AccountSessionService.remove_account_from_device(db, device_id, user_id)
    return {"success": success}


@router.post("/accounts/switch/{user_id}")
async def switch_account(
    user_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Switch to another account on device."""
    device_id = request.cookies.get("device_id") or request.headers.get("X-Device-ID")
    
    if not device_id:
        raise HTTPException(status_code=400, detail="Device ID required")
    
    # Verify the account exists on this device
    session = AccountSessionService.switch_account(db, device_id, user_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Account not found on this device")
    
    # Get user details
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate new token for switched user
    from app.services.auth_service import create_token
    token_data = create_token(user)
    
    return {
        "success": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role.value if user.role else "client"
        },
        "token": token_data
    }
