#!/usr/bin/env python3
"""
Test Script for the SQL Chat Application
Tests the conversational capabilities and context management
"""

import os
import sys
import time
from datetime import datetime

# Set API key
os.environ["TOGETHER_API_KEY"] = "tgp_v1_XELYRCJuDTY69-ICL7OBEONSAYquezhyLAMfyi5-Cgc"

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_chat_functionality():
    """Test the chat app's conversational capabilities."""
    print("💬 Testing SQL Chat Application")
    print("=" * 50)
    print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔑 API Key: ✅ Configured")
    
    try:
        # Import the chat app components
        from app_chat import ConversationalSQLAgent
        
        # Initialize the conversational agent
        print("\n🤖 Initializing Conversational SQL Agent...")
        chat_agent = ConversationalSQLAgent()
        
        # Get API key and initialize
        api_key = os.getenv("TOGETHER_API_KEY")
        if not chat_agent.initialize_agent(api_key):
            print("❌ Failed to initialize chat agent")
            return False
        
        print("✅ Chat Agent initialized successfully")
        
        # Test conversation flow
        print("\n🗣️ Testing Conversation Flow...")
        print("-" * 30)
        
        # Conversation test scenarios
        test_conversations = [
            {
                "scenario": "Initial Query",
                "messages": [
                    "What are the top 5 selling artists by total sales?"
                ]
            },
            {
                "scenario": "Follow-up Question",
                "messages": [
                    "What are the top 5 selling artists by total sales?",
                    "Tell me more about the top artist from those results"
                ]
            },
            {
                "scenario": "Comparison Query",
                "messages": [
                    "Show me revenue by country",
                    "Compare this with sales by media type"
                ]
            },
            {
                "scenario": "Context-aware Query",
                "messages": [
                    "What is the most popular genre?",
                    "Show me the artists in that genre",
                    "What about their album sales?"
                ]
            }
        ]
        
        results = {"total_scenarios": 0, "passed": 0, "failed": 0}
        
        for scenario in test_conversations:
            print(f"\n📋 Testing Scenario: {scenario['scenario']}")
            print("=" * 40)
            
            # Reset agent for each scenario
            chat_agent.conversation_history = []
            
            scenario_passed = True
            
            for i, message in enumerate(scenario['messages'], 1):
                print(f"\n{i}. User: {message}")
                
                start_time = time.time()
                try:
                    result = chat_agent.query(message)
                    execution_time = time.time() - start_time
                    
                    if result.get("success", False):
                        print(f"   ✅ Response ({execution_time:.2f}s)")
                        print(f"   📝 Answer: {result['answer'][:100]}...")
                        
                        # Check for follow-up detection
                        if i > 1:
                            is_followup = result.get("is_followup", False)
                            print(f"   🔄 Follow-up detected: {'✅ Yes' if is_followup else '❌ No'}")
                        
                        # Check for charts
                        charts_count = len(result.get("generated_charts", []))
                        if charts_count > 0:
                            print(f"   📊 Charts generated: {charts_count}")
                        
                        # Check for insights
                        insights_count = len(result.get("visualization_insights", []))
                        if insights_count > 0:
                            print(f"   💡 Insights provided: {insights_count}")
                        
                    else:
                        print(f"   ❌ Failed: {result.get('answer', 'Unknown error')}")
                        scenario_passed = False
                    
                except Exception as e:
                    print(f"   ❌ Exception: {str(e)}")
                    scenario_passed = False
                
                # Brief pause between messages
                time.sleep(1)
            
            # Scenario results
            results["total_scenarios"] += 1
            if scenario_passed:
                results["passed"] += 1
                print(f"\n✅ Scenario '{scenario['scenario']}' PASSED")
            else:
                results["failed"] += 1
                print(f"\n❌ Scenario '{scenario['scenario']}' FAILED")
            
            # Show conversation context
            context = chat_agent.get_conversation_context()
            if context:
                print(f"\n🧠 Context Length: {len(context)} characters")
                print(f"📚 Conversation History: {len(chat_agent.conversation_history)} exchanges")
        
        # Final results
        print("\n" + "=" * 50)
        print("📊 CHAT APP TEST RESULTS")
        print("=" * 50)
        
        total_scenarios = results["total_scenarios"]
        passed_scenarios = results["passed"]
        success_rate = (passed_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0
        
        print(f"📈 Success Rate: {success_rate:.1f}% ({passed_scenarios}/{total_scenarios})")
        print(f"✅ Passed Scenarios: {passed_scenarios}")
        print(f"❌ Failed Scenarios: {results['failed']}")
        
        # Test specific chat features
        print("\n🧪 Testing Chat Features...")
        print("-" * 30)
        
        # Test follow-up detection
        test_messages = [
            ("What are the top artists?", False),
            ("Tell me more about those results", True),
            ("Show me more details", True),
            ("What about the albums?", True),
            ("How many customers are there?", False)
        ]
        
        feature_tests = {"passed": 0, "total": 0}
        
        for message, expected_followup in test_messages:
            detected_followup = chat_agent.is_followup_question(message)
            feature_tests["total"] += 1
            
            if detected_followup == expected_followup:
                feature_tests["passed"] += 1
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
            
            print(f"{status} Follow-up detection: '{message}' -> {detected_followup}")
        
        feature_success_rate = (feature_tests["passed"] / feature_tests["total"] * 100)
        print(f"\n🎯 Feature Detection Accuracy: {feature_success_rate:.1f}%")
        
        # Overall assessment
        if success_rate >= 75 and feature_success_rate >= 80:
            print("\n🎉 Chat App is working excellently!")
            print("💡 Ready for conversational SQL queries with context awareness.")
            return True
        elif success_rate >= 50:
            print("\n⚠️ Chat App is working but may have some issues.")
            print("💡 Consider reviewing failed scenarios above.")
            return True
        else:
            print("\n❌ Chat App has significant issues.")
            print("💡 Please review the errors and check dependencies.")
            return False
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure app_chat.py is in the current directory.")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def main():
    """Main test function."""
    # Check prerequisites
    if not os.path.exists("chinook.db"):
        print("❌ Error: chinook.db not found!")
        print("Make sure you're running this from the correct directory.")
        sys.exit(1)
    
    if not os.path.exists("app_chat.py"):
        print("❌ Error: app_chat.py not found!")
        print("Make sure the chat app file is in the current directory.")
        sys.exit(1)
    
    # Run chat tests
    success = test_chat_functionality()
    
    # Offer to start the chat app
    if success:
        print("\n" + "-" * 50)
        try:
            response = input("🚀 Would you like to start the Chat App now? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                print("💬 Starting Chat App...")
                print("🌐 The app will open at: http://localhost:8501")
                print("Press Ctrl+C to stop the app when done.")
                time.sleep(2)
                os.system("streamlit run app_chat.py")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
    else:
        print("\n💡 Fix the issues above before running the Chat App.")

if __name__ == "__main__":
    main() 