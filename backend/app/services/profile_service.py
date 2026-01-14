"""Profile management service."""

import logging
import json
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.db_models import User, UserProfile, UserConsent
from app.services.gcs_service import get_gcs_service, GcsService
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class ProfileService:
    """Service for managing user profiles and consent."""

    def __init__(self, gcs_service: GcsService = None):
        self.gcs_service = gcs_service or get_gcs_service()

    def get_user_profile(self, db: Session, user_id: str) -> Optional[UserProfile]:
        """Fetch a user's profile."""
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not user_profile:
            # If profile doesn't exist, create a basic one
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user_profile = UserProfile(
                    user_id=user_id,
                    display_name=user.name,
                    email=user.email  # Add email field to UserProfile if needed
                )
                db.add(user_profile)
                db.commit()
                db.refresh(user_profile)
                logger.info(f"Created new profile for user {user_id}")
        return user_profile

    def update_user_profile(self, db: Session, user_id: str, profile_data: Dict[str, Any]) -> UserProfile:
        """Update a user's profile."""
        user_profile = self.get_user_profile(db, user_id)
        if not user_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found")

        # Validate username uniqueness if provided
        if 'username' in profile_data and profile_data['username']:
            existing = db.query(UserProfile).filter(
                UserProfile.username == profile_data['username'],
                UserProfile.user_id != user_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )

        # Update fields
        for key, value in profile_data.items():
            if hasattr(user_profile, key):
                setattr(user_profile, key, value)

        # Update user's name if display_name is provided
        if 'display_name' in profile_data:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.name = profile_data['display_name']
                db.add(user)

        db.add(user_profile)
        db.commit()
        db.refresh(user_profile)
        logger.info(f"Updated profile for user {user_id}")
        return user_profile

    def get_avatar_upload_signed_url(self, user_id: str, filename: str, content_type: str) -> Dict[str, str]:
        """Generate a signed URL for avatar upload to GCS."""
        if not self.gcs_service:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="GCS service not configured")

        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
            )

        # Validate file size (from Content-Length header if provided, but we'll check on upload)
        # For now, just validate filename
        if not filename or len(filename) > 255:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename")

        # Define a path for avatars, e.g., avatars/{user_id}/{filename}
        blob_name = f"avatars/{user_id}/{filename}"
        signed_url = self.gcs_service.generate_upload_signed_url(blob_name, content_type)

        return {
            "signed_url": signed_url,
            "file_path": blob_name,
            "public_url": self.gcs_service.get_public_url(blob_name)
        }

    def update_avatar_url(self, db: Session, user_id: str, avatar_url: str) -> UserProfile:
        """Update the user's avatar URL in their profile."""
        user_profile = self.get_user_profile(db, user_id)
        if not user_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found")

        user_profile.avatar_url = avatar_url
        db.add(user_profile)
        db.commit()
        db.refresh(user_profile)
        logger.info(f"Updated avatar URL for user {user_id}")
        return user_profile

    def get_user_consent(self, db: Session, user_id: str) -> Optional[UserConsent]:
        """Fetch a user's consent settings."""
        user_consent = db.query(UserConsent).filter(UserConsent.user_id == user_id).first()
        if not user_consent:
            # Create default consent if none exists
            user_consent = UserConsent(user_id=user_id)
            db.add(user_consent)
            db.commit()
            db.refresh(user_consent)
            logger.info(f"Created default consent for user {user_id}")
        return user_consent

    def update_user_consent(self, db: Session, user_id: str, consent_data: Dict[str, bool]) -> UserConsent:
        """Update a user's consent settings."""
        user_consent = self.get_user_consent(db, user_id)
        if not user_consent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User consent not found")

        for key, value in consent_data.items():
            if hasattr(user_consent, key):
                setattr(user_consent, key, value)

        db.add(user_consent)
        db.commit()
        db.refresh(user_consent)
        logger.info(f"Updated consent for user {user_id}")
        return user_consent

# Global service instance
_profile_service = None

def get_profile_service() -> ProfileService:
    """Get the global profile service instance."""
    global _profile_service
    if _profile_service is None:
        _profile_service = ProfileService()
    return _profile_service