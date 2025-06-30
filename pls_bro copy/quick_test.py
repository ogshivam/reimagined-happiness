#!/usr/bin/env python3
"""
Quick Test Script for Enhanced Text-to-SQL Application
Tests basic functionality of all three approaches with a simple query
"""

import os
import sys
import time
from datetime import datetime

# Set API key
os.environ["TOGETHER_API_KEY"] = "tgp_v1_XELYRCJuDTY69-ICL7OBEONSAYquezhyLAMfyi5-Cgc"

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """Test basic functionality of all approaches."""
    print("🚀 Quick Test - Enhanced Text-to-SQL Application")
    print("=" * 50)
    print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔑 API Key: ✅ Configured")
    
    # Simple test query
    test_query = "How many artists are in the database?"
    print(f"🔍 Test Query: {test_query}")
    print("-" * 50)
    
    results = {"passed": 0, "failed": 0, "tests": []}
    
    # Test 1: SQL Chain
    print("\n⚡ Testing SQL Chain...")
    try:
        from sql_chain import SQLChain
        
        start_time = time.time()
        chain = SQLChain("chinook.db")
        result = chain.query(test_query)
        execution_time = time.time() - start_time
        
        if result.get("success", False):
            print(f"✅ SQL Chain Success ({execution_time:.2f}s)")
            print(f"   Answer: {result['answer'][:100]}...")
            results["passed"] += 1
        else:
            print(f"❌ SQL Chain Failed: {result.get('answer', 'Unknown error')}")
            results["failed"] += 1
        
        results["tests"].append(("SQL Chain", result.get("success", False), execution_time))
        
    except Exception as e:
        print(f"❌ SQL Chain Error: {str(e)}")
        results["failed"] += 1
        results["tests"].append(("SQL Chain", False, 0))
    
    # Test 2: Simple Agent
    print("\n🤖 Testing Simple Agent...")
    try:
        from sql_agent_simple import SimpleSQLAgent
        
        start_time = time.time()
        agent = SimpleSQLAgent("chinook.db")
        result = agent.query(test_query)
        execution_time = time.time() - start_time
        
        if result.get("success", False):
            print(f"✅ Simple Agent Success ({execution_time:.2f}s)")
            print(f"   Answer: {result['answer'][:100]}...")
            results["passed"] += 1
        else:
            print(f"❌ Simple Agent Failed: {result.get('error', 'Unknown error')}")
            results["failed"] += 1
        
        results["tests"].append(("Simple Agent", result.get("success", False), execution_time))
        
    except Exception as e:
        print(f"❌ Simple Agent Error: {str(e)}")
        results["failed"] += 1
        results["tests"].append(("Simple Agent", False, 0))
    
    # Test 3: Enhanced Agent
    print("\n🚀 Testing Enhanced Agent...")
    try:
        from sql_agent_enhanced import create_enhanced_sql_agent
        
        start_time = time.time()
        enhanced_agent = create_enhanced_sql_agent("chinook.db")
        result = enhanced_agent.query(test_query)
        execution_time = time.time() - start_time
        
        if result.get("success", False):
            charts_count = len(result.get("generated_charts", []))
            insights_count = len(result.get("visualization_insights", []))
            
            print(f"✅ Enhanced Agent Success ({execution_time:.2f}s)")
            print(f"   Answer: {result['answer'][:100]}...")
            print(f"   📊 Charts: {charts_count}, 💡 Insights: {insights_count}")
            results["passed"] += 1
        else:
            print(f"❌ Enhanced Agent Failed: {result.get('answer', 'Unknown error')}")
            results["failed"] += 1
        
        results["tests"].append(("Enhanced Agent", result.get("success", False), execution_time))
        
    except Exception as e:
        print(f"❌ Enhanced Agent Error: {str(e)}")
        results["failed"] += 1
        results["tests"].append(("Enhanced Agent", False, 0))
    
    # Final Results
    print("\n" + "=" * 50)
    print("📊 QUICK TEST RESULTS")
    print("=" * 50)
    
    total_tests = results["passed"] + results["failed"]
    success_rate = (results["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📈 Overall Success Rate: {success_rate:.1f}% ({results['passed']}/{total_tests})")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    
    print("\n📋 Test Details:")
    for test_name, success, exec_time in results["tests"]:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {test_name} ({exec_time:.2f}s)")
    
    if results["passed"] == total_tests:
        print("\n🎉 All tests passed! Your app is working correctly.")
        print("💡 You can now run: streamlit run app_enhanced.py")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
    
    return results

def main():
    """Main function."""
    # Check prerequisites
    if not os.path.exists("chinook.db"):
        print("❌ Error: chinook.db not found!")
        print("Make sure you're running this from the correct directory.")
        sys.exit(1)
    
    if not os.path.exists("app_enhanced.py"):
        print("❌ Error: app_enhanced.py not found!")
        print("Make sure you're running this from the correct directory.")
        sys.exit(1)
    
    # Run tests
    results = test_basic_functionality()
    
    # Ask if user wants to run the app
    if results["passed"] > 0:
        print("\n" + "-" * 50)
        try:
            response = input("🚀 Would you like to start the Streamlit app now? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                print("🌐 Starting Streamlit app...")
                os.system("streamlit run app_enhanced.py")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")

if __name__ == "__main__":
    main() 