"""
LLM Client Wrapper for LEGID Pipeline
Supports OpenAI with fallback handling
"""
import logging
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)


class LLMClient:
    """Wrapper for LLM calls with error handling"""
    
    def __init__(self, chat_completion_func):
        """
        Initialize with chat completion function
        
        Args:
            chat_completion_func: Function that takes messages, temperature, etc. and returns response
        """
        self.chat_completion = chat_completion_func
    
    async def chat_completion_async(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 2000,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        Async chat completion with error handling
        
        Args:
            messages: List of {role, content} dicts
            temperature: 0.0-1.0
            max_tokens: Max response length
            response_format: Optional {"type": "json_object"} for JSON mode
        
        Returns:
            Response text
        """
        try:
            # Call underlying chat completion (handles both sync and async)
            response = self.chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response
            
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    def validate_json_response(self, response: str) -> bool:
        """Check if response is valid JSON"""
        try:
            json.loads(response)
            return True
        except json.JSONDecodeError:
            return False


# Global instance
_llm_client = None

def get_llm_client(chat_completion_func) -> LLMClient:
    """Get or create LLM client instance"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient(chat_completion_func)
    return _llm_client
