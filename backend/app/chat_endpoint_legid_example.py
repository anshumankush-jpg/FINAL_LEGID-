"""
LEGID Master Prompt - Chat Endpoint Implementation Examples
Drop these into your main.py or create new endpoints

These are production-ready examples showing exactly how to integrate LEGID.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
import logging

from app.legid_master_prompt import (
    LEGID_MASTER_PROMPT,
    get_legid_prompt,
    build_legid_system_prompt
)
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


# ═══════════════════════════════════════════════════════════════
# EXAMPLE 1: Simple Direct Replacement
# ═══════════════════════════════════════════════════════════════

@router.post("/api/chat/legid")
async def chat_with_legid(request: dict):
    """
    Simplest implementation - just swap the system prompt.
    
    This immediately upgrades your responses to paralegal-grade.
    """
    try:
        messages = [
            {'role': 'system', 'content': LEGID_MASTER_PROMPT},
            {'role': 'user', 'content': request['message']}
        ]
        
        # Your existing OpenAI call
        response = await openai_chat_completion(
            messages=messages,
            temperature=0.2,  # LEGID works best with low temperature
            max_tokens=2000   # LEGID responses are more detailed
        )
        
        return {
            "answer": response,
            "prompt_version": "legid_master",
            "mode": "master"
        }
    except Exception as e:
        logger.error(f"LEGID chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════
# EXAMPLE 2: Mode Selection (Paralegal/Lawyer/Research)
# ═══════════════════════════════════════════════════════════════

@router.post("/api/chat/legid/advanced")
async def chat_with_legid_modes(request: dict):
    """
    Allow different modes for different use cases.
    
    Frontend can specify mode, or backend can determine it.
    """
    # Get mode from request or use default
    mode = request.get('mode', 'paralegal')  # master, paralegal, lawyer, research
    
    # Validate mode
    valid_modes = ['master', 'paralegal', 'lawyer', 'research']
    if mode not in valid_modes:
        mode = 'paralegal'
    
    system_prompt = get_legid_prompt(mode=mode)
    
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': request['message']}
    ]
    
    response = await openai_chat_completion(
        messages=messages,
        temperature=0.2
    )
    
    return {
        "answer": response,
        "mode": mode,
        "prompt_version": "legid"
    }


# ═══════════════════════════════════════════════════════════════
# EXAMPLE 3: Full Context-Aware (Recommended for Production)
# ═══════════════════════════════════════════════════════════════

@router.post("/api/chat/legid/context-aware")
async def chat_with_context_aware_legid(
    request: dict,
    user: dict = Depends(get_current_user)  # Your auth dependency
):
    """
    Production-ready implementation with full context awareness.
    
    Automatically adjusts prompt based on:
    - User role (client/lawyer/paralegal)
    - User preferences (response style)
    - Jurisdiction
    - Question context
    """
    
    # Determine mode based on user role
    mode_mapping = {
        "client": "paralegal",      # Accessible but rigorous
        "paralegal": "paralegal",   # Practical focus
        "lawyer": "lawyer",         # Maximum sophistication
        "researcher": "research",   # Deep analysis
        "admin": "master"           # Default
    }
    mode = mode_mapping.get(user.get('role', 'client'), 'paralegal')
    
    # Get jurisdiction (from request or user profile)
    jurisdiction = request.get('jurisdiction') or user.get('jurisdiction', 'Ontario')
    
    # Get response style preference
    response_style = user.get('preferences', {}).get('response_style', 'detailed')
    
    # Build context-aware system prompt
    system_prompt = build_legid_system_prompt(
        mode=mode,
        user_role=user.get('role'),
        jurisdiction=jurisdiction,
        response_style=response_style,
        enable_self_grading=True  # Quality assurance
    )
    
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': request['message']}
    ]
    
    # Add conversation history if available
    if 'conversation_id' in request:
        history = await get_conversation_history(request['conversation_id'])
        # Insert history before user message
        messages = messages[:1] + history + messages[1:]
    
    response = await openai_chat_completion(
        messages=messages,
        temperature=0.2,
        max_tokens=2000
    )
    
    # Log for analytics
    logger.info(f"LEGID response | mode={mode} | jurisdiction={jurisdiction} | user_role={user.get('role')}")
    
    return {
        "answer": response,
        "mode": mode,
        "jurisdiction": jurisdiction,
        "response_style": response_style,
        "prompt_version": "legid_context_aware"
    }


# ═══════════════════════════════════════════════════════════════
# EXAMPLE 4: Hybrid System (LEGID + RAG/Document Retrieval)
# ═══════════════════════════════════════════════════════════════

@router.post("/api/chat/legid/rag")
async def chat_with_legid_and_rag(
    request: dict,
    user: dict = Depends(get_current_user)
):
    """
    Combine LEGID Master Prompt with document retrieval.
    
    This is THE killer combination:
    - LEGID enforces structure and rigor
    - RAG provides authoritative sources
    """
    
    # Get LEGID prompt
    mode = 'paralegal' if user.get('role') == 'client' else 'lawyer'
    system_prompt = get_legid_prompt(mode=mode)
    
    # Retrieve relevant documents (your existing RAG system)
    retrieved_docs = await retrieve_relevant_documents(
        query=request['message'],
        jurisdiction=request.get('jurisdiction', 'Ontario'),
        top_k=5
    )
    
    # Build context with retrieved documents
    context = "\n\n".join([
        f"[Document: {doc['title']}, Page {doc.get('page', 'N/A')}]\n{doc['content']}"
        for doc in retrieved_docs
    ])
    
    # Enhanced user message with context
    user_message_with_context = f"""RETRIEVED LEGAL DOCUMENTS:
{context}

USER QUESTION:
{request['message']}

Using the above documents as authoritative sources, provide a structured legal analysis."""
    
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_message_with_context}
    ]
    
    response = await openai_chat_completion(
        messages=messages,
        temperature=0.2,
        max_tokens=2500
    )
    
    return {
        "answer": response,
        "mode": mode,
        "sources": [doc['title'] for doc in retrieved_docs],
        "chunks_used": len(retrieved_docs),
        "prompt_version": "legid_rag"
    }


# ═══════════════════════════════════════════════════════════════
# EXAMPLE 5: Gradual Migration (Feature Flag)
# ═══════════════════════════════════════════════════════════════

@router.post("/api/chat")
async def smart_chat(request: dict, user: dict = Depends(get_current_user)):
    """
    Production migration strategy: Use feature flag to gradually roll out LEGID.
    
    This lets you:
    - A/B test LEGID vs old prompts
    - Roll out to specific users first
    - Easy rollback if needed
    """
    
    # Check if LEGID is enabled (from settings or user preference)
    use_legid = (
        settings.LEGID_MASTER_PROMPT_ENABLED and
        user.get('preferences', {}).get('enable_legid', True)
    )
    
    if use_legid:
        # Use LEGID Master Prompt
        mode = 'paralegal' if user.get('role') == 'client' else 'lawyer'
        system_prompt = get_legid_prompt(mode=mode)
        prompt_version = f"legid_{mode}"
    else:
        # Use legacy prompt
        from app.legal_prompts import LegalPromptSystem
        system_prompt = LegalPromptSystem.PROFESSIONAL_SYSTEM_PROMPT
        prompt_version = "legacy"
    
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': request['message']}
    ]
    
    response = await openai_chat_completion(
        messages=messages,
        temperature=0.2
    )
    
    # Log for A/B testing analytics
    logger.info(f"Chat response | prompt={prompt_version} | user_id={user.get('id')}")
    
    return {
        "answer": response,
        "prompt_version": prompt_version
    }


# ═══════════════════════════════════════════════════════════════
# EXAMPLE 6: Quick Fix - Update Existing Endpoint
# ═══════════════════════════════════════════════════════════════

"""
If you want to quickly upgrade your EXISTING endpoint in main.py:

BEFORE:
-------
@app.post("/api/chat/simple")
async def simple_chat(request: ChatRequest):
    messages = [
        {'role': 'system', 'content': settings.SYSTEM_PROMPT},
        {'role': 'user', 'content': request.message}
    ]
    ...

AFTER:
------
from app.legid_master_prompt import LEGID_MASTER_PROMPT

@app.post("/api/chat/simple")
async def simple_chat(request: ChatRequest):
    messages = [
        {'role': 'system', 'content': LEGID_MASTER_PROMPT},  # ✅ Only change needed!
        {'role': 'user', 'content': request.message}
    ]
    ...

That's it! Your chat is now paralegal-grade.
"""


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS (Example implementations)
# ═══════════════════════════════════════════════════════════════

async def openai_chat_completion(messages: list, temperature: float = 0.2, max_tokens: int = 1500) -> str:
    """
    Your OpenAI completion function.
    Replace with your actual implementation.
    """
    # Example using openai library
    import openai
    
    response = openai.ChatCompletion.create(
        model=settings.OPENAI_CHAT_MODEL or "gpt-4",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return response.choices[0].message.content


async def get_current_user():
    """Your authentication dependency - example placeholder"""
    # Replace with actual auth
    return {
        "id": "user123",
        "role": "client",
        "jurisdiction": "Ontario",
        "preferences": {
            "response_style": "detailed",
            "enable_legid": True
        }
    }


async def retrieve_relevant_documents(query: str, jurisdiction: str, top_k: int = 5):
    """Your RAG/document retrieval - example placeholder"""
    # Replace with actual retrieval logic
    return [
        {
            "title": "Residential Tenancies Act, 2006",
            "content": "Section 43: Notice of termination...",
            "page": 12
        }
    ]


async def get_conversation_history(conversation_id: str):
    """Get previous messages - example placeholder"""
    # Replace with actual conversation retrieval
    return [
        {'role': 'user', 'content': 'Previous question'},
        {'role': 'assistant', 'content': 'Previous answer'}
    ]


# ═══════════════════════════════════════════════════════════════
# USAGE GUIDE
# ═══════════════════════════════════════════════════════════════

"""
HOW TO USE THESE EXAMPLES:

1. QUICK START (5 minutes):
   - Copy Example 1 into your main.py
   - Test with: curl -X POST localhost:8000/api/chat/legid -d '{"message":"Can landlords evict without notice in Ontario?"}'
   - Compare response to old endpoint

2. PRODUCTION (30 minutes):
   - Use Example 3 (context-aware)
   - Wire up your auth system
   - Deploy with feature flag (Example 5)

3. ADVANCED (1 hour):
   - Combine with RAG (Example 4)
   - Add mode selection UI
   - Implement analytics

RECOMMENDED MIGRATION PATH:

Week 1: Deploy Example 5 (feature flag) with LEGID_MASTER_PROMPT_ENABLED=false
Week 2: Enable for 10% of users, collect feedback
Week 3: Enable for 50% of users
Week 4: Full rollout to 100%

TESTING CHECKLIST:

□ Legal question gets 5-part structured response
□ Jurisdiction is explicitly identified
□ Statutes are named (not hallucinated)
□ Professional tone (no emojis)
□ Response is more rigorous than ChatGPT
□ No casual phrases ("basically", "just")
□ Appropriate disclaimer included
"""


# ═══════════════════════════════════════════════════════════════
# MONITORING & ANALYTICS
# ═══════════════════════════════════════════════════════════════

def log_legid_analytics(
    prompt_version: str,
    mode: str,
    user_role: str,
    response_length: int,
    question: str,
    answer: str
):
    """
    Track LEGID performance metrics.
    
    Use this to measure:
    - Average response quality
    - User satisfaction by mode
    - Response completeness
    """
    
    analytics = {
        "prompt_version": prompt_version,
        "mode": mode,
        "user_role": user_role,
        "response_length": response_length,
        "has_structure": all([
            "ISSUE IDENTIFICATION" in answer or "Issue:" in answer,
            "GOVERNING LAW" in answer or "Legal Framework:" in answer,
            "ANALYSIS" in answer or "Analysis:" in answer,
        ]),
        "has_citations": any([
            "Act" in answer,
            "Section" in answer,
            "S.O." in answer,
            "S.C." in answer
        ]),
        "professional_tone": not any([
            "😊" in answer,
            "basically" in answer.lower(),
            "just" in answer[:100].lower()  # Check first 100 chars
        ])
    }
    
    logger.info(f"LEGID Analytics: {analytics}")
    # Send to your analytics system (Mixpanel, PostHog, etc.)
    
    return analytics


# Export router
__all__ = ['router']
