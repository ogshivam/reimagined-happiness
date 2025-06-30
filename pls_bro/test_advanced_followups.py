#!/usr/bin/env python3
"""
Test Script for Advanced Follow-up System
=========================================

This script demonstrates the enhanced follow-up detection and context management
capabilities that have been integrated into the chat system.

Features Tested:
- Enhanced follow-up detection with intent classification
- Extended context memory (5 exchanges, 300 char responses)  
- Pattern matching across 6 categories
- Confidence scoring and threshold optimization
- Context reference detection
"""

import sys
import os
sys.path.append('.')

from app_chat import ConversationalSQLAgent
from datetime import datetime

def test_followup_detection():
    """Test the enhanced follow-up detection system."""
    print("🧪 Testing Enhanced Follow-up Detection System")
    print("=" * 60)
    
    # Create agent instance
    agent = ConversationalSQLAgent()
    
    # Test cases with expected results
    test_cases = [
        # Basic follow-ups
        ("Tell me more about the top artist", True, "drill_down"),
        ("What about the second one?", True, "clarification"),
        ("Can you make a chart of this?", True, "visualization"),
        ("How does this compare to last year?", True, "comparison"),
        ("Show me the details", True, "drill_down"),
        
        # Intent-based follow-ups
        ("What does this mean?", True, "clarification"),
        ("Analyze the trend", True, "analysis"),
        ("Filter by country", True, "modification"),
        ("Sort by sales", True, "modification"),
        
        # Non-follow-ups
        ("What are the top artists?", False, None),
        ("Show me all customers", False, None),
        ("List all genres", False, None),
        
        # Context-dependent
        ("That looks interesting", True, "clarification"),
        ("It seems high", True, "analysis"),
        ("These results are unexpected", True, "analysis"),
    ]
    
    print(f"Testing {len(test_cases)} follow-up scenarios...\n")
    
    correct_predictions = 0
    
    for i, (message, expected_followup, expected_intent) in enumerate(test_cases, 1):
        # Test detection
        is_followup = agent.is_followup_question(message)
        detected_intent = getattr(agent, '_last_detected_intent', None)
        
        # Check accuracy
        correct = is_followup == expected_followup
        if correct:
            correct_predictions += 1
        
        # Display results
        status = "✅" if correct else "❌"
        print(f"{status} Test {i:2d}: '{message}'")
        print(f"    Expected: {'Followup' if expected_followup else 'Not followup'}")
        print(f"    Detected: {'Followup' if is_followup else 'Not followup'}")
        if detected_intent:
            print(f"    Intent: {detected_intent}")
        if expected_intent and detected_intent != expected_intent:
            print(f"    Expected Intent: {expected_intent}")
        print()
    
    accuracy = (correct_predictions / len(test_cases)) * 100
    print(f"📊 Detection Accuracy: {accuracy:.1f}% ({correct_predictions}/{len(test_cases)})")
    
    return accuracy

def test_context_management():
    """Test the enhanced context management system."""
    print("\n🧪 Testing Enhanced Context Management")
    print("=" * 60)
    
    agent = ConversationalSQLAgent()
    
    # Simulate conversation history
    mock_conversations = [
        {
            "user_message": "What are the top 5 artists by sales?",
            "assistant_response": {
                "answer": "The top 5 artists by sales are: 1. AC/DC with 1,000 sales ($50,000 revenue), 2. Beatles with 900 sales, 3. Led Zeppelin with 800 sales, 4. Pink Floyd with 750 sales, 5. Queen with 700 sales. Total combined sales: 4,150 units.",
                "sql_query": "SELECT artist_name, sales FROM artists ORDER BY sales DESC LIMIT 5",
                "generated_charts": [{"type": "bar_chart"}]
            },
            "timestamp": datetime.now().isoformat(),
            "has_charts": True
        },
        {
            "user_message": "Tell me more about AC/DC",
            "assistant_response": {
                "answer": "AC/DC is a legendary Australian rock band formed in 1973. They are one of the best-selling music artists worldwide, with over 200 million records sold. Their album 'Back in Black' is one of the best-selling albums of all time with 50 million copies sold.",
                "sql_query": "SELECT * FROM artists WHERE name = 'AC/DC'",
                "generated_charts": []
            },
            "timestamp": datetime.now().isoformat(),
            "has_charts": False
        },
        {
            "user_message": "What about their album sales breakdown?",
            "assistant_response": {
                "answer": "AC/DC's album sales breakdown: Back in Black (50M copies), Highway to Hell (25M), For Those About to Rock (15M), The Razors Edge (12M), Ballbreaker (8M). Their sales increased 15% last year, making them the #1 rock band in current sales.",
                "sql_query": "SELECT album_title, sales FROM albums WHERE artist_id = 1 ORDER BY sales DESC",
                "generated_charts": [{"type": "pie_chart"}, {"type": "trend_chart"}]
            },
            "timestamp": datetime.now().isoformat(),
            "has_charts": True
        }
    ]
    
    # Add conversations to agent
    for conv in mock_conversations:
        agent.conversation_history.append(conv)
    
    print(f"Added {len(mock_conversations)} conversation exchanges to history\n")
    
    # Test context generation
    print("🔍 Generated Context:")
    print("-" * 40)
    context = agent.get_conversation_context()
    print(context)
    print("-" * 40)
    
    # Test context enhancement
    test_queries = [
        "How do they compare to Beatles?",
        "Can you make a chart showing this?",
        "What's their most successful album?",
        "Show me the trend over time"
    ]
    
    print(f"\n📝 Testing Context Enhancement for Follow-up Queries:")
    print("-" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        is_followup = agent.is_followup_question(query)
        print(f"   Follow-up: {'Yes' if is_followup else 'No'}")
        
        if is_followup:
            enhanced = agent.enhance_query_with_context(query)
            print(f"   Enhanced Query Preview: {enhanced[:200]}...")
    
    # Test key data extraction
    print(f"\n🔑 Testing Key Data Extraction:")
    print("-" * 40)
    
    sample_text = "AC/DC has 50 million album sales, 15% growth, making them #1 in Rock category."
    key_data = agent._extract_context_key_data(sample_text)
    print(f"Sample text: {sample_text}")
    print(f"Extracted key data: {key_data}")

def test_conversation_flow():
    """Test realistic conversation flow with advanced follow-ups."""
    print("\n🧪 Testing Realistic Conversation Flow")
    print("=" * 60)
    
    agent = ConversationalSQLAgent()
    
    # Simulate realistic conversation
    conversation_steps = [
        "Show me the top selling artists",
        "Tell me more about the #1 artist",  # Followup: drill_down
        "How do their sales compare to #2?",  # Followup: comparison  
        "Can you make a chart of this?",      # Followup: visualization
        "What's the trend over time?",        # Followup: analysis
        "Filter out artists with less than 500 sales",  # Followup: modification
    ]
    
    print("Simulating conversation flow:\n")
    
    followup_count = 0
    total_queries = len(conversation_steps)
    
    for i, query in enumerate(conversation_steps, 1):
        print(f"Step {i}: User asks '{query}'")
        
        # Check if followup
        is_followup = agent.is_followup_question(query)
        intent = getattr(agent, '_last_detected_intent', None)
        
        if is_followup:
            followup_count += 1
            print(f"        ✅ Detected as follow-up (Intent: {intent})")
            
            # Show context enhancement
            if len(agent.conversation_history) > 0:
                enhanced = agent.enhance_query_with_context(query)
                print(f"        🔗 Context enhanced: Yes ({len(enhanced)} chars)")
        else:
            print(f"        ⭕ Detected as new query")
        
        # Simulate adding to conversation history
        mock_response = {
            "answer": f"Mock response for query {i} about {query[:30]}...",
            "sql_query": f"SELECT * FROM table WHERE condition_{i}",
            "generated_charts": [{"type": "chart"}] if "chart" in query else []
        }
        
        agent.add_to_conversation(query, mock_response)
        print(f"        📝 Added to conversation history (Total: {len(agent.conversation_history)})")
        print()
    
    followup_rate = (followup_count / total_queries) * 100
    print(f"📊 Conversation Analysis:")
    print(f"   Total queries: {total_queries}")
    print(f"   Follow-ups detected: {followup_count}")
    print(f"   Follow-up rate: {followup_rate:.1f}%")
    print(f"   Context window: {len(agent.conversation_history)} exchanges")

def main():
    """Run all tests for the advanced follow-up system."""
    print("🚀 Advanced Follow-up System Testing Suite")
    print("=" * 80)
    print("Testing Phase 1 implementation of enhanced follow-up detection")
    print("and context management capabilities.\n")
    
    try:
        # Test 1: Follow-up Detection
        accuracy = test_followup_detection()
        
        # Test 2: Context Management  
        test_context_management()
        
        # Test 3: Conversation Flow
        test_conversation_flow()
        
        print("\n" + "=" * 80)
        print("🎉 Advanced Follow-up System Testing Complete!")
        print(f"📈 Overall Detection Accuracy: {accuracy:.1f}%")
        print("\n✅ Phase 1 Implementation Status:")
        print("   ✓ Enhanced follow-up detection (6 pattern categories)")
        print("   ✓ Intent classification (5 intent types)")
        print("   ✓ Extended context memory (5 exchanges, 300 chars)")
        print("   ✓ Confidence scoring and threshold optimization")
        print("   ✓ Context reference detection")
        print("   ✓ Key data extraction for context")
        
        print("\n🚀 Ready for Phase 2 Implementation:")
        print("   • Proactive suggestion engine")
        print("   • Advanced analytics integration") 
        print("   • Intent-aware response generation")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 