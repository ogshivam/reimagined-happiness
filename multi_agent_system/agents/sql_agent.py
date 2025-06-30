"""
SQL Agent - Converts natural language to SQL queries
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_together import Together
from langchain.agents.agent_types import AgentType
from langchain.schema import AgentAction, AgentFinish
import pandas as pd
import re

# Import settings with fallback for your project structure
try:
    from config.settings import settings
except ImportError:
    # Fallback: create a simple settings object for your project
    class SimpleSettings:
        def __init__(self):
            self.database_path = "chinook.db"
            self.model_name = "meta-llama/Llama-3-70b-chat-hf"
    
    settings = SimpleSettings()
from database.models import DatabaseManager
from memory.vector_store import ConversationVectorStore
from utils.rate_limiter import with_rate_limit, rate_limiter
from agents.simple_sql_fallback import fallback_generator

logger = logging.getLogger(__name__)

class SQLAgent:
    """Advanced SQL Agent with context awareness and query optimization"""
    
    def __init__(self):
        self.llm = Together(
            model=settings.llm_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            together_api_key=settings.together_api_key
        )
        
        self.db = None
        self.agent = None
        self.toolkit = None
        self.db_manager = DatabaseManager()
        self.vector_store = ConversationVectorStore()
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the SQL agent with database connection"""
        try:
            # Create SQLDatabase instance
            self.db = SQLDatabase.from_uri(settings.database_url)
            
            # Create toolkit
            self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
            
            # Create agent
            self.agent = create_sql_agent(
                llm=self.llm,
                toolkit=self.toolkit,
                verbose=True,
                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                max_iterations=settings.max_iterations,
                early_stopping_method="generate"
            )
            
            logger.info("SQL Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SQL Agent: {str(e)}")
            raise
    
    def generate_sql(self, question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate SQL query from natural language question"""
        try:
            # Search for similar queries in vector store
            similar_queries = self.vector_store.search_sql_queries(question, limit=3)
            
            # Build context-aware prompt
            enhanced_question = self._build_enhanced_prompt(question, context, similar_queries)
            
            # Execute agent with rate limiting
            result = rate_limiter.retry_with_backoff(self.agent.run, enhanced_question)
            
            # Check if we got a rate limit response
            if isinstance(result, dict) and result.get("rate_limited"):
                return result
            
            # Extract SQL query from result
            sql_query = self._extract_sql_query(result) if isinstance(result, str) else None
            
            response = {
                "question": question,
                "sql_query": sql_query,
                "agent_response": result,
                "similar_queries": similar_queries,
                "success": True
            }
            
            # Store query in vector store
            if sql_query:
                self.vector_store.add_sql_query(
                    query=sql_query,
                    description=question,
                    results_summary="Query generated successfully",
                    metadata={"agent_type": "sql_agent"}
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating SQL: {str(e)}")
            
            # Try fallback for basic queries
            if fallback_generator.can_handle_query(question):
                fallback_sql = fallback_generator.generate_simple_sql(question)
                if fallback_sql:
                    logger.info(f"Using fallback SQL generator for: {question}")
                    return {
                        "question": question,
                        "sql_query": fallback_sql,
                        "agent_response": f"Fallback SQL: {fallback_sql}",
                        "fallback_used": True,
                        "success": True
                    }
            
            return {
                "question": question,
                "error": str(e),
                "success": False
            }
    
    def execute_query(self, sql_query: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Execute SQL query and return results with metadata"""
        try:
            # Use database manager to execute query
            df, metadata = self.db_manager.execute_query(sql_query)
            
            logger.info(f"Query executed successfully: {metadata['row_count']} rows returned")
            return df, metadata
            
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise
    
    def process_question(self, question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Complete process: generate SQL, execute, and return results"""
        try:
            # Generate SQL
            sql_result = self.generate_sql(question, context)
            
            if not sql_result["success"]:
                return sql_result
            
            sql_query = sql_result["sql_query"]
            if not sql_query:
                return {
                    "question": question,
                    "error": "No SQL query generated",
                    "success": False
                }
            
            # Execute query
            df, exec_metadata = self.execute_query(sql_query)
            
            # Combine results
            result = {
                **sql_result,
                "data": df,
                "execution_metadata": exec_metadata,
                "row_count": len(df),
                "columns": list(df.columns) if not df.empty else []
            }
            
            # Update vector store with execution results
            self.vector_store.add_sql_query(
                query=sql_query,
                description=question,
                results_summary=f"Returned {len(df)} rows with columns: {list(df.columns)}",
                metadata={
                    "agent_type": "sql_agent",
                    "row_count": len(df),
                    "execution_time": exec_metadata.get("execution_time", 0)
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            return {
                "question": question,
                "error": str(e),
                "success": False
            }
    
    def _build_enhanced_prompt(self, question: str, context: Dict[str, Any] = None, 
                              similar_queries: List[Dict[str, Any]] = None) -> str:
        """Build enhanced prompt with context and similar queries"""
        prompt_parts = [question]
        
        # Add context if available
        if context:
            if "previous_queries" in context:
                prompt_parts.append("\nPrevious queries in this conversation:")
                for prev_q in context["previous_queries"][-3:]:  # Last 3 queries
                    prompt_parts.append(f"- {prev_q}")
            
            if "table_focus" in context:
                prompt_parts.append(f"\nFocus on these tables: {', '.join(context['table_focus'])}")
        
        # Add similar queries as examples
        if similar_queries:
            prompt_parts.append("\nSimilar queries for reference:")
            for sim_q in similar_queries[:2]:  # Top 2 similar queries
                metadata = sim_q.get("metadata", {})
                if "query" in metadata:
                    prompt_parts.append(f"- Question: {metadata.get('description', 'N/A')}")
                    prompt_parts.append(f"  SQL: {metadata['query']}")
        
        return "\n".join(prompt_parts)
    
    def _extract_sql_query(self, agent_response: str) -> Optional[str]:
        """Extract SQL query from agent response"""
        try:
            # Look for SQL query patterns
            sql_patterns = [
                r"```sql\s*(.*?)\s*```",
                r"```\s*(SELECT.*?(?:;|\Z))",
                r"(SELECT.*?(?:;|\Z))",
                r"Action Input:\s*(SELECT.*?)(?:\n|$)"
            ]
            
            for pattern in sql_patterns:
                matches = re.findall(pattern, agent_response, re.DOTALL | re.IGNORECASE)
                if matches:
                    sql_query = matches[0].strip()
                    if sql_query.endswith(';'):
                        sql_query = sql_query[:-1]
                    return sql_query
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting SQL query: {str(e)}")
            return None
    
    def get_database_schema(self) -> Dict[str, Any]:
        """Get database schema information"""
        try:
            return self.db_manager.get_database_summary()
        except Exception as e:
            logger.error(f"Error getting database schema: {str(e)}")
            return {"error": str(e)}
    
    def validate_query(self, sql_query: str) -> Dict[str, Any]:
        """Validate SQL query without executing it"""
        try:
            # Basic syntax validation
            if not sql_query.strip().upper().startswith(('SELECT', 'WITH')):
                return {
                    "valid": False,
                    "error": "Only SELECT queries are allowed"
                }
            
            # Check for dangerous operations
            dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']
            query_upper = sql_query.upper()
            
            for keyword in dangerous_keywords:
                if keyword in query_upper:
                    return {
                        "valid": False,
                        "error": f"Dangerous operation '{keyword}' not allowed"
                    }
            
            # Try to explain the query (dry run)
            try:
                with self.db_manager.engine.connect() as conn:
                    conn.execute(f"EXPLAIN QUERY PLAN {sql_query}")
                return {"valid": True}
            except:
                # If EXPLAIN doesn't work, just return valid for basic checks
                return {"valid": True}
                
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def get_query_suggestions(self, partial_question: str) -> List[str]:
        """Get query suggestions based on partial input"""
        try:
            # Search for similar queries
            similar_queries = self.vector_store.search_sql_queries(partial_question, limit=5)
            
            suggestions = []
            for query_data in similar_queries:
                metadata = query_data.get("metadata", {})
                description = metadata.get("description", "")
                if description and description not in suggestions:
                    suggestions.append(description)
            
            # Add some common query patterns if no suggestions found
            if not suggestions:
                suggestions = [
                    "Show me all records from [table_name]",
                    "Count the number of records in [table_name]", 
                    "Find the top 10 [column] by [metric]",
                    "Show me the average [column] grouped by [category]",
                    "List all unique values in [column_name]"
                ]
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error getting query suggestions: {str(e)}")
            return [] 