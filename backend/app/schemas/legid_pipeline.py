"""
Pydantic schemas for LEGID 5-stage cognitive pipeline
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class UrgencyLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SourceType(str, Enum):
    PRIMARY_LAW = "primary_law"
    OFFICIAL_GUIDANCE = "official_guidance"
    TRIBUNAL_OR_COURT = "tribunal_or_court"
    CASE_LAW = "case_law"
    SECONDARY = "secondary"


class AuthorityLevel(str, Enum):
    PRIMARY = "primary"
    OFFICIAL = "official"
    SECONDARY = "secondary"


# STAGE 1: Classification
class Jurisdiction(BaseModel):
    country: str = Field(..., description="Canada|USA|Unknown")
    province_state: Optional[str] = Field(None, description="Ontario|BC|California|...")
    confidence: float = Field(..., ge=0.0, le=1.0)


class Classification(BaseModel):
    jurisdiction: Jurisdiction
    practice_area: str
    urgency_level: UrgencyLevel
    urgency_indicators: List[str] = []
    key_facts_present: List[str] = []
    missing_facts_that_matter: List[str] = []
    topic_keywords: List[str] = []


# STAGE 2: Retrieval
class RetrievalQuery(BaseModel):
    queries: List[str] = Field(..., min_length=6, max_length=10)
    preferred_source_types: List[SourceType]
    must_cover: List[str]
    chunk_limit: int = 8


class RetrievedChunk(BaseModel):
    chunk_id: str
    text: str
    source: str
    url: Optional[str] = None
    authority: AuthorityLevel
    score: float = 0.0
    metadata: Dict[str, Any] = {}


class RetrievalResult(BaseModel):
    queries_used: List[str]
    chunks: List[RetrievedChunk]
    total_chunks_found: int


# STAGE 3: Reasoning
class StatutoryLayer(BaseModel):
    governing_laws: List[str]
    authority: str
    federal_vs_provincial: str


class ProceduralLayer(BaseModel):
    forms_required: List[str] = []
    deadlines: List[str] = []
    service_requirements: List[str] = []
    eligibility_thresholds: List[str] = []
    common_procedural_failures: List[str] = []


class DefenceExceptionLayer(BaseModel):
    exemptions: List[str] = []
    credits_refunds: List[str] = []
    defences: List[str] = []
    offsets: List[str] = []
    what_facts_change_outcome: List[str] = []


class PracticalOutcomeLayer(BaseModel):
    what_usually_happens: List[str] = []
    institutional_behavior: str
    common_user_mistakes: List[str] = []
    strategic_considerations: List[str] = []


class EvidenceRequirements(BaseModel):
    documents_needed: List[str] = []
    witness_types: List[str] = []
    proof_of_service: List[str] = []


class CitationMapping(BaseModel):
    claim: str
    supporting_chunk_ids: List[str]
    source_authority: AuthorityLevel


class ReasoningOutput(BaseModel):
    statutory_layer: StatutoryLayer
    procedural_layer: ProceduralLayer
    defence_exception_layer: DefenceExceptionLayer
    practical_outcome_layer: PracticalOutcomeLayer
    evidence_requirements: EvidenceRequirements
    citation_map: List[CitationMapping]
    missing_in_sources: List[str] = []
    anxiety_factors: List[str] = []


# STAGE 4: Writing
class DraftedAnswer(BaseModel):
    content: str
    word_count: int
    uses_bullets: bool
    uses_numbered_lists: bool


# STAGE 5: Verification
class BannedPattern(BaseModel):
    pattern: str
    line: str
    severity: str  # critical|high|medium


class CitationViolation(BaseModel):
    claim: str
    problem: str
    severity: str


class ToneIssue(BaseModel):
    issue: str
    line: str


class VerificationResult(BaseModel):
    banned_patterns_found: List[BannedPattern] = []
    citation_violations: List[CitationViolation] = []
    tone_issues: List[ToneIssue] = []
    passes_quality_gate: bool
    required_fixes: List[str] = []
    rewritten_answer: Optional[str] = None


# STAGE 6: Follow-ups
class FollowUpSuggestion(BaseModel):
    label: str
    intent: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)


class FollowUpResult(BaseModel):
    suggestions: List[FollowUpSuggestion] = []
    progressive_disclosure_available: bool = False
    natural_prompt: Optional[str] = None
    topic: str = "general"


# Final Response
class LEGIDResponse(BaseModel):
    answer: str
    follow_ups: List[FollowUpSuggestion] = []
    citations: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}
    confidence: float = 0.0
    chunks_used: int = 0


# Pipeline State (tracks progress through stages)
class PipelineState(BaseModel):
    question: str
    classification: Optional[Classification] = None
    retrieval_result: Optional[RetrievalResult] = None
    reasoning: Optional[ReasoningOutput] = None
    draft: Optional[DraftedAnswer] = None
    verification: Optional[VerificationResult] = None
    follow_ups: Optional[FollowUpResult] = None
    final_response: Optional[LEGIDResponse] = None
