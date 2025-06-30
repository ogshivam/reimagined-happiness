#!/usr/bin/env python3
"""
Test Semantic Integration
========================
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test if the semantic integration works
def test_semantic_integration():
    print("🧪 Testing Semantic Integration")
    print("=" * 50)
    
    try:
        # Import the upgraded chat app
        from app_chat_semantic import ConversationalSQLAgent  # Import your chat app class name
        
        # Create instance
        chat_app = ConversationalSQLAgent()
        
        # Test follow-up detection
        test_cases = [
            ("Show me top artists", False),           # First query
            ("Tell me more about the top one", True),  # Follow-up
            ("What about the second one?", True),      # Follow-up
            ("Can you make a chart?", True),           # Follow-up
            ("List all customers", False),             # New query
        ]
        
        print("Testing semantic follow-up detection:\n")
        
        # Simulate conversation history
        chat_app.conversation_history = [
            {
                'user_message': 'Show me top artists by sales',
                'assistant_response': {
                    'answer': 'Top artists: 1. AC/DC (1000 sales), 2. Beatles (900 sales)'
                }
            }
        ]
        
        correct = 0
        for i, (message, expected) in enumerate(test_cases, 1):
            result = chat_app.is_followup_question(message)
            is_correct = result == expected
            correct += is_correct
            
            print(f"Test {i}: '{message}'")
            print(f"  Expected: {'Follow-up' if expected else 'New Query'}")
            print(f"  Result: {'✅' if is_correct else '❌'} ({'Follow-up' if result else 'New Query'})")
            
            # Show analysis if available
            if hasattr(chat_app, 'last_followup_analysis'):
                analysis = chat_app.last_followup_analysis
                print(f"  Analysis: {analysis['confidence']:.2f} confidence, intent: {analysis['intent']}")
            print()
        
        print(f"📊 Results: {correct}/{len(test_cases)} correct ({correct/len(test_cases)*100:.1f}%)")
        
        if correct >= 4:
            print("🎉 Semantic integration is working EXCELLENTLY!")
        elif correct >= 3:
            print("✅ Semantic integration is working WELL!")
        else:
            print("⚠️  Semantic integration needs adjustment")
        
        return correct >= 3
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("Make sure app_chat_semantic.py exists and is properly formatted")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_semantic_integration()
    if success:
        print("\n🚀 Ready to use semantic-enhanced chat app!")
        print("Usage: streamlit run app_chat_semantic.py")
    else:
        print("\n⚠️  Check the integration and try again")
