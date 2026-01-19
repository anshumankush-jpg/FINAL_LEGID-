"""
LEGID 5-Stage Cognitive Architecture Pipeline

Stages:
1. Classify → Identify jurisdiction, practice area, urgency
2. Retrieve → Multi-query expansion for comprehensive coverage
3. Reason → 4-layer analysis (Statutory → Procedural → Defence → Practical)
4. Write → Natural human paralegal style
5. Verify → Template detector + citation validator
6. FollowUps → Context-aware suggestions

This eliminates generic templates and produces natural paralegal responses.
"""
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Load prompts from files
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(filename: str) -> str:
    """Load prompt from file"""
    try:
        prompt_path = PROMPTS_DIR / filename
        if prompt_path.exists():
            return prompt_path.read_text(encoding='utf-8')
        else:
            logger.warning(f"Prompt file not found: {filename}")
            return ""
    except Exception as e:
        logger.error(f"Error loading prompt {filename}: {e}")
        return ""


SYSTEM_PROMPT = load_prompt("legid_system.txt")
CLASSIFIER_PROMPT = load_prompt("legid_classifier.txt")
RETRIEVER_PROMPT = load_prompt("legid_retriever.txt")
REASONER_PROMPT = load_prompt("legid_reasoner.txt")
WRITER_PROMPT = load_prompt("legid_writer.txt")
VERIFIER_PROMPT = load_prompt("legid_verifier.txt")
FOLLOWUPS_PROMPT = load_prompt("legid_followups.txt")


class LEGIDPipeline:
    """5-stage cognitive architecture pipeline"""
    
    def __init__(self, llm_client, retriever_client=None):
        self.llm = llm_client
        self.retriever = retriever_client
        
    async def classify(self, question: str) -> Dict[str, Any]:
        """
        STAGE 1: Classify question
        - Jurisdiction
        - Practice area
        - Urgency
        - Missing facts
        """
        messages = [
            {'role': 'system', 'content': CLASSIFIER_PROMPT},
            {'role': 'user', 'content': f"Question: {question}"}
        ]
        
        response = await self.llm.chat_completion(
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        try:
            classification = json.loads(response)
            logger.info(f"Classification: {classification.get('practice_area')}, {classification.get('jurisdiction')}")
            return classification
        except json.JSONDecodeError:
            logger.error(f"Failed to parse classification JSON: {response}")
            return self._default_classification()
    
    async def retrieve(self, question: str, classification: Dict[str, Any]) -> Dict[str, Any]:
        """
        STAGE 2: Multi-query retrieval
        - Generate 6-10 queries
        - Retrieve from official sources
        - Rank by authority
        """
        if not self.retriever:
            logger.warning("No retriever available, skipping retrieval stage")
            return {"queries_used": [], "chunks": [], "total_chunks_found": 0}
        
        # Generate queries
        messages = [
            {'role': 'system', 'content': RETRIEVER_PROMPT},
            {'role': 'user', 'content': f"Question: {question}\n\nClassification: {json.dumps(classification)}"}
        ]
        
        response = await self.llm.chat_completion(
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        try:
            retrieval_plan = json.loads(response)
            queries = retrieval_plan.get('queries', [])
            
            # Execute retrieval for each query
            all_chunks = []
            for query in queries[:8]:  # Limit to 8 queries
                chunks = await self.retriever.search(query, k=3)
                all_chunks.extend(chunks)
            
            # Deduplicate and rank
            unique_chunks = self._deduplicate_chunks(all_chunks)
            
            return {
                "queries_used": queries,
                "chunks": unique_chunks[:retrieval_plan.get('chunk_limit', 8)],
                "total_chunks_found": len(unique_chunks)
            }
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse retrieval JSON: {response}")
            return {"queries_used": [], "chunks": [], "total_chunks_found": 0}
    
    async def reason(self, question: str, classification: Dict, retrieval: Dict) -> Dict[str, Any]:
        """
        STAGE 3: 4-layer reasoning
        - Statutory layer
        - Procedural layer
        - Defence/exception layer
        - Practical outcome layer
        """
        chunks_text = "\n\n".join([
            f"[Chunk {i+1} - {chunk.get('source', 'Unknown')}]\n{chunk.get('text', '')}"
            for i, chunk in enumerate(retrieval.get('chunks', []))
        ])
        
        messages = [
            {'role': 'system', 'content': REASONER_PROMPT},
            {'role': 'user', 'content': f"""Question: {question}

Classification:
{json.dumps(classification, indent=2)}

Retrieved Sources:
{chunks_text}

Analyze using 4-layer reasoning and output JSON."""}
        ]
        
        response = await self.llm.chat_completion(
            messages=messages,
            temperature=0.15,
            response_format={"type": "json_object"}
        )
        
        try:
            reasoning = json.loads(response)
            logger.info(f"Reasoning complete: {len(reasoning.get('citation_map', []))} citations mapped")
            return reasoning
        except json.JSONDecodeError:
            logger.error(f"Failed to parse reasoning JSON: {response}")
            return self._default_reasoning()
    
    async def write(self, reasoning: Dict) -> str:
        """
        STAGE 4: Write natural human paralegal answer
        - No templates
        - Natural flow
        - Anxiety-aware
        """
        messages = [
            {'role': 'system', 'content': WRITER_PROMPT},
            {'role': 'user', 'content': f"""Reasoning Output:
{json.dumps(reasoning, indent=2)}

Write a natural human paralegal answer. Remember the hard bans!"""}
        ]
        
        response = await self.llm.chat_completion(
            messages=messages,
            temperature=0.25,  # Slightly higher for natural language
            max_tokens=3000
        )
        
        logger.info(f"Draft written: {len(response)} chars")
        return response
    
    async def verify(self, draft: str, reasoning: Dict) -> Dict[str, Any]:
        """
        STAGE 5: Template detection + citation validation
        - Check for banned patterns
        - Validate citations
        - Force rewrite if quality gate fails
        """
        messages = [
            {'role': 'system', 'content': VERIFIER_PROMPT},
            {'role': 'user', 'content': f"""Drafted Answer:
{draft}

Citation Map (from reasoner):
{json.dumps(reasoning.get('citation_map', []), indent=2)}

Verify and output JSON."""}
        ]
        
        response = await self.llm.chat_completion(
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        try:
            verification = json.loads(response)
            
            if not verification.get('passes_quality_gate', True):
                logger.warning(f"Quality gate FAILED. Banned patterns: {verification.get('banned_patterns_found', [])}")
                logger.warning(f"Required fixes: {verification.get('required_fixes', [])}")
            else:
                logger.info("Quality gate PASSED")
            
            return verification
        except json.JSONDecodeError:
            logger.error(f"Failed to parse verification JSON: {response}")
            return {"passes_quality_gate": True, "banned_patterns_found": [], "citation_violations": []}
    
    async def suggest_followups(self, question: str, classification: Dict, answer: str) -> Dict[str, Any]:
        """
        STAGE 6: Context-aware follow-up suggestions
        - 2-4 natural suggestions
        - No menu language
        - Topic-specific
        """
        messages = [
            {'role': 'system', 'content': FOLLOWUPS_PROMPT},
            {'role': 'user', 'content': f"""Question: {question}

Classification:
{json.dumps(classification, indent=2)}

Main Answer:
{answer[:500]}...

Generate 2-4 natural follow-up suggestions as JSON."""}
        ]
        
        response = await self.llm.chat_completion(
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        try:
            followups = json.loads(response)
            logger.info(f"Generated {len(followups.get('suggestions', []))} follow-up suggestions")
            return followups
        except json.JSONDecodeError:
            logger.error(f"Failed to parse follow-ups JSON: {response}")
            return {"suggestions": [], "progressive_disclosure_available": False}
    
    async def run_full_pipeline(self, question: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute complete 5-stage pipeline
        
        Returns final LEGID response with natural paralegal answer
        """
        logger.info(f"Starting LEGID pipeline for question: {question[:100]}...")
        
        # STAGE 1: Classify
        classification = await self.classify(question)
        
        # STAGE 2: Retrieve
        retrieval_result = await self.retrieve(question, classification)
        
        # STAGE 3: Reason
        reasoning = await self.reason(question, classification, retrieval_result)
        
        # STAGE 4: Write
        draft_answer = await self.write(reasoning)
        
        # STAGE 5: Verify
        verification = await self.verify(draft_answer, reasoning)
        
        # Use rewritten answer if quality gate failed
        if not verification.get('passes_quality_gate', True) and verification.get('rewritten_answer'):
            final_answer = verification['rewritten_answer']
            logger.info("Using rewritten answer (quality gate failed)")
        else:
            final_answer = draft_answer
        
        # STAGE 6: Follow-ups
        followups = await self.suggest_followups(question, classification, final_answer)
        
        # Build final response
        response = {
            "answer": final_answer,
            "follow_ups": followups.get('suggestions', []),
            "citations": self._build_citations(retrieval_result, reasoning),
            "metadata": {
                "pipeline_version": "5_stage_cognitive",
                "practice_area": classification.get('practice_area'),
                "jurisdiction": classification.get('jurisdiction'),
                "urgency": classification.get('urgency_level'),
                "chunks_used": len(retrieval_result.get('chunks', [])),
                "queries_used": len(retrieval_result.get('queries_used', [])),
                "quality_gate_passed": verification.get('passes_quality_gate', True),
                "banned_patterns_detected": len(verification.get('banned_patterns_found', [])),
                "follow_up_topic": followups.get('topic', 'general')
            },
            "confidence": self._calculate_confidence(classification, retrieval_result, verification),
            "chunks_used": len(retrieval_result.get('chunks', []))
        }
        
        logger.info(f"Pipeline complete. Final answer: {len(final_answer)} chars, Confidence: {response['confidence']}")
        
        return response
    
    def _deduplicate_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Remove duplicate chunks based on text similarity"""
        seen = set()
        unique = []
        for chunk in chunks:
            text_key = chunk.get('text', '')[:100]  # First 100 chars as key
            if text_key not in seen:
                seen.add(text_key)
                unique.append(chunk)
        return unique
    
    def _build_citations(self, retrieval_result: Dict, reasoning: Dict) -> List[Dict]:
        """Build citation list from retrieval + reasoning"""
        citations = []
        citation_map = reasoning.get('citation_map', [])
        chunks = {chunk.get('chunk_id'): chunk for chunk in retrieval_result.get('chunks', [])}
        
        for mapping in citation_map:
            for chunk_id in mapping.get('supporting_chunk_ids', []):
                if chunk_id in chunks:
                    chunk = chunks[chunk_id]
                    citations.append({
                        'source': chunk.get('source', 'Unknown'),
                        'url': chunk.get('url'),
                        'authority': chunk.get('authority', 'secondary'),
                        'claim': mapping.get('claim', '')
                    })
        
        return citations
    
    def _calculate_confidence(self, classification: Dict, retrieval: Dict, verification: Dict) -> float:
        """Calculate confidence score based on pipeline results"""
        base_confidence = 0.5
        
        # Boost for good classification
        if classification.get('jurisdiction', {}).get('confidence', 0) > 0.8:
            base_confidence += 0.1
        
        # Boost for good retrieval
        if retrieval.get('total_chunks_found', 0) >= 5:
            base_confidence += 0.15
        
        # Boost for passing quality gate
        if verification.get('passes_quality_gate', False):
            base_confidence += 0.2
        
        # Penalty for banned patterns
        if verification.get('banned_patterns_found', []):
            base_confidence -= 0.15
        
        # Penalty for citation violations
        if verification.get('citation_violations', []):
            base_confidence -= 0.1
        
        return min(0.99, max(0.3, base_confidence))
    
    def _default_classification(self) -> Dict:
        """Fallback classification if parsing fails"""
        return {
            "jurisdiction": {"country": "Canada", "province_state": "Unknown", "confidence": 0.5},
            "practice_area": "General Legal",
            "urgency_level": "medium",
            "urgency_indicators": [],
            "key_facts_present": [],
            "missing_facts_that_matter": [],
            "topic_keywords": []
        }
    
    def _default_reasoning(self) -> Dict:
        """Fallback reasoning if parsing fails"""
        return {
            "statutory_layer": {"governing_laws": [], "authority": "Unknown", "federal_vs_provincial": "unknown"},
            "procedural_layer": {"forms_required": [], "deadlines": [], "service_requirements": [], "eligibility_thresholds": [], "common_procedural_failures": []},
            "defence_exception_layer": {"exemptions": [], "credits_refunds": [], "defences": [], "offsets": [], "what_facts_change_outcome": []},
            "practical_outcome_layer": {"what_usually_happens": [], "institutional_behavior": "", "common_user_mistakes": [], "strategic_considerations": []},
            "evidence_requirements": {"documents_needed": [], "witness_types": [], "proof_of_service": []},
            "citation_map": [],
            "missing_in_sources": [],
            "anxiety_factors": []
        }


# Global instance
_pipeline = None

def get_legid_pipeline(llm_client, retriever_client=None) -> LEGIDPipeline:
    """Get or create LEGID pipeline instance"""
    global _pipeline
    if _pipeline is None:
        _pipeline = LEGIDPipeline(llm_client, retriever_client)
    return _pipeline
