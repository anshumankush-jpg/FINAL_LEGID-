"""
Persistent file-based storage for conversations and messages.
This ensures history is preserved across server restarts.
"""
import json
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from threading import Lock

logger = logging.getLogger(__name__)


class PersistentStorage:
    """
    File-based persistent storage for conversations and messages.
    Automatically saves to disk and loads on startup.
    """
    
    def __init__(self, storage_dir: str = None):
        if storage_dir is None:
            # Default to backend/data/history
            storage_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'data', 'history'
            )
        
        self.storage_dir = Path(storage_dir)
        self.conversations_file = self.storage_dir / 'conversations.json'
        self.messages_file = self.storage_dir / 'messages.json'
        
        # In-memory cache
        self._conversations: Dict[str, Dict] = {}
        self._messages: Dict[str, Dict] = {}
        
        # Thread safety
        self._lock = Lock()
        
        # Initialize storage
        self._ensure_storage_dir()
        self._load_from_disk()
    
    def _ensure_storage_dir(self):
        """Create storage directory if it doesn't exist."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Storage directory: {self.storage_dir}")
    
    def _load_from_disk(self):
        """Load conversations and messages from disk."""
        try:
            if self.conversations_file.exists():
                with open(self.conversations_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert date strings back to datetime
                    for conv in data.values():
                        if 'created_at' in conv and isinstance(conv['created_at'], str):
                            conv['created_at'] = datetime.fromisoformat(conv['created_at'])
                        if 'updated_at' in conv and isinstance(conv['updated_at'], str):
                            conv['updated_at'] = datetime.fromisoformat(conv['updated_at'])
                    self._conversations = data
                    logger.info(f"Loaded {len(self._conversations)} conversations from disk")
            
            if self.messages_file.exists():
                with open(self.messages_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert date strings back to datetime
                    for msg in data.values():
                        if 'created_at' in msg and isinstance(msg['created_at'], str):
                            msg['created_at'] = datetime.fromisoformat(msg['created_at'])
                    self._messages = data
                    logger.info(f"Loaded {len(self._messages)} messages from disk")
        except Exception as e:
            logger.error(f"Failed to load from disk: {e}")
    
    def _save_conversations(self):
        """Save conversations to disk."""
        try:
            with self._lock:
                # Convert datetime to ISO format strings for JSON
                data = {}
                for k, v in self._conversations.items():
                    conv = v.copy()
                    if 'created_at' in conv and isinstance(conv['created_at'], datetime):
                        conv['created_at'] = conv['created_at'].isoformat()
                    if 'updated_at' in conv and isinstance(conv['updated_at'], datetime):
                        conv['updated_at'] = conv['updated_at'].isoformat()
                    data[k] = conv
                
                with open(self.conversations_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save conversations: {e}")
    
    def _save_messages(self):
        """Save messages to disk."""
        try:
            with self._lock:
                # Convert datetime to ISO format strings for JSON
                data = {}
                for k, v in self._messages.items():
                    msg = v.copy()
                    if 'created_at' in msg and isinstance(msg['created_at'], datetime):
                        msg['created_at'] = msg['created_at'].isoformat()
                    data[k] = msg
                
                with open(self.messages_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save messages: {e}")
    
    # ===== CONVERSATION METHODS =====
    
    def get_conversations(self) -> Dict[str, Dict]:
        """Get all conversations."""
        return self._conversations
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Get a specific conversation."""
        return self._conversations.get(conversation_id)
    
    def get_user_conversations(self, user_id: str) -> List[Dict]:
        """Get all conversations for a user."""
        return [
            conv for conv in self._conversations.values()
            if conv.get('user_id') == user_id
        ]
    
    def save_conversation(self, conversation: Dict) -> Dict:
        """Save or update a conversation."""
        conversation_id = conversation['conversation_id']
        self._conversations[conversation_id] = conversation
        self._save_conversations()
        return conversation
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation and its messages."""
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            self._save_conversations()
            
            # Also delete associated messages
            messages_to_delete = [
                msg_id for msg_id, msg in self._messages.items()
                if msg.get('conversation_id') == conversation_id
            ]
            for msg_id in messages_to_delete:
                del self._messages[msg_id]
            if messages_to_delete:
                self._save_messages()
            
            return True
        return False
    
    def search_conversations(self, user_id: str, query: str) -> List[Dict]:
        """Search conversations by title or preview."""
        query_lower = query.lower()
        user_conversations = self.get_user_conversations(user_id)
        return [
            conv for conv in user_conversations
            if query_lower in conv.get('title', '').lower() or
               query_lower in conv.get('preview', '').lower()
        ]
    
    # ===== MESSAGE METHODS =====
    
    def get_messages(self) -> Dict[str, Dict]:
        """Get all messages."""
        return self._messages
    
    def get_message(self, message_id: str) -> Optional[Dict]:
        """Get a specific message."""
        return self._messages.get(message_id)
    
    def get_conversation_messages(self, conversation_id: str, user_id: str) -> List[Dict]:
        """Get all messages for a conversation."""
        return [
            msg for msg in self._messages.values()
            if msg.get('conversation_id') == conversation_id and msg.get('user_id') == user_id
        ]
    
    def save_message(self, message: Dict) -> Dict:
        """Save a message."""
        message_id = message['message_id']
        self._messages[message_id] = message
        self._save_messages()
        
        # Update conversation's preview and message count
        conv_id = message.get('conversation_id')
        if conv_id and conv_id in self._conversations:
            conv = self._conversations[conv_id]
            conv['message_count'] = conv.get('message_count', 0) + 1
            if message.get('role') == 'user':
                conv['preview'] = message.get('content', '')[:100]
            conv['updated_at'] = datetime.now()
            
            # Auto-update title based on first user message
            if conv.get('message_count', 0) == 1 and message.get('role') == 'user':
                content = message.get('content', '')
                conv['title'] = content[:50] + ('...' if len(content) > 50 else '')
            
            self._save_conversations()
        
        return message
    
    def delete_message(self, message_id: str) -> bool:
        """Delete a message."""
        if message_id in self._messages:
            del self._messages[message_id]
            self._save_messages()
            return True
        return False


# Singleton instance
_persistent_storage: Optional[PersistentStorage] = None


def get_persistent_storage() -> PersistentStorage:
    """Get the singleton PersistentStorage instance."""
    global _persistent_storage
    if _persistent_storage is None:
        _persistent_storage = PersistentStorage()
    return _persistent_storage
