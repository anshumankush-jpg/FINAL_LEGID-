"""
LEGID 110% Verifier and Rewriter

Final quality control layer that enforces 110% standard:
- Hard fail check (banned patterns)
- Thinking check (authority-aware, coherent narrative)
- Humanity check (sounds like real paralegal)
- Case law enforcement (remove unless directly helpful)
- Final clean output

This is what makes LEGID consistently better than ChatGPT.
"""
import re
import logging
from typing import Dict, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

# Load verifier prompt
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
VERIFIER_110_PROMPT = ""
try:
    prompt_path = PROMPTS_DIR / "legid_verifier_110.txt"
    if prompt_path.exists():
        VERIFIER_110_PROMPT = prompt_path.read_text(encoding='utf-8')
except Exception as e:
    logger.error(f"Failed to load verifier_110 prompt: {e}")


# Hard fail patterns (exact matches)
HARD_FAIL_PATTERNS = [
    r"Quick [Tt]ake",
    r"What I [Uu]nderstood",
    r"Your [Oo]ptions?",
    r"Option [AB12]",
    r"[Pp]ros\s*:",
    r"[Cc]ons\s*:",
    r"[Rr]isk [Ll]evel",
    r"TITLE\s*:",
    r"⚖️|📋|✅|❌|🔍|⚠️|💡|📊"  # Common emojis
]


class LEGID110Verifier:
    """110% Quality verifier and rewriter"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def detect_hard_fails(self, text: str) -> List[Dict[str, str]]:
        """
        STEP 1: Detect hard fail patterns
        
        Returns list of violations
        """
        violations = []
        lines = text.split('\n')
        
        for pattern in HARD_FAIL_PATTERNS:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    violations.append({
                        "pattern": pattern,
                        "line": line.strip(),
                        "line_number": line_num,
                        "severity": "CRITICAL"
                    })
        
        # Check for clarifying questions at start
        first_100 = text[:100].lower()
        if any(phrase in first_100 for phrase in ["could you clarify", "can you provide", "what province", "which jurisdiction"]):
            violations.append({
                "pattern": "Clarifying question at start",
                "line": text[:100],
                "line_number": 1,
                "severity": "CRITICAL"
            })
        
        return violations
    
    def check_authority_awareness(self, text: str) -> bool:
        """
        STEP 2: Check if answer explains how authority thinks
        
        Returns True if authority-aware
        """
        # Check for authority-aware language
        authority_indicators = [
            r"(judge|adjudicator|board|court|CRA|IRS|police|prosecutor|tribunal).{0,50}(care about|look at|scrutinize|focus on|consider|weigh)",
            r"what.{0,20}(authority|judge|board|CRA|court|tribunal).{0,30}(actually|typically|usually)",
            r"(evidence|procedure|credibility|pattern|conduct).{0,30}(matters|counts|weighs)",
            r"how.{0,20}(judge|court|board|CRA|LTB|tribunal).{0,30}(thinks|decides|evaluates|assesses)"
        ]
        
        for pattern in authority_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def check_coherent_narrative(self, text: str) -> bool:
        """Check if answer is coherent narrative (not disconnected sections)"""
        # Simple heuristic: if text has many isolated section headers, it's not coherent
        section_headers = re.findall(r'^[A-Z][A-Z\s]+:$', text, re.MULTILINE)
        
        if len(section_headers) > 5:
            return False  # Too many rigid sections
        
        return True
    
    def check_humanity(self, text: str) -> Tuple[bool, List[str]]:
        """
        STEP 3: Check if answer sounds human
        
        Returns (passes, list of issues)
        """
        issues = []
        
        # Check for robotic repetition
        lines = text.split('\n')
        line_starts = [line.strip()[:15] for line in lines if len(line.strip()) > 15]
        
        # Count repeated starts
        from collections import Counter
        start_counts = Counter(line_starts)
        repeated = [start for start, count in start_counts.items() if count > 2]
        
        if repeated:
            issues.append(f"Robotic repetition: '{repeated[0]}...' appears {start_counts[repeated[0]]} times")
        
        # Check for overly academic language
        academic_phrases = [
            r"it is important to note",
            r"it should be noted",
            r"pursuant to",
            r"aforementioned",
            r"heretofore"
        ]
        
        for phrase in academic_phrases:
            if re.search(phrase, text, re.IGNORECASE):
                issues.append(f"Overly academic: '{phrase}'")
        
        # Check opening (should be direct, not formal)
        first_line = lines[0] if lines else ""
        if first_line.startswith("In accordance with") or first_line.startswith("Pursuant to"):
            issues.append("Opening too formal")
        
        passes = len(issues) == 0
        return passes, issues
    
    def count_case_law_citations(self, text: str) -> int:
        """
        STEP 4: Count case law citations
        
        Should be 0-1 in most cases
        """
        # Look for case law patterns: "R v. X", "X v. Y (year)", etc.
        case_patterns = [
            r"\bR\s+v\.?\s+\w+",
            r"\w+\s+v\.?\s+\w+\s+\(\d{4}\)",
            r"\[20\d{2}\]\s+SCC\s+\d+",
            r"\d+\s+S\.?C\.?R\.?\s+\d+"
        ]
        
        total = 0
        for pattern in case_patterns:
            matches = re.findall(pattern, text)
            total += len(matches)
        
        return total
    
    async def verify_and_rewrite(self, draft: str, question: str) -> Dict[str, any]:
        """
        Complete verification and rewriting if needed
        
        Returns:
        {
            "passes": bool,
            "violations": [...],
            "final_answer": str,
            "rewrite_required": bool
        }
        """
        # STEP 1: Hard fail check
        hard_fails = self.detect_hard_fails(draft)
        
        # STEP 2: Thinking check
        is_authority_aware = self.check_authority_awareness(draft)
        is_coherent = self.check_coherent_narrative(draft)
        
        # STEP 3: Humanity check
        is_human, humanity_issues = self.check_humanity(draft)
        
        # STEP 4: Case law check
        case_count = self.count_case_law_citations(draft)
        
        # Determine if rewrite needed
        rewrite_needed = (
            len(hard_fails) > 0 or
            not is_authority_aware or
            not is_coherent or
            not is_human or
            case_count > 2
        )
        
        violations = []
        if hard_fails:
            violations.extend([f"HARD FAIL: {v['pattern']}" for v in hard_fails])
        if not is_authority_aware:
            violations.append("Missing authority-aware thinking")
        if not is_coherent:
            violations.append("Not coherent narrative (too many sections)")
        if not is_human:
            violations.extend([f"Humanity issue: {issue}" for issue in humanity_issues])
        if case_count > 2:
            violations.append(f"Too many case citations ({case_count})")
        
        if rewrite_needed:
            logger.warning(f"110% Verifier: Answer FAILED quality gate. Violations: {violations}")
            logger.info("Forcing rewrite...")
            
            # Use verifier prompt to rewrite
            messages = [
                {'role': 'system', 'content': VERIFIER_110_PROMPT},
                {'role': 'user', 'content': f"""Original Question:
{question}

Drafted Answer (FAILED quality check):
{draft}

Violations detected:
{chr(10).join(violations)}

REWRITE this answer to 110% standard. Remember:
- No banned patterns
- Authority-aware thinking
- Coherent narrative
- Sounds human
- Minimal/zero case law
- Direct, calming opening
- Natural paragraphs
- Practical next steps"""}
            ]
            
            rewritten = await self.llm.chat_completion(
                messages=messages,
                temperature=0.25,
                max_tokens=3000
            )
            
            logger.info(f"Answer rewritten. New length: {len(rewritten)} chars")
            
            return {
                "passes": False,
                "violations": violations,
                "final_answer": rewritten,
                "rewrite_required": True,
                "original_length": len(draft),
                "rewritten_length": len(rewritten)
            }
        else:
            logger.info("110% Verifier: Answer PASSED quality gate")
            return {
                "passes": True,
                "violations": [],
                "final_answer": draft,
                "rewrite_required": False
            }


# Global instance
_verifier_110 = None

def get_110_verifier(llm_client):
    """Get or create 110% verifier instance"""
    global _verifier_110
    if _verifier_110 is None:
        _verifier_110 = LEGID110Verifier(llm_client)
    return _verifier_110
