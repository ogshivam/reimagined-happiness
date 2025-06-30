#!/usr/bin/env python3
"""
Comprehensive Test Suite for Enhanced Text-to-SQL Application
Tests all functionalities: SQL Chain, Simple Agent, Enhanced Agent with Visualizations
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, Any, List
import pandas as pd

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from sql_chain import SQLChain
    from sql_agent_simple import SimpleSQLAgent
    from sql_agent_enhanced import EnhancedSQLAgent, create_enhanced_sql_agent
    from database_tools import DatabaseManager
    from config import SAMPLE_QUERIES, TOGETHER_MODELS
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running this from the correct directory with all dependencies installed.")
    sys.exit(1)

class ComprehensiveTestSuite:
    """Comprehensive test suite for the Text-to-SQL application."""
    
    def __init__(self, api_key: str, database_path: str = "chinook.db"):
        """Initialize the test suite."""
        self.api_key = api_key
        self.database_path = database_path
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "database_path": database_path,
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "detailed_results": []
        }
        
        # Test queries for different scenarios
        self.test_queries = {
            "basic_count": "How many artists are in the database?",
            "aggregation": "What are the top 5 selling artists by total sales?",
            "grouping": "Show me the revenue by country",
            "time_series": "Show sales trends by year",
            "comparison": "Compare sales performance by media type",
            "distribution": "What is the distribution of track lengths?",
            "complex_join": "Which customers have spent the most money and what genres do they prefer?",
            "analytical": "What are the most popular music genres and their average track duration?",
        }
        
        print("🚀 Initializing Comprehensive Test Suite...")
        print(f"📅 Test Run: {self.results['timestamp']}")
        print(f"🗄️ Database: {database_path}")
        print(f"🔑 API Key: {'✅ Provided' if api_key else '❌ Missing'}")
        print("-" * 60)
    
    def test_database_connection(self) -> bool:
        """Test database connectivity."""
        print("\n🔍 Testing Database Connection...")
        try:
            db_manager = DatabaseManager(self.database_path)
            tables = db_manager.list_tables()
            
            if not tables:
                raise Exception("No tables found in database")
            
            print(f"✅ Database connected successfully")
            print(f"📊 Found {len(tables)} tables: {', '.join(tables[:5])}")
            self._log_test("Database Connection", True, f"Found {len(tables)} tables")
            return True
            
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
            self._log_test("Database Connection", False, str(e))
            return False
    
    def test_sql_chain(self) -> Dict[str, Any]:
        """Test SQL Chain approach."""
        print("\n⚡ Testing SQL Chain Approach...")
        results = {}
        
        try:
            # Initialize SQL Chain
            chain = SQLChain(self.database_path, api_key=self.api_key)
            print("✅ SQL Chain initialized successfully")
            
            # Test different query types
            for query_type, question in self.test_queries.items():
                print(f"  🔄 Testing {query_type}: {question[:50]}...")
                
                start_time = time.time()
                try:
                    result = chain.query(question, return_intermediate=True)
                    execution_time = time.time() - start_time
                    
                    success = result.get("success", False)
                    if success:
                        print(f"    ✅ Success ({execution_time:.2f}s)")
                        results[query_type] = {
                            "success": True,
                            "execution_time": execution_time,
                            "has_sql": bool(result.get("sql_query")),
                            "has_answer": bool(result.get("answer")),
                        }
                    else:
                        print(f"    ❌ Failed: {result.get('answer', 'Unknown error')}")
                        results[query_type] = {"success": False, "error": result.get("answer", "Unknown error")}
                    
                    self._log_test(f"SQL Chain - {query_type}", success, 
                                 f"Time: {execution_time:.2f}s" if success else result.get("answer", "Unknown error"))
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    print(f"    ❌ Exception: {str(e)}")
                    results[query_type] = {"success": False, "error": str(e)}
                    self._log_test(f"SQL Chain - {query_type}", False, str(e))
                
                time.sleep(1)  # Rate limiting
            
            return results
            
        except Exception as e:
            print(f"❌ SQL Chain initialization failed: {str(e)}")
            self._log_test("SQL Chain - Initialization", False, str(e))
            return {"initialization_error": str(e)}
    
    def test_simple_agent(self) -> Dict[str, Any]:
        """Test Simple SQL Agent approach."""
        print("\n🤖 Testing Simple Agent Approach...")
        results = {}
        
        try:
            # Initialize Simple Agent
            agent = SimpleSQLAgent(self.database_path, api_key=self.api_key)
            print("✅ Simple Agent initialized successfully")
            
            # Test key queries (subset to avoid rate limits)
            key_queries = ["basic_count", "aggregation", "grouping"]
            
            for query_type in key_queries:
                question = self.test_queries[query_type]
                print(f"  🔄 Testing {query_type}: {question[:50]}...")
                
                start_time = time.time()
                try:
                    result = agent.query(question)
                    execution_time = time.time() - start_time
                    
                    success = result.get("success", False)
                    if success:
                        print(f"    ✅ Success ({execution_time:.2f}s)")
                        results[query_type] = {
                            "success": True,
                            "execution_time": execution_time,
                            "has_answer": bool(result.get("answer")),
                        }
                    else:
                        print(f"    ❌ Failed: {result.get('error', 'Unknown error')}")
                        results[query_type] = {"success": False, "error": result.get("error", "Unknown error")}
                    
                    self._log_test(f"Simple Agent - {query_type}", success, 
                                 f"Time: {execution_time:.2f}s" if success else result.get("error", "Unknown error"))
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    print(f"    ❌ Exception: {str(e)}")
                    results[query_type] = {"success": False, "error": str(e)}
                    self._log_test(f"Simple Agent - {query_type}", False, str(e))
                
                time.sleep(2)  # Rate limiting
            
            return results
            
        except Exception as e:
            print(f"❌ Simple Agent initialization failed: {str(e)}")
            self._log_test("Simple Agent - Initialization", False, str(e))
            return {"initialization_error": str(e)}
    
    def test_enhanced_agent(self) -> Dict[str, Any]:
        """Test Enhanced SQL Agent with visualization features."""
        print("\n🚀 Testing Enhanced Agent Approach...")
        results = {}
        
        try:
            # Initialize Enhanced Agent
            enhanced_agent = create_enhanced_sql_agent(self.database_path, api_key=self.api_key)
            print("✅ Enhanced Agent initialized successfully")
            
            # Test visualization-friendly queries
            viz_queries = ["aggregation", "grouping", "distribution", "comparison"]
            
            for query_type in viz_queries:
                question = self.test_queries[query_type]
                print(f"  🔄 Testing {query_type}: {question[:50]}...")
                
                start_time = time.time()
                try:
                    result = enhanced_agent.query(question)
                    execution_time = time.time() - start_time
                    
                    success = result.get("success", False)
                    if success:
                        # Analyze visualization results
                        charts_generated = len(result.get("generated_charts", []))
                        insights_count = len(result.get("visualization_insights", []))
                        has_dashboard = bool(result.get("dashboard_layout"))
                        
                        print(f"    ✅ Success ({execution_time:.2f}s)")
                        print(f"      📊 Charts: {charts_generated}, 💡 Insights: {insights_count}, 📋 Dashboard: {has_dashboard}")
                        
                        results[query_type] = {
                            "success": True,
                            "execution_time": execution_time,
                            "has_answer": bool(result.get("answer")),
                            "has_sql": bool(result.get("sql_query")),
                            "charts_generated": charts_generated,
                            "insights_count": insights_count,
                            "has_dashboard": has_dashboard,
                            "has_raw_data": bool(result.get("raw_data")),
                            "export_options": len(result.get("export_options", [])),
                        }
                    else:
                        print(f"    ❌ Failed: {result.get('answer', 'Unknown error')}")
                        results[query_type] = {"success": False, "error": result.get("answer", "Unknown error")}
                    
                    self._log_test(f"Enhanced Agent - {query_type}", success, 
                                 f"Time: {execution_time:.2f}s, Charts: {charts_generated if success else 0}" 
                                 if success else result.get("answer", "Unknown error"))
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    print(f"    ❌ Exception: {str(e)}")
                    results[query_type] = {"success": False, "error": str(e)}
                    self._log_test(f"Enhanced Agent - {query_type}", False, str(e))
                
                time.sleep(3)  # Rate limiting for more complex queries
            
            return results
            
        except Exception as e:
            print(f"❌ Enhanced Agent initialization failed: {str(e)}")
            self._log_test("Enhanced Agent - Initialization", False, str(e))
            return {"initialization_error": str(e)}
    
    def test_visualization_features(self) -> Dict[str, Any]:
        """Test specific visualization features."""
        print("\n🎨 Testing Visualization Features...")
        
        try:
            from sql_agent_enhanced import ChartTypeDetector, VisualizationGenerator
            
            # Test data analysis
            test_data = pd.DataFrame({
                'category': ['A', 'B', 'C', 'D', 'E'],
                'value': [10, 25, 15, 30, 20],
                'date': pd.date_range('2023-01-01', periods=5)
            })
            
            # Test chart detection
            detector = ChartTypeDetector()
            analysis = detector.analyze_data(test_data)
            suggestions = detector.suggest_chart_types(test_data, analysis)
            
            print(f"✅ Chart detection: {len(suggestions)} suggestions")
            print(f"✅ Data analysis: {analysis['num_rows']} rows, {analysis['num_columns']} columns")
            
            self._log_test("Visualization - Chart Detection", True, f"{len(suggestions)} chart types suggested")
            
            return {
                "chart_detection": True,
                "suggestions_count": len(suggestions),
                "data_analysis": analysis
            }
            
        except Exception as e:
            print(f"❌ Visualization features test failed: {str(e)}")
            self._log_test("Visualization Features", False, str(e))
            return {"error": str(e)}
    
    def _log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result."""
        self.results["tests_run"] += 1
        if success:
            self.results["tests_passed"] += 1
        else:
            self.results["tests_failed"] += 1
        
        self.results["detailed_results"].append({
            "test_name": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def generate_report(self) -> str:
        """Generate comprehensive test report."""
        print("\n" + "="*60)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("="*60)
        
        total_tests = self.results["tests_run"]
        passed_tests = self.results["tests_passed"]
        failed_tests = self.results["tests_failed"]
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📅 Test Date: {self.results['timestamp']}")
        print(f"🗄️ Database: {self.results['database_path']}")
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print("-" * 60)
        
        # Group results by category
        categories = {}
        for result in self.results["detailed_results"]:
            category = result["test_name"].split(" - ")[0]
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "tests": []}
            
            if result["success"]:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
            categories[category]["tests"].append(result)
        
        # Print category summaries
        for category, data in categories.items():
            total_cat = data["passed"] + data["failed"]
            rate = (data["passed"] / total_cat * 100) if total_cat > 0 else 0
            print(f"\n🔸 {category}")
            print(f"   ✅ {data['passed']}/{total_cat} tests passed ({rate:.1f}%)")
            
            # Show failed tests
            for test in data["tests"]:
                if not test["success"]:
                    print(f"   ❌ {test['test_name']}: {test['details']}")
        
        # Save detailed report
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: {report_file}")
        
        return report_file
    
    def run_all_tests(self):
        """Run the complete test suite."""
        print("🚀 Starting Comprehensive Test Suite...")
        
        # Test 1: Database Connection
        if not self.test_database_connection():
            print("❌ Database connection failed. Stopping tests.")
            return self.generate_report()
        
        # Test 2: SQL Chain
        chain_results = self.test_sql_chain()
        
        # Test 3: Simple Agent
        agent_results = self.test_simple_agent()
        
        # Test 4: Enhanced Agent
        enhanced_results = self.test_enhanced_agent()
        
        # Test 5: Visualization Features
        viz_results = self.test_visualization_features()
        
        # Generate final report
        return self.generate_report()

def main():
    """Main test runner."""
    # Check for API key
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        print("❌ TOGETHER_API_KEY environment variable not found!")
        print("Please set it using: export TOGETHER_API_KEY=your_api_key")
        sys.exit(1)
    
    # Check for database
    database_path = "chinook.db"
    if not os.path.exists(database_path):
        print(f"❌ Database file '{database_path}' not found!")
        print("Make sure you're running this from the correct directory.")
        sys.exit(1)
    
    print("🧪 Enhanced Text-to-SQL Application - Comprehensive Test Suite")
    print("="*60)
    
    # Initialize and run tests
    test_suite = ComprehensiveTestSuite(api_key, database_path)
    report_file = test_suite.run_all_tests()
    
    print(f"\n🎯 Testing Complete! Report saved to: {report_file}")

if __name__ == "__main__":
    main() 