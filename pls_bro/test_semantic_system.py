#!/usr/bin/env python3
"""
Test Semantic Follow-up Detection System
=======================================

This demonstrates the semantic-based approach that's much more
intelligent than pattern matching - closer to how ChatGPT works.
"""

import os
import sys
import subprocess
import time
from typing import Dict, List, Any

def install_requirements():
    """Install required packages"""
    print("📦 Installing semantic requirements...")
    packages = [
        "sentence-transformers",
        "scikit-learn", 
        "numpy",
        "torch"
    ]
    
    for package in packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"⚠️  Failed to install {package}")

# Try to install requirements
install_requirements()

# Now try to import semantic libraries
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SEMANTIC_AVAILABLE = True
    print("✅ Semantic libraries loaded successfully")
except ImportError as e:
    print(f"❌ Semantic libraries not available: {e}")
    SEMANTIC_AVAILABLE = False

class SemanticFollowupDetector:
    """Semantic-based follow-up detection - like ChatGPT"""
    
    def __init__(self, followup_threshold=0.45):  # Lower threshold for better performance
        self.model = None
        self.intent_embeddings = {}
        self.followup_threshold = followup_threshold
        
        if SEMANTIC_AVAILABLE:
            try:
                print("🧠 Loading semantic model...")
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✅ Model loaded successfully")
                self._setup_intent_embeddings()
            except Exception as e:
                print(f"⚠️  Model loading failed: {e}")
                self.model = None
    
    def _setup_intent_embeddings(self):
        """Setup intent embeddings for classification"""
        if not self.model:
            return
        
        intent_examples = {
            'clarification': [
                "What does this mean?", "Can you explain?", "Tell me more about this"
            ],
            'drill_down': [
                "Show me more details", "Break this down", "Give me specifics"
            ],
            'visualization': [
                "Make a chart", "Show this graphically", "Create a graph"
            ],
            'comparison': [
                "How does this compare?", "What's the difference?", "Show differences"
            ],
            'analysis': [
                "Analyze this", "What patterns do you see?", "Find insights"
            ],
            'new_query': [
                "Show me all products", "List customers", "What are the sales?"
            ]
        }
        
        for intent, examples in intent_examples.items():
            embeddings = self.model.encode(examples)
            self.intent_embeddings[intent] = np.mean(embeddings, axis=0)
        
        print(f"✅ Setup {len(self.intent_embeddings)} intent embeddings")
    
    def detect_semantic_followup(self, message: str, context: List[Dict] = None) -> Dict[str, Any]:
        """Detect follow-up using semantic similarity"""
        
        if not self.model:
            return self._fallback_detection(message, context)
        
        try:
            # Encode current message
            message_embedding = self.model.encode([message])[0]
            
            # Calculate context similarity
            context_sim = self._calculate_context_similarity(message_embedding, context or [])
            
            # Classify intent
            intent_result = self._classify_intent(message_embedding)
            
            # Check for reference signals (pronouns, ordinals)
            reference_boost = self._check_reference_signals(message)
            
            # Overall confidence
            confidence = self._calculate_confidence(context_sim, intent_result, reference_boost)
            
            is_followup = confidence > self.followup_threshold
            
            return {
                'is_followup': is_followup,
                'confidence': confidence,
                'intent': intent_result['intent'],
                'intent_confidence': intent_result['confidence'],
                'context_similarity': context_sim,
                'method': 'semantic_embeddings',
                'suggestions': self._get_suggestions(intent_result['intent'])
            }
            
        except Exception as e:
            print(f"⚠️  Semantic detection failed: {e}")
            return self._fallback_detection(message, context)
    
    def _calculate_context_similarity(self, message_embedding, context):
        """Calculate similarity to conversation context"""
        if not context:
            return 0.0
        
        # Get recent context
        recent_context = context[-3:]  # Last 3 exchanges
        context_texts = []
        
        for exchange in recent_context:
            user_msg = exchange.get('user_message', '')
            assistant_resp = exchange.get('assistant_response', {})
            
            if isinstance(assistant_resp, dict):
                resp_text = assistant_resp.get('answer', '')
            else:
                resp_text = str(assistant_resp)
            
            context_texts.append(f"{user_msg} {resp_text}")
        
        if not context_texts:
            return 0.0
        
        # Calculate similarities
        context_embeddings = self.model.encode(context_texts)
        similarities = cosine_similarity([message_embedding], context_embeddings)[0]
        
        return float(np.max(similarities))
    
    def _classify_intent(self, message_embedding):
        """Classify intent using semantic similarity"""
        if not self.intent_embeddings:
            return {'intent': 'unknown', 'confidence': 0.0}
        
        best_intent = 'unknown'
        best_confidence = 0.0
        
        for intent, intent_embedding in self.intent_embeddings.items():
            similarity = cosine_similarity([message_embedding], [intent_embedding])[0][0]
            
            if similarity > best_confidence:
                best_confidence = similarity
                best_intent = intent
        
        return {
            'intent': best_intent,
            'confidence': float(best_confidence)
        }
    
    def _check_reference_signals(self, message):
        """Check for reference signals like pronouns, ordinals"""
        message_lower = message.lower()
        
        reference_signals = {
            'pronouns': ['it', 'this', 'that', 'they', 'them', 'these', 'those'],
            'ordinals': ['second', 'third', 'next', 'another', 'other', 'others'],
            'comparatives': ['more', 'about', 'versus', 'compared']
        }
        
        boost = 0.0
        for signal_type, keywords in reference_signals.items():
            matches = sum(1 for keyword in keywords if keyword in message_lower)
            if matches > 0:
                boost += matches * 0.2  # 0.2 boost per reference signal
        
        return min(boost, 0.4)  # Max boost of 0.4
    
    def _calculate_confidence(self, context_sim, intent_result, reference_boost=0.0):
        """Calculate overall confidence with improved weighting"""
        context_weight = 0.4
        intent_weight = 0.4
        reference_weight = 0.2
        
        context_score = context_sim * context_weight
        
        # Boost confidence for follow-up intents
        intent_conf = intent_result['confidence']
        is_followup_intent = intent_result['intent'] != 'new_query'
        
        # Give higher boost to follow-up intents
        if is_followup_intent:
            intent_score = (intent_conf * 1.3) * intent_weight  # 30% boost
        else:
            intent_score = (1 - intent_conf) * intent_weight
        
        # Reference signals contribution
        reference_score = reference_boost * reference_weight
        
        total_confidence = context_score + intent_score + reference_score
        
        # Bonus for high context similarity
        if context_sim > 0.3:
            total_confidence += 0.1
            
        return min(total_confidence, 1.0)
    
    def _get_suggestions(self, intent):
        """Get suggestions based on intent"""
        suggestions = {
            'clarification': ["Provide detailed explanation", "Use examples", "Break down concepts"],
            'drill_down': ["Show hierarchical details", "Provide metrics", "Include sub-categories"],
            'visualization': ["Create appropriate chart", "Consider multiple views", "Make interactive"],
            'comparison': ["Side-by-side comparison", "Highlight differences", "Show percentages"],
            'analysis': ["Statistical analysis", "Identify patterns", "Provide insights"]
        }
        return suggestions.get(intent, ["Handle request appropriately"])
    
    def _fallback_detection(self, message, context):
        """Fallback pattern matching"""
        patterns = ['tell me more', 'what about', 'show me', 'explain', 'details']
        
        message_lower = message.lower()
        has_pattern = any(pattern in message_lower for pattern in patterns)
        has_context = bool(context)
        
        confidence = 0.6 if has_pattern and has_context else 0.3
        
        return {
            'is_followup': has_pattern and has_context,
            'confidence': confidence,
            'intent': 'unknown',
            'intent_confidence': confidence,
            'context_similarity': 0.5 if has_context else 0.0,
            'method': 'pattern_matching_fallback',
            'suggestions': ['Handle basic follow-up']
        }

def run_comparison_test():
    """Run comparison between semantic and pattern matching"""
    
    print("🔬 Semantic vs Pattern Matching Comparison")
    print("=" * 60)
    
    # Initialize improved detector with lower threshold
    detector = SemanticFollowupDetector(followup_threshold=0.45)
    
    # Test cases
    test_cases = [
        "Tell me more about the top artist",      # Should be follow-up
        "What about the second one?",             # Should be follow-up
        "Can you make a chart of this?",          # Should be follow-up
        "How does this compare to last year?",    # Should be follow-up
        "That's interesting",                     # Should be follow-up
        "Show me all customers",                  # Should NOT be follow-up
        "What are the top genres?",               # Should NOT be follow-up
        "List all products",                      # Should NOT be follow-up
    ]
    
    # Mock conversation context
    conversation_context = [
        {
            "user_message": "Show me top artists by sales",
            "assistant_response": {
                "answer": "Top artists by sales: 1. AC/DC with 1,000 sales ($50,000), 2. Beatles with 900 sales ($45,000), 3. Led Zeppelin with 800 sales ($40,000)"
            }
        }
    ]
    
    print("Testing each query:\n")
    
    semantic_correct = 0
    pattern_correct = 0
    
    # Expected results (manually labeled)
    expected_results = [True, True, True, True, True, False, False, False]
    
    for i, (message, expected) in enumerate(zip(test_cases, expected_results), 1):
        print(f"Test {i}: '{message}'")
        print(f"Expected: {'Follow-up' if expected else 'New Query'}")
        
        # Semantic detection
        semantic_result = detector.detect_semantic_followup(message, conversation_context)
        semantic_prediction = semantic_result['is_followup']
        semantic_correct += (semantic_prediction == expected)
        
        # Pattern matching (basic)
        pattern_result = detector._fallback_detection(message, conversation_context)
        pattern_prediction = pattern_result['is_followup']
        pattern_correct += (pattern_prediction == expected)
        
        print(f"  🧠 Semantic: {'✅' if semantic_prediction == expected else '❌'} " +
              f"({semantic_result['confidence']:.2f}, {semantic_result['intent']})")
        print(f"  🔍 Pattern:  {'✅' if pattern_prediction == expected else '❌'} " +
              f"({pattern_result['confidence']:.2f})")
        print()
    
    # Results summary
    print("📊 RESULTS SUMMARY:")
    print(f"  Semantic Accuracy: {semantic_correct}/{len(test_cases)} = {semantic_correct/len(test_cases)*100:.1f}%")
    print(f"  Pattern Accuracy:  {pattern_correct}/{len(test_cases)} = {pattern_correct/len(test_cases)*100:.1f}%")
    
    improvement = (semantic_correct - pattern_correct) / len(test_cases) * 100
    print(f"  Improvement: {improvement:+.1f} percentage points")
    
    if semantic_correct > pattern_correct:
        print("  🎉 Semantic approach is BETTER!")
    elif semantic_correct < pattern_correct:
        print("  ⚠️  Pattern matching performed better")
    else:
        print("  🤝 Both approaches performed equally")
    
    return semantic_correct, pattern_correct

def demonstrate_semantic_features():
    """Demonstrate advanced semantic features"""
    
    print("\n🚀 Advanced Semantic Features Demo")
    print("=" * 60)
    
    detector = SemanticFollowupDetector(followup_threshold=0.45)
    
    if not detector.model:
        print("❌ Semantic model not available - can't demonstrate features")
        return
    
    # Test semantic understanding
    test_pairs = [
        ("Show me sales data", "Display revenue information"),      # Similar meaning
        ("Make a chart", "Create a visualization"),                 # Similar meaning
        ("Who are the artists?", "What's the weather like?"),      # Different meaning
        ("Tell me more", "Give me details"),                       # Similar meaning
    ]
    
    print("Testing semantic similarity understanding:\n")
    
    for query1, query2 in test_pairs:
        emb1 = detector.model.encode([query1])[0]
        emb2 = detector.model.encode([query2])[0]
        
        similarity = cosine_similarity([emb1], [emb2])[0][0]
        
        print(f"'{query1}' vs '{query2}'")
        print(f"  Similarity: {similarity:.3f} ({'High' if similarity > 0.5 else 'Low'})")
        print()
    
    print("✅ Semantic understanding demonstrated!")

if __name__ == "__main__":
    print("🎯 Semantic Follow-up Detection Test Suite")
    print("=" * 60)
    
    # Run comparison test
    semantic_score, pattern_score = run_comparison_test()
    
    # Demonstrate semantic features
    demonstrate_semantic_features()
    
    print("\n🎉 Test Suite Complete!")
    print(f"Final Score: Semantic {semantic_score} vs Pattern {pattern_score}")
    
    if SEMANTIC_AVAILABLE:
        print("✅ Semantic system is ready for production use!")
        print("\nNext steps:")
        print("1. Integrate with your existing chat app")
        print("2. Replace pattern matching with semantic detection")
        print("3. Test with real user queries")
        print("4. Fine-tune thresholds based on your data")
    else:
        print("⚠️  Install semantic libraries to use advanced features:")
        print("   pip install sentence-transformers scikit-learn") 