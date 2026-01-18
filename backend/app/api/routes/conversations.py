"""
Conversation management endpoints for LEGID
Handles CRUD operations for user conversations with persistent file storage
"""
import logging
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.api.routes.auth_v2 import get_current_user
from app.services.persistent_storage import get_persistent_storage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversations", tags=["conversations"])

# Request/Response Models
class ConversationCreate(BaseModel):
    title: str = "New Chat"

class ConversationUpdate(BaseModel):
    title: Optional[str] = None

class ConversationResponse(BaseModel):
    conversation_id: str
    user_id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int = 0
    preview: Optional[str] = None

# Use persistent storage instead of in-memory dict
def get_storage():
    return get_persistent_storage()

@router.post("", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new conversation"""
    try:
        user_id = current_user['user_id']
        storage = get_storage()
        
        conversation = {
            "conversation_id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": request.title,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "message_count": 0,
            "preview": None
        }

        # Store in persistent storage
        storage.save_conversation(conversation)
        logger.info(f"Created conversation {conversation['conversation_id']} for user {user_id}")

        return ConversationResponse(
            conversation_id=conversation['conversation_id'],
            user_id=conversation['user_id'],
            title=conversation['title'],
            created_at=conversation['created_at'].isoformat() if isinstance(conversation['created_at'], datetime) else conversation['created_at'],
            updated_at=conversation['updated_at'].isoformat() if isinstance(conversation['updated_at'], datetime) else conversation['updated_at'],
            message_count=conversation['message_count'],
            preview=conversation['preview']
        )

    except Exception as e:
        logger.error(f"Failed to create conversation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create conversation")

@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: dict = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """List user's conversations"""
    try:
        user_id = current_user['user_id']
        storage = get_storage()
        
        # Get conversations for this user from persistent storage
        user_conversations = storage.get_user_conversations(user_id)
        
        logger.info(f"Found {len(user_conversations)} conversations for user {user_id}")

        # Sort by updated_at desc
        user_conversations.sort(
            key=lambda x: x['updated_at'] if isinstance(x['updated_at'], datetime) else datetime.fromisoformat(x['updated_at']), 
            reverse=True
        )

        # Apply pagination
        paginated = user_conversations[offset:offset + limit]

        return [
            ConversationResponse(
                conversation_id=conv['conversation_id'],
                user_id=conv['user_id'],
                title=conv['title'],
                created_at=conv['created_at'].isoformat() if isinstance(conv['created_at'], datetime) else conv['created_at'],
                updated_at=conv['updated_at'].isoformat() if isinstance(conv['updated_at'], datetime) else conv['updated_at'],
                message_count=conv.get('message_count', 0),
                preview=conv.get('preview')
            )
            for conv in paginated
        ]

    except Exception as e:
        logger.error(f"Failed to list conversations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list conversations")

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific conversation"""
    try:
        storage = get_storage()
        conv = storage.get_conversation(conversation_id)
        
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Verify ownership
        if conv['user_id'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Access denied")

        return ConversationResponse(
            conversation_id=conv['conversation_id'],
            user_id=conv['user_id'],
            title=conv['title'],
            created_at=conv['created_at'].isoformat() if isinstance(conv['created_at'], datetime) else conv['created_at'],
            updated_at=conv['updated_at'].isoformat() if isinstance(conv['updated_at'], datetime) else conv['updated_at'],
            message_count=conv.get('message_count', 0),
            preview=conv.get('preview')
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get conversation")

@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    request: ConversationUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update conversation (e.g., rename)"""
    try:
        storage = get_storage()
        conv = storage.get_conversation(conversation_id)
        
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Verify ownership
        if conv['user_id'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Access denied")

        # Update fields
        if request.title is not None:
            conv['title'] = request.title
        
        conv['updated_at'] = datetime.now()
        
        # Save changes
        storage.save_conversation(conv)

        return ConversationResponse(
            conversation_id=conv['conversation_id'],
            user_id=conv['user_id'],
            title=conv['title'],
            created_at=conv['created_at'].isoformat() if isinstance(conv['created_at'], datetime) else conv['created_at'],
            updated_at=conv['updated_at'].isoformat() if isinstance(conv['updated_at'], datetime) else conv['updated_at'],
            message_count=conv.get('message_count', 0),
            preview=conv.get('preview')
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update conversation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update conversation")

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a conversation"""
    try:
        storage = get_storage()
        conv = storage.get_conversation(conversation_id)
        
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Verify ownership
        if conv['user_id'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Access denied")

        # Delete conversation (also deletes associated messages)
        storage.delete_conversation(conversation_id)
        logger.info(f"Deleted conversation {conversation_id}")

        return {"success": True, "message": "Conversation deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete conversation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete conversation")

@router.get("/search", response_model=List[ConversationResponse])
async def search_conversations(
    query: str,
    current_user: dict = Depends(get_current_user),
    limit: int = 20
):
    """Search conversations by title or content"""
    try:
        user_id = current_user['user_id']
        storage = get_storage()
        
        # Search conversations
        results = storage.search_conversations(user_id, query)

        # Sort by relevance (for now, just by updated_at)
        results.sort(
            key=lambda x: x['updated_at'] if isinstance(x['updated_at'], datetime) else datetime.fromisoformat(x['updated_at']),
            reverse=True
        )

        # Limit results
        results = results[:limit]

        return [
            ConversationResponse(
                conversation_id=conv['conversation_id'],
                user_id=conv['user_id'],
                title=conv['title'],
                created_at=conv['created_at'].isoformat() if isinstance(conv['created_at'], datetime) else conv['created_at'],
                updated_at=conv['updated_at'].isoformat() if isinstance(conv['updated_at'], datetime) else conv['updated_at'],
                message_count=conv.get('message_count', 0),
                preview=conv.get('preview')
            )
            for conv in results
        ]

    except Exception as e:
        logger.error(f"Failed to search conversations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Search failed")
