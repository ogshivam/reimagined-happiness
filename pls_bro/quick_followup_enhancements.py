#!/usr/bin/env python3
"""
Quick Follow-up Enhancements
Practical improvements that can be applied immediately to the current chat system.
"""

def enhanced_followup_detection(message: str) -> dict:
    """
    Enhanced follow-up detection with better keyword coverage.
    Can replace the current is_followup_question method.
    """
    message_lower = message.lower()
    
    # Enhanced follow-up indicators organized by intent
    followup_patterns = {
        'data_exploration': [
            'show me more', 'tell me about', 'show me the', 'what about',
            'next 10', 'next 5', 'first 10', 'last 10', 'top 10', 'bottom 10',
            'drill down', 'break down', 'expand', 'dive deeper', 'get into'
        ],
        
        'comparison': [
            'compare', 'versus', 'vs', 'against', 'relative to', 'compared to',
            'difference', 'gap', 'variation', 'contrast', 'how does', 'better than'
        ],
        
        'temporal': [
            'trend', 'over time', 'timeline', 'historical', 'past', 'previous',
            'growth', 'decline', 'change', 'evolution', 'by year', 'by month',
            'annually', 'monthly', 'daily', 'weekly'
        ],
        
        'visualization': [
            'chart', 'graph', 'plot', 'visualize', 'show as', 'display as',
            'pie chart', 'bar chart', 'line chart', 'scatter plot',
            'make it', 'change to', 'convert to', 'as a'
        ],
        
        'analytical': [
            'why', 'how', 'what causes', 'what drives', 'reason', 'because',
            'analyze', 'analysis', 'pattern', 'correlation', 'relationship',
            'significant', 'important', 'key factors'
        ],
        
        'data_quality': [
            'missing', 'null', 'empty', 'incomplete', 'outlier', 'anomaly',
            'duplicate', 'unique', 'distinct', 'clean', 'quality',
            'unusual', 'strange', 'unexpected'
        ]
    }
    
    detected_intents = []
    for intent_type, keywords in followup_patterns.items():
        if any(keyword in message_lower for keyword in keywords):
            detected_intents.append(intent_type)
    
    # Basic follow-up indicators
    basic_indicators = any([
        message_lower.startswith(('can you', 'could you', 'would you', 'will you')),
        message_lower.startswith(('show me', 'tell me', 'give me')),
        'also' in message_lower,
        'additionally' in message_lower,
        'furthermore' in message_lower,
        'specifically' in message_lower,
        'details' in message_lower
    ])
    
    is_followup = basic_indicators or bool(detected_intents)
    
    return {
        'is_followup': is_followup,
        'intents': detected_intents,
        'primary_intent': detected_intents[0] if detected_intents else 'general',
        'confidence': len(detected_intents) / len(followup_patterns) if detected_intents else 0
    }

def enhanced_context_generation(conversation_history: list, current_message: str, intent_info: dict) -> str:
    """
    Enhanced context generation with more detail and intent-awareness.
    Can replace the current get_conversation_context method.
    """
    if not conversation_history:
        return ""
    
    context_parts = ["Previous conversation context:"]
    
    # Use more exchanges for context (3 -> 4)
    recent_exchanges = conversation_history[-4:] if len(conversation_history) >= 4 else conversation_history
    
    for i, exchange in enumerate(recent_exchanges, 1):
        context_parts.append(f"\n{i}. User asked: {exchange['user_message']}")
        
        if exchange.get('sql_query'):
            context_parts.append(f"   SQL query: {exchange['sql_query']}")
        
        # Increase answer memory from 100 to 300 characters
        answer = exchange['assistant_response'].get('answer', '')
        if answer:
            summary = answer[:300] + "..." if len(answer) > 300 else answer
            context_parts.append(f"   Answer: {summary}")
        
        # Add visualization info if relevant
        if exchange.get('has_charts') and 'visualization' in intent_info.get('intents', []):
            context_parts.append(f"   Generated visualizations: Yes")
    
    # Add intent-specific context enhancement
    if intent_info.get('primary_intent') != 'general':
        context_parts.append(f"\nCurrent request type: {intent_info['primary_intent']}")
        context_parts.append("Please provide a response that builds on the previous conversation.")
    
    context_parts.append(f"\nCurrent question: {current_message}")
    
    return "\n".join(context_parts)

def generate_smart_suggestions(last_response: dict, intent_info: dict) -> list:
    """
    Generate smart follow-up suggestions based on the last response and detected intent.
    This is a new feature that can be added to the chat interface.
    """
    suggestions = []
    
    answer = last_response.get("answer", "").lower()
    has_charts = len(last_response.get("generated_charts", [])) > 0
    
    # Intent-based suggestions
    if intent_info.get('primary_intent') == 'data_exploration':
        suggestions.extend([
            "Show me more details about this data",
            "Break this down by category",
            "What are the key patterns here?"
        ])
    
    elif intent_info.get('primary_intent') == 'visualization':
        suggestions.extend([
            "Try a different chart type",
            "Add trend lines or annotations", 
            "Export this visualization"
        ])
    
    elif intent_info.get('primary_intent') == 'comparison':
        suggestions.extend([
            "Compare with a different time period",
            "Add more items to compare",
            "Show percentage differences"
        ])
    
    # Content-based suggestions
    if any(word in answer for word in ['top', 'highest', 'best']):
        suggestions.append("What about the bottom/lowest results?")
    
    if any(word in answer for word in ['total', 'sum', 'count']):
        suggestions.append("Show me the breakdown by category")
    
    if has_charts:
        suggestions.append("Create additional visualizations")
    
    if any(word in answer for word in ['increase', 'growth', 'rise']):
        suggestions.append("What's driving this growth?")
    
    # Limit to top 3 suggestions and remove duplicates
    unique_suggestions = list(dict.fromkeys(suggestions))
    return unique_suggestions[:3]

def enhanced_conversation_metadata(user_message: str, assistant_response: dict, intent_info: dict) -> dict:
    """
    Enhanced metadata extraction for better conversation memory.
    Can extend the current add_to_conversation method.
    """
    # Extract key metrics from the response
    answer = assistant_response.get("answer", "")
    
    # Simple metric extraction (numbers with context)
    import re
    metrics = []
    
    # Find numbers with units
    number_patterns = [
        r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(dollars?|USD|\$|revenue|sales)',
        r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(percent|%|percentage)',
        r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(customers?|users?|records?|items?)'
    ]
    
    for pattern in number_patterns:
        matches = re.findall(pattern, answer, re.IGNORECASE)
        for match in matches:
            metrics.append({
                'value': match[0],
                'unit': match[1],
                'context': 'extracted_from_answer'
            })
    
    # Enhanced metadata
    enhanced_metadata = {
        'timestamp': assistant_response.get('timestamp'),
        'user_message': user_message,
        'assistant_response': assistant_response,
        'sql_query': assistant_response.get('sql_query', ''),
        'has_charts': len(assistant_response.get('generated_charts', [])) > 0,
        'chart_count': len(assistant_response.get('generated_charts', [])),
        'intent_info': intent_info,
        'key_metrics': metrics[:3],  # Store top 3 metrics
        'answer_length': len(answer),
        'response_type': 'analytical' if intent_info.get('intents') else 'informational'
    }
    
    return enhanced_metadata

# Example usage showing how to integrate with existing system
def demonstrate_integration():
    """Show how these enhancements integrate with the current system."""
    
    print("🔄 Quick Follow-up Enhancements Demo")
    print("=" * 45)
    
    # Simulate conversation
    sample_messages = [
        "What are the top 5 selling artists?",
        "Tell me more about the #1 artist", 
        "Show me their sales trends over time",
        "Can you make this a line chart?",
        "What's driving the recent growth?"
    ]
    
    # Simulate conversation history
    conversation_history = []
    
    for i, message in enumerate(sample_messages):
        print(f"\n💬 Message {i+1}: \"{message}\"")
        
        # Enhanced follow-up detection
        intent_info = enhanced_followup_detection(message)
        print(f"🎯 Follow-up: {intent_info['is_followup']}")
        print(f"🧠 Primary Intent: {intent_info['primary_intent']}")
        print(f"📊 All Intents: {intent_info['intents']}")
        
        # Enhanced context (if follow-up)
        if intent_info['is_followup'] and conversation_history:
            context = enhanced_context_generation(conversation_history, message, intent_info)
            print(f"🔄 Enhanced Context: {len(context)} characters")
        
        # Simulate response
        mock_response = {
            'answer': f'Enhanced response to: {message}',
            'sql_query': 'SELECT * FROM mock_table;',
            'generated_charts': [{'type': 'bar'}] if i > 1 else []
        }
        
        # Generate suggestions
        suggestions = generate_smart_suggestions(mock_response, intent_info)
        print(f"💡 Suggestions: {suggestions}")
        
        # Add to conversation history with enhanced metadata
        enhanced_exchange = enhanced_conversation_metadata(message, mock_response, intent_info)
        conversation_history.append(enhanced_exchange)
        
        print("-" * 30)
    
    print(f"\n📊 Final conversation length: {len(conversation_history)} exchanges")
    print("✅ All enhancements demonstrated successfully!")

if __name__ == "__main__":
    demonstrate_integration() 