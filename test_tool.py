"""
Test script for the Text-to-SQL tool components.
Run this to verify everything is working correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test environment setup."""
    print("🧪 Testing Environment Setup...")
    print("-" * 40)
    
    # Check for Together AI API key
    api_key = os.getenv("TOGETHER_API_KEY")
    if api_key:
        print("✅ Together AI API key found")
        print(f"   Key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}")
    else:
        print("❌ Together AI API key not found")
        print("   Please set TOGETHER_API_KEY environment variable")
        print("   Get your API key from: https://api.together.xyz/settings/api-keys")
        return False
    
    # Test API connection
    try:
        import requests
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get("https://api.together.xyz/v1/models", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Together AI API accessible")
            models_data = response.json()
            llama_models = [m for m in models_data if "llama" in m.get("id", "").lower()]
            if llama_models:
                print(f"   Available Llama models: {len(llama_models)} found")
            else:
                print("   No Llama models found in response")
        else:
            print(f"❌ Together AI API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Together AI API: {e}")
        return False
    
    # Check for database
    if os.path.exists("chinook.db"):
        print("✅ Chinook database found")
    else:
        print("❌ Chinook database not found")
        print("   Please run: python setup_database.py")
        return False
    
    return True

def test_database_tools():
    """Test database tools and utilities."""
    print("\n🔧 Testing Database Tools...")
    print("-" * 40)
    
    try:
        from database_tools import DatabaseManager, create_database_tools
        
        # Test database manager
        db_manager = DatabaseManager("chinook.db")
        
        # Test table listing
        tables = db_manager.list_tables()
        print(f"✅ Found {len(tables)} tables: {', '.join(tables[:5])}...")
        
        # Test table info
        if tables:
            table_info = db_manager.get_table_info([tables[0]])
            print(f"✅ Retrieved schema info for {tables[0]}")
        
        # Test sample query
        sample_df = db_manager.execute_query("SELECT COUNT(*) as total FROM Artist")
        artist_count = sample_df['total'].iloc[0]
        print(f"✅ Sample query successful: {artist_count} artists in database")
        
        return True
        
    except Exception as e:
        print(f"❌ Database tools test failed: {e}")
        return False

def test_sql_chain():
    """Test SQL chain implementation."""
    print("\n⛓️ Testing SQL Chain...")
    print("-" * 40)
    
    try:
        from sql_chain import SQLChain
        
        # Create chain
        model = os.getenv("TOGETHER_MODEL", "meta-llama/Llama-3-70b-chat-hf")
        api_key = os.getenv("TOGETHER_API_KEY")
        chain = SQLChain("chinook.db", model=model, api_key=api_key)
        print("✅ SQL Chain initialized successfully")
        
        # Test simple query
        result = chain.query("How many artists are in the database?")
        
        if result["success"]:
            print("✅ Chain query successful")
            print(f"   Question: {result['question']}")
            print(f"   Answer: {result['answer']}")
        else:
            print(f"❌ Chain query failed: {result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ SQL Chain test failed: {e}")
        return False

def test_sql_agent():
    """Test SQL agent implementation."""
    print("\n🤖 Testing SQL Agent...")
    print("-" * 40)
    
    try:
        from sql_agent_simple import SimpleSQLAgent
        
        # Create agent
        model = os.getenv("TOGETHER_MODEL", "meta-llama/Llama-3-70b-chat-hf")
        api_key = os.getenv("TOGETHER_API_KEY")
        agent = SimpleSQLAgent("chinook.db", model=model, api_key=api_key)
        print("✅ SQL Agent initialized successfully")
        
        # Test simple query
        result = agent.query("How many customers are there?")
        
        if result["success"]:
            print("✅ Agent query successful")
            print(f"   Question: {result['question']}")
            print(f"   Answer: {result['answer']}")
        else:
            print(f"❌ Agent query failed: {result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ SQL Agent test failed: {e}")
        return False

def test_comparative_performance():
    """Test both approaches on the same questions."""
    print("\n📊 Testing Comparative Performance...")
    print("-" * 40)
    
    try:
        from sql_chain import SQLChain
        from sql_agent_simple import SimpleSQLAgent
        
        model = os.getenv("TOGETHER_MODEL", "meta-llama/Llama-3-70b-chat-hf")
        api_key = os.getenv("TOGETHER_API_KEY")
        chain = SQLChain("chinook.db", model=model, api_key=api_key)
        agent = SimpleSQLAgent("chinook.db", model=model, api_key=api_key)
        
        test_questions = [
            "What are the top 3 selling artists?",
            "How many tracks are there?",
        ]
        
        for question in test_questions:
            print(f"\nQuestion: {question}")
            
            # Test chain
            chain_result = chain.query(question)
            if chain_result["success"]:
                print(f"✅ Chain: {chain_result['answer'][:100]}...")
            else:
                print(f"❌ Chain failed: {chain_result.get('error', 'Unknown')}")
            
            # Test agent
            agent_result = agent.query(question)
            if agent_result["success"]:
                print(f"✅ Agent: {agent_result['answer'][:100]}...")
            else:
                print(f"❌ Agent failed: {agent_result.get('error', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Comparative test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Text-to-SQL Tool Test Suite")
    print("=" * 50)
    
    tests = [
        ("Environment", test_environment),
        ("Database Tools", test_database_tools),
        ("SQL Chain", test_sql_chain),
        ("SQL Agent", test_sql_agent),
        ("Comparative Performance", test_comparative_performance),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name}: PASSED")
            else:
                print(f"\n❌ {test_name}: FAILED")
        except Exception as e:
            print(f"\n❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📋 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Text-to-SQL tool is ready to use.")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Open the web interface in your browser")
        print("3. Start asking questions about the music store!")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 