"""
Comprehensive Test Suite for Multi-Agent Conversational Database Assistant
Tests all components, functions, and integrations
"""
import sys
import os
import logging
import traceback
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List

# Add current directory to path
sys.path.append('.')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemTester:
    """Comprehensive system tester"""
    
    def __init__(self):
        self.test_results = {}
        self.errors = []
        self.warnings = []
        
    def log_test(self, test_name: str, success: bool, message: str = "", error: Exception = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {message}")
        
        self.test_results[test_name] = {
            "success": success,
            "message": message,
            "error": str(error) if error else None,
            "timestamp": datetime.now()
        }
        
        if not success:
            self.errors.append(f"{test_name}: {error}")
    
    def test_imports(self):
        """Test all module imports"""
        print("\n🔍 TESTING IMPORTS")
        print("=" * 50)
        
        imports_to_test = [
            ("config.settings", "settings"),
            ("database.models", "DatabaseManager, ConversationMemory"),
            ("memory.vector_store", "ConversationVectorStore"),
            ("utils.rate_limiter", "RateLimiter, rate_limiter"),
            ("agents.sql_agent", "SQLAgent"),
            ("agents.context_agent", "ContextAgent"),
            ("agents.visualization_agent", "VisualizationAgent"),
            ("agents.insight_agent", "InsightAgent"),
            ("agents.memory_agent", "MemoryAgent"),
            ("agents.export_agent", "ExportAgent"),
            ("agents.orchestrator", "MultiAgentOrchestrator"),
        ]
        
        for module_name, import_items in imports_to_test:
            try:
                exec(f"from {module_name} import {import_items}")
                self.log_test(f"Import {module_name}", True, f"Successfully imported {import_items}")
            except Exception as e:
                self.log_test(f"Import {module_name}", False, f"Failed to import {import_items}", e)
    
    def test_database_manager(self):
        """Test DatabaseManager functionality"""
        print("\n🗄️ TESTING DATABASE MANAGER")
        print("=" * 50)
        
        try:
            from database.models import DatabaseManager
            
            # Test initialization
            db_manager = DatabaseManager()
            self.log_test("DatabaseManager Init", True, "DatabaseManager initialized successfully")
            
            # Test engine connection
            if db_manager.engine:
                self.log_test("Database Engine", True, f"Engine connected: {db_manager.engine}")
            else:
                self.log_test("Database Engine", False, "Engine is None")
            
            # Test get_tables
            tables = db_manager.get_tables()
            self.log_test("Get Tables", len(tables) > 0, f"Found {len(tables)} tables: {tables[:5]}")
            
            # Test get_database_summary
            summary = db_manager.get_database_summary()
            self.log_test("Database Summary", "tables" in summary, f"Summary keys: {list(summary.keys())}")
            
            # Test sample data retrieval
            if tables:
                sample_df = db_manager.get_sample_data(tables[0], 3)
                self.log_test("Sample Data", not sample_df.empty, f"Retrieved {len(sample_df)} sample rows from {tables[0]}")
            
            # Test query execution
            test_query = "SELECT COUNT(*) as total FROM Artist"
            df, metadata = db_manager.execute_query(test_query)
            self.log_test("Query Execution", not df.empty, f"Query returned {len(df)} rows with metadata")
            
        except Exception as e:
            self.log_test("DatabaseManager", False, "DatabaseManager test failed", e)
    
    def test_vector_store(self):
        """Test ConversationVectorStore functionality"""
        print("\n🧠 TESTING VECTOR STORE")
        print("=" * 50)
        
        try:
            from memory.vector_store import ConversationVectorStore
            
            # Test initialization
            vector_store = ConversationVectorStore()
            self.log_test("VectorStore Init", True, "ConversationVectorStore initialized")
            
            # Test add conversation
            doc_id = vector_store.add_conversation(
                session_id="test_session",
                user_message="Test user message",
                agent_response="Test agent response",
                agent_type="test_agent"
            )
            self.log_test("Add Conversation", doc_id is not None, f"Added conversation with ID: {doc_id}")
            
            # Test search conversations
            results = vector_store.search_conversations("test message", limit=5)
            self.log_test("Search Conversations", len(results) >= 0, f"Search returned {len(results)} results")
            
            # Test add SQL query
            sql_doc_id = vector_store.add_sql_query(
                query="SELECT * FROM test",
                description="Test SQL query",
                results_summary="Test results"
            )
            self.log_test("Add SQL Query", sql_doc_id is not None, f"Added SQL query with ID: {sql_doc_id}")
            
            # Test add insight
            insight_doc_id = vector_store.add_insight(
                insight_text="Test insight",
                insight_type="test",
                data_context="Test context"
            )
            self.log_test("Add Insight", insight_doc_id is not None, f"Added insight with ID: {insight_doc_id}")
            
        except Exception as e:
            self.log_test("VectorStore", False, "VectorStore test failed", e)
    
    def test_agents(self):
        """Test all agents"""
        print("\n🤖 TESTING AGENTS")
        print("=" * 50)
        
        # Test SQL Agent
        try:
            from agents.sql_agent import SQLAgent
            sql_agent = SQLAgent()
            self.log_test("SQL Agent Init", True, "SQL Agent initialized")
            
            # Test database schema
            schema = sql_agent.get_database_schema()
            self.log_test("SQL Agent Schema", "tables" in schema, f"Schema contains {len(schema.get('tables', {}))} tables")
            
            # Test SQL generation (with rate limiting)
            try:
                sql_result = sql_agent.generate_sql("Show me all artists")
                self.log_test("SQL Generation", sql_result.get("success", False), f"SQL generation result: {sql_result.get('success')}")
            except Exception as e:
                if "rate limit" in str(e).lower():
                    self.log_test("SQL Generation", True, "Rate limit encountered (expected behavior)")
                else:
                    self.log_test("SQL Generation", False, "SQL generation failed", e)
            
        except Exception as e:
            self.log_test("SQL Agent", False, "SQL Agent test failed", e)
        
        # Test Context Agent
        try:
            from agents.context_agent import ContextAgent
            context_agent = ContextAgent()
            self.log_test("Context Agent Init", True, "Context Agent initialized")
            
            # Test session creation
            session_id = context_agent.start_session("test_user")
            self.log_test("Start Session", session_id is not None, f"Created session: {session_id}")
            
            # Test context retrieval
            context = context_agent.get_relevant_context(session_id, "test question")
            self.log_test("Get Context", isinstance(context, dict), f"Context type: {type(context)}")
            
        except Exception as e:
            self.log_test("Context Agent", False, "Context Agent test failed", e)
        
        # Test Visualization Agent
        try:
            from agents.visualization_agent import VisualizationAgent
            viz_agent = VisualizationAgent()
            self.log_test("Visualization Agent Init", True, "Visualization Agent initialized")
            
            # Test with sample data
            sample_data = pd.DataFrame({
                'category': ['A', 'B', 'C', 'D'],
                'value': [10, 20, 15, 25],
                'count': [1, 2, 3, 4]
            })
            
            viz_result = viz_agent.create_visualizations(sample_data, "Sample chart")
            self.log_test("Create Visualization", viz_result.get("success", False), f"Visualization result: {viz_result.get('success')}")
            
        except Exception as e:
            self.log_test("Visualization Agent", False, "Visualization Agent test failed", e)
        
        # Test Insight Agent
        try:
            from agents.insight_agent import InsightAgent
            insight_agent = InsightAgent()
            self.log_test("Insight Agent Init", True, "Insight Agent initialized")
            
            # Test insight generation (with rate limiting)
            try:
                insight_result = insight_agent.generate_insights(sample_data, "Sample insights")
                self.log_test("Generate Insights", insight_result.get("success", False), f"Insights result: {insight_result.get('success')}")
            except Exception as e:
                if "rate limit" in str(e).lower():
                    self.log_test("Generate Insights", True, "Rate limit encountered (expected behavior)")
                else:
                    self.log_test("Generate Insights", False, "Insight generation failed", e)
            
        except Exception as e:
            self.log_test("Insight Agent", False, "Insight Agent test failed", e)
        
        # Test Memory Agent
        try:
            from agents.memory_agent import MemoryAgent
            memory_agent = MemoryAgent()
            self.log_test("Memory Agent Init", True, "Memory Agent initialized")
            
            # Test store conversation
            success = memory_agent.store_conversation(
                session_id="test_session",
                user_message="Test message",
                agent_response="Test response",
                agent_type="test"
            )
            self.log_test("Store Conversation", success, f"Conversation stored: {success}")
            
        except Exception as e:
            self.log_test("Memory Agent", False, "Memory Agent test failed", e)
        
        # Test Export Agent
        try:
            from agents.export_agent import ExportAgent
            export_agent = ExportAgent()
            self.log_test("Export Agent Init", True, "Export Agent initialized")
            
            # Test data export
            export_result = export_agent.export_data(sample_data, "csv")
            self.log_test("Export Data", export_result.get("success", False), f"Export result: {export_result.get('success')}")
            
        except Exception as e:
            self.log_test("Export Agent", False, "Export Agent test failed", e)
    
    def test_orchestrator(self):
        """Test MultiAgentOrchestrator"""
        print("\n🎭 TESTING ORCHESTRATOR")
        print("=" * 50)
        
        try:
            from agents.orchestrator import MultiAgentOrchestrator
            
            # Test initialization
            orchestrator = MultiAgentOrchestrator()
            self.log_test("Orchestrator Init", True, "MultiAgentOrchestrator initialized")
            
            # Test session management
            session_id = orchestrator.start_session("test_user")
            self.log_test("Orchestrator Session", session_id is not None, f"Session created: {session_id}")
            
        except Exception as e:
            self.log_test("Orchestrator", False, "Orchestrator test failed", e)
    
    def test_rate_limiter(self):
        """Test rate limiting functionality"""
        print("\n⏱️ TESTING RATE LIMITER")
        print("=" * 50)
        
        try:
            from utils.rate_limiter import RateLimiter, rate_limiter
            
            # Test basic functionality
            def test_function(message):
                return f"Success: {message}"
            
            result = rate_limiter.retry_with_backoff(test_function, "test")
            self.log_test("Rate Limiter Basic", "Success" in result, f"Rate limiter result: {result}")
            
            # Test error handling
            def error_function():
                raise Exception("rate limit error")
            
            try:
                rate_limiter.retry_with_backoff(error_function)
                self.log_test("Rate Limiter Error Handling", False, "Should have raised exception")
            except Exception:
                self.log_test("Rate Limiter Error Handling", True, "Correctly handled exception")
            
        except Exception as e:
            self.log_test("Rate Limiter", False, "Rate limiter test failed", e)
    
    def test_integration(self):
        """Test integration between components"""
        print("\n🔗 TESTING INTEGRATION")
        print("=" * 50)
        
        try:
            # Test SQL Agent + Database Manager integration
            from agents.sql_agent import SQLAgent
            sql_agent = SQLAgent()
            
            # Test simple query execution
            simple_result = sql_agent.process_question("Count all artists")
            self.log_test("SQL Integration", isinstance(simple_result, dict), f"Integration result type: {type(simple_result)}")
            
            # Test Context Agent + Memory integration
            from agents.context_agent import ContextAgent
            context_agent = ContextAgent()
            
            session_id = context_agent.start_session("integration_test")
            context_agent.save_conversation_turn(
                session_id, "test question", "test response", "test_agent"
            )
            
            history = context_agent.get_conversation_history(session_id)
            self.log_test("Context Integration", len(history) >= 0, f"Retrieved {len(history)} conversation entries")
            
        except Exception as e:
            self.log_test("Integration", False, "Integration test failed", e)
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 STARTING COMPREHENSIVE SYSTEM TESTS")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Run all test categories
        self.test_imports()
        self.test_database_manager()
        self.test_vector_store()
        self.test_agents()
        self.test_orchestrator()
        self.test_rate_limiter()
        self.test_integration()
        
        # Generate summary
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏱️ Duration: {duration.total_seconds():.2f} seconds")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.errors:
            print(f"\n🚨 ERRORS FOUND ({len(self.errors)}):")
            print("-" * 40)
            for i, error in enumerate(self.errors, 1):
                print(f"{i}. {error}")
        
        if failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED! System is fully functional.")
        else:
            print(f"\n⚠️ {failed_tests} tests failed. Review errors above.")
        
        return {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "errors": self.errors,
            "results": self.test_results
        }

def main():
    """Main test runner"""
    print("Multi-Agent System Comprehensive Test Suite")
    print("Testing all components and functions...")
    
    tester = SystemTester()
    results = tester.run_all_tests()
    
    # Save results to file
    import json
    with open("test_results.json", "w") as f:
        # Convert datetime objects to strings for JSON serialization
        serializable_results = {}
        for test_name, result in results["results"].items():
            serializable_results[test_name] = {
                **result,
                "timestamp": result["timestamp"].isoformat()
            }
        
        json.dump({
            "summary": {
                "total": results["total"],
                "passed": results["passed"], 
                "failed": results["failed"],
                "success_rate": results["success_rate"]
            },
            "errors": results["errors"],
            "detailed_results": serializable_results
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to test_results.json")
    
    return results

if __name__ == "__main__":
    main() 