"""
LEGID Shadow Answer System

Generates TWO independent answers, compares them, and outputs the stronger one.

This is how you reach 110-120% consistency:
- Draft A: GEN-2 Master
- Draft B: 110% Master
- Shadow Comparator: Evaluates both and outputs superior hybrid

This catches failures that single-pass systems miss.
"""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class LEGIDShadowSystem:
    """Shadow answer comparison system"""
    
    def __init__(self, llm_client, gen2_prompt, ultimate_110_prompt, shadow_prompt):
        self.llm = llm_client
        self.gen2_prompt = gen2_prompt
        self.ultimate_110_prompt = ultimate_110_prompt
        self.shadow_prompt = shadow_prompt
    
    async def generate_answer_a(self, question: str) -> str:
        """
        Generate Draft A using GEN-2 Master
        
        7-layer thinking pipeline
        """
        messages = [
            {'role': 'system', 'content': self.gen2_prompt},
            {'role': 'user', 'content': question}
        ]
        
        logger.info("Generating Draft A (GEN-2 Master)...")
        
        answer_a = await self.llm.chat_completion_async(
            messages=messages,
            temperature=0.22,
            max_tokens=3000
        )
        
        logger.info(f"Draft A complete: {len(answer_a)} chars")
        return answer_a
    
    async def generate_answer_b(self, question: str) -> str:
        """
        Generate Draft B using 110% Master
        
        5-filter thinking model
        """
        messages = [
            {'role': 'system', 'content': self.ultimate_110_prompt},
            {'role': 'user', 'content': question}
        ]
        
        logger.info("Generating Draft B (110% Master)...")
        
        answer_b = await self.llm.chat_completion_async(
            messages=messages,
            temperature=0.22,
            max_tokens=3000
        )
        
        logger.info(f"Draft B complete: {len(answer_b)} chars")
        return answer_b
    
    async def compare_and_select(self, question: str, answer_a: str, answer_b: str) -> Dict:
        """
        Shadow Comparator
        
        Evaluates both answers and outputs superior hybrid
        """
        messages = [
            {'role': 'system', 'content': self.shadow_prompt},
            {'role': 'user', 'content': f"""Question:
{question}

Draft Answer A (GEN-2 Master):
{answer_a}

Draft Answer B (110% Master):
{answer_b}

Evaluate both answers on:
1. Authority awareness (1-10)
2. Procedural realism (1-10)
3. Strategic value (1-10)
4. Humanity (1-10)
5. Safety (1-10)

Output the superior answer or hybrid combination."""}
        ]
        
        logger.info("Shadow Comparator evaluating both answers...")
        
        final_answer = await self.llm.chat_completion_async(
            messages=messages,
            temperature=0.2,
            max_tokens=3500
        )
        
        logger.info(f"Shadow comparison complete: {len(final_answer)} chars")
        
        return {
            "draft_a": answer_a,
            "draft_b": answer_b,
            "final_answer": final_answer,
            "comparison_performed": True
        }
    
    async def run_shadow_comparison(self, question: str) -> Dict:
        """
        Execute complete shadow answer system
        
        Returns best answer after comparison
        """
        logger.info(f"Starting Shadow Answer System: {question[:100]}...")
        
        # Generate both drafts in parallel (if async supported)
        # For now, sequential:
        answer_a = await self.generate_answer_a(question)
        answer_b = await self.generate_answer_b(question)
        
        # Compare and select superior
        result = await self.compare_and_select(question, answer_a, answer_b)
        
        logger.info("Shadow Answer System complete")
        
        return {
            "answer": result['final_answer'],
            "draft_a_length": len(answer_a),
            "draft_b_length": len(answer_b),
            "final_length": len(result['final_answer']),
            "shadow_comparison": True
        }


# Global instance
_shadow_system = None

def get_shadow_system(llm_client, gen2_prompt, ultimate_110_prompt, shadow_prompt):
    """Get or create shadow system instance"""
    global _shadow_system
    if _shadow_system is None:
        _shadow_system = LEGIDShadowSystem(llm_client, gen2_prompt, ultimate_110_prompt, shadow_prompt)
    return _shadow_system
