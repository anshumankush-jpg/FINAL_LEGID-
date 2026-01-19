"""
LEGID Gen-2 Authority Rewriter

Automatic transformer that takes any draft and upgrades it to 110% standard:
- Structural purge (delete banned patterns)
- Domain & jurisdiction lock
- Authority thinking injection
- Procedural reality sequence
- Failure-mode warning
- Human style enforcement
- Natural follow-ups

This is the automatic quality upgrade system.
"""
import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)

# Load rewriter prompt
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
GEN2_REWRITER_PROMPT = ""
try:
    prompt_path = PROMPTS_DIR / "legid_gen2_rewriter.txt"
    if prompt_path.exists():
        GEN2_REWRITER_PROMPT = prompt_path.read_text(encoding='utf-8')
    else:
        logger.warning(f"GEN-2 rewriter prompt not found at {prompt_path}")
except Exception as e:
    logger.error(f"Failed to load GEN-2 rewriter prompt: {e}")


class Gen2AuthorityRewriter:
    """Gen-2 Authority Rewriter - automatic quality transformer"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
        self.prompt = GEN2_REWRITER_PROMPT
    
    async def rewrite_to_110_percent(self, draft: str, question: str) -> Dict:
        """
        Automatic transformation to 110% standard
        
        7-step process:
        1. Structural purge (delete banned patterns)
        2. Domain & jurisdiction lock (remove irrelevant)
        3. Authority thinking injection (who has power)
        4. Procedural reality sequence (what happens next)
        5. Failure-mode warning (common mistakes)
        6. Human style enforcement (natural paragraphs)
        7. Natural follow-ups (conversational)
        
        Returns:
        {
            "rewritten_answer": str,
            "transformations_applied": list,
            "banned_patterns_removed": list,
            "authority_thinking_added": bool,
            "original_length": int,
            "rewritten_length": int
        }
        """
        if not self.prompt:
            logger.warning("GEN-2 rewriter prompt not available, returning original")
            return {
                "rewritten_answer": draft,
                "transformations_applied": [],
                "banned_patterns_removed": [],
                "authority_thinking_added": False,
                "original_length": len(draft),
                "rewritten_length": len(draft)
            }
        
        messages = [
            {'role': 'system', 'content': self.prompt},
            {'role': 'user', 'content': f"""Original Question:
{question}

Drafted Answer (needs 110% transformation):
{draft}

Transform this to 110% standard using all 7 steps:
1. Structural purge
2. Domain & jurisdiction lock
3. Authority thinking injection
4. Procedural reality sequence
5. Failure-mode warning
6. Human style enforcement
7. Natural follow-ups

Return ONLY the rewritten answer."""}
        ]
        
        logger.info("Gen-2 Authority Rewriter: Transforming draft to 110% standard...")
        
        rewritten = await self.llm.chat_completion_async(
            messages=messages,
            temperature=0.23,  # Slightly higher for natural rewrites
            max_tokens=3500
        )
        
        # Detect what was transformed
        transformations = self._detect_transformations(draft, rewritten)
        
        logger.info(f"Gen-2 rewrite complete: {len(draft)} → {len(rewritten)} chars")
        logger.info(f"Transformations applied: {len(transformations)}")
        
        return {
            "rewritten_answer": rewritten,
            "transformations_applied": transformations,
            "banned_patterns_removed": self._detect_banned_patterns(draft),
            "authority_thinking_added": self._has_authority_thinking(rewritten),
            "original_length": len(draft),
            "rewritten_length": len(rewritten)
        }
    
    def _detect_transformations(self, original: str, rewritten: str) -> list:
        """Detect what transformations were applied"""
        transformations = []
        
        # Check if banned patterns removed
        banned_in_original = self._detect_banned_patterns(original)
        banned_in_rewritten = self._detect_banned_patterns(rewritten)
        
        if len(banned_in_original) > len(banned_in_rewritten):
            transformations.append(f"Removed {len(banned_in_original) - len(banned_in_rewritten)} banned patterns")
        
        # Check if authority thinking added
        if not self._has_authority_thinking(original) and self._has_authority_thinking(rewritten):
            transformations.append("Authority thinking injected")
        
        # Check if structure changed
        if "Option A" in original and "Option A" not in rewritten:
            transformations.append("False choices eliminated")
        
        # Check length change
        if len(rewritten) > len(original) * 1.2:
            transformations.append("Expanded with procedural detail")
        
        return transformations
    
    def _detect_banned_patterns(self, text: str) -> list:
        """Detect banned patterns in text"""
        banned = []
        banned_terms = [
            "Quick Take", "What I understood", "Your Options",
            "Option A", "Option B", "Pros:", "Cons:", "Risk Level"
        ]
        
        for term in banned_terms:
            if term in text:
                banned.append(term)
        
        return banned
    
    def _has_authority_thinking(self, text: str) -> bool:
        """Check if text has authority-aware thinking"""
        authority_indicators = [
            "adjudicator", "judge", "court", "CRA", "IRS", "LTB", "tribunal",
            "police", "Crown", "prosecutor"
        ]
        
        # Check if authority is mentioned AND their thinking/focus is explained
        for authority in authority_indicators:
            if authority.lower() in text.lower():
                # Check for thinking/focus language nearby
                if any(phrase in text.lower() for phrase in [
                    "care about", "look at", "focus on", "scrutinize",
                    "weigh", "consider", "typically", "usually review"
                ]):
                    return True
        
        return False


# Global instance
_gen2_rewriter = None

def get_gen2_rewriter(llm_client):
    """Get or create Gen-2 rewriter instance"""
    global _gen2_rewriter
    if _gen2_rewriter is None:
        _gen2_rewriter = Gen2AuthorityRewriter(llm_client)
    return _gen2_rewriter
