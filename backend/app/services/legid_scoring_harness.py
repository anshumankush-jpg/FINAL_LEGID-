"""
LEGID Scoring Harness — Self-Grading System

Scores every draft answer BEFORE sending to user.

Scoring criteria (each 1-10):
1. Authority Awareness → Does it explain what decision-makers care about?
2. Procedural Realism → Timeline not textbook?
3. Human Tone → Sounds like real paralegal?
4. Strategic Value → Common mistakes identified?
5. Safety Compliance → Refuses evasion?

Minimum passing score: 40/50 (80%)
Target score: 45/50 (90%)
Excellence score: 48+/50 (96%+)

If score < 40 → Force rewrite
If score 40-44 → Warning flag
If score 45+ → Pass through
"""
import re
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class LEGIDScoringHarness:
    """Self-grading system for LEGID answers"""
    
    def __init__(self):
        pass
    
    def score_authority_awareness(self, text: str) -> Tuple[int, str]:
        """
        Score 1-10: Does answer explain what decision-makers care about?
        
        10 = Explicitly explains authority thinking ("WSIB adjudicators weigh...")
        5 = Mentions authority but doesn't explain their thinking
        1 = No authority awareness
        """
        score = 1
        feedback = ""
        
        # Check for authority mentions
        authorities = [
            "adjudicator", "judge", "court", "WSIB", "CRA", "IRS", 
            "LTB", "tribunal", "police", "Crown", "prosecutor"
        ]
        
        authority_mentioned = any(auth.lower() in text.lower() for auth in authorities)
        
        if authority_mentioned:
            score = 5
            feedback = "Authority mentioned"
            
            # Check for thinking/behavior language
            thinking_patterns = [
                r"(adjudicator|judge|court|WSIB|CRA|LTB|tribunal).{0,50}(care about|look at|weigh|focus on|scrutinize|examine|consider)",
                r"what.{0,20}(authority|judge|WSIB|court).{0,30}(actually|typically|usually)",
                r"how.{0,20}(judge|court|WSIB|tribunal).{0,30}(thinks|decides|evaluates|treats)"
            ]
            
            for pattern in thinking_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    score = 9
                    feedback = "Authority thinking explained"
                    break
            
            # Bonus for power dynamics
            if any(phrase in text.lower() for phrase in [
                "employer benefit", "incentive", "why they", "crown's job is not"
            ]):
                score = 10
                feedback = "Power dynamics + authority thinking"
        else:
            feedback = "No authority awareness detected"
        
        return score, feedback
    
    def score_procedural_realism(self, text: str) -> Tuple[int, str]:
        """
        Score 1-10: Timeline not textbook?
        
        10 = Explains what happens next in real life
        5 = Mentions procedure but stays abstract
        1 = Pure statute explanation
        """
        score = 1
        feedback = ""
        
        # Check for procedural language
        procedural_patterns = [
            r"what (usually|typically|normally) happens (next|is|at this stage)",
            r"in practice",
            r"what (police|Crown|WSIB|tribunal|court) (usually|typically) (do|review|check)",
            r"timeline",
            r"delay (affects|creates|causes|matters)"
        ]
        
        matches = 0
        for pattern in procedural_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches += 1
        
        if matches == 0:
            score = 2
            feedback = "No procedural reality"
        elif matches == 1:
            score = 5
            feedback = "Some procedural mentions"
        elif matches >= 2:
            score = 8
            feedback = "Good procedural reality"
            
            # Bonus for specific timelines
            if any(word in text.lower() for word in ["within", "days", "months", "deadline"]):
                score = 10
                feedback = "Excellent procedural detail"
        
        return score, feedback
    
    def score_human_tone(self, text: str) -> Tuple[int, str]:
        """
        Score 1-10: Sounds like real paralegal?
        
        10 = Natural, confident, human
        5 = Functional but robotic
        1 = Template-heavy, scripted
        """
        score = 10
        penalties = []
        
        # Detect banned patterns
        banned = [
            "Quick Take", "What I understood", "Your Options",
            "Option A", "Option B", "Pros:", "Cons:", "Risk Level"
        ]
        
        for pattern in banned:
            if pattern in text:
                score -= 3
                penalties.append(f"Template: '{pattern}'")
        
        # Detect hedging language
        hedging = [
            "you may want to consider",
            "it might be helpful to",
            "generally speaking"
        ]
        
        hedging_count = sum(1 for phrase in hedging if phrase in text.lower())
        if hedging_count > 2:
            score -= 2
            penalties.append("Excessive hedging")
        
        # Detect opening questions
        if text[:100].lower().count("?") > 1:
            score -= 2
            penalties.append("Opens with questions")
        
        # Check for robotic symmetry
        lines = text.split('\n')
        section_headers = [line for line in lines if line.isupper() and len(line) > 5]
        if len(section_headers) > 3:
            score -= 1
            penalties.append("Too many section headers")
        
        score = max(1, score)
        feedback = "Human tone" if score >= 7 else f"Issues: {', '.join(penalties)}"
        
        return score, feedback
    
    def score_strategic_value(self, text: str) -> Tuple[int, str]:
        """
        Score 1-10: Common mistakes identified?
        
        10 = Specific failure modes + strategic guidance
        5 = Generic advice
        1 = No strategic value
        """
        score = 1
        feedback = ""
        
        # Check for mistake identification
        mistake_patterns = [
            r"(most common|common) mistake",
            r"what (people|workers|employers) (usually|often) get wrong",
            r"where (cases|claims) (fail|collapse|weaken)",
            r"second mistake",
            r"what not to (do|say)"
        ]
        
        mistake_mentions = sum(1 for pattern in mistake_patterns if re.search(pattern, text, re.IGNORECASE))
        
        if mistake_mentions == 0:
            score = 3
            feedback = "No failure modes identified"
        elif mistake_mentions == 1:
            score = 6
            feedback = "One mistake identified"
        elif mistake_mentions >= 2:
            score = 9
            feedback = "Multiple failure modes identified"
        
        # Bonus for evidence weighting
        if re.search(r"(evidence|documentation).{0,50}(matters more|carries weight|weighed|trusted)", text, re.IGNORECASE):
            score = min(10, score + 1)
            feedback += " + evidence weighting"
        
        return score, feedback
    
    def score_safety_compliance(self, text: str) -> Tuple[int, str]:
        """
        Score 1-10: Refuses evasion? Re-anchors to lawful?
        
        10 = Explicitly refuses evasion, guides to lawful
        7 = Neutral (no evasion issues)
        1 = Helps evade law
        """
        score = 7  # Default neutral
        feedback = "No safety issues"
        
        # Check for evasion language
        evasion_patterns = [
            r"how to (avoid|get out of|evade)",
            r"don't tell (police|insurance|employer|CRA)",
            r"hide",
            r"destroy (evidence|records)"
        ]
        
        for pattern in evasion_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score = 1
                feedback = "CRITICAL: Contains evasion guidance"
                return score, feedback
        
        # Check for safety anchoring
        safety_patterns = [
            r"cannot legally (help|advise|assist) (with|in) (evading|avoiding)",
            r"insurance fraud",
            r"must disclose",
            r"legal obligation to"
        ]
        
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in safety_patterns):
            score = 10
            feedback = "Excellent: Refuses evasion, explains legal obligations"
        
        return score, feedback
    
    def grade_answer(self, text: str, question: str = "") -> Dict:
        """
        Complete grading of answer
        
        Returns:
        {
            "total_score": int (1-50),
            "percentage": float (0-100),
            "grade": "A|B|C|D|F",
            "passes_threshold": bool,
            "scores": {...},
            "feedback": [...],
            "recommendation": "pass|warning|rewrite"
        }
        """
        # Score each dimension
        authority_score, authority_feedback = self.score_authority_awareness(text)
        procedural_score, procedural_feedback = self.score_procedural_realism(text)
        human_score, human_feedback = self.score_human_tone(text)
        strategic_score, strategic_feedback = self.score_strategic_value(text)
        safety_score, safety_feedback = self.score_safety_compliance(text)
        
        total = authority_score + procedural_score + human_score + strategic_score + safety_score
        percentage = (total / 50) * 100
        
        # Determine grade
        if percentage >= 96:
            grade = "A+"
        elif percentage >= 90:
            grade = "A"
        elif percentage >= 80:
            grade = "B"
        elif percentage >= 70:
            grade = "C"
        else:
            grade = "F"
        
        # Determine recommendation
        if total < 40:
            recommendation = "rewrite"
        elif total < 45:
            recommendation = "warning"
        else:
            recommendation = "pass"
        
        result = {
            "total_score": total,
            "max_score": 50,
            "percentage": round(percentage, 1),
            "grade": grade,
            "passes_threshold": total >= 40,
            "scores": {
                "authority_awareness": {"score": authority_score, "max": 10, "feedback": authority_feedback},
                "procedural_realism": {"score": procedural_score, "max": 10, "feedback": procedural_feedback},
                "human_tone": {"score": human_score, "max": 10, "feedback": human_feedback},
                "strategic_value": {"score": strategic_score, "max": 10, "feedback": strategic_feedback},
                "safety_compliance": {"score": safety_score, "max": 10, "feedback": safety_feedback}
            },
            "feedback": [
                f"Authority: {authority_feedback}",
                f"Procedural: {procedural_feedback}",
                f"Human: {human_feedback}",
                f"Strategic: {strategic_feedback}",
                f"Safety: {safety_feedback}"
            ],
            "recommendation": recommendation
        }
        
        logger.info(f"Scoring complete: {total}/50 ({percentage}%) - Grade: {grade} - Recommendation: {recommendation}")
        
        return result


# Global instance
_scoring_harness = None

def get_scoring_harness():
    """Get or create scoring harness instance"""
    global _scoring_harness
    if _scoring_harness is None:
        _scoring_harness = LEGIDScoringHarness()
    return _scoring_harness
