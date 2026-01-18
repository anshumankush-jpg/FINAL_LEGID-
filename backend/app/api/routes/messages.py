"""
Messages management endpoints for LEGID
Handles message CRUD and chat streaming with persistent file storage
"""
import logging
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from app.api.routes.auth_v2 import get_current_user
from app.services.persistent_storage import get_persistent_storage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/messages", tags=["messages"])

# Request/Response Models
class MessageCreate(BaseModel):
    conversation_id: str
    role: str  # 'user' | 'assistant' | 'system'
    content: str
    attachments: Optional[List[dict]] = None
    metadata: Optional[dict] = None

class MessageResponse(BaseModel):
    message_id: str
    conversation_id: str
    user_id: str
    role: str
    content: str
    attachments: Optional[List[dict]] = None
    metadata: Optional[dict] = None
    created_at: str

# Use persistent storage
def get_storage():
    return get_persistent_storage()

@router.get("", response_model=List[MessageResponse])
async def list_messages(
    conversationId: str = Query(...),
    current_user: dict = Depends(get_current_user),
    limit: int = 100
):
    """Get messages for a conversation"""
    try:
        user_id = current_user['user_id']
        storage = get_storage()
        
        # Get messages for this conversation from persistent storage
        messages = storage.get_conversation_messages(conversationId, user_id)
        
        logger.info(f"Found {len(messages)} messages for conversation {conversationId}")

        # Sort by created_at asc
        messages.sort(key=lambda x: x['created_at'] if isinstance(x['created_at'], datetime) else datetime.fromisoformat(x['created_at']))

        # Limit
        messages = messages[:limit]

        return [
            MessageResponse(
                message_id=msg['message_id'],
                conversation_id=msg['conversation_id'],
                user_id=msg['user_id'],
                role=msg['role'],
                content=msg['content'],
                attachments=msg.get('attachments'),
                metadata=msg.get('metadata'),
                created_at=msg['created_at'].isoformat() if isinstance(msg['created_at'], datetime) else msg['created_at']
            )
            for msg in messages
        ]

    except Exception as e:
        logger.error(f"Failed to list messages: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list messages")

@router.post("", response_model=MessageResponse)
async def create_message(
    request: MessageCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new message"""
    try:
        user_id = current_user['user_id']
        storage = get_storage()
        
        message = {
            "message_id": str(uuid.uuid4()),
            "conversation_id": request.conversation_id,
            "user_id": user_id,
            "role": request.role,
            "content": request.content,
            "attachments": request.attachments,
            "metadata": request.metadata,
            "created_at": datetime.now()
        }

        # Store in persistent storage (also updates conversation preview)
        storage.save_message(message)
        logger.info(f"Created message {message['message_id']} in conversation {request.conversation_id}")

        return MessageResponse(
            message_id=message['message_id'],
            conversation_id=message['conversation_id'],
            user_id=message['user_id'],
            role=message['role'],
            content=message['content'],
            attachments=message.get('attachments'),
            metadata=message.get('metadata'),
            created_at=message['created_at'].isoformat() if isinstance(message['created_at'], datetime) else message['created_at']
        )

    except Exception as e:
        logger.error(f"Failed to create message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create message")

@router.delete("/{message_id}")
async def delete_message(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a message"""
    try:
        storage = get_storage()
        msg = storage.get_message(message_id)
        
        if not msg:
            raise HTTPException(status_code=404, detail="Message not found")

        # Verify ownership
        if msg['user_id'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Access denied")

        # Delete message
        storage.delete_message(message_id)
        logger.info(f"Deleted message {message_id}")

        return {"success": True, "message": "Message deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete message")
