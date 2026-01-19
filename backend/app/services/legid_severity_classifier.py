"""
LEGID Severity Classifier

Automatically detects severity level of legal question:
- LOW: Informational, low risk
- MEDIUM: Real exposure but not urgent
- HIGH: Serious legal exposure
- CRITICAL: Immediate legal danger

This enables adaptive behavior: different tone/depth based on situation.
"""
import re
import logging
from enum import Enum
from typing import Tuple, List

logger = logging.getLogger(__name__)


class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# Detection patterns
CRITICAL_PATTERNS = [
    r"\b(crashed|hit|killed|died|death|fatality)\b",
    r"\b(serious injury|severe injury|hospitalized)\b",
    r"\b(overdose|suicide attempt)\b",
    r"\barrested\b",
    r"\b(shooting|stabbing|assault causing bodily harm)\b",
    r"\b(streetcar|pedestrian struck|hit and run)\b",
    r"\bdeportation order\b",
    r"\bwarrant\b"
]

HIGH_PATTERNS = [
    r"\b(DUI|impaired|drunk driving|breathalyzer)\b",
    r"\b(criminal charge|charged with|arraignment)\b",
    r"\b(WSIB|workers.?comp|workplace injury)\b",
    r"\b(eviction notice|Form N4|losing home)\b",
    r"\b(fired|terminated|wrongful dismissal)\b",
    r"\b(immigration denied|visa refused)\b",
    r"\b(assault|theft|fraud) charge\b"
]

MEDIUM_PATTERNS = [
    r"\b(landlord|tenant|rent dispute|lease)\b",
    r"\b(employment issue|workplace dispute)\b",
    r"\b(tax issue|CRA|IRS audit)\b",
    r"\b(small claims|civil suit)\b",
    r"\b(divorce|custody|support)\b"
]

LOW_PATTERNS = [
    r"\b(what is|how does|explain|definition)\b",
    r"\b(general question|just wondering|curious about)\b",
    r"\b(can you tell me about)\b"
]


class SeverityClassifier:
    """Classifies legal question severity"""
    
    def classify(self, question: str) -> Tuple[SeverityLevel, float, List[str]]:
        """
        Classify severity of legal question
        
        Returns: (severity_level, confidence, indicators)
        """
        question_lower = question.lower()
        indicators = []
        
        # Check CRITICAL first (highest priority)
        for pattern in CRITICAL_PATTERNS:
            if re.search(pattern, question_lower):
                indicators.append(f"Critical: {pattern}")
        
        if indicators:
            logger.info(f"Severity: CRITICAL - Indicators: {indicators}")
            return SeverityLevel.CRITICAL, 0.95, indicators
        
        # Check HIGH
        for pattern in HIGH_PATTERNS:
            if re.search(pattern, question_lower):
                indicators.append(f"High: {pattern}")
        
        if indicators:
            logger.info(f"Severity: HIGH - Indicators: {indicators}")
            return SeverityLevel.HIGH, 0.85, indicators
        
        # Check MEDIUM
        for pattern in MEDIUM_PATTERNS:
            if re.search(pattern, question_lower):
                indicators.append(f"Medium: {pattern}")
        
        if indicators:
            logger.info(f"Severity: MEDIUM - Indicators: {indicators}")
            return SeverityLevel.MEDIUM, 0.75, indicators
        
        # Default to LOW
        logger.info("Severity: LOW (default)")
        return SeverityLevel.LOW, 0.6, ["Default: informational"]
    
    def get_behavior_rules(self, severity: SeverityLevel) -> Dict[str, any]:
        """
        Get behavior rules for severity level
        
        Returns guidance for tone, structure, warnings
        """
        rules = {
            SeverityLevel.CRITICAL: {
                "no_questions_first": True,
                "no_templates": True,
                "no_casual_language": True,
                "tone": "firm, grounded, containment-focused",
                "opening_style": "Right now, the biggest risk is...",
                "focus": "What authorities will do NEXT, what makes things worse immediately",
                "temperature": 0.18  # Very low for crisis accuracy
            },
            SeverityLevel.HIGH: {
                "no_questions_first": True,
                "no_templates": True,
                "no_casual_language": False,
                "tone": "serious, authority-aware, risk-conscious",
                "opening_style": "At this stage, what matters most is...",
                "focus": "Risks, authority behavior, irreversible mistakes",
                "temperature": 0.20
            },
            SeverityLevel.MEDIUM: {
                "no_questions_first": False,
                "no_templates": True,
                "no_casual_language": False,
                "tone": "professional, leverage-aware",
                "opening_style": "This situation involves...",
                "focus": "Leverage, consequences, common mistakes",
                "temperature": 0.22
            },
            SeverityLevel.LOW: {
                "no_questions_first": False,
                "no_templates": False,
                "no_casual_language": False,
                "tone": "calm, explanatory, educational",
                "opening_style": "Here's how this generally works...",
                "focus": "Process explanation, basic understanding",
                "temperature": 0.25
            }
        }
        
        return rules.get(severity, rules[SeverityLevel.MEDIUM])


# Global instance
_severity_classifier = None

def get_severity_classifier() -> SeverityClassifier:
    """Get or create severity classifier instance"""
    global _severity_classifier
    if _severity_classifier is None:
        _severity_classifier = SeverityClassifier()
    return _severity_classifier
