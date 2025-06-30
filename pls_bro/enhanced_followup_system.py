#!/usr/bin/env python3
"""
Enhanced Follow-up System for Conversational SQL Agent
Implements Phase 1 improvements for better follow-up handling.
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class EnhancedFollowupDetector:
    """Advanced follow-up detection with intent recognition."""
    
    def __init__(self):
        self.followup_patterns = {
            # Data Exploration
            'drill_down': [
                r'\b(drill down|break down|show more|expand|dive deeper|get into)\b',
                r'\b(next \d+|more results|additional|further)\b',
                r'\b(top \d+|bottom \d+|first \d+|last \d+)\b'
            ],
            
            # Comparison & Analysis
            'comparison': [
                r'\b(compare|versus|vs|against|relative to)\b',
                r'\b(difference|gap|variation|contrast)\b',
                r'\b(how does .* compare|what about .* compared)\b'
            ],
            
            # Temporal Analysis
            'temporal': [
                r'\b(trend|over time|timeline|historical|past|previous)\b',
                r'\b(year|month|quarter|week|daily|annually)\b',
                r'\b(growth|decline|change|evolution)\b'
            ],
            
            # Visualization Requests
            'visualization': [
                r'\b(chart|graph|plot|visualize|show as)\b',
                r'\b(pie chart|bar chart|line chart|scatter plot)\b',
                r'\b(make it|change to|convert to|display as)\b'
            ],
            
            # Data Quality
            'data_quality': [
                r'\b(missing|null|empty|incomplete|outlier)\b',
                r'\b(duplicate|unique|distinct|clean)\b',
                r'\b(quality|accuracy|freshness|validity)\b'
            ],
            
            # Statistical Analysis
            'statistical': [
                r'\b(average|mean|median|mode|standard deviation)\b',
                r'\b(correlation|significant|pattern|distribution)\b',
                r'\b(anomaly|unusual|strange|unexpected)\b'
            ],
            
            # Business Context
            'business': [
                r'\b(impact|implication|meaning|significance)\b',
                r'\b(business|revenue|profit|cost|ROI)\b',
                r'\b(recommendation|action|strategy|decision)\b'
            ]
        }
    
    def detect_followup_intent(self, message: str) -> Dict[str, Any]:
        """Detect follow-up intent and classify the type."""
        message_lower = message.lower()
        
        # Check if it's a follow-up
        basic_indicators = [
            "show me", "tell me", "what about", "also", "additionally",
            "furthermore", "expand", "details", "specifically", "can you"
        ]
        
        is_followup = any(indicator in message_lower for indicator in basic_indicators)
        
        # Detect intent categories
        intents = {}
        for intent_type, patterns in self.followup_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    intents[intent_type] = True
                    break
        
        return {
            'is_followup': is_followup or bool(intents),
            'intents': list(intents.keys()),
            'confidence': len(intents) / len(self.followup_patterns),
            'primary_intent': max(intents.keys()) if intents else 'general'
        }

class EnhancedContextManager:
    """Enhanced context management with better memory and summarization."""
    
    def __init__(self, max_exchanges: int = 8, max_context_chars: int = 2000):
        self.max_exchanges = max_exchanges
        self.max_context_chars = max_context_chars
        self.conversation_history = []
        self.key_findings = []  # Store important insights
        self.visualization_history = []  # Store chart metadata
    
    def add_exchange(self, user_message: str, assistant_response: Dict[str, Any]):
        """Add an exchange with enhanced metadata."""
        
        # Extract key metrics and findings
        key_metrics = self._extract_key_metrics(assistant_response)
        visualization_info = self._extract_visualization_info(assistant_response)
        
        exchange = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "sql_query": assistant_response.get("sql_query", ""),
            "answer_full": assistant_response.get("answer", ""),
            "answer_summary": assistant_response.get("answer", "")[:300] + "...",
            "key_metrics": key_metrics,
            "has_charts": len(assistant_response.get("generated_charts", [])) > 0,
            "chart_types": [viz.get('type', 'unknown') for viz in visualization_info],
            "data_insights": assistant_response.get("visualization_insights", [])
        }
        
        self.conversation_history.append(exchange)
        
        # Store key findings for long-term memory
        if key_metrics:
            self.key_findings.extend(key_metrics)
            
        if visualization_info:
            self.visualization_history.extend(visualization_info)
        
        # Manage memory limits
        self._manage_memory_limits()
    
    def _extract_key_metrics(self, response: Dict[str, Any]) -> List[Dict]:
        """Extract key metrics and numbers from response."""
        key_metrics = []
        
        # Extract from answer text
        answer = response.get("answer", "")
        
        # Look for numbers and metrics
        import re
        number_patterns = [
            r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(dollars?|USD|\$)',  # Money
            r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(percent|%)',        # Percentages
            r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(customers?|users?|records?)', # Counts
        ]
        
        for pattern in number_patterns:
            matches = re.findall(pattern, answer, re.IGNORECASE)
            for match in matches:
                key_metrics.append({
                    'value': match[0],
                    'unit': match[1],
                    'context': 'extracted_from_answer'
                })
        
        return key_metrics[:5]  # Limit to top 5 metrics
    
    def _extract_visualization_info(self, response: Dict[str, Any]) -> List[Dict]:
        """Extract visualization metadata."""
        charts = response.get("generated_charts", [])
        viz_info = []
        
        for chart in charts:
            config = chart.get('config', {})
            viz_info.append({
                'type': config.get('chart_type', 'unknown'),
                'title': config.get('title', 'Untitled'),
                'timestamp': datetime.now().isoformat()
            })
        
        return viz_info
    
    def _manage_memory_limits(self):
        """Manage memory to stay within limits."""
        # Keep only recent exchanges
        if len(self.conversation_history) > self.max_exchanges:
            # Move older exchanges to summary
            old_exchanges = self.conversation_history[:-self.max_exchanges]
            self._summarize_old_exchanges(old_exchanges)
            self.conversation_history = self.conversation_history[-self.max_exchanges:]
        
        # Limit key findings
        if len(self.key_findings) > 20:
            self.key_findings = self.key_findings[-20:]
            
        # Limit visualization history
        if len(self.visualization_history) > 10:
            self.visualization_history = self.visualization_history[-10:]
    
    def _summarize_old_exchanges(self, old_exchanges: List[Dict]):
        """Summarize old exchanges into key findings."""
        for exchange in old_exchanges:
            # Extract key points for future reference
            if exchange.get('key_metrics'):
                self.key_findings.extend(exchange['key_metrics'])
    
    def get_enhanced_context(self, current_message: str, intent_info: Dict) -> str:
        """Generate enhanced context based on intent and history."""
        if not self.conversation_history:
            return ""
        
        context_parts = ["Previous conversation context:"]
        
        # Add recent exchanges (more detail for recent ones)
        for i, exchange in enumerate(self.conversation_history[-3:], 1):
            context_parts.append(f"\n{i}. User: {exchange['user_message']}")
            if exchange['sql_query']:
                context_parts.append(f"   SQL: {exchange['sql_query']}")
            context_parts.append(f"   Response: {exchange['answer_summary']}")
            
            # Add chart info if relevant to current intent
            if 'visualization' in intent_info.get('intents', []) and exchange['has_charts']:
                context_parts.append(f"   Charts: {', '.join(exchange['chart_types'])}")
        
        # Add relevant key findings for business/analytical intents
        if any(intent in intent_info.get('intents', []) for intent in ['business', 'statistical', 'comparison']):
            if self.key_findings:
                context_parts.append(f"\nKey findings from earlier: {self.key_findings[-3:]}")
        
        # Add visualization context for chart-related requests
        if 'visualization' in intent_info.get('intents', []) and self.visualization_history:
            recent_charts = [viz['type'] for viz in self.visualization_history[-3:]]
            context_parts.append(f"\nRecent chart types used: {', '.join(recent_charts)}")
        
        context_parts.append(f"\nCurrent question: {current_message}")
        context_parts.append("Please provide a relevant response considering the conversation context and intent.")
        
        return "\n".join(context_parts)

class SmartSuggestionEngine:
    """Generate smart follow-up suggestions based on context and data."""
    
    def __init__(self):
        self.suggestion_templates = {
            'after_top_results': [
                "Would you like to see the bottom {n} results?",
                "Shall I show you trends over time for these items?",
                "Want to break this down by category or region?"
            ],
            'after_aggregation': [
                "Would you like to see this data visualized differently?",
                "Shall I analyze what's driving these numbers?",
                "Want to compare this to a different time period?"
            ],
            'after_visualization': [
                "Would you like to export this chart?",
                "Shall I create additional visualizations?",
                "Want to drill down into any specific data point?"
            ],
            'after_comparison': [
                "Would you like to see statistical significance?",
                "Shall I analyze what's causing the differences?",
                "Want to add more items to compare?"
            ]
        }
    
    def generate_suggestions(self, last_response: Dict[str, Any], 
                           conversation_context: List[Dict]) -> List[str]:
        """Generate contextual follow-up suggestions."""
        suggestions = []
        
        # Analyze last response
        has_charts = len(last_response.get("generated_charts", [])) > 0
        answer = last_response.get("answer", "").lower()
        
        # Pattern-based suggestions
        if "top" in answer and any(char.isdigit() for char in answer):
            suggestions.extend(self.suggestion_templates['after_top_results'][:2])
        
        if any(word in answer for word in ['sum', 'total', 'average', 'count']):
            suggestions.extend(self.suggestion_templates['after_aggregation'][:2])
        
        if has_charts:
            suggestions.extend(self.suggestion_templates['after_visualization'][:2])
        
        if any(word in answer for word in ['compared', 'versus', 'than']):
            suggestions.extend(self.suggestion_templates['after_comparison'][:2])
        
        # Limit to 3 suggestions
        return suggestions[:3]

# Example integration with existing chat system
class EnhancedConversationalAgent:
    """Enhanced version with better follow-up capabilities."""
    
    def __init__(self):
        self.followup_detector = EnhancedFollowupDetector()
        self.context_manager = EnhancedContextManager()
        self.suggestion_engine = SmartSuggestionEngine()
        self.base_agent = None  # Will be the original agent
    
    def process_message(self, user_message: str) -> Dict[str, Any]:
        """Process message with enhanced follow-up handling."""
        
        # Detect follow-up intent
        intent_info = self.followup_detector.detect_followup_intent(user_message)
        
        # Get enhanced context
        enhanced_context = self.context_manager.get_enhanced_context(user_message, intent_info)
        
        # Build enhanced query
        if intent_info['is_followup'] and enhanced_context:
            enhanced_query = f"""
            {enhanced_context}
            
            Intent detected: {intent_info['primary_intent']}
            Specific intents: {', '.join(intent_info['intents'])}
            
            Please provide a response that considers:
            1. The conversation history and context
            2. The detected intent type: {intent_info['primary_intent']}
            3. Continuity with previous responses
            """
        else:
            enhanced_query = user_message
        
        # Process with base agent (would be the enhanced SQL agent)
        # result = self.base_agent.query(enhanced_query)
        
        # For demonstration, return mock result
        result = {
            "answer": f"Enhanced response for: {user_message}",
            "sql_query": "SELECT * FROM demo;",
            "generated_charts": [],
            "intent_info": intent_info,
            "enhanced_query": enhanced_query
        }
        
        # Add to context
        self.context_manager.add_exchange(user_message, result)
        
        # Generate suggestions
        suggestions = self.suggestion_engine.generate_suggestions(
            result, self.context_manager.conversation_history
        )
        result["suggestions"] = suggestions
        
        return result

# Demo usage
if __name__ == "__main__":
    agent = EnhancedConversationalAgent()
    
    # Simulate conversation
    messages = [
        "What are the top 5 selling artists?",
        "Tell me more about the top artist",
        "Show me their albums",
        "Can you make this a pie chart?",
        "What about sales trends over time?"
    ]
    
    print("🤖 Enhanced Follow-up System Demo")
    print("=" * 40)
    
    for i, message in enumerate(messages, 1):
        print(f"\n🔵 Message {i}: {message}")
        result = agent.process_message(message)
        
        intent = result.get('intent_info', {})
        print(f"📊 Intent: {intent.get('primary_intent', 'none')}")
        print(f"🎯 Is Follow-up: {intent.get('is_followup', False)}")
        print(f"💡 Suggestions: {result.get('suggestions', [])}")
        print("-" * 30) 