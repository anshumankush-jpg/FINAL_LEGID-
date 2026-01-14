"""
Profile Service - Manages user profiles, preferences, and settings.
"""
import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.models.db_models import (
    User, UserProfile, UserConsent, Conversation, ChatMessage,
    AccessRequest, AccountSession
)

logger = logging.getLogger(__name__)


class ProfileService:
    """Service for managing user profiles and preferences."""
    
    @staticmethod
    def get_or_create_profile(db: Session, user_id: str) -> UserProfile:
        """
        Get user profile, creating it if it doesn't exist.
        """
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        if not profile:
            # Create default profile
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User not found: {user_id}")
            
            profile = UserProfile(
                user_id=user_id,
                display_name=user.name,
                preferences_json={
                    "theme": "dark",
                    "font_size": "medium",
                    "response_style": "detailed",
                    "auto_read": False,
                    "language": "en"
                }
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
            logger.info(f"Created profile for user: {user_id}")
        
        return profile
    
    @staticmethod
    def update_profile(
        db: Session,
        user_id: str,
        update_data: Dict[str, Any]
    ) -> UserProfile:
        """
        Update user profile.
        """
        profile = ProfileService.get_or_create_profile(db, user_id)
        
        # Allowed fields to update
        allowed_fields = [
            'display_name', 'username', 'avatar_url', 'phone',
            'address_line_1', 'address_line_2', 'city',
            'province_state', 'postal_zip', 'country'
        ]
        
        for field in allowed_fields:
            if field in update_data:
                setattr(profile, field, update_data[field])
        
        profile.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(profile)
        
        logger.info(f"Updated profile for user: {user_id}")
        return profile
    
    @staticmethod
    def update_preferences(
        db: Session,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> UserProfile:
        """
        Update user preferences.
        """
        profile = ProfileService.get_or_create_profile(db, user_id)
        
        # Merge with existing preferences
        current_prefs = profile.preferences_json or {}
        current_prefs.update(preferences)
        profile.preferences_json = current_prefs
        profile.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(profile)
        
        logger.info(f"Updated preferences for user: {user_id}")
        return profile
    
    @staticmethod
    def check_username_available(db: Session, username: str, exclude_user_id: str = None) -> bool:
        """
        Check if username is available.
        """
        query = db.query(UserProfile).filter(UserProfile.username == username)
        if exclude_user_id:
            query = query.filter(UserProfile.user_id != exclude_user_id)
        return query.first() is None
    
    @staticmethod
    def get_full_user_data(db: Session, user_id: str) -> Dict[str, Any]:
        """
        Get complete user data including profile and consent.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        profile = ProfileService.get_or_create_profile(db, user_id)
        consent = ConsentService.get_or_create_consent(db, user_id)
        
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role.value if user.role else "client",
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
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
                },
                "preferences": profile.preferences_json,
                "lawyer_status": profile.lawyer_status
            },
            "consent": {
                "necessary": consent.necessary,
                "analytics": consent.analytics,
                "marketing": consent.marketing,
                "functional": consent.functional,
                "updated_at": consent.updated_at.isoformat() if consent.updated_at else None
            }
        }


class ConsentService:
    """Service for managing user consent preferences."""
    
    @staticmethod
    def get_or_create_consent(db: Session, user_id: str) -> UserConsent:
        """
        Get user consent, creating default if doesn't exist.
        """
        consent = db.query(UserConsent).filter(UserConsent.user_id == user_id).first()
        
        if not consent:
            consent = UserConsent(
                user_id=user_id,
                necessary=True,
                analytics=False,
                marketing=False,
                functional=True
            )
            db.add(consent)
            db.commit()
            db.refresh(consent)
            logger.info(f"Created consent record for user: {user_id}")
        
        return consent
    
    @staticmethod
    def update_consent(
        db: Session,
        user_id: str,
        consent_data: Dict[str, bool],
        ip_address: str = None,
        user_agent: str = None
    ) -> UserConsent:
        """
        Update user consent preferences.
        """
        consent = ConsentService.get_or_create_consent(db, user_id)
        
        # Update consent values
        if 'analytics' in consent_data:
            consent.analytics = consent_data['analytics']
        if 'marketing' in consent_data:
            consent.marketing = consent_data['marketing']
        if 'functional' in consent_data:
            consent.functional = consent_data['functional']
        
        # necessary is always true
        consent.necessary = True
        
        consent.updated_at = datetime.utcnow()
        consent.consent_ip = ip_address
        consent.consent_user_agent = user_agent
        
        db.commit()
        db.refresh(consent)
        
        logger.info(f"Updated consent for user: {user_id}")
        return consent


class ConversationService:
    """Service for managing user conversations."""
    
    @staticmethod
    def create_conversation(
        db: Session,
        user_id: str,
        title: str = None,
        law_type: str = None,
        jurisdiction_country: str = None,
        jurisdiction_region: str = None
    ) -> Conversation:
        """
        Create a new conversation.
        """
        conversation = Conversation(
            user_id=user_id,
            title=title or "New Chat",
            law_type=law_type,
            jurisdiction_country=jurisdiction_country,
            jurisdiction_region=jurisdiction_region
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        logger.info(f"Created conversation {conversation.id} for user: {user_id}")
        return conversation
    
    @staticmethod
    def get_user_conversations(
        db: Session,
        user_id: str,
        include_archived: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Conversation]:
        """
        Get user's conversations.
        """
        query = db.query(Conversation).filter(Conversation.user_id == user_id)
        
        if not include_archived:
            query = query.filter(Conversation.is_archived == False)
        
        return query.order_by(Conversation.updated_at.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def add_message(
        db: Session,
        conversation_id: str,
        role: str,
        content: str,
        attachments: List[Dict] = None
    ) -> ChatMessage:
        """
        Add a message to conversation.
        """
        message = ChatMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            has_attachments=bool(attachments),
            attachments_json=attachments or []
        )
        db.add(message)
        
        # Update conversation
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            conversation.last_message_at = datetime.utcnow()
            conversation.updated_at = datetime.utcnow()
            
            # Auto-title from first user message
            if not conversation.title or conversation.title == "New Chat":
                if role == "user":
                    conversation.title = content[:50] + ("..." if len(content) > 50 else "")
        
        db.commit()
        db.refresh(message)
        
        return message
    
    @staticmethod
    def get_conversation_messages(
        db: Session,
        conversation_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[ChatMessage]:
        """
        Get messages in a conversation.
        """
        return db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.created_at.asc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def archive_conversation(db: Session, conversation_id: str, user_id: str) -> bool:
        """
        Archive a conversation.
        """
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()
        
        if conversation:
            conversation.is_archived = True
            db.commit()
            return True
        return False
    
    @staticmethod
    def delete_conversation(db: Session, conversation_id: str, user_id: str) -> bool:
        """
        Delete a conversation.
        """
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()
        
        if conversation:
            db.delete(conversation)
            db.commit()
            return True
        return False


class AccessRequestService:
    """Service for managing access requests."""
    
    @staticmethod
    def create_request(
        db: Session,
        email: str,
        name: str = None,
        requested_role: str = "client",
        reason: str = None,
        organization: str = None
    ) -> AccessRequest:
        """
        Create an access request.
        """
        # Check if pending request exists
        existing = db.query(AccessRequest).filter(
            AccessRequest.email == email,
            AccessRequest.status == "pending"
        ).first()
        
        if existing:
            logger.info(f"Access request already pending for: {email}")
            return existing
        
        request = AccessRequest(
            email=email,
            name=name,
            requested_role=requested_role,
            reason=reason,
            organization=organization
        )
        db.add(request)
        db.commit()
        db.refresh(request)
        
        logger.info(f"Created access request for: {email}")
        return request
    
    @staticmethod
    def get_pending_requests(db: Session, limit: int = 50) -> List[AccessRequest]:
        """
        Get pending access requests for admin review.
        """
        return db.query(AccessRequest).filter(
            AccessRequest.status == "pending"
        ).order_by(AccessRequest.created_at.asc()).limit(limit).all()
    
    @staticmethod
    def approve_request(
        db: Session,
        request_id: str,
        reviewer_id: str,
        notes: str = None
    ) -> Optional[User]:
        """
        Approve an access request and create user.
        """
        request = db.query(AccessRequest).filter(AccessRequest.id == request_id).first()
        if not request or request.status != "pending":
            return None
        
        # Create user
        from app.models.db_models import UserRole
        user = User(
            email=request.email,
            name=request.name,
            role=UserRole(request.requested_role) if request.requested_role in ['client', 'lawyer'] else UserRole.CLIENT,
            is_active=True
        )
        db.add(user)
        
        # Update request
        request.status = "approved"
        request.reviewed_by_user_id = reviewer_id
        request.reviewed_at = datetime.utcnow()
        request.reviewer_notes = notes
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"Approved access request for: {request.email}")
        return user
    
    @staticmethod
    def reject_request(
        db: Session,
        request_id: str,
        reviewer_id: str,
        notes: str = None
    ) -> bool:
        """
        Reject an access request.
        """
        request = db.query(AccessRequest).filter(AccessRequest.id == request_id).first()
        if not request or request.status != "pending":
            return False
        
        request.status = "rejected"
        request.reviewed_by_user_id = reviewer_id
        request.reviewed_at = datetime.utcnow()
        request.reviewer_notes = notes
        
        db.commit()
        
        logger.info(f"Rejected access request for: {request.email}")
        return True


class AccountSessionService:
    """Service for managing multi-account sessions."""
    
    @staticmethod
    def add_account_to_device(
        db: Session,
        device_id: str,
        user_id: str,
        device_name: str = None
    ) -> AccountSession:
        """
        Add an account to a device for multi-account support.
        """
        # Check if this account already exists on device
        existing = db.query(AccountSession).filter(
            AccountSession.device_id == device_id,
            AccountSession.user_id == user_id
        ).first()
        
        if existing:
            existing.is_active = True
            existing.last_used_at = datetime.utcnow()
            db.commit()
            return existing
        
        session = AccountSession(
            device_id=device_id,
            user_id=user_id,
            device_name=device_name,
            is_active=True
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        logger.info(f"Added account {user_id} to device {device_id[:8]}...")
        return session
    
    @staticmethod
    def get_device_accounts(db: Session, device_id: str) -> List[Dict[str, Any]]:
        """
        Get all accounts on a device.
        """
        sessions = db.query(AccountSession).filter(
            AccountSession.device_id == device_id,
            AccountSession.is_active == True
        ).order_by(AccountSession.last_used_at.desc()).all()
        
        accounts = []
        for session in sessions:
            user = db.query(User).filter(User.id == session.user_id).first()
            if user:
                profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
                accounts.append({
                    "session_id": session.id,
                    "user_id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "role": user.role.value if user.role else "client",
                    "avatar_url": profile.avatar_url if profile else None,
                    "display_name": profile.display_name if profile else user.name,
                    "last_used_at": session.last_used_at.isoformat() if session.last_used_at else None
                })
        
        return accounts
    
    @staticmethod
    def remove_account_from_device(
        db: Session,
        device_id: str,
        user_id: str
    ) -> bool:
        """
        Remove an account from a device.
        """
        session = db.query(AccountSession).filter(
            AccountSession.device_id == device_id,
            AccountSession.user_id == user_id
        ).first()
        
        if session:
            session.is_active = False
            db.commit()
            logger.info(f"Removed account {user_id} from device {device_id[:8]}...")
            return True
        return False
    
    @staticmethod
    def switch_account(
        db: Session,
        device_id: str,
        user_id: str
    ) -> Optional[AccountSession]:
        """
        Switch to a different account on the device.
        """
        session = db.query(AccountSession).filter(
            AccountSession.device_id == device_id,
            AccountSession.user_id == user_id,
            AccountSession.is_active == True
        ).first()
        
        if session:
            session.last_used_at = datetime.utcnow()
            db.commit()
            return session
        return None
