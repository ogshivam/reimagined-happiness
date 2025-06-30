#!/usr/bin/env python3
"""
Semantic Follow-up Detection System
==================================

This implements a ChatGPT-like approach using:
- Sentence embeddings for semantic understanding
- Vector similarity for follow-up detection  
- Intelligent conversation state management
- Memory networks for context understanding

This is much more advanced than pattern matching and closer to how
modern AI systems like ChatGPT actually work.
"""

import numpy as np
import json
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import pickle
import os

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    SEMANTIC_AVAILABLE = True
    print("✅ Semantic libraries available")
except ImportError:
    SEMANTIC_AVAILABLE = False
    print("⚠️  Installing semantic dependencies...")
    import subprocess
    subprocess.run(["pip", "install", "sentence-transformers", "scikit-learn"], check=False)


class ConversationState(Enum):
    """Intelligent conversation states"""
    INITIAL = "initial"
    EXPLORING = "exploring" 
    DRILLING_DOWN = "drilling_down"
    COMPARING = "comparing"
    VISUALIZING = "visualizing"
    ANALYZING = "analyzing"
    MODIFYING = "modifying"
    CONCLUDING = "concluding"


@dataclass
class SemanticContext:
    """Semantic context for conversation understanding"""
    current_topic: str
    mentioned_entities: List[str]
    key_metrics: List[str]
    conversation_state: ConversationState
    confidence_score: float
    embedding: Optional[np.ndarray] = None
    related_contexts: List[str] = None
    
    def __post_init__(self):
        if self.related_contexts is None:
            self.related_contexts = []


@dataclass
class ConversationMemory:
    """Enhanced memory with semantic understanding"""
    exchange_id: str
    user_message: str
    assistant_response: str
    timestamp: str
    embedding: np.ndarray
    semantic_context: SemanticContext
    importance_score: float
    access_count: int = 0
    last_accessed: Optional[str] = None


class SemanticFollowupDetector:
    """Advanced semantic-based follow-up detection system"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize with semantic capabilities"""
        self.model_name = model_name
        self.model = None
        self.conversation_memory: List[ConversationMemory] = []
        self.context_cache: Dict[str, SemanticContext] = {}
        self.similarity_threshold = 0.6  # Tunable threshold
        
        # Initialize semantic model
        if SEMANTIC_AVAILABLE:
            try:
                print(f"🧠 Loading semantic model: {model_name}")
                self.model = SentenceTransformer(model_name)
                print("✅ Semantic model loaded successfully")
                
                # Pre-compute intent embeddings
                self.intent_embeddings = self._initialize_intent_embeddings()
            except Exception as e:
                print(f"⚠️  Failed to load model: {e}")
                self.model = None
        
        # Conversation state tracking
        self.current_state = ConversationState.INITIAL
        self.state_history: List[Tuple[ConversationState, str]] = []
        
        # Intent patterns for hybrid approach
        self.intent_embeddings = self._initialize_intent_embeddings()
    
    def _initialize_intent_embeddings(self) -> Dict[str, Any]:
        """Pre-compute embeddings for common intents"""
        if not self.model:
            return {}
        
        intent_phrases = {
            'followup_clarification': [
                "What does this mean?", "Can you explain?", "I don't understand",
                "What is that?", "Tell me more about this"
            ],
            'followup_drill_down': [
                "Show me more details", "Break this down", "Give me specifics",
                "Dive deeper into this", "More information about"
            ],
            'followup_comparison': [
                "How does this compare?", "What's the difference?", "Compare these",
                "Show differences", "Versus this"
            ],
            'followup_visualization': [
                "Make a chart", "Show this graphically", "Visualize this data",
                "Create a graph", "Plot this"
            ],
            'followup_analysis': [
                "Analyze this trend", "What patterns do you see?", "Find insights",
                "Statistical analysis", "What does this mean?"
            ],
            'new_query': [
                "Show me all customers", "List all products", "What are the sales?",
                "New question", "Different topic"
            ]
        }
        
        intent_embeddings = {}
        for intent, phrases in intent_phrases.items():
            embeddings = self.model.encode(phrases)
            intent_embeddings[intent] = np.mean(embeddings, axis=0)
        
        return intent_embeddings
    
    def detect_followup_semantic(self, 
                                current_message: str,
                                conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Advanced semantic follow-up detection using embeddings
        
        Returns comprehensive analysis including:
        - is_followup: boolean
        - confidence: float (0-1)
        - intent: detected intent
        - semantic_similarity: similarity to recent context
        - context_references: referenced previous content
        - suggested_actions: AI-generated suggestions
        """
        
        if not self.model:
            # Fallback to enhanced pattern matching
            return self._fallback_detection(current_message, conversation_history)
        
        try:
            # Encode current message
            current_embedding = self.model.encode([current_message])[0]
            
            # Analyze against conversation history
            context_similarity = self._analyze_context_similarity(
                current_embedding, conversation_history or []
            )
            
            # Intent classification using semantic similarity
            intent_analysis = self._classify_intent_semantic(current_embedding)
            
            # Conversation state analysis
            state_analysis = self._analyze_conversation_state(
                current_message, current_embedding, conversation_history or []
            )
            
            # Context reference detection
            context_refs = self._detect_context_references_semantic(
                current_embedding, conversation_history or []
            )
            
            # Combine all signals for final decision
            overall_confidence = self._calculate_overall_confidence(
                context_similarity, intent_analysis, state_analysis, context_refs
            )
            
            is_followup = overall_confidence >= self.similarity_threshold
            
            # Generate intelligent suggestions
            suggestions = self._generate_intelligent_suggestions(
                intent_analysis, context_refs, state_analysis
            )
            
            # Update conversation state
            if is_followup:
                self._update_conversation_state(intent_analysis['intent'], current_message)
            
            return {
                'is_followup': is_followup,
                'confidence': overall_confidence,
                'intent': intent_analysis['intent'],
                'intent_confidence': intent_analysis['confidence'],
                'semantic_similarity': context_similarity,
                'context_references': context_refs,
                'conversation_state': self.current_state.value,
                'suggested_actions': suggestions,
                'analysis_method': 'semantic_embeddings'
            }
            
        except Exception as e:
            print(f"⚠️  Semantic analysis failed: {e}")
            return self._fallback_detection(current_message, conversation_history)
    
    def _analyze_context_similarity(self, 
                                   current_embedding: np.ndarray,
                                   conversation_history: List[Dict]) -> float:
        """Analyze semantic similarity to recent conversation context"""
        
        if not conversation_history:
            return 0.0
        
        # Get recent conversation context (last 3 exchanges)
        recent_exchanges = conversation_history[-3:]
        context_texts = []
        
        for exchange in recent_exchanges:
            # Combine user message and assistant response for context
            user_msg = exchange.get('user_message', '')
            assistant_resp = exchange.get('assistant_response', {})
            
            if isinstance(assistant_resp, dict):
                resp_text = assistant_resp.get('answer', '')
            else:
                resp_text = str(assistant_resp)
            
            context_texts.append(f"{user_msg} {resp_text}")
        
        if not context_texts:
            return 0.0
        
        # Encode context and calculate similarity
        context_embeddings = self.model.encode(context_texts)
        similarities = cosine_similarity([current_embedding], context_embeddings)[0]
        
        # Return maximum similarity to any recent context
        return float(np.max(similarities))
    
    def _classify_intent_semantic(self, current_embedding: np.ndarray) -> Dict[str, Any]:
        """Classify intent using semantic similarity to intent embeddings"""
        
        if not self.intent_embeddings:
            return {'intent': 'unknown', 'confidence': 0.0}
        
        best_intent = 'unknown'
        best_confidence = 0.0
        
        for intent, intent_embedding in self.intent_embeddings.items():
            similarity = cosine_similarity(
                [current_embedding], [intent_embedding]
            )[0][0]
            
            if similarity > best_confidence:
                best_confidence = similarity
                best_intent = intent
        
        # Remove the 'followup_' prefix for cleaner intent names
        clean_intent = best_intent.replace('followup_', '') if 'followup_' in best_intent else best_intent
        
        return {
            'intent': clean_intent,
            'confidence': float(best_confidence),
            'all_scores': {
                intent.replace('followup_', ''): float(cosine_similarity(
                    [current_embedding], [emb]
                )[0][0]) for intent, emb in self.intent_embeddings.items()
            }
        }
    
    def _analyze_conversation_state(self,
                                   current_message: str,
                                   current_embedding: np.ndarray,
                                   conversation_history: List[Dict]) -> Dict[str, Any]:
        """Analyze conversation state transitions"""
        
        # Simple state analysis based on conversation length and content
        num_exchanges = len(conversation_history)
        
        if num_exchanges == 0:
            expected_state = ConversationState.INITIAL
        elif num_exchanges <= 2:
            expected_state = ConversationState.EXPLORING
        else:
            # Use semantic analysis to determine state
            if any(word in current_message.lower() for word in ['chart', 'graph', 'plot', 'visualize']):
                expected_state = ConversationState.VISUALIZING
            elif any(word in current_message.lower() for word in ['compare', 'difference', 'versus']):
                expected_state = ConversationState.COMPARING
            elif any(word in current_message.lower() for word in ['analyze', 'trend', 'pattern']):
                expected_state = ConversationState.ANALYZING
            elif any(word in current_message.lower() for word in ['more', 'details', 'breakdown']):
                expected_state = ConversationState.DRILLING_DOWN
            else:
                expected_state = ConversationState.EXPLORING
        
        return {
            'current_state': self.current_state.value,
            'expected_state': expected_state.value,
            'state_transition_needed': self.current_state != expected_state,
            'conversation_length': num_exchanges
        }
    
    def _detect_context_references_semantic(self,
                                           current_embedding: np.ndarray,
                                           conversation_history: List[Dict]) -> List[Dict[str, Any]]:
        """Detect semantic references to previous context"""
        
        if not conversation_history:
            return []
        
        references = []
        
        # Check last 5 exchanges for semantic similarity
        recent_exchanges = conversation_history[-5:]
        
        for i, exchange in enumerate(recent_exchanges):
            assistant_resp = exchange.get('assistant_response', {})
            if isinstance(assistant_resp, dict):
                response_text = assistant_resp.get('answer', '')
            else:
                response_text = str(assistant_resp)
            
            if response_text:
                response_embedding = self.model.encode([response_text])[0]
                similarity = cosine_similarity(
                    [current_embedding], [response_embedding]
                )[0][0]
                
                if similarity > 0.3:  # Lower threshold for context detection
                    references.append({
                        'exchange_index': len(conversation_history) - len(recent_exchanges) + i,
                        'similarity': float(similarity),
                        'reference_type': 'semantic_content',
                        'content_preview': response_text[:100] + "..." if len(response_text) > 100 else response_text
                    })
        
        return references
    
    def _calculate_overall_confidence(self,
                                     context_similarity: float,
                                     intent_analysis: Dict[str, Any],
                                     state_analysis: Dict[str, Any],
                                     context_refs: List[Dict]) -> float:
        """Calculate overall confidence score for follow-up detection"""
        
        # Weight different signals
        context_weight = 0.4
        intent_weight = 0.3
        state_weight = 0.2
        references_weight = 0.1
        
        # Context similarity contribution
        context_score = context_similarity * context_weight
        
        # Intent contribution (higher for follow-up intents)
        intent_conf = intent_analysis['confidence']
        is_followup_intent = intent_analysis['intent'] != 'new_query'
        intent_score = (intent_conf if is_followup_intent else (1 - intent_conf)) * intent_weight
        
        # State transition contribution
        state_score = (0.8 if state_analysis['state_transition_needed'] else 0.2) * state_weight
        
        # Context references contribution
        ref_score = min(len(context_refs) * 0.3, 1.0) * references_weight
        
        total_score = context_score + intent_score + state_score + ref_score
        
        return min(total_score, 1.0)
    
    def _generate_intelligent_suggestions(self,
                                         intent_analysis: Dict[str, Any],
                                         context_refs: List[Dict],
                                         state_analysis: Dict[str, Any]) -> List[str]:
        """Generate intelligent suggestions based on semantic analysis"""
        
        suggestions = []
        intent = intent_analysis['intent']
        
        # Intent-based suggestions
        if intent == 'clarification':
            suggestions.extend([
                "Provide detailed explanation with examples",
                "Break down complex concepts",
                "Use analogies for better understanding"
            ])
        elif intent == 'drill_down':
            suggestions.extend([
                "Show hierarchical breakdown",
                "Provide specific metrics and details",
                "Include relevant sub-categories"
            ])
        elif intent == 'visualization':
            suggestions.extend([
                "Generate appropriate chart type",
                "Consider multiple visualization options",
                "Include interactive elements if possible"
            ])
        elif intent == 'comparison':
            suggestions.extend([
                "Create side-by-side comparison",
                "Highlight key differences",
                "Show relative metrics and percentages"
            ])
        elif intent == 'analysis':
            suggestions.extend([
                "Perform statistical analysis",
                "Identify trends and patterns",
                "Provide business insights and recommendations"
            ])
        
        # Context-based suggestions
        if context_refs:
            suggestions.append("Reference previous conversation context")
            suggestions.append("Build upon earlier findings")
        
        # State-based suggestions
        if state_analysis['state_transition_needed']:
            suggestions.append(f"Transition to {state_analysis['expected_state']} mode")
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _update_conversation_state(self, intent: str, message: str):
        """Update conversation state based on detected intent"""
        
        new_state = self.current_state
        
        if intent == 'clarification':
            new_state = ConversationState.EXPLORING
        elif intent == 'drill_down':
            new_state = ConversationState.DRILLING_DOWN
        elif intent == 'comparison':
            new_state = ConversationState.COMPARING
        elif intent == 'visualization':
            new_state = ConversationState.VISUALIZING
        elif intent == 'analysis':
            new_state = ConversationState.ANALYZING
        
        if new_state != self.current_state:
            self.state_history.append((self.current_state, datetime.now().isoformat()))
            self.current_state = new_state
    
    def _fallback_detection(self, message: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Fallback to enhanced pattern matching when semantic model unavailable"""
        
        # Enhanced pattern matching (better than original basic version)
        patterns = {
            'clarification': ['what does', 'what is', 'explain', 'meaning', 'clarify'],
            'drill_down': ['more details', 'show me', 'breakdown', 'expand', 'specific'],
            'visualization': ['chart', 'graph', 'plot', 'visualize', 'show'],
            'comparison': ['compare', 'contrast', 'versus', 'vs', 'difference'],
            'analysis': ['analyze', 'trend', 'pattern', 'insight', 'finding']
        }
        
        message_lower = message.lower()
        best_intent = 'unknown'
        best_score = 0
        
        for intent, keywords in patterns.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > best_score:
                best_score = score
                best_intent = intent
        
        # Simple context check
        has_context = bool(conversation_history) and len(conversation_history) > 0
        context_score = 0.5 if has_context else 0.0
        
        confidence = min((best_score * 0.3 + context_score), 1.0)
        is_followup = confidence >= 0.4
        
        return {
            'is_followup': is_followup,
            'confidence': confidence,
            'intent': best_intent,
            'intent_confidence': confidence,
            'semantic_similarity': context_score,
            'context_references': [],
            'conversation_state': self.current_state.value,
            'suggested_actions': [f"Handle {best_intent} request"],
            'analysis_method': 'pattern_matching_fallback'
        }
    
    def add_to_memory(self,
                     user_message: str,
                     assistant_response: str,
                     importance_score: float = 0.5):
        """Add conversation exchange to semantic memory"""
        
        if not self.model:
            return
        
        try:
            # Create embedding for the exchange
            combined_text = f"{user_message} {assistant_response}"
            embedding = self.model.encode([combined_text])[0]
            
            # Extract semantic context
            semantic_context = self._extract_semantic_context(
                user_message, assistant_response, embedding
            )
            
            # Create memory entry
            exchange_id = hashlib.md5(
                f"{user_message}_{datetime.now().isoformat()}".encode()
            ).hexdigest()[:8]
            
            memory = ConversationMemory(
                exchange_id=exchange_id,
                user_message=user_message,
                assistant_response=assistant_response,
                timestamp=datetime.now().isoformat(),
                embedding=embedding,
                semantic_context=semantic_context,
                importance_score=importance_score
            )
            
            self.conversation_memory.append(memory)
            
            # Maintain memory size (keep last 20 exchanges)
            if len(self.conversation_memory) > 20:
                self.conversation_memory = self.conversation_memory[-20:]
                
        except Exception as e:
            print(f"⚠️  Failed to add to semantic memory: {e}")
    
    def _extract_semantic_context(self,
                                 user_message: str,
                                 assistant_response: str,
                                 embedding: np.ndarray) -> SemanticContext:
        """Extract semantic context from conversation exchange"""
        
        # Simple entity extraction (can be enhanced with NER models)
        import re
        
        combined_text = f"{user_message} {assistant_response}"
        
        # Extract entities (capitalized words)
        entities = re.findall(r'\b[A-Z][a-z]+\b', combined_text)
        entities = list(set(entities))[:5]  # Limit to 5 unique entities
        
        # Extract metrics (numbers, percentages, currency)
        metrics = re.findall(r'\b\d+(?:\.\d+)?%?\b|\$\d+(?:,\d{3})*(?:\.\d{2})?\b', combined_text)
        metrics = list(set(metrics))[:5]  # Limit to 5 unique metrics
        
        # Determine topic (first few words of user message)
        topic = ' '.join(user_message.split()[:5])
        
        return SemanticContext(
            current_topic=topic,
            mentioned_entities=entities,
            key_metrics=metrics,
            conversation_state=self.current_state,
            confidence_score=0.8,  # Default confidence
            embedding=embedding
        )
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get intelligent conversation summary"""
        
        if not self.conversation_memory:
            return {'status': 'no_memory'}
        
        # Calculate memory statistics
        total_exchanges = len(self.conversation_memory)
        unique_entities = set()
        unique_metrics = set()
        
        for memory in self.conversation_memory:
            unique_entities.update(memory.semantic_context.mentioned_entities)
            unique_metrics.update(memory.semantic_context.key_metrics)
        
        return {
            'total_exchanges': total_exchanges,
            'unique_entities': list(unique_entities),
            'unique_metrics': list(unique_metrics),
            'current_state': self.current_state.value,
            'state_history': [(state.value, timestamp) for state, timestamp in self.state_history],
            'memory_capability': 'semantic_embeddings' if self.model else 'pattern_matching',
            'similarity_threshold': self.similarity_threshold
        }

# Integration functions for existing chat system
def create_semantic_detector(model_name: str = "all-MiniLM-L6-v2") -> SemanticFollowupDetector:
    """Factory function to create semantic detector"""
    return SemanticFollowupDetector(model_name)

def semantic_followup_detection(message: str,
                               conversation_history: List[Dict] = None,
                               detector: SemanticFollowupDetector = None) -> bool:
    """
    Drop-in replacement for basic follow-up detection
    Maintains backward compatibility while providing semantic capabilities
    """
    if detector is None:
        detector = create_semantic_detector()
    
    result = detector.detect_followup_semantic(message, conversation_history)
    return result['is_followup']

# Example usage and testing
if __name__ == "__main__":
    print("🚀 Semantic Follow-up Detection System")
    print("=" * 60)
    
    # Initialize detector
    detector = create_semantic_detector()
    
    # Test semantic vs pattern matching
    test_cases = [
        "Tell me more about the top artist",
        "What about the second one?", 
        "Can you make a chart of this?",
        "How does this compare to last year?",
        "Show me the details",
        "What are the top artists?",  # This should NOT be a follow-up
        "That's interesting",
        "Why is that the case?",
    ]
    
    # Simulate conversation history
    conversation_history = [
        {
            "user_message": "Show me top artists by sales",
            "assistant_response": {
                "answer": "The top artists are: 1. AC/DC with 1,000 sales, 2. Beatles with 900 sales, 3. Led Zeppelin with 800 sales."
            }
        }
    ]
    
    print("Testing semantic follow-up detection:\n")
    
    for i, message in enumerate(test_cases, 1):
        result = detector.detect_followup_semantic(message, conversation_history)
        
        print(f"Test {i}: '{message}'")
        print(f"  ✅ Follow-up: {result['is_followup']}")
        print(f"  📊 Confidence: {result['confidence']:.3f}")
        print(f"  🎯 Intent: {result['intent']}")
        print(f"  🔍 Method: {result['analysis_method']}")
        print(f"  💡 Suggestions: {result['suggested_actions'][:2]}")
        print()
        
        # Add to memory for next iteration
        detector.add_to_memory(
            message, 
            f"Response to: {message}",
            importance_score=0.7
        )
    
    # Show conversation summary
    print("📊 Conversation Summary:")
    summary = detector.get_conversation_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print(f"\n🎉 Semantic System Test Complete!")
    if detector.model:
        print(f"✅ Using advanced semantic embeddings")
    else:
        print(f"⚠️  Using fallback pattern matching") 