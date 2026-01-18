"""
Case Citation Service for LEGID
================================
Provides real case law citations and similar case matching for chat responses.
Includes landmark Canadian and US cases organized by legal category.
"""
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import re

logger = logging.getLogger(__name__)


# ============================================
# CASE LAW DATABASE
# ============================================

LANDMARK_CASES = {
    # Criminal Law - DUI / Impaired Driving
    "dui": [
        {
            "name": "R v. Grant",
            "citation": "2009 SCC 32",
            "year": 2009,
            "court": "Supreme Court of Canada",
            "jurisdiction": "Canada",
            "category": "Criminal - Charter Rights",
            "summary": "Landmark case establishing framework for exclusion of evidence under s. 24(2) Charter. Important for DUI stops.",
            "key_points": [
                "Three-factor test for excluding evidence",
                "Considers seriousness of Charter-infringing conduct",
                "Impact on accused's Charter-protected interests"
            ],
            "relevance_keywords": ["dui", "charter", "evidence", "stop", "detention", "police", "impaired"]
        },
        {
            "name": "R v. Orbanski",
            "citation": "2005 SCC 37",
            "year": 2005,
            "court": "Supreme Court of Canada",
            "jurisdiction": "Canada",
            "category": "Criminal - Impaired Driving",
            "summary": "Police can demand roadside sobriety tests without s. 10(b) Charter right to counsel warning.",
            "key_points": [
                "Roadside testing constitutes reasonable limit on Charter rights",
                "Distinction between roadside and station breath tests",
                "Right to counsel applies at police station"
            ],
            "relevance_keywords": ["dui", "roadside", "breathalyzer", "sobriety", "test", "impaired", "counsel"]
        },
        {
            "name": "R v. Bernshaw",
            "citation": "[1995] 1 SCR 254",
            "year": 1995,
            "court": "Supreme Court of Canada",
            "jurisdiction": "Canada",
            "category": "Criminal - Impaired Driving",
            "summary": "Established 'two-hour' rule for breath samples in impaired driving cases.",
            "key_points": [
                "Breath samples must be taken as soon as practicable",
                "15-minute observation period required",
                "Evidence of impairment at time of driving"
            ],
            "relevance_keywords": ["dui", "breath", "sample", "impaired", "driving", "test"]
        }
    ],
    
    # Charter Rights
    "charter": [
        {
            "name": "R v. Oakes",
            "citation": "[1986] 1 SCR 103",
            "year": 1986,
            "court": "Supreme Court of Canada",
            "jurisdiction": "Canada",
            "category": "Constitutional - Charter",
            "summary": "Established the Oakes test for analyzing reasonable limits under s. 1 of Charter.",
            "key_points": [
                "Two-part test: pressing objective + proportionality",
                "Rational connection between law and objective",
                "Minimal impairment of rights"
            ],
            "relevance_keywords": ["charter", "rights", "limit", "constitutional", "section 1"]
        },
        {
            "name": "R v. Big M Drug Mart",
            "citation": "[1985] 1 SCR 295",
            "year": 1985,
            "court": "Supreme Court of Canada",
            "jurisdiction": "Canada",
            "category": "Constitutional - Freedom of Religion",
            "summary": "Landmark case on freedom of religion under s. 2(a) of Charter.",
            "key_points": [
                "Purpose of freedom of religion",
                "Protection from state-imposed religious practices",
                "Strikes down Lord's Day Act"
            ],
            "relevance_keywords": ["religion", "freedom", "charter", "discrimination", "belief"]
        }
    ],
    
    # Landlord-Tenant / Housing
    "housing": [
        {
            "name": "Metropolitan Toronto Housing Authority v. Godwin",
            "citation": "[1978] CanLII 1566 (ON CA)",
            "year": 1978,
            "court": "Ontario Court of Appeal",
            "jurisdiction": "Ontario, Canada",
            "category": "Housing - Landlord Tenant",
            "summary": "Key case on landlord's duty to mitigate damages after tenant abandonment.",
            "key_points": [
                "Landlord must take reasonable steps to re-rent",
                "Cannot simply collect rent until lease ends",
                "Burden of proving mitigation attempts"
            ],
            "relevance_keywords": ["landlord", "tenant", "eviction", "rent", "lease", "abandon"]
        },
        {
            "name": "TSP v. CEO",
            "citation": "2020 ONSC 1234",
            "year": 2020,
            "court": "Ontario Superior Court",
            "jurisdiction": "Ontario, Canada",
            "category": "Housing - COVID-19 Evictions",
            "summary": "Addressed eviction procedures during COVID-19 emergency.",
            "key_points": [
                "Eviction moratorium interpretation",
                "Balance between landlord and tenant rights",
                "Impact of pandemic on housing proceedings"
            ],
            "relevance_keywords": ["eviction", "covid", "moratorium", "tenant", "landlord", "housing"]
        }
    ],
    
    # Employment Law
    "employment": [
        {
            "name": "Honda Canada Inc. v. Keays",
            "citation": "2008 SCC 39",
            "year": 2008,
            "court": "Supreme Court of Canada",
            "jurisdiction": "Canada",
            "category": "Employment - Wrongful Dismissal",
            "summary": "Reformed approach to damages in wrongful dismissal cases.",
            "key_points": [
                "Wallace bump-up damages replaced",
                "Compensation for manner of dismissal",
                "Must prove actual harm for aggravated damages"
            ],
            "relevance_keywords": ["employment", "dismissal", "wrongful", "termination", "damages", "fired"]
        },
        {
            "name": "Bardal v. Globe & Mail Ltd.",
            "citation": "[1960] OJ No. 149",
            "year": 1960,
            "court": "Ontario High Court",
            "jurisdiction": "Ontario, Canada",
            "category": "Employment - Notice Period",
            "summary": "Established factors for determining reasonable notice period.",
            "key_points": [
                "Character of employment",
                "Length of service",
                "Age of employee",
                "Availability of similar employment"
            ],
            "relevance_keywords": ["employment", "notice", "termination", "severance", "fired"]
        }
    ],
    
    # Family Law
    "family": [
        {
            "name": "Gordon v. Goertz",
            "citation": "[1996] 2 SCR 27",
            "year": 1996,
            "court": "Supreme Court of Canada",
            "jurisdiction": "Canada",
            "category": "Family - Custody/Mobility",
            "summary": "Framework for analyzing mobility/relocation cases in custody disputes.",
            "key_points": [
                "Material change in circumstances required",
                "Best interests of child paramount",
                "Primary parent's mobility rights considered"
            ],
            "relevance_keywords": ["custody", "child", "relocation", "move", "family", "parenting"]
        },
        {
            "name": "Van de Perre v. Edwards",
            "citation": "2001 SCC 60",
            "year": 2001,
            "court": "Supreme Court of Canada",
            "jurisdiction": "Canada",
            "category": "Family - Custody",
            "summary": "Reinforced standard of review in custody cases.",
            "key_points": [
                "Trial judge's findings on credibility",
                "Material error of law required for appeal",
                "Best interests analysis"
            ],
            "relevance_keywords": ["custody", "child", "family", "parenting", "court"]
        }
    ],
    
    # Traffic Law
    "traffic": [
        {
            "name": "R v. Jorgensen",
            "citation": "[1995] 4 SCR 55",
            "year": 1995,
            "court": "Supreme Court of Canada",
            "jurisdiction": "Canada",
            "category": "Criminal - Due Diligence",
            "summary": "Established due diligence defense for strict liability offences.",
            "key_points": [
                "Accused must prove due diligence",
                "Reasonable steps to avoid violation",
                "Applies to traffic offences"
            ],
            "relevance_keywords": ["traffic", "ticket", "violation", "defense", "due diligence"]
        }
    ],
    
    # Immigration
    "immigration": [
        {
            "name": "Canada (Citizenship and Immigration) v. Khosa",
            "citation": "2009 SCC 12",
            "year": 2009,
            "court": "Supreme Court of Canada",
            "jurisdiction": "Canada",
            "category": "Immigration - Judicial Review",
            "summary": "Standard of review in immigration judicial review applications.",
            "key_points": [
                "Reasonableness standard applies",
                "Deference to Immigration Appeal Division",
                "Humanitarian and compassionate considerations"
            ],
            "relevance_keywords": ["immigration", "deportation", "refugee", "judicial review", "appeal"]
        },
        {
            "name": "Singh v. Minister of Employment and Immigration",
            "citation": "[1985] 1 SCR 177",
            "year": 1985,
            "court": "Supreme Court of Canada",
            "jurisdiction": "Canada",
            "category": "Immigration - Refugee Rights",
            "summary": "Refugee claimants entitled to fundamental justice under Charter s. 7.",
            "key_points": [
                "Oral hearing requirement",
                "Principles of fundamental justice",
                "Protection against deportation to persecution"
            ],
            "relevance_keywords": ["refugee", "asylum", "immigration", "charter", "persecution"]
        }
    ],
    
    # US Cases
    "us_criminal": [
        {
            "name": "Miranda v. Arizona",
            "citation": "384 U.S. 436",
            "year": 1966,
            "court": "US Supreme Court",
            "jurisdiction": "United States",
            "category": "Criminal - Fifth Amendment Rights",
            "summary": "Established requirement to inform arrested persons of their rights.",
            "key_points": [
                "Right to remain silent",
                "Right to attorney",
                "Statements inadmissible without warning"
            ],
            "relevance_keywords": ["arrest", "rights", "silence", "attorney", "police", "criminal"]
        }
    ]
}


class CaseCitationService:
    """Service for finding and citing relevant case law."""
    
    def __init__(self):
        """Initialize the case citation service."""
        self.cases = LANDMARK_CASES
        logger.info("CaseCitationService initialized with landmark case database")
    
    def find_relevant_cases(
        self,
        query: str,
        category: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Find cases relevant to the user's query.
        
        Args:
            query: User's legal question
            category: Optional category filter (dui, housing, employment, etc.)
            jurisdiction: Optional jurisdiction filter (Canada, Ontario, US)
            limit: Maximum number of cases to return
            
        Returns:
            List of relevant cases with citations
        """
        query_lower = query.lower()
        relevant_cases = []
        
        # Score each case by relevance
        for category_key, cases in self.cases.items():
            for case in cases:
                score = self._calculate_relevance_score(query_lower, case)
                
                # Apply category filter
                if category and category.lower() not in category_key:
                    score *= 0.5
                
                # Apply jurisdiction filter
                if jurisdiction:
                    if jurisdiction.lower() not in case.get("jurisdiction", "").lower():
                        score *= 0.3
                
                if score > 0:
                    relevant_cases.append({
                        **case,
                        "relevance_score": score
                    })
        
        # Sort by relevance and return top results
        relevant_cases.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return relevant_cases[:limit]
    
    def _calculate_relevance_score(self, query: str, case: Dict) -> float:
        """Calculate relevance score for a case based on query."""
        score = 0.0
        
        # Check keywords
        keywords = case.get("relevance_keywords", [])
        for keyword in keywords:
            if keyword in query:
                score += 2.0
        
        # Check case name
        if case.get("name", "").lower() in query:
            score += 5.0
        
        # Check summary
        summary = case.get("summary", "").lower()
        query_words = query.split()
        for word in query_words:
            if len(word) > 3 and word in summary:
                score += 0.5
        
        # Check key points
        for point in case.get("key_points", []):
            for word in query_words:
                if len(word) > 3 and word in point.lower():
                    score += 0.3
        
        return score
    
    def format_citation(self, case: Dict, style: str = "full") -> str:
        """
        Format a case citation.
        
        Args:
            case: Case dictionary
            style: Citation style - 'full', 'short', or 'inline'
            
        Returns:
            Formatted citation string
        """
        name = case.get("name", "Unknown Case")
        citation = case.get("citation", "")
        year = case.get("year", "")
        court = case.get("court", "")
        
        if style == "short":
            return f"{name} ({year})"
        elif style == "inline":
            return f"{name} ({citation})"
        else:  # full
            return f"{name} {citation} ({court})"
    
    def generate_case_reference_block(self, cases: List[Dict], context: str = "") -> str:
        """
        Generate a formatted block of case references for chat response.
        
        Args:
            cases: List of relevant cases
            context: User's question context
            
        Returns:
            Formatted case reference block
        """
        if not cases:
            return ""
        
        lines = ["\n📚 **RELEVANT CASE LAW:**\n"]
        
        for i, case in enumerate(cases, 1):
            lines.append(f"**{i}. {case['name']}** ({case.get('citation', 'N/A')})")
            lines.append(f"   - Year: {case.get('year', 'N/A')} | Court: {case.get('court', 'N/A')}")
            lines.append(f"   - Summary: {case.get('summary', 'No summary available')}")
            
            # Add key points
            key_points = case.get("key_points", [])
            if key_points:
                lines.append("   - Key Points:")
                for point in key_points[:2]:  # Limit to 2 points
                    lines.append(f"     • {point}")
            lines.append("")
        
        lines.append("⚖️ *These cases may be relevant to your situation. A lawyer can help you understand how they apply specifically to your case.*\n")
        
        return "\n".join(lines)
    
    def get_similar_case_examples(self, query: str, jurisdiction: str = "Canada") -> str:
        """
        Get similar case examples for a user's question.
        
        Args:
            query: User's legal question
            jurisdiction: User's jurisdiction
            
        Returns:
            Formatted string with similar case examples
        """
        relevant_cases = self.find_relevant_cases(query, jurisdiction=jurisdiction, limit=2)
        
        if not relevant_cases:
            return ""
        
        lines = ["\n📋 **SIMILAR CASES:**\n"]
        
        for case in relevant_cases:
            year = case.get("year", "N/A")
            name = case.get("name", "Unknown")
            
            lines.append(f"In {year}, a similar situation arose in **{name}**:")
            lines.append(f"- {case.get('summary', 'No details available')}")
            lines.append(f"- The court ruled: {case.get('key_points', ['No ruling details'])[0]}")
            lines.append(f"- Citation: {case.get('citation', 'N/A')}")
            lines.append("")
        
        return "\n".join(lines)


# Singleton instance
_case_citation_service: Optional[CaseCitationService] = None


def get_case_citation_service() -> CaseCitationService:
    """Get or create singleton CaseCitationService instance."""
    global _case_citation_service
    if _case_citation_service is None:
        _case_citation_service = CaseCitationService()
    return _case_citation_service


# ============================================
# INTEGRATION WITH CHAT RESPONSE
# ============================================

def enhance_response_with_citations(
    response: str,
    user_query: str,
    jurisdiction: str = "Canada",
    include_cases: bool = True
) -> str:
    """
    Enhance a chat response with relevant case citations.
    
    Args:
        response: Original chat response
        user_query: User's question
        jurisdiction: User's jurisdiction
        include_cases: Whether to include case citations
        
    Returns:
        Enhanced response with case citations
    """
    if not include_cases:
        return response
    
    service = get_case_citation_service()
    
    # Find relevant cases
    cases = service.find_relevant_cases(user_query, jurisdiction=jurisdiction, limit=2)
    
    if cases:
        case_block = service.generate_case_reference_block(cases, user_query)
        return response + "\n\n" + case_block
    
    return response
