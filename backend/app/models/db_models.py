"""Database models for the LegalAI application."""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
import datetime
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    CLIENT = "client"
    LAWYER = "lawyer"
    EMPLOYEE = "employee"
    EMPLOYEE_ADMIN = "employee_admin"

class LawyerStatus(str, enum.Enum):
    NOT_APPLICABLE = "not_applicable"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class OAuthProvider(str, enum.Enum):
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    EMAIL = "email"

class Environment(str, enum.Enum):
    DEV = "dev"
    PROD = "prod"

class User(Base):
    """User model with role and lawyer status."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CLIENT)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_provisioned = Column(Boolean, default=False, nullable=False)
    lawyer_status = Column(Enum(LawyerStatus), nullable=False, default=LawyerStatus.NOT_APPLICABLE)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    oauth_identities = relationship("OAuthIdentity", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    password_resets = relationship("PasswordReset", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    employee_assignments = relationship("EmployeeAssignment",
                                       foreign_keys="[EmployeeAssignment.employee_user_id]",
                                       back_populates="employee")
    matters = relationship("MatterDB", back_populates="user")
    email_connections = relationship("EmailConnection", back_populates="user", cascade="all, delete-orphan")
    user_profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    user_consent = relationship("UserConsent", back_populates="user", uselist=False, cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    account_sessions = relationship("AccountSession", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"

class OAuthIdentity(Base):
    """OAuth identity mappings."""
    __tablename__ = "oauth_identities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    provider = Column(Enum(OAuthProvider), nullable=False)
    provider_user_id = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    picture = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="oauth_identities")

    def __repr__(self):
        return f"<OAuthIdentity {self.provider}:{self.provider_user_id}>"

class RefreshToken(Base):
    """Refresh tokens for session management."""
    __tablename__ = "refresh_tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    token_hash = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="refresh_tokens")

class PasswordReset(Base):
    """Password reset tokens."""
    __tablename__ = "password_resets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    token_hash = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="password_resets")

class AuditLog(Base):
    """Audit logs for user actions."""
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    action = Column(String(255), nullable=False)
    details = Column(JSON, default=dict)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="audit_logs")

class UserProfile(Base):
    """Extended user profile for personalization and settings."""
    __tablename__ = "user_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    display_name = Column(String(255), nullable=True)
    username = Column(String(255), unique=True, nullable=True)
    avatar_url = Column(String(1000), nullable=True)
    phone = Column(String(50), nullable=True)
    address_line_1 = Column(String(255), nullable=True)
    address_line_2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    province_state = Column(String(100), nullable=True)
    postal_zip = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    preferences_json = Column(JSON, default=dict)  # theme, font size, response style toggles
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="user_profile")

    def __repr__(self):
        return f"<UserProfile for user {self.user_id}>"

class UserConsent(Base):
    """User consent for cookies and data usage."""
    __tablename__ = "user_consent"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    necessary = Column(Boolean, default=True, nullable=False)
    analytics = Column(Boolean, default=False, nullable=False)
    marketing = Column(Boolean, default=False, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="user_consent")

    def __repr__(self):
        return f"<UserConsent for user {self.user_id}>"

class Conversation(Base):
    """Represents a chat conversation, scoped by user_id."""
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation {self.title} by user {self.user_id}>"

class Message(Base):
    """Chat messages within a conversation."""
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    meta_data = Column(JSON, default=dict)

    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message {self.role} in conversation {self.conversation_id}>"

class Attachment(Base):
    """Files attached to a conversation."""
    __tablename__ = "attachments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    file_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)
    storage_path = Column(String(1000), nullable=False)  # GCS path
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    meta_data = Column(JSON, default=dict)

    conversation = relationship("Conversation", back_populates="attachments")

    def __repr__(self):
        return f"<Attachment {self.filename} in conversation {self.conversation_id}>"

class AccountSession(Base):
    """Active account sessions for multi-account support."""
    __tablename__ = "account_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    device_id = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_used_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    device_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="account_sessions")

    def __repr__(self):
        return f"<AccountSession {self.user_id} on {self.device_id}>"

class AccessRequest(Base):
    """Access requests for non-provisioned users."""
    __tablename__ = "access_requests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    requested_role = Column(Enum(UserRole), nullable=False, default=UserRole.CLIENT)
    reason = Column(Text, nullable=True)
    organization = Column(String(255), nullable=True)
    status = Column(String(50), default="pending", nullable=False)  # pending, approved, rejected
    reviewed_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    reviewed_by_user = relationship("User")

    def __repr__(self):
        return f"<AccessRequest {self.email} - {self.status}>"

# Legacy models for backward compatibility
class MatterDB(Base):
    """Legacy matter model."""
    __tablename__ = "matters"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="matters")

class EmployeeAssignment(Base):
    """Employee assignments."""
    __tablename__ = "employee_assignments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    assigned_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    employee = relationship("User", foreign_keys=[employee_user_id], back_populates="employee_assignments")

class EmailConnection(Base):
    """Email connections for employee users."""
    __tablename__ = "email_connections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    provider = Column(String(50), nullable=False)  # gmail, outlook
    email_address = Column(String(255), nullable=False)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="email_connections")