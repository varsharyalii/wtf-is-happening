"""
Query Preprocessor for Conversation-Aware RAG

Detects follow-up questions and enhances them with conversation context.
"""

import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class ProcessedQuery:
    """Result of query preprocessing."""
    original_query: str
    enhanced_query: str
    is_follow_up: bool
    suggested_guest_filter: Optional[str]
    detected_guest_mention: Optional[str]
    confidence: float  # 0.0 to 1.0


class QueryPreprocessor:
    """
    Preprocesses queries to detect follow-ups and enhance with context.
    
    Handles:
    - Follow-up question detection
    - Guest name extraction
    - Query enhancement with conversation context
    - Soft filtering suggestions
    """
    
    # Patterns that indicate follow-up questions
    FOLLOW_UP_PATTERNS = [
        r'\b(he|she|they|his|her|their)\b',  # Pronouns
        r'^(what about|how about|and|also|tell me more)',  # Follow-up phrases
        r'^(what does|what did|how does|how did)\s+\w+\s+(think|say|mention)',  # "what does X think/say"
    ]
    
    # Common guest name patterns in the WTF podcast
    GUEST_INDICATORS = [
        r'sam altman',
        r'vinod khosla',
        r'bill gates',
        r'nikhil kamath',
        r'dara khosrowshahi',
        r'nikesh arora',
    ]
    
    def __init__(self):
        """Initialize query preprocessor."""
        self.follow_up_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.FOLLOW_UP_PATTERNS]
        self.guest_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.GUEST_INDICATORS]
    
    def preprocess(
        self,
        query: str,
        conversation_context: Optional[Dict[str, Any]] = None,
    ) -> ProcessedQuery:
        """
        Preprocess a query with conversation context.
        
        Args:
            query: User's question
            conversation_context: Current conversation context (from ConversationMemory)
            
        Returns:
            ProcessedQuery with enhanced query and suggestions
        """
        query = query.strip()
        
        # Detect if this is a follow-up question
        is_follow_up = self._is_follow_up_question(query)
        
        # Extract any explicitly mentioned guest
        detected_guest = self._extract_guest_name(query)
        
        # Determine if we should suggest guest filtering
        suggested_guest = None
        confidence = 0.5
        
        if conversation_context and conversation_context.get("has_context"):
            active_guests = conversation_context.get("active_guests", [])
            recent_topics = conversation_context.get("recent_topics", [])
            
            # If user mentions a specific guest, use that
            if detected_guest:
                suggested_guest = detected_guest
                confidence = 0.9
            
            # If it's a follow-up without a specific guest mention, suggest the active guest
            elif is_follow_up and active_guests:
                suggested_guest = active_guests[0]
                confidence = 0.7
            
            # Enhance the query with context
            enhanced_query = self._enhance_query(query, active_guests, recent_topics, detected_guest)
        else:
            # No context available
            enhanced_query = query
            if detected_guest:
                suggested_guest = detected_guest
                confidence = 0.9
        
        return ProcessedQuery(
            original_query=query,
            enhanced_query=enhanced_query,
            is_follow_up=is_follow_up,
            suggested_guest_filter=suggested_guest,
            detected_guest_mention=detected_guest,
            confidence=confidence,
        )
    
    def _is_follow_up_question(self, query: str) -> bool:
        """
        Detect if a query is a follow-up question.
        
        Args:
            query: User's question
            
        Returns:
            True if likely a follow-up
        """
        query_lower = query.lower()
        
        # Check for follow-up patterns
        for pattern in self.follow_up_regex:
            if pattern.search(query_lower):
                return True
        
        # Short queries without context are likely follow-ups
        if len(query.split()) <= 5 and not any(
            query_lower.startswith(prefix) for prefix in ["who", "what is", "explain", "tell me about"]
        ):
            return True
        
        return False
    
    def _extract_guest_name(self, query: str) -> Optional[str]:
        """
        Extract guest name from query if explicitly mentioned.
        
        Args:
            query: User's question
            
        Returns:
            Guest name or None
        """
        query_lower = query.lower()
        
        for pattern in self.guest_regex:
            match = pattern.search(query_lower)
            if match:
                # Return the matched name with proper capitalization
                return match.group(0).title()
        
        return None
    
    def _enhance_query(
        self,
        query: str,
        active_guests: List[str],
        recent_topics: List[str],
        detected_guest: Optional[str],
    ) -> str:
        """
        Enhance query with conversation context.
        
        Args:
            query: Original query
            active_guests: List of recently discussed guests
            recent_topics: List of recent topics
            detected_guest: Explicitly mentioned guest name
            
        Returns:
            Enhanced query string
        """
        # If query is very short or uses pronouns, add context
        query_lower = query.lower()
        
        # Check if query references "he", "she", "they" without a name
        has_pronoun = any(pronoun in query_lower for pronoun in ["he ", "she ", "they ", "his ", "her ", "their "])
        
        if has_pronoun and active_guests:
            # Replace pronoun context with guest name
            enhanced = f"{query} (in the context of {active_guests[0]})"
            return enhanced
        
        # Check for vague follow-ups like "what does X think" without topic
        if re.search(r'what (does|did) \w+ (think|say|mention)$', query_lower):
            if recent_topics:
                enhanced = f"{query} about {recent_topics[0]}"
                return enhanced
        
        # Otherwise, return original query
        return query


if __name__ == "__main__":
    # Test the preprocessor
    print("🧪 Testing Query Preprocessor\n")
    
    preprocessor = QueryPreprocessor()
    
    # Test cases
    test_cases = [
        {
            "query": "how can i secure my job as an engineer in the AI future?",
            "context": None,
        },
        {
            "query": "what does sam altman think",
            "context": {
                "active_guests": ["Vinod Khosla"],
                "recent_topics": ["securing jobs in AI future", "flexibility"],
                "has_context": True,
            },
        },
        {
            "query": "what about bill gates?",
            "context": {
                "active_guests": ["Vinod Khosla"],
                "recent_topics": ["AI impact"],
                "has_context": True,
            },
        },
        {
            "query": "tell me about autonomous vehicles",
            "context": None,
        },
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}: {test['query']}")
        print("="*80)
        
        result = preprocessor.preprocess(test["query"], test["context"])
        
        print(f"Original: {result.original_query}")
        print(f"Enhanced: {result.enhanced_query}")
        print(f"Is Follow-up: {result.is_follow_up}")
        print(f"Suggested Guest Filter: {result.suggested_guest_filter}")
        print(f"Detected Guest: {result.detected_guest_mention}")
        print(f"Confidence: {result.confidence:.2f}")
    
    print("\n" + "="*80)
    print("✓ Query preprocessor test complete")

