"""
Demonstration script for the Enhanced SQL Agent with Auto-Visualization Engine.
Shows examples of different query types and their automatic visualizations.
"""

import os
import sys
from typing import Dict, Any
import pandas as pd
from datetime import datetime

# Add the current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from sql_agent_enhanced import EnhancedSQLAgent, create_enhanced_sql_agent
    from database_tools import DatabaseManager
    from config import TOGETHER_MODELS
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you have installed all requirements: pip install -r requirements.txt")
    sys.exit(1)

def setup_environment():
    """Setup the environment and check requirements."""
    print("🔧 Setting up Enhanced SQL Agent Demo...")
    
    # Check API key
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        print("❌ Error: TOGETHER_API_KEY environment variable not found!")
        print("Please set your Together AI API key:")
        print("export TOGETHER_API_KEY=your_api_key_here")
        return False
    
    # Check database
    if not os.path.exists("chinook.db"):
        print("❌ Error: chinook.db not found!")
        print("Please run setup_database.py first to download the database.")
        return False
    
    print("✅ Environment setup complete!")
    return True

def display_result(question: str, result: Dict[str, Any], demo_number: int):
    """Display the result of a query in a formatted way."""
    print(f"\n{'='*80}")
    print(f"📊 DEMO {demo_number}: {question}")
    print(f"{'='*80}")
    
    if result["success"]:
        print("✅ Status: SUCCESS")
        print(f"🎯 Approach: {result['approach']}")
        
        # Basic metrics
        print(f"\n📈 METRICS:")
        print(f"   • Charts Generated: {len(result.get('generated_charts', []))}")
        print(f"   • Insights Generated: {len(result.get('visualization_insights', []))}")
        print(f"   • Export Options: {len(result.get('export_options', []))}")
        
        # SQL Query
        if result.get("sql_query"):
            print(f"\n🔍 GENERATED SQL:")
            print(f"   {result['sql_query']}")
        
        # Answer
        print(f"\n💬 ANSWER:")
        print(f"   {result['answer']}")
        
        # Data Analysis
        data_analysis = result.get("data_analysis", {})
        if data_analysis and "error" not in data_analysis:
            print(f"\n📊 DATA ANALYSIS:")
            print(f"   • Rows: {data_analysis.get('num_rows', 'N/A')}")
            print(f"   • Columns: {data_analysis.get('num_columns', 'N/A')}")
            print(f"   • Numeric Columns: {len(data_analysis.get('numeric_columns', []))}")
            print(f"   • Categorical Columns: {len(data_analysis.get('categorical_columns', []))}")
        
        # Chart Suggestions
        suggested_charts = result.get("suggested_charts", [])
        if suggested_charts:
            print(f"\n🎨 CHART SUGGESTIONS:")
            for i, suggestion in enumerate(suggested_charts[:3], 1):
                print(f"   {i}. {suggestion['type'].upper()}: {suggestion.get('description', 'No description')}")
        
        # Generated Charts
        generated_charts = result.get("generated_charts", [])
        if generated_charts:
            print(f"\n📈 GENERATED VISUALIZATIONS:")
            for i, chart_data in enumerate(generated_charts, 1):
                config = chart_data["config"]
                print(f"   {i}. {config['title']} ({config['type']})")
                print(f"      Description: {config['description']}")
        
        # Insights
        insights = result.get("visualization_insights", [])
        if insights:
            print(f"\n💡 KEY INSIGHTS:")
            for i, insight in enumerate(insights, 1):
                print(f"   {i}. {insight}")
        
        # Dashboard Info
        dashboard = result.get("dashboard_layout")
        if dashboard:
            print(f"\n📋 DASHBOARD:")
            print(f"   • Title: {dashboard.get('title', 'N/A')}")
            print(f"   • Layout: {dashboard.get('layout', 'N/A')}")
            print(f"   • Charts: {len(dashboard.get('charts', []))}")
        
    else:
        print("❌ Status: FAILED")
        print(f"💥 Error: {result.get('error', 'Unknown error')}")
        print(f"💬 Message: {result.get('answer', 'No message')}")

def run_demo_queries(agent: EnhancedSQLAgent):
    """Run a series of demo queries showcasing different visualization types."""
    
    demo_queries = [
        {
            "question": "What are the top 10 selling artists by total sales?",
            "description": "Bar chart showing artist rankings",
            "expected_charts": ["bar"]
        },
        {
            "question": "Show me the revenue by country",
            "description": "Geographic distribution visualization",
            "expected_charts": ["bar", "pie"]
        },
        {
            "question": "What is the distribution of track lengths?",
            "description": "Histogram showing data distribution",
            "expected_charts": ["histogram"]
        },
        {
            "question": "How do album sales vary by genre?",
            "description": "Categorical comparison visualization",
            "expected_charts": ["bar", "pie"]
        },
        {
            "question": "Show customer purchase patterns by age group",
            "description": "Demographic analysis with grouping",
            "expected_charts": ["bar", "box"]
        },
        {
            "question": "What are the correlations between track length, price, and sales?",
            "description": "Multi-variable analysis with scatter plots",
            "expected_charts": ["scatter", "heatmap"]
        },
        {
            "question": "Show sales trends over time by month",
            "description": "Time series analysis",
            "expected_charts": ["line"]
        },
        {
            "question": "Compare the performance of different media types",
            "description": "Comparative analysis across categories",
            "expected_charts": ["bar", "pie"]
        }
    ]
    
    print("\n🚀 Starting Enhanced SQL Agent Demo with Auto-Visualization...")
    print(f"📅 Demo Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🤖 Agent Type: Enhanced LangGraph Agent with Visualization Engine")
    
    results = []
    
    for i, demo in enumerate(demo_queries, 1):
        question = demo["question"]
        print(f"\n⏳ Processing Demo {i}/{len(demo_queries)}...")
        print(f"📝 Question: {question}")
        print(f"🎯 Expected: {demo['description']}")
        
        try:
            # Process the query
            result = agent.query(question)
            results.append({
                "demo_number": i,
                "question": question,
                "result": result,
                "expected_charts": demo["expected_charts"]
            })
            
            # Display result
            display_result(question, result, i)
            
            # Brief pause between demos
            import time
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error in demo {i}: {str(e)}")
            continue
    
    return results

def analyze_demo_results(results: list):
    """Analyze the results of all demo queries."""
    print(f"\n{'='*80}")
    print("📊 DEMO ANALYSIS SUMMARY")
    print(f"{'='*80}")
    
    total_demos = len(results)
    successful_demos = sum(1 for r in results if r["result"]["success"])
    total_charts = sum(len(r["result"].get("generated_charts", [])) for r in results)
    total_insights = sum(len(r["result"].get("visualization_insights", [])) for r in results)
    
    print(f"📈 Overall Statistics:")
    print(f"   • Total Demos: {total_demos}")
    print(f"   • Successful: {successful_demos} ({successful_demos/total_demos*100:.1f}%)")
    print(f"   • Failed: {total_demos - successful_demos}")
    print(f"   • Total Charts Generated: {total_charts}")
    print(f"   • Total Insights: {total_insights}")
    print(f"   • Average Charts per Query: {total_charts/successful_demos:.1f}")
    
    print(f"\n🎨 Chart Type Distribution:")
    chart_types = {}
    for result in results:
        for chart_data in result["result"].get("generated_charts", []):
            chart_type = chart_data["config"]["type"]
            chart_types[chart_type] = chart_types.get(chart_type, 0) + 1
    
    for chart_type, count in sorted(chart_types.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {chart_type.upper()}: {count} charts")
    
    print(f"\n💡 Most Common Insights:")
    all_insights = []
    for result in results:
        all_insights.extend(result["result"].get("visualization_insights", []))
    
    # Show first few insights as examples
    for i, insight in enumerate(all_insights[:5], 1):
        print(f"   {i}. {insight}")
    
    print(f"\n🏆 Best Performing Queries:")
    # Sort by number of charts + insights
    sorted_results = sorted(results, key=lambda x: (
        len(x["result"].get("generated_charts", [])) + 
        len(x["result"].get("visualization_insights", []))
    ), reverse=True)
    
    for i, result in enumerate(sorted_results[:3], 1):
        charts = len(result["result"].get("generated_charts", []))
        insights = len(result["result"].get("visualization_insights", []))
        print(f"   {i}. Demo {result['demo_number']}: {charts} charts, {insights} insights")
        print(f"      Question: {result['question'][:60]}...")

def main():
    """Main demo function."""
    print("🎯 Enhanced SQL Agent with Auto-Visualization Demo")
    print("=" * 60)
    
    # Setup
    if not setup_environment():
        return
    
    # Get API key and model
    api_key = os.getenv("TOGETHER_API_KEY")
    model = "meta-llama/Llama-3-70b-chat-hf"  # Default model
    
    print(f"\n🤖 Creating Enhanced SQL Agent...")
    print(f"   • Model: {model}")
    print(f"   • Database: chinook.db")
    print(f"   • Features: Auto-visualization, Chart detection, Export options")
    
    try:
        # Create the enhanced agent using the factory function
        agent = create_enhanced_sql_agent(
            database_path="chinook.db",
            model=model,
            api_key=api_key
        )
        print("✅ Enhanced Agent created successfully!")
        
        # Run demo queries
        results = run_demo_queries(agent)
        
        # Analyze results
        if results:
            analyze_demo_results(results)
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"📊 Check the generated visualizations and insights above.")
        print(f"🚀 To run the full interactive interface, use: streamlit run app_enhanced.py")
        
    except Exception as e:
        print(f"❌ Error creating agent: {str(e)}")
        return

if __name__ == "__main__":
    main() 