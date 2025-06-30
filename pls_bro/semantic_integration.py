#!/usr/bin/env python3
"""
Semantic Integration Layer
=========================

This integrates semantic-based systems with the existing chat app:
- Replaces pattern matching with semantic detection
- Adds intelligent context management
- Maintains backward compatibility
- Provides enhanced follow-up capabilities

Use this to upgrade your chat app with ChatGPT-like intelligence.
"""

import sys
import os
from typing import Dict, List, Optional, Any, Tuple
import json
import time

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import existing modules
try:
    from semantic_followup_system import SemanticFollowupDetector, create_semantic_detector
    from intelligent_context_manager import IntelligentContextManager, create_intelligent_context_manager
    SEMANTIC_MODULES_AVAILABLE = True
except ImportError:
    print("⚠️  Semantic modules not available, using fallback")
    SEMANTIC_MODULES_AVAILABLE = False

class SemanticEnhancedChatSystem:
    """
    Enhanced chat system with semantic intelligence
    
    This class provides a drop-in replacement for the existing chat system
    with advanced semantic capabilities:
    - Intelligent follow-up detection
    - Context-aware responses
    - Semantic memory management
    - Conversation state tracking
    """
    
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2",
                 max_context_exchanges: int = 8,
                 semantic_threshold: float = 0.6):
        """Initialize semantic enhanced chat system"""
        
        self.model_name = model_name
        self.max_context_exchanges = max_context_exchanges
        self.semantic_threshold = semantic_threshold
        
        # Initialize semantic components
        if SEMANTIC_MODULES_AVAILABLE:
            print("🚀 Initializing Semantic Enhanced Chat System...")
            self.followup_detector = create_semantic_detector(model_name)
            self.context_manager = create_intelligent_context_manager(
                model_name=model_name,
                max_context_length=max_context_exchanges
            )
            self.semantic_enabled = True
            print("✅ Semantic intelligence enabled")
        else:
            print("⚠️  Semantic modules unavailable, using basic mode")
            self.followup_detector = None
            self.context_manager = None
            self.semantic_enabled = False
        
        # Session tracking
        self.session_id = self._generate_session_id()
        self.conversation_history = []
        self.performance_metrics = {
            'total_queries': 0,
            'followup_detections': 0,
            'semantic_analyses': 0,
            'context_generations': 0,
            'average_response_time': 0.0
        }
    
    def process_user_query(self, 
                          user_message: str,
                          sql_agent_function: callable,
                          additional_context: Dict = None) -> Dict[str, Any]:
        """
        Process user query with semantic intelligence
        
        This is the main method that replaces the existing chat processing
        with enhanced semantic capabilities.
        """
        
        start_time = time.time()
        
        # Detect if this is a follow-up query
        followup_analysis = self.detect_followup_with_intelligence(user_message)
        
        # Generate intelligent context
        context = self.generate_intelligent_context(user_message, followup_analysis)
        
        # Prepare enhanced prompt for SQL agent
        enhanced_prompt = self.prepare_semantic_prompt(
            user_message, context, followup_analysis
        )
        
        # Execute SQL agent with enhanced context
        try:
            sql_response = sql_agent_function(enhanced_prompt)
        except Exception as e:
            sql_response = {
                'answer': f"Error processing query: {str(e)}",
                'sql_query': None,
                'data': None
            }
        
        # Add to conversation history and context
        self.add_to_conversation_history(user_message, sql_response, followup_analysis)
        
        # Prepare enhanced response
        enhanced_response = self.prepare_enhanced_response(
            sql_response, followup_analysis, context
        )
        
        # Update performance metrics
        processing_time = time.time() - start_time
        self.update_performance_metrics(processing_time, followup_analysis)
        
        return enhanced_response
    
    def detect_followup_with_intelligence(self, user_message: str) -> Dict[str, Any]:
        """Detect follow-up with semantic intelligence"""
        
        if not self.semantic_enabled or not self.followup_detector:
            # Fallback to basic pattern matching
            return self._basic_followup_detection(user_message)
        
        # Use semantic follow-up detection
        return self.followup_detector.detect_followup_semantic(
            user_message, self.conversation_history
        )
    
    def generate_intelligent_context(self, 
                                   user_message: str,
                                   followup_analysis: Dict[str, Any]) -> str:
        """Generate intelligent context for the query"""
        
        if not self.semantic_enabled or not self.context_manager:
            # Fallback to basic context
            return self._basic_context_generation()
        
        # Use intelligent context generation
        return self.context_manager.get_intelligent_context(
            user_message, max_exchanges=self.max_context_exchanges
        )
    
    def prepare_semantic_prompt(self, 
                               user_message: str,
                               context: str,
                               followup_analysis: Dict[str, Any]) -> str:
        """Prepare enhanced prompt with semantic intelligence"""
        
        prompt_parts = []
        
        # Add intelligent context
        if context:
            prompt_parts.append(context)
            prompt_parts.append("\n" + "="*60 + "\n")
        
        # Add follow-up intelligence
        if followup_analysis['is_followup']:
            prompt_parts.append("🔗 FOLLOW-UP QUERY DETECTED")
            prompt_parts.append(f"Intent: {followup_analysis['intent']}")
            prompt_parts.append(f"Confidence: {followup_analysis['confidence']:.2f}")
            
            if followup_analysis.get('suggested_actions'):
                prompt_parts.append("Suggested Actions:")
                for action in followup_analysis['suggested_actions'][:3]:
                    prompt_parts.append(f"  • {action}")
            
            prompt_parts.append("\nℹ️  This query builds on previous conversation.")
            prompt_parts.append("Reference relevant previous context when appropriate.")
            prompt_parts.append("Maintain conversation continuity and coherence.")
            prompt_parts.append("\n" + "-"*60 + "\n")
        
        # Add current query
        prompt_parts.append(f"🎯 CURRENT QUERY: {user_message}")
        
        return "\n".join(prompt_parts)
    
    def add_to_conversation_history(self,
                                   user_message: str,
                                   sql_response: Dict[str, Any],
                                   followup_analysis: Dict[str, Any]):
        """Add exchange to conversation history with intelligence"""
        
        # Add to basic history
        exchange = {
            'user_message': user_message,
            'assistant_response': sql_response,
            'timestamp': time.time(),
            'followup_analysis': followup_analysis
        }
        self.conversation_history.append(exchange)
        
        # Add to intelligent context manager
        if self.semantic_enabled and self.context_manager:
            self.context_manager.add_exchange(
                user_message=user_message,
                assistant_response=sql_response.get('answer', ''),
                intent=followup_analysis.get('intent', 'unknown'),
                importance=followup_analysis.get('confidence', 0.5)
            )
        
        # Maintain history size
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def prepare_enhanced_response(self,
                                 sql_response: Dict[str, Any],
                                 followup_analysis: Dict[str, Any],
                                 context: str) -> Dict[str, Any]:
        """Prepare enhanced response with semantic intelligence"""
        
        enhanced_response = sql_response.copy()
        
        # Add semantic metadata
        enhanced_response['semantic_metadata'] = {
            'is_followup': followup_analysis['is_followup'],
            'intent': followup_analysis['intent'],
            'confidence': followup_analysis['confidence'],
            'analysis_method': followup_analysis.get('analysis_method', 'basic'),
            'context_used': bool(context),
            'semantic_enabled': self.semantic_enabled
        }
        
        # Add conversation intelligence
        if self.semantic_enabled and self.context_manager:
            analytics = self.context_manager.get_conversation_analytics()
            enhanced_response['conversation_intelligence'] = {
                'topics_discussed': analytics.get('unique_topics', []),
                'entities_mentioned': analytics.get('unique_entities', []),
                'conversation_depth': analytics.get('total_exchanges', 0),
                'semantic_capability': analytics.get('semantic_capability', 'disabled')
            }
        
        # Add performance metrics
        enhanced_response['performance'] = self.performance_metrics.copy()
        
        return enhanced_response
    
    def _basic_followup_detection(self, user_message: str) -> Dict[str, Any]:
        """Fallback basic follow-up detection"""
        
        basic_patterns = [
            'tell me more', 'what about', 'show me', 'can you', 'how about',
            'explain', 'details', 'more info', 'expand', 'clarify'
        ]
        
        message_lower = user_message.lower()
        has_pattern = any(pattern in message_lower for pattern in basic_patterns)
        has_context = len(self.conversation_history) > 0
        
        confidence = 0.6 if has_pattern and has_context else 0.3
        
        return {
            'is_followup': has_pattern and has_context,
            'confidence': confidence,
            'intent': 'unknown',
            'analysis_method': 'basic_pattern_matching',
            'suggested_actions': ['Handle basic follow-up']
        }
    
    def _basic_context_generation(self) -> str:
        """Fallback basic context generation"""
        
        if not self.conversation_history:
            return ""
        
        # Get last 3 exchanges
        recent_exchanges = self.conversation_history[-3:]
        context_parts = ["📚 Recent Conversation Context:"]
        
        for i, exchange in enumerate(recent_exchanges, 1):
            user_msg = exchange['user_message']
            response = exchange['assistant_response']
            
            context_parts.append(f"\n{i}. User: {user_msg}")
            
            if isinstance(response, dict):
                answer = response.get('answer', '')[:200]
            else:
                answer = str(response)[:200]
            
            context_parts.append(f"   Assistant: {answer}...")
        
        return "\n".join(context_parts)
    
    def update_performance_metrics(self, 
                                  processing_time: float,
                                  followup_analysis: Dict[str, Any]):
        """Update performance metrics"""
        
        self.performance_metrics['total_queries'] += 1
        
        if followup_analysis['is_followup']:
            self.performance_metrics['followup_detections'] += 1
        
        if followup_analysis.get('analysis_method') == 'semantic_embeddings':
            self.performance_metrics['semantic_analyses'] += 1
        
        self.performance_metrics['context_generations'] += 1
        
        # Update average response time
        total_time = (self.performance_metrics['average_response_time'] * 
                     (self.performance_metrics['total_queries'] - 1) + processing_time)
        self.performance_metrics['average_response_time'] = (
            total_time / self.performance_metrics['total_queries']
        )
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import hashlib
        from datetime import datetime
        return hashlib.md5(
            f"semantic_chat_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:8]
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and capabilities"""
        
        status = {
            'session_id': self.session_id,
            'semantic_enabled': self.semantic_enabled,
            'model_name': self.model_name,
            'max_context_exchanges': self.max_context_exchanges,
            'semantic_threshold': self.semantic_threshold,
            'conversation_length': len(self.conversation_history),
            'performance_metrics': self.performance_metrics
        }
        
        if self.semantic_enabled and self.context_manager:
            status['context_analytics'] = self.context_manager.get_conversation_analytics()
        
        return status


# Integration function for existing chat app
def enhance_chat_app_with_semantics(chat_app_instance, 
                                   semantic_config: Dict[str, Any] = None):
    """
    Enhance existing chat app with semantic capabilities
    
    This function provides a way to upgrade your existing chat app
    with semantic intelligence while maintaining backward compatibility.
    """
    
    if semantic_config is None:
        semantic_config = {
            'model_name': 'all-MiniLM-L6-v2',
            'max_context_exchanges': 8,
            'semantic_threshold': 0.6
        }
    
    # Create semantic enhanced system
    semantic_system = SemanticEnhancedChatSystem(**semantic_config)
    
    # Replace the is_followup_question method
    def enhanced_is_followup_question(message: str) -> bool:
        """Enhanced follow-up detection with semantic intelligence"""
        result = semantic_system.detect_followup_with_intelligence(message)
        return result['is_followup']
    
    # Replace the get_conversation_context method
    def enhanced_get_conversation_context(message: str = "") -> str:
        """Enhanced context generation with semantic intelligence"""
        return semantic_system.generate_intelligent_context(
            message, {'is_followup': True, 'intent': 'unknown', 'confidence': 0.5}
        )
    
    # Add new semantic processing method
    def process_with_semantic_intelligence(user_message: str, sql_agent_func: callable) -> Dict[str, Any]:
        """Process query with full semantic intelligence"""
        return semantic_system.process_user_query(user_message, sql_agent_func)
    
    # Monkey patch the chat app instance
    chat_app_instance.is_followup_question = enhanced_is_followup_question
    chat_app_instance.get_conversation_context = enhanced_get_conversation_context
    chat_app_instance.process_with_semantic_intelligence = process_with_semantic_intelligence
    chat_app_instance.semantic_system = semantic_system
    
    print("✅ Chat app enhanced with semantic intelligence!")
    print(f"   - Semantic capability: {semantic_system.semantic_enabled}")
    print(f"   - Model: {semantic_system.model_name}")
    print(f"   - Context window: {semantic_system.max_context_exchanges} exchanges")
    
    return chat_app_instance


# Example usage
if __name__ == "__main__":
    print("🔬 Testing Semantic Integration Layer")
    print("=" * 60)
    
    # Create semantic enhanced chat system
    semantic_chat = SemanticEnhancedChatSystem()
    
    # Mock SQL agent function
    def mock_sql_agent(prompt: str) -> Dict[str, Any]:
        return {
            'answer': f"Mock response to query. Context length: {len(prompt)} chars",
            'sql_query': "SELECT * FROM artists",
            'data': [{'artist': 'AC/DC', 'sales': 1000}]
        }
    
    # Test queries
    test_queries = [
        "Show me top artists by sales",
        "Tell me more about the top artist",
        "How do they compare to other artists?",
        "Can you make a chart of this data?"
    ]
    
    print("Processing queries with semantic intelligence:\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}: '{query}'")
        
        response = semantic_chat.process_user_query(query, mock_sql_agent)
        
        print(f"  ✅ Processed: {response['semantic_metadata']['is_followup']}")
        print(f"  🎯 Intent: {response['semantic_metadata']['intent']}")
        print(f"  📊 Confidence: {response['semantic_metadata']['confidence']:.2f}")
        print(f"  🔍 Method: {response['semantic_metadata']['analysis_method']}")
        print()
    
    # Show system status
    print("📊 System Status:")
    status = semantic_chat.get_system_status()
    for key, value in status.items():
        if isinstance(value, dict):
            print(f"  {key}: {len(value)} items")
        else:
            print(f"  {key}: {value}")
    
    print("\n🎉 Semantic Integration Test Complete!") 