"""
LangGraph SQL Agent implementation for text-to-SQL conversion.
Features workflow: fetch tables → decide relevance → get schemas → generate query → validate → execute → fix errors → respond
"""

import os
from typing import Dict, Any, List, Annotated, Literal
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from database_tools import DatabaseManager, create_database_tools, get_chinook_schema_description
import pandas as pd
from pydantic import BaseModel
from typing_extensions import TypedDict

# Define the state for our agent
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    question: str
    current_step: str
    tables_fetched: bool
    relevant_tables: List[str]
    schema_info: str
    sql_query: str
    query_valid: bool
    query_results: str
    error_count: int
    max_errors: int
    final_answer: str

class SQLAgent:
    """LangGraph-based SQL agent with sophisticated workflow."""
    
    def __init__(self, database_path: str = "chinook.db", model: str = "gpt-3.5-turbo"):
        """Initialize the SQL agent.
        
        Args:
            database_path: Path to the SQLite database
            model: OpenAI model to use
        """
        self.database_path = database_path
        self.db_manager = DatabaseManager(database_path)
        self.llm = ChatOpenAI(model=model, temperature=0)
        
        # Get database tools
        self.db_manager, self.toolkit = create_database_tools(database_path)
        self.tools = self.toolkit.get_tools()
        
        # Create the agent graph
        self.graph = self._create_agent_graph()
        
        # Optional: Add memory/checkpointing
        self.memory = SqliteSaver.from_conn_string(":memory:")
    
    def _create_agent_graph(self) -> StateGraph:
        """Create the LangGraph workflow for the SQL agent."""
        
        # Create the state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("fetch_tables", self._fetch_tables_node)
        workflow.add_node("decide_relevance", self._decide_relevance_node)
        workflow.add_node("get_schemas", self._get_schemas_node)
        workflow.add_node("generate_query", self._generate_query_node)
        workflow.add_node("validate_query", self._validate_query_node)
        workflow.add_node("execute_query", self._execute_query_node)
        workflow.add_node("fix_errors", self._fix_errors_node)
        workflow.add_node("generate_response", self._generate_response_node)
        
        # Set entry point
        workflow.set_entry_point("fetch_tables")
        
        # Add edges
        workflow.add_edge("fetch_tables", "decide_relevance")
        workflow.add_edge("decide_relevance", "get_schemas")
        workflow.add_edge("get_schemas", "generate_query")
        workflow.add_edge("generate_query", "validate_query")
        
        # Conditional edges
        workflow.add_conditional_edges(
            "validate_query",
            self._validate_query_condition,
            {
                "execute": "execute_query",
                "fix": "fix_errors"
            }
        )
        
        workflow.add_conditional_edges(
            "execute_query",
            self._execute_query_condition,
            {
                "success": "generate_response",
                "error": "fix_errors"
            }
        )
        
        workflow.add_conditional_edges(
            "fix_errors",
            self._fix_errors_condition,
            {
                "retry": "generate_query",
                "give_up": "generate_response"
            }
        )
        
        workflow.add_edge("generate_response", END)
        
        return workflow.compile(checkpointer=self.memory)
    
    def _fetch_tables_node(self, state: AgentState) -> AgentState:
        """Fetch all available tables from the database."""
        try:
            tables = self.db_manager.list_tables()
            state["tables_fetched"] = True
            state["current_step"] = "tables_fetched"
            
            # Add system message about available tables
            table_message = f"Available tables: {', '.join(tables)}"
            state["messages"].append(SystemMessage(content=table_message))
            
            return state
        except Exception as e:
            state["messages"].append(SystemMessage(content=f"Error fetching tables: {str(e)}"))
            return state
    
    def _decide_relevance_node(self, state: AgentState) -> AgentState:
        """Decide which tables are relevant to the question."""
        try:
            question = state["question"]
            tables = self.db_manager.list_tables()
            
            # Use LLM to determine relevant tables
            relevance_prompt = f"""
            Given the question: "{question}"
            And these available tables: {', '.join(tables)}
            
            Based on the question and the Chinook database schema (a digital media store), 
            which tables are most relevant? Return only the table names, comma-separated.
            
            Schema context: {get_chinook_schema_description()}
            """
            
            response = self.llm.invoke([HumanMessage(content=relevance_prompt)])
            relevant_tables_str = response.content.strip()
            
            # Parse the response
            relevant_tables = [t.strip() for t in relevant_tables_str.split(",") if t.strip() in tables]
            
            # Fallback if no relevant tables found
            if not relevant_tables:
                relevant_tables = ["artists", "albums", "tracks", "customers", "invoices"]
            
            state["relevant_tables"] = relevant_tables
            state["current_step"] = "relevance_decided"
            
            message = f"Relevant tables identified: {', '.join(relevant_tables)}"
            state["messages"].append(SystemMessage(content=message))
            
            return state
        except Exception as e:
            # Fallback to common tables
            state["relevant_tables"] = ["artists", "albums", "tracks", "customers", "invoices"]
            state["messages"].append(SystemMessage(content=f"Error deciding relevance, using default tables: {str(e)}"))
            return state
    
    def _get_schemas_node(self, state: AgentState) -> AgentState:
        """Get detailed schema information for relevant tables."""
        try:
            relevant_tables = state["relevant_tables"]
            schema_info = self.db_manager.get_table_info(relevant_tables)
            
            state["schema_info"] = schema_info
            state["current_step"] = "schemas_retrieved"
            
            message = f"Schema information retrieved for tables: {', '.join(relevant_tables)}"
            state["messages"].append(SystemMessage(content=message))
            
            return state
        except Exception as e:
            state["messages"].append(SystemMessage(content=f"Error getting schemas: {str(e)}"))
            return state
    
    def _generate_query_node(self, state: AgentState) -> AgentState:
        """Generate SQL query based on the question and schema."""
        try:
            question = state["question"]
            schema_info = state.get("schema_info", "")
            relevant_tables = state.get("relevant_tables", [])
            
            query_prompt = f"""
            Generate a SQL query to answer this question: "{question}"
            
            Use ONLY these tables and their schemas:
            {schema_info}
            
            Relevant tables: {', '.join(relevant_tables)}
            
            Important guidelines:
            - Use only SQLite-compatible syntax
            - Be precise with column names and table joins
            - Use appropriate aggregations and sorting
            - Limit results if appropriate (use LIMIT)
            - Return ONLY the SQL query, no explanation
            """
            
            response = self.llm.invoke([HumanMessage(content=query_prompt)])
            sql_query = response.content.strip()
            
            # Clean up the query (remove markdown formatting if present)
            if sql_query.startswith("```"):
                sql_query = sql_query.split("\n", 1)[1]
            if sql_query.endswith("```"):
                sql_query = sql_query.rsplit("\n", 1)[0]
            
            state["sql_query"] = sql_query
            state["current_step"] = "query_generated"
            
            message = f"SQL query generated: {sql_query}"
            state["messages"].append(SystemMessage(content=message))
            
            return state
        except Exception as e:
            state["messages"].append(SystemMessage(content=f"Error generating query: {str(e)}"))
            return state
    
    def _validate_query_node(self, state: AgentState) -> AgentState:
        """Validate the generated SQL query."""
        try:
            sql_query = state["sql_query"]
            validation = self.db_manager.validate_query(sql_query)
            
            state["query_valid"] = validation["valid"]
            state["current_step"] = "query_validated"
            
            if validation["valid"]:
                message = "SQL query validation: PASSED"
            else:
                message = f"SQL query validation: FAILED - {validation['message']}"
            
            state["messages"].append(SystemMessage(content=message))
            
            return state
        except Exception as e:
            state["query_valid"] = False
            state["messages"].append(SystemMessage(content=f"Error validating query: {str(e)}"))
            return state
    
    def _execute_query_node(self, state: AgentState) -> AgentState:
        """Execute the validated SQL query."""
        try:
            sql_query = state["sql_query"]
            results = self.db_manager.execute_query(sql_query)
            
            # Format results for the state
            if results.empty:
                results_str = "No results found."
            else:
                if len(results) > 20:
                    results_str = f"First 20 of {len(results)} results:\n{results.head(20).to_string(index=False)}"
                else:
                    results_str = results.to_string(index=False)
            
            state["query_results"] = results_str
            state["current_step"] = "query_executed"
            
            message = f"Query executed successfully. Results: {len(results)} rows"
            state["messages"].append(SystemMessage(content=message))
            
            return state
        except Exception as e:
            state["query_results"] = f"Error: {str(e)}"
            state["error_count"] = state.get("error_count", 0) + 1
            state["messages"].append(SystemMessage(content=f"Error executing query: {str(e)}"))
            return state
    
    def _fix_errors_node(self, state: AgentState) -> AgentState:
        """Attempt to fix errors in the SQL query."""
        try:
            question = state["question"]
            sql_query = state["sql_query"]
            error_msg = state["query_results"] if "Error:" in state.get("query_results", "") else "Validation failed"
            schema_info = state.get("schema_info", "")
            
            fix_prompt = f"""
            The following SQL query has an error:
            Query: {sql_query}
            Error: {error_msg}
            
            Question: {question}
            Schema: {schema_info}
            
            Please provide a corrected SQL query that fixes the error.
            Return ONLY the corrected SQL query, no explanation.
            """
            
            response = self.llm.invoke([HumanMessage(content=fix_prompt)])
            corrected_query = response.content.strip()
            
            # Clean up the query
            if corrected_query.startswith("```"):
                corrected_query = corrected_query.split("\n", 1)[1]
            if corrected_query.endswith("```"):
                corrected_query = corrected_query.rsplit("\n", 1)[0]
            
            state["sql_query"] = corrected_query
            state["current_step"] = "error_fixed"
            
            message = f"Attempted to fix query: {corrected_query}"
            state["messages"].append(SystemMessage(content=message))
            
            return state
        except Exception as e:
            state["messages"].append(SystemMessage(content=f"Error fixing query: {str(e)}"))
            return state
    
    def _generate_response_node(self, state: AgentState) -> AgentState:
        """Generate the final natural language response."""
        try:
            question = state["question"]
            sql_query = state.get("sql_query", "")
            query_results = state.get("query_results", "")
            
            response_prompt = f"""
            Based on the question and query results, provide a natural language answer.
            
            Question: {question}
            SQL Query: {sql_query}
            Results: {query_results}
            
            Provide a helpful, natural language answer to the user's question.
            If there was an error, explain what went wrong in a user-friendly way.
            """
            
            response = self.llm.invoke([HumanMessage(content=response_prompt)])
            final_answer = response.content.strip()
            
            state["final_answer"] = final_answer
            state["current_step"] = "completed"
            
            state["messages"].append(AIMessage(content=final_answer))
            
            return state
        except Exception as e:
            error_response = f"I apologize, but I encountered an error while processing your question: {str(e)}"
            state["final_answer"] = error_response
            state["messages"].append(AIMessage(content=error_response))
            return state
    
    # Condition functions for routing
    def _validate_query_condition(self, state: AgentState) -> Literal["execute", "fix"]:
        return "execute" if state.get("query_valid", False) else "fix"
    
    def _execute_query_condition(self, state: AgentState) -> Literal["success", "error"]:
        query_results = state.get("query_results", "")
        return "error" if query_results.startswith("Error:") else "success"
    
    def _fix_errors_condition(self, state: AgentState) -> Literal["retry", "give_up"]:
        error_count = state.get("error_count", 0)
        max_errors = state.get("max_errors", 3)
        return "give_up" if error_count >= max_errors else "retry"
    
    def query(self, question: str, max_errors: int = 3) -> Dict[str, Any]:
        """Process a text-to-SQL query using the agent workflow.
        
        Args:
            question: Natural language question
            max_errors: Maximum number of error recovery attempts
            
        Returns:
            Dictionary with query results and metadata
        """
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=question)],
            "question": question,
            "current_step": "starting",
            "tables_fetched": False,
            "relevant_tables": [],
            "schema_info": "",
            "sql_query": "",
            "query_valid": False,
            "query_results": "",
            "error_count": 0,
            "max_errors": max_errors,
            "final_answer": ""
        }
        
        # Configure for this session
        config = {"configurable": {"thread_id": "sql_session"}}
        
        try:
            # Run the workflow
            final_state = self.graph.invoke(initial_state, config)
            
            return {
                "question": question,
                "answer": final_state.get("final_answer", "No answer generated"),
                "sql_query": final_state.get("sql_query", ""),
                "query_results": final_state.get("query_results", ""),
                "relevant_tables": final_state.get("relevant_tables", []),
                "error_count": final_state.get("error_count", 0),
                "success": final_state.get("current_step") == "completed",
                "workflow_steps": [msg.content for msg in final_state.get("messages", []) if isinstance(msg, SystemMessage)]
            }
        except Exception as e:
            return {
                "question": question,
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "success": False,
                "error": str(e)
            }

# Convenience function to create agent
def create_sql_agent(database_path: str = "chinook.db") -> SQLAgent:
    """Create a SQL agent with default configuration.
    
    Args:
        database_path: Path to the SQLite database
        
    Returns:
        Configured SQLAgent instance
    """
    return SQLAgent(database_path)

# Example usage and testing
if __name__ == "__main__":
    # Create the SQL agent
    agent = SQLAgent()
    
    # Test queries
    test_questions = [
        "What are the top 5 selling artists?",
        "How many customers are from each country?",
        "What is the most popular genre?",
        "Show me the revenue by year.",
        "Which employee has the highest sales?"
    ]
    
    print("Testing SQL Agent...")
    print("=" * 50)
    
    for question in test_questions:
        print(f"\nQuestion: {question}")
        result = agent.query(question)
        
        if result["success"]:
            print(f"SQL Query: {result['sql_query']}")
            print(f"Answer: {result['answer']}")
            print(f"Relevant Tables: {result['relevant_tables']}")
            print(f"Error Count: {result['error_count']}")
            print(f"Workflow Steps: {len(result['workflow_steps'])}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
        
        print("-" * 30) 