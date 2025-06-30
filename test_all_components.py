#!/usr/bin/env python3
"""
Comprehensive test script for all Text-to-SQL components.
Tests Chain, Simple Agent, Enhanced Agent, and Auto-Viz functionality.
"""

import os
import sys
from typing import Dict, Any

def test_component(name: str, test_func, query: str = "How many artists are in the database?"):
    """Test a specific component and return results."""
    print(f"\n{'='*60}")
    print(f"🧪 TESTING {name.upper()}")
    print(f"{'='*60}")
    print(f"Query: {query}")
    
    try:
        result = test_func(query)
        
        if result.get("success", False):
            print(f"✅ {name} - SUCCESS")
            print(f"   Answer: {result.get('answer', 'No answer')[:100]}...")
            print(f"   SQL Query: {result.get('sql_query', 'No SQL')}")
            
            # Enhanced features
            if 'generated_charts' in result:
                print(f"   Charts: {len(result.get('generated_charts', []))}")
            if 'visualization_insights' in result:
                print(f"   Insights: {len(result.get('visualization_insights', []))}")
                
            return True
        else:
            print(f"❌ {name} - FAILED")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ {name} - EXCEPTION")
        print(f"   Error: {str(e)}")
        return False

def test_sql_chain(query: str) -> Dict[str, Any]:
    """Test SQL Chain component."""
    from sql_chain import SQLChain
    api_key = os.getenv("TOGETHER_API_KEY")
    chain = SQLChain("chinook.db", api_key=api_key)
    return chain.query(query)

def test_simple_agent(query: str) -> Dict[str, Any]:
    """Test Simple SQL Agent component."""
    from sql_agent_simple import SimpleSQLAgent
    api_key = os.getenv("TOGETHER_API_KEY")
    agent = SimpleSQLAgent("chinook.db", api_key=api_key)
    return agent.query(query)

def test_enhanced_agent(query: str) -> Dict[str, Any]:
    """Test Enhanced SQL Agent component."""
    from sql_agent_enhanced import create_enhanced_sql_agent
    api_key = os.getenv("TOGETHER_API_KEY")
    agent = create_enhanced_sql_agent("chinook.db", api_key=api_key)
    return agent.query(query)

def main():
    """Main test function."""
    print("🎯 COMPREHENSIVE TEXT-TO-SQL COMPONENT TEST")
    print("=" * 80)
    
    # Check API key
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        print("❌ TOGETHER_API_KEY environment variable not found!")
        print("Please set your Together AI API key:")
        print("export TOGETHER_API_KEY=your_api_key_here")
        return
    
    print(f"✅ API Key configured: {api_key[:20]}...")
    
    # Test queries
    test_queries = [
        "How many artists are in the database?",
        "What are the top 5 selling artists by total sales?",
        "Show me the revenue by country"
    ]
    
    results = {}
    
    for query in test_queries:
        print(f"\n🔍 TESTING QUERY: {query}")
        print("-" * 80)
        
        query_results = {}
        
        # Test each component
        query_results["chain"] = test_component("SQL Chain", test_sql_chain, query)
        query_results["simple_agent"] = test_component("Simple Agent", test_simple_agent, query)
        query_results["enhanced_agent"] = test_component("Enhanced Agent", test_enhanced_agent, query)
        
        results[query] = query_results
    
    # Summary
    print(f"\n{'='*80}")
    print("📊 FINAL SUMMARY")
    print(f"{'='*80}")
    
    component_scores = {"chain": 0, "simple_agent": 0, "enhanced_agent": 0}
    total_tests = len(test_queries)
    
    for query, query_results in results.items():
        print(f"\nQuery: {query[:50]}...")
        for component, success in query_results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {component.replace('_', ' ').title()}: {status}")
            if success:
                component_scores[component] += 1
    
    print(f"\n🏆 COMPONENT SCORES:")
    for component, score in component_scores.items():
        percentage = (score / total_tests) * 100
        print(f"  {component.replace('_', ' ').title()}: {score}/{total_tests} ({percentage:.1f}%)")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if component_scores["enhanced_agent"] == total_tests:
        print("  🎉 Enhanced Agent is working perfectly! Use it for auto-visualization.")
    elif component_scores["chain"] == total_tests:
        print("  ⚡ SQL Chain is reliable for fast queries.")
    elif component_scores["simple_agent"] == total_tests:
        print("  🤖 Simple Agent is working well for complex reasoning.")
    else:
        print("  ⚠️  Some components have issues. Check the errors above.")
    
    print(f"\n🚀 STREAMLIT APP STATUS:")
    print("  The Streamlit app is running at: http://localhost:8502")
    print("  All working components should be available in the web interface.")
    
    print(f"\n✨ TEST COMPLETED!")

if __name__ == "__main__":
    main() 