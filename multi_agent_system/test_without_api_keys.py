#!/usr/bin/env python3
"""
Test script for components that work without API keys
This allows users to verify the system is working even without Together AI credentials
"""

import sys
import traceback
from typing import Dict, Any
import pandas as pd
from datetime import datetime

def test_database():
    """Test database connectivity and operations"""
    try:
        from database.models import DatabaseManager
        print("🗄️  Testing Database...")
        
        db = DatabaseManager()
        
        # Test connection
        tables = db.get_tables()
        print(f"   ✅ Connected to database with {len(tables)} tables")
        
        # Test query execution
        result, metadata = db.execute_query("SELECT COUNT(*) as artist_count FROM Artist")
        artist_count = result.iloc[0]['artist_count']
        print(f"   ✅ Found {artist_count} artists in database")
        
        # Test sample data
        sample_data = db.get_sample_data("Album", 3)
        print(f"   ✅ Retrieved {len(sample_data)} sample albums")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Database test failed: {str(e)}")
        return False

def test_vector_store():
    """Test vector store operations"""
    try:
        from memory.vector_store import ConversationVectorStore
        print("🧠 Testing Vector Store...")
        
        vs = ConversationVectorStore()
        
        # Test adding conversation
        session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        conversation_id = vs.add_conversation(
            session_id=session_id,
            user_message="What are the top selling albums?",
            assistant_response="Here are the top selling albums...",
            metadata={"test": True}
        )
        print(f"   ✅ Added conversation with ID: {conversation_id[:8]}...")
        
        # Test searching conversations
        results = vs.search_conversations("top selling albums", limit=3)
        print(f"   ✅ Found {len(results)} similar conversations")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Vector store test failed: {str(e)}")
        return False

def test_visualization():
    """Test visualization generation"""
    try:
        from agents.visualization_agent import VisualizationAgent
        print("📊 Testing Visualization...")
        
        va = VisualizationAgent()
        
        # Create sample data
        sample_data = pd.DataFrame({
            'Artist': ['The Beatles', 'Elvis Presley', 'Michael Jackson', 'Madonna', 'Elton John'],
            'Albums': [23, 18, 15, 12, 10],
            'Sales_Million': [183, 146, 140, 120, 101]
        })
        
        # Test visualization creation
        charts = va.create_visualizations(sample_data, "Top Artists by Album Sales")
        print(f"   ✅ Generated {len(charts)} visualizations")
        
        # Test chart types
        chart_types = [chart.get('type', 'unknown') for chart in charts]
        print(f"   ✅ Chart types: {', '.join(chart_types)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Visualization test failed: {str(e)}")
        return False

def test_export():
    """Test export functionality"""
    try:
        from agents.export_agent import ExportAgent
        print("📤 Testing Export...")
        
        ea = ExportAgent()
        
        # Create sample data
        sample_data = pd.DataFrame({
            'Genre': ['Rock', 'Pop', 'Jazz', 'Classical'],
            'Track_Count': [1297, 1054, 130, 74],
            'Avg_Duration': [4.2, 3.8, 5.1, 8.9]
        })
        
        # Test export functions
        export_results = ea.export_data(
            data=sample_data,
            formats=['csv', 'json'],
            filename_prefix='test_export'
        )
        
        print(f"   ✅ Exported data in {len(export_results)} formats")
        
        # Test metadata
        metadata = ea.generate_export_metadata(sample_data, "Test Export")
        print(f"   ✅ Generated metadata with {len(metadata)} fields")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Export test failed: {str(e)}")
        return False

def test_context_agent():
    """Test context management"""
    try:
        from agents.context_agent import ContextAgent
        print("🔍 Testing Context Agent...")
        
        ca = ContextAgent()
        
        # Test session creation
        session_id = ca.start_session("test_user")
        print(f"   ✅ Created session: {session_id}")
        
        # Test context retrieval
        context = ca.get_relevant_context(session_id, "show me albums")
        print(f"   ✅ Retrieved context with {len(context)} keys")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Context agent test failed: {str(e)}")
        return False

def test_rate_limiter():
    """Test rate limiting functionality"""
    try:
        from utils.rate_limiter import RateLimiter
        print("⏱️  Testing Rate Limiter...")
        
        rate_limiter = RateLimiter()
        
        # Test basic functionality
        def test_function():
            return "Rate limiter working"
        
        result = rate_limiter.retry_with_backoff(test_function)
        print(f"   ✅ Rate limiter result: {result}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Rate limiter test failed: {str(e)}")
        return False

def main():
    """Run all tests that don't require API keys"""
    print("🧪 TESTING SYSTEM COMPONENTS (No API Keys Required)")
    print("=" * 60)
    
    tests = [
        ("Database Operations", test_database),
        ("Vector Store", test_vector_store),
        ("Visualization", test_visualization),
        ("Export Functions", test_export),
        ("Context Management", test_context_agent),
        ("Rate Limiter", test_rate_limiter),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"📊 RESULTS: {passed} passed, {failed} failed")
    print(f"🎯 Success Rate: {(passed / (passed + failed) * 100):.1f}%")
    
    if failed == 0:
        print("🎉 All non-API components are working perfectly!")
        print("\n💡 To enable AI features (SQL generation, insights):")
        print("   1. Get a Together AI API key from: https://api.together.xyz/settings/api-keys")
        print("   2. Update TOGETHER_API_KEY in your .env file")
        print("   3. Run: python test_complete_system.py")
    else:
        print(f"\n⚠️  {failed} components need attention. Check the errors above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 