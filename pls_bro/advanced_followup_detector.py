"""
Advanced Follow-up Detection System
==================================

This module provides enhanced follow-up detection capabilities with intent classification,
confidence scoring, and context-aware analysis.

Key Features:
- Intent-based classification (6 categories)
- Confidence scoring for detection accuracy
- Context metadata extraction
- Backward compatibility with existing system
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class FollowupIntent(Enum):
    """Classification of follow-up question intents"""
    CLARIFICATION = "clarification"       # "What does this mean?"
    DRILL_DOWN = "drill_down"            # "Show me more details"
    COMPARISON = "comparison"            # "How does this compare?"
    VISUALIZATION = "visualization"      # "Make a chart"
    ANALYSIS = "analysis"               # "What's the trend?"
    MODIFICATION = "modification"       # "Change the filter"


@dataclass
class FollowupResult:
    """Result of follow-up detection analysis"""
    is_followup: bool
    confidence: float
    intent: Optional[FollowupIntent]
    detected_patterns: List[str]
    context_references: List[str]
    suggested_actions: List[str]


class AdvancedFollowupDetector:
    """Enhanced follow-up detection with intent classification"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.intent_keywords = self._initialize_intent_keywords()
        
    def _initialize_patterns(self) -> Dict[str, List[str]]:
        """Initialize detection patterns by category"""
        return {
            # Basic follow-up indicators
            'pronouns': [
                r'\b(this|that|these|those|it|they|them)\b',
                r'\b(the (above|previous|last|first))\b',
                r'\b(such|similar)\b'
            ],
            
            # Question patterns
            'questions': [
                r'\b(what about|how about|what if)\b',
                r'\b(can you|could you|would you)\b',
                r'\b(why|how|when|where|which)\b',
                r'^(show|tell|explain|describe|list)'
            ],
            
            # Continuation patterns
            'continuations': [
                r'\b(also|additionally|furthermore|moreover)\b',
                r'\b(and|but|however|although)\b',
                r'\b(next|then|after that|following)\b'
            ],
            
            # Modification patterns
            'modifications': [
                r'\b(change|modify|update|alter|adjust)\b',
                r'\b(instead|rather|different|another)\b',
                r'\b(add|remove|include|exclude)\b'
            ],
            
            # Comparison patterns
            'comparisons': [
                r'\b(compare|contrast|versus|vs|against)\b',
                r'\b(difference|similar|same|different)\b',
                r'\b(better|worse|higher|lower|more|less)\b'
            ],
            
            # Context references
            'context_refs': [
                r'\b(from (the|that|this) (result|data|table|chart))\b',
                r'\b(in (the|that|this) (query|search|analysis))\b',
                r'\b(based on (the|that|this))\b'
            ]
        }
    
    def _initialize_intent_keywords(self) -> Dict[FollowupIntent, List[str]]:
        """Initialize intent classification keywords"""
        return {
            FollowupIntent.CLARIFICATION: [
                'what does', 'what is', 'explain', 'meaning', 'definition',
                'clarify', 'understand', 'confused', 'unclear'
            ],
            
            FollowupIntent.DRILL_DOWN: [
                'more details', 'show me', 'breakdown', 'expand', 'specific',
                'details about', 'information on', 'tell me about', 'deep dive'
            ],
            
            FollowupIntent.COMPARISON: [
                'compare', 'contrast', 'versus', 'vs', 'difference', 'similar',
                'same', 'different', 'against', 'relative to', 'compared to'
            ],
            
            FollowupIntent.VISUALIZATION: [
                'chart', 'graph', 'plot', 'visualize', 'show', 'display',
                'pie chart', 'bar chart', 'line chart', 'histogram', 'map'
            ],
            
            FollowupIntent.ANALYSIS: [
                'trend', 'pattern', 'correlation', 'analyze', 'analysis',
                'insight', 'finding', 'conclusion', 'interpretation', 'summary'
            ],
            
            FollowupIntent.MODIFICATION: [
                'change', 'modify', 'update', 'alter', 'adjust', 'filter',
                'sort', 'group by', 'limit', 'where', 'add', 'remove'
            ]
        }
    
    def detect_followup(self, 
                       current_message: str, 
                       conversation_history: List[Dict],
                       last_response: str = "") -> FollowupResult:
        """
        Detect if current message is a follow-up with enhanced analysis
        
        Args:
            current_message: The user's current message
            conversation_history: Previous conversation exchanges
            last_response: The assistant's last response
            
        Returns:
            FollowupResult with detailed analysis
        """
        message_lower = current_message.lower()
        
        # Pattern detection
        detected_patterns = self._detect_patterns(message_lower)
        
        # Intent classification
        intent, intent_confidence = self._classify_intent(message_lower)
        
        # Context reference detection
        context_references = self._detect_context_references(message_lower, last_response)
        
        # Calculate overall confidence
        base_confidence = len(detected_patterns) * 0.15
        intent_boost = intent_confidence * 0.4
        context_boost = len(context_references) * 0.2
        
        # Conversation continuity check
        continuity_score = self._check_conversation_continuity(
            current_message, conversation_history
        )
        
        total_confidence = min(1.0, base_confidence + intent_boost + context_boost + continuity_score)
        
        # Decision threshold
        is_followup = total_confidence >= 0.3
        
        # Generate suggestions
        suggested_actions = self._generate_suggestions(intent, detected_patterns, context_references)
        
        return FollowupResult(
            is_followup=is_followup,
            confidence=total_confidence,
            intent=intent,
            detected_patterns=detected_patterns,
            context_references=context_references,
            suggested_actions=suggested_actions
        )
    
    def _detect_patterns(self, message: str) -> List[str]:
        """Detect follow-up patterns in message"""
        detected = []
        
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    detected.append(f"{category}:{pattern}")
        
        return detected
    
    def _classify_intent(self, message: str) -> Tuple[Optional[FollowupIntent], float]:
        """Classify the intent of the follow-up question"""
        intent_scores = {}
        
        for intent, keywords in self.intent_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in message:
                    # Weight longer phrases higher
                    score += len(keyword.split()) * 0.1
            intent_scores[intent] = score
        
        if not intent_scores or max(intent_scores.values()) == 0:
            return None, 0.0
        
        best_intent = max(intent_scores.keys(), key=lambda x: intent_scores[x])
        confidence = min(1.0, intent_scores[best_intent])
        
        return best_intent, confidence
    
    def _detect_context_references(self, message: str, last_response: str) -> List[str]:
        """Detect references to previous context"""
        references = []
        
        # Check for pronoun references
        pronouns = ['it', 'this', 'that', 'these', 'those', 'they', 'them']
        for pronoun in pronouns:
            if f' {pronoun} ' in f' {message} ':
                references.append(f"pronoun:{pronoun}")
        
        # Check for specific references to last response content
        if last_response:
            # Extract key terms from last response (simple approach)
            response_words = set(last_response.lower().split())
            message_words = set(message.split())
            
            # Find common significant words (excluding common words)
            common_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
            significant_overlap = (response_words & message_words) - set(common_words)
            
            for word in significant_overlap:
                if len(word) > 3:  # Only significant words
                    references.append(f"content:{word}")
        
        return references
    
    def _check_conversation_continuity(self, message: str, history: List[Dict]) -> float:
        """Check if message continues the conversation flow"""
        if not history:
            return 0.0
        
        # Simple continuity check - if message is short and contains context words
        if len(message.split()) <= 10:
            context_words = ['more', 'details', 'about', 'what', 'how', 'why', 'show', 'tell']
            score = sum(1 for word in context_words if word in message.lower()) * 0.1
            return min(0.3, score)
        
        return 0.0
    
    def _generate_suggestions(self, 
                            intent: Optional[FollowupIntent], 
                            patterns: List[str], 
                            references: List[str]) -> List[str]:
        """Generate suggested actions based on detected intent and patterns"""
        suggestions = []
        
        if intent == FollowupIntent.CLARIFICATION:
            suggestions.extend([
                "Provide detailed explanation",
                "Include relevant context",
                "Use examples for clarity"
            ])
        elif intent == FollowupIntent.DRILL_DOWN:
            suggestions.extend([
                "Show additional details",
                "Provide breakdown analysis",
                "Include related metrics"
            ])
        elif intent == FollowupIntent.VISUALIZATION:
            suggestions.extend([
                "Generate appropriate chart",
                "Consider multiple chart types",
                "Include data labels"
            ])
        elif intent == FollowupIntent.COMPARISON:
            suggestions.extend([
                "Create comparison table",
                "Highlight key differences",
                "Show relative metrics"
            ])
        elif intent == FollowupIntent.ANALYSIS:
            suggestions.extend([
                "Provide statistical analysis",
                "Identify trends and patterns",
                "Include business insights"
            ])
        elif intent == FollowupIntent.MODIFICATION:
            suggestions.extend([
                "Apply requested changes",
                "Maintain result consistency",
                "Show impact of changes"
            ])
        
        # Add pattern-based suggestions
        if any('visualization' in p for p in patterns):
            suggestions.append("Generate data visualization")
        
        if any('comparison' in p for p in patterns):
            suggestions.append("Provide comparative analysis")
        
        return list(set(suggestions))  # Remove duplicates


def create_enhanced_detector() -> AdvancedFollowupDetector:
    """Factory function to create enhanced detector"""
    return AdvancedFollowupDetector()


# Backward compatibility function
def is_enhanced_followup_question(message: str, 
                                 conversation_history: List[Dict] = None,
                                 last_response: str = "") -> bool:
    """
    Enhanced version of is_followup_question with backward compatibility
    
    This function maintains the same interface as the original but provides
    enhanced detection capabilities.
    """
    detector = create_enhanced_detector()
    result = detector.detect_followup(
        message, 
        conversation_history or [], 
        last_response
    )
    return result.is_followup


# Example usage and testing
if __name__ == "__main__":
    detector = create_enhanced_detector()
    
    # Test cases
    test_cases = [
        ("Tell me more about the top artist", "SELECT artist_name FROM artists ORDER BY sales DESC LIMIT 5"),
        ("What about the second one?", "The top artist is AC/DC with 1000 sales"),
        ("Can you make a chart of this?", "Here are the sales figures: AC/DC: 1000, Beatles: 900"),
        ("How does this compare to last year?", "Current sales data shows strong performance"),
        ("Show me the details", "Summary: Total sales increased by 15%"),
    ]
    
    print("🧪 Testing Enhanced Follow-up Detection\n")
    
    for i, (message, context) in enumerate(test_cases, 1):
        result = detector.detect_followup(message, [], context)
        
        print(f"Test {i}: '{message}'")
        print(f"  ✅ Follow-up: {result.is_followup}")
        print(f"  📊 Confidence: {result.confidence:.2f}")
        print(f"  🎯 Intent: {result.intent.value if result.intent else 'None'}")
        print(f"  🔍 Patterns: {len(result.detected_patterns)}")
        print(f"  🔗 References: {len(result.context_references)}")
        print(f"  💡 Suggestions: {result.suggested_actions[:2]}")
        print() 