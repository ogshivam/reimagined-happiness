"""
Multi-Agent Orchestrator - Coordinates all agents using LangGraph
"""
import logging
from typing import Dict, List, Any, Optional, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
import asyncio
import sqlite3
from pathlib import Path

from .sql_agent import SQLAgent
from .context_agent import ContextAgent
from .visualization_agent import VisualizationAgent
from .insight_agent import InsightAgent
from .memory_agent import MemoryAgent
from .export_agent import ExportAgent

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

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """State shared between all agents"""
    session_id: str
    user_message: str
    question: str
    sql_query: Optional[str]
    data: Optional[Any]
    charts: List[Dict[str, Any]]
    insights: Dict[str, Any]
    context: Dict[str, Any]
    agent_responses: Dict[str, Any]
    final_response: str
    error: Optional[str]
    step_count: int

class MultiAgentOrchestrator:
    """Orchestrates multiple agents using LangGraph workflow"""
    
    def __init__(self):
        # Initialize all agents
        self.sql_agent = SQLAgent()
        self.context_agent = ContextAgent()
        self.visualization_agent = VisualizationAgent()
        self.insight_agent = InsightAgent()
        self.memory_agent = MemoryAgent()
        self.export_agent = ExportAgent()
        
        # Setup memory first
        self.memory = self._setup_memory()
        
        # Initialize LangGraph workflow
        self.workflow = self._create_workflow()
        
    def _setup_memory(self):
        """Setup SQLite memory for LangGraph checkpointing"""
        try:
            # Ensure memory directory exists
            Path("memory").mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect("memory/langgraph_memory.db", check_same_thread=False)
            return SqliteSaver(conn)
        except Exception as e:
            logger.error(f"Error setting up memory: {str(e)}")
            return None
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes for each agent
        workflow.add_node("context_analysis", self._analyze_context)
        workflow.add_node("sql_generation", self._generate_sql)
        workflow.add_node("data_retrieval", self._retrieve_data)
        workflow.add_node("visualization", self._create_visualizations)
        workflow.add_node("insight_generation", self._generate_insights)
        workflow.add_node("response_synthesis", self._synthesize_response)
        workflow.add_node("memory_storage", self._store_in_memory)
        
        # Define the workflow edges
        workflow.set_entry_point("context_analysis")
        
        workflow.add_edge("context_analysis", "sql_generation")
        workflow.add_edge("sql_generation", "data_retrieval")
        workflow.add_edge("data_retrieval", "visualization")
        workflow.add_edge("visualization", "insight_generation")
        workflow.add_edge("insight_generation", "response_synthesis")
        workflow.add_edge("response_synthesis", "memory_storage")
        workflow.add_edge("memory_storage", END)
        
        return workflow.compile(checkpointer=self.memory)
    
    async def process_question(self, session_id: str, question: str, 
                              context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a user question through the multi-agent workflow"""
        try:
            # Initialize state
            initial_state = AgentState(
                session_id=session_id,
                user_message=question,
                question=question,
                sql_query=None,
                data=None,
                charts=[],
                insights={},
                context=context or {},
                agent_responses={},
                final_response="",
                error=None,
                step_count=0
            )
            
            # Run the workflow
            config = {"configurable": {"thread_id": session_id}}
            final_state = await self.workflow.ainvoke(initial_state, config)
            
            return {
                "success": final_state.get("error") is None,
                "response": final_state.get("final_response", ""),
                "sql_query": final_state.get("sql_query"),
                "data": final_state.get("data"),
                "charts": final_state.get("charts", []),
                "insights": final_state.get("insights", {}),
                "agent_responses": final_state.get("agent_responses", {}),
                "error": final_state.get("error")
            }
            
        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": f"I encountered an error while processing your question: {str(e)}"
            }
    
    def _analyze_context(self, state: AgentState) -> AgentState:
        """Analyze conversation context"""
        try:
            session_id = state["session_id"]
            question = state["question"]
            
            # Get relevant context from context agent
            context = self.context_agent.get_relevant_context(session_id, question)
            
            state["context"] = context
            state["step_count"] += 1
            
            logger.info(f"Context analysis completed for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error in context analysis: {str(e)}")
            state["error"] = f"Context analysis failed: {str(e)}"
        
        return state
    
    def _generate_sql(self, state: AgentState) -> AgentState:
        """Generate SQL query"""
        try:
            question = state["question"]
            context = state["context"]
            
            # Use SQL agent to generate query
            sql_result = self.sql_agent.generate_sql(question, context)
            
            if sql_result["success"]:
                state["sql_query"] = sql_result["sql_query"]
                state["agent_responses"]["sql_agent"] = sql_result
            else:
                state["error"] = sql_result.get("error", "SQL generation failed")
            
            state["step_count"] += 1
            
        except Exception as e:
            logger.error(f"Error in SQL generation: {str(e)}")
            state["error"] = f"SQL generation failed: {str(e)}"
        
        return state
    
    def _retrieve_data(self, state: AgentState) -> AgentState:
        """Retrieve data using SQL query"""
        try:
            sql_query = state["sql_query"]
            
            if not sql_query:
                state["error"] = "No SQL query available for data retrieval"
                return state
            
            # Execute query using SQL agent
            df, metadata = self.sql_agent.execute_query(sql_query)
            
            state["data"] = df
            state["agent_responses"]["data_retrieval"] = {
                "success": True,
                "metadata": metadata,
                "row_count": len(df)
            }
            state["step_count"] += 1
            
        except Exception as e:
            logger.error(f"Error in data retrieval: {str(e)}")
            state["error"] = f"Data retrieval failed: {str(e)}"
        
        return state
    
    def _create_visualizations(self, state: AgentState) -> AgentState:
        """Create visualizations"""
        try:
            data = state["data"]
            question = state["question"]
            
            if data is None or data.empty:
                state["charts"] = []
                return state
            
            # Use visualization agent to create charts
            viz_result = self.visualization_agent.create_visualizations(data, question)
            
            if viz_result["success"]:
                state["charts"] = viz_result["charts"]
                state["agent_responses"]["visualization_agent"] = viz_result
            else:
                logger.warning(f"Visualization creation failed: {viz_result.get('error')}")
                state["charts"] = []
            
            state["step_count"] += 1
            
        except Exception as e:
            logger.error(f"Error in visualization creation: {str(e)}")
            state["charts"] = []
        
        return state
    
    def _generate_insights(self, state: AgentState) -> AgentState:
        """Generate insights"""
        try:
            data = state["data"]
            question = state["question"]
            context = state["context"]
            
            if data is None or data.empty:
                state["insights"] = {}
                return state
            
            # Use insight agent to generate insights
            insight_result = self.insight_agent.generate_insights(data, question, context)
            
            if insight_result["success"]:
                state["insights"] = insight_result["insights"]
                state["agent_responses"]["insight_agent"] = insight_result
            else:
                logger.warning(f"Insight generation failed: {insight_result.get('error')}")
                state["insights"] = {}
            
            state["step_count"] += 1
            
        except Exception as e:
            logger.error(f"Error in insight generation: {str(e)}")
            state["insights"] = {}
        
        return state
    
    def _synthesize_response(self, state: AgentState) -> AgentState:
        """Synthesize final response"""
        try:
            question = state["question"]
            data = state["data"]
            charts = state["charts"]
            insights = state["insights"]
            sql_query = state["sql_query"]
            
            # Build comprehensive response
            response_parts = []
            
            # Add query information
            if sql_query:
                response_parts.append(f"I executed the following SQL query to answer your question:")
                response_parts.append(f"```sql\n{sql_query}\n```")
            
            # Add data summary
            if data is not None and not data.empty:
                response_parts.append(f"\n📊 **Results Summary:**")
                response_parts.append(f"- Found {len(data)} records")
                response_parts.append(f"- Columns: {', '.join(data.columns)}")
            
            # Add insights
            if insights:
                response_parts.append(f"\n💡 **Key Insights:**")
                
                # Add AI insights if available
                ai_insights = insights.get("ai_insights", [])
                if ai_insights:
                    for insight in ai_insights[:3]:  # Top 3 AI insights
                        response_parts.append(f"• {insight}")
                
                # Add statistical insights
                stats_insights = insights.get("statistical_insights", [])
                if stats_insights:
                    response_parts.append(f"\n📈 **Statistical Summary:**")
                    for insight in stats_insights[:2]:  # Top 2 statistical insights
                        response_parts.append(f"• {insight}")
            
            # Add visualization information
            if charts:
                response_parts.append(f"\n📊 **Visualizations:**")
                response_parts.append(f"I've created {len(charts)} charts to help visualize the data.")
            
            final_response = "\n".join(response_parts)
            
            if not final_response.strip():
                final_response = "I was able to process your question, but no specific results were found."
            
            state["final_response"] = final_response
            state["step_count"] += 1
            
        except Exception as e:
            logger.error(f"Error in response synthesis: {str(e)}")
            state["final_response"] = f"I encountered an error while preparing the response: {str(e)}"
        
        return state
    
    def _store_in_memory(self, state: AgentState) -> AgentState:
        """Store conversation in memory"""
        try:
            session_id = state["session_id"]
            user_message = state["user_message"]
            final_response = state["final_response"]
            
            # Prepare metadata
            metadata = {
                "sql_query": state["sql_query"],
                "chart_count": len(state["charts"]),
                "insight_count": len(state.get("insights", {})),
                "step_count": state["step_count"]
            }
            
            # Store in context agent
            self.context_agent.save_conversation_turn(
                session_id=session_id,
                user_message=user_message,
                agent_response=final_response,
                agent_type="multi_agent_orchestrator",
                metadata=metadata
            )
            
            state["step_count"] += 1
            
        except Exception as e:
            logger.error(f"Error storing in memory: {str(e)}")
        
        return state
    
    def start_session(self, user_id: str = None) -> str:
        """Start a new conversation session"""
        return self.context_agent.start_session(user_id)
    
    def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session"""
        return self.context_agent.get_session_statistics(session_id)
    
    def clear_session(self, session_id: str):
        """Clear session data"""
        self.context_agent.clear_session(session_id) 