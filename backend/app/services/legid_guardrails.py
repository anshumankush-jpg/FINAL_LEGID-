"""
LEGID Guardrails — Template Detector and Citation Validator

Ensures responses are natural (not templated) and citations are valid.
"""
import re
from typing import List, Dict, Tuple


# Banned patterns (exact matches and variations)
BANNED_PATTERNS = [
    # Template headers
    r"Quick [Tt]ake",
    r"What I [Uu]nderstood",
    r"Your [Oo]ptions?",
    r"Option [AB12]",
    r"[Pp]ros:?",
    r"[Cc]ons:?",
    r"[Rr]isk [Ll]evel",
    r"TITLE:",
    
    # Menu-style options
    r"Option \d+\s*[-:]",
    r"Choice [AB12]",
    r"Path [AB12]",
    
    # Generic labels
    r"Advantages?:",
    r"Disadvantages?:",
    r"Benefits?:",
    r"Drawbacks?:",
    
    # Emojis (common legal ones)
    r"⚖️|📋|✅|❌|🔍|⚠️|💡|📊|🏛️|👨‍⚖️"
]


def detect_banned_patterns(text: str) -> List[Dict[str, str]]:
    """
    Detect banned template patterns in text
    
    Returns list of violations with pattern, line, and severity
    """
    violations = []
    lines = text.split('\n')
    
    for pattern in BANNED_PATTERNS:
        for line_num, line in enumerate(lines, 1):
            if re.search(pattern, line, re.IGNORECASE):
                violations.append({
                    "pattern": pattern,
                    "line": line.strip(),
                    "line_number": line_num,
                    "severity": "critical"
                })
    
    return violations


def validate_citations(answer: str, citation_map: List[Dict], chunks: List[Dict]) -> List[Dict[str, str]]:
    """
    Validate that every citation claim is supported by actual chunks
    
    Returns list of citation violations
    """
    violations = []
    chunk_dict = {chunk.get('chunk_id'): chunk.get('text', '') for chunk in chunks}
    
    for mapping in citation_map:
        claim = mapping.get('claim', '')
        chunk_ids = mapping.get('supporting_chunk_ids', [])
        
        # Check if claim is in answer
        if claim not in answer:
            continue
        
        # Check if chunks support the claim
        supported = False
        for chunk_id in chunk_ids:
            if chunk_id in chunk_dict:
                chunk_text = chunk_dict[chunk_id]
                # Simple keyword overlap check (can be improved with semantic similarity)
                claim_keywords = set(claim.lower().split())
                chunk_keywords = set(chunk_text.lower().split())
                overlap = len(claim_keywords & chunk_keywords) / max(len(claim_keywords), 1)
                
                if overlap > 0.3:  # At least 30% keyword overlap
                    supported = True
                    break
        
        if not supported and chunk_ids:
            violations.append({
                "claim": claim,
                "problem": "Chunks do not sufficiently support this claim",
                "chunk_ids": chunk_ids,
                "severity": "high"
            })
        elif not chunk_ids:
            violations.append({
                "claim": claim,
                "problem": "No supporting chunks provided",
                "severity": "high"
            })
    
    return violations


def detect_tone_issues(text: str) -> List[Dict[str, str]]:
    """
    Detect robotic or overly academic tone
    
    Returns list of tone issues
    """
    issues = []
    
    # Check for overly academic phrases
    academic_phrases = [
        r"it is important to note that",
        r"it should be noted that",
        r"it is worth noting",
        r"pursuant to",
        r"heretofore",
        r"aforementioned"
    ]
    
    for phrase in academic_phrases:
        if re.search(phrase, text, re.IGNORECASE):
            issues.append({
                "issue": "overly academic",
                "phrase": phrase,
                "suggestion": "Use simpler language"
            })
    
    # Check for robotic repetition
    lines = text.split('\n')
    line_starts = [line.strip()[:20] for line in lines if line.strip()]
    if len(line_starts) != len(set(line_starts)):
        issues.append({
            "issue": "repetitive sentence starts",
            "suggestion": "Vary sentence structure"
        })
    
    return issues


def full_quality_check(
    answer: str,
    citation_map: List[Dict],
    chunks: List[Dict]
) -> Tuple[bool, List[str]]:
    """
    Run complete quality check
    
    Returns (passes, list_of_issues)
    """
    issues = []
    
    # Check 1: Banned patterns
    banned = detect_banned_patterns(answer)
    if banned:
        for violation in banned:
            issues.append(f"Banned pattern: '{violation['pattern']}' in line {violation['line_number']}")
    
    # Check 2: Citation validation
    citation_violations = validate_citations(answer, citation_map, chunks)
    if citation_violations:
        for violation in citation_violations:
            issues.append(f"Citation issue: {violation['problem']} for claim '{violation['claim'][:50]}...'")
    
    # Check 3: Tone
    tone_issues = detect_tone_issues(answer)
    if tone_issues:
        for issue in tone_issues:
            issues.append(f"Tone issue: {issue['issue']}")
    
    passes = len(issues) == 0
    
    return passes, issues
