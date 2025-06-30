"""
Standalone Streamlit Frontend for Multi-Agent Conversational Database Assistant
This version works without requiring the backend API
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Optional
import json
import time
from datetime import datetime
import sys
import os

# Add the parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.sql_agent import SQLAgent
from agents.context_agent import ContextAgent
from agents.visualization_agent import VisualizationAgent
from agents.insight_agent import InsightAgent
from config.settings import settings
from frontend.session_manager import session_manager, auto_save_session, restore_session_if_exists
from utils.pagination import render_large_dataframe

# Configure Streamlit page
st.set_page_config(
    page_title="Multi-Agent Database Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .agent-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .user-message {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .agent-message {
        background: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize agents (cached to avoid recreation)
@st.cache_resource
def initialize_agents():
    """Initialize all agents"""
    try:
        sql_agent = SQLAgent()
        context_agent = ContextAgent()
        viz_agent = VisualizationAgent()
        insight_agent = InsightAgent()
        
        return {
            "sql_agent": sql_agent,
            "context_agent": context_agent,
            "viz_agent": viz_agent,
            "insight_agent": insight_agent
        }
    except Exception as e:
        st.error(f"Failed to initialize agents: {str(e)}")
        return None

# Session state initialization
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'agents' not in st.session_state:
    st.session_state.agents = initialize_agents()

# Try to restore session from URL or previous state
if not st.session_state.session_id:
    restore_session_if_exists()

# Header
st.markdown("""
<div class="main-header">
    <h1>🤖 Multi-Agent Conversational Database Assistant</h1>
    <p>Powered by LangGraph, Together AI, and specialized agents for SQL, Visualization, and Insights</p>
</div>
""", unsafe_allow_html=True)

# Check if agents initialized successfully
if st.session_state.agents is None:
    st.error("❌ Failed to initialize agents. Please check your configuration and API keys.")
    st.stop()

# Sidebar
with st.sidebar:
    st.header("🎛️ Control Panel")
    
    # Session Management
    st.subheader("Session Management")
    
    if st.button("🆕 New Session", type="primary"):
        st.session_state.session_id = st.session_state.agents["context_agent"].start_session("streamlit_user")
        st.session_state.conversation_history = []
        if st.session_state.session_id:
            # Update URL with session ID
            st.query_params["session"] = st.session_state.session_id
            st.success(f"New session created: {st.session_state.session_id[:8]}...")
            auto_save_session()
    
    if st.session_state.session_id:
        st.info(f"Current Session: {st.session_state.session_id[:8]}...")
        
        if st.button("🗑️ Clear Session"):
            st.session_state.agents["context_agent"].clear_session(st.session_state.session_id)
            session_manager.delete_session(st.session_state.session_id)
            st.session_state.conversation_history = []
            st.query_params.clear()  # Clear URL params
            st.success("Session cleared!")
    
    # Database Information
    st.subheader("📊 Database Info")
    
    try:
        schema = st.session_state.agents["sql_agent"].get_database_schema()
        if schema:
            tables = schema.get("tables", {})
            # Convert dict keys to list if tables is a dictionary
            if isinstance(tables, dict):
                table_list = list(tables.keys())
            else:
                table_list = tables if isinstance(tables, list) else []
            
            st.metric("Total Tables", len(table_list))
            
            with st.expander("📋 Table Details"):
                for table in table_list[:10]:  # Show first 10 tables
                    st.write(f"**{table}**")
    except Exception as e:
        st.error(f"Error loading database schema: {str(e)}")
    
    # Session History
    st.subheader("📚 Session History")
    
    sessions = session_manager.list_sessions()
    if sessions:
        for session in sessions[:5]:  # Show last 5 sessions
            session_id_short = session["session_id"][:8]
            msg_count = session["message_count"]
            
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"📂 {session_id_short}... ({msg_count} msgs)", key=f"load_{session['session_id']}"):
                    # Load the session
                    session_data = session_manager.load_session(session["session_id"])
                    if session_data:
                        st.session_state.session_id = session["session_id"]
                        st.session_state.conversation_history = session_data.get("conversation_history", [])
                        st.query_params["session"] = session["session_id"]
                        st.success(f"Loaded session {session_id_short}...")
                        st.rerun()
            
            with col2:
                if st.button("🗑️", key=f"del_{session['session_id']}", help="Delete session"):
                    session_manager.delete_session(session["session_id"])
                    st.rerun()
    else:
        st.info("No previous sessions found")
    
    # Cleanup old sessions
    if st.button("🧹 Cleanup Old Sessions", help="Remove sessions older than 7 days"):
        cleaned = session_manager.cleanup_old_sessions(days_old=7)
        st.success(f"Cleaned up {cleaned} old sessions")
    
    # Agent Status
    st.subheader("🤖 Agent Status")
    
    agents_status = [
        {"name": "SQL Agent", "icon": "🔍", "status": "Active"},
        {"name": "Context Agent", "icon": "🧠", "status": "Active"},
        {"name": "Visualization Agent", "icon": "📊", "status": "Active"},
        {"name": "Insight Agent", "icon": "💡", "status": "Active"}
    ]
    
    for agent in agents_status:
        st.markdown(f"**{agent['icon']} {agent['name']}**: ✅ {agent['status']}")

# Main Content
if not st.session_state.session_id:
    st.warning("⚠️ Please create a new session to start chatting!")
    
    # Sample Questions
    st.subheader("💡 Sample Questions")
    
    sample_questions = [
        "Show me all categories",
        "What are the top 5 selling artists?",
        "Show me sales by country",
        "Create a chart of revenue by genre",
        "Which albums have the highest sales?",
        "Show me customer demographics"
    ]
    
    cols = st.columns(2)
    for i, question in enumerate(sample_questions):
        col = cols[i % 2]
        if col.button(f"💬 {question}", key=f"sample_{i}"):
            # Create session and process question
            st.session_state.session_id = st.session_state.agents["context_agent"].start_session("streamlit_user")
            st.session_state.conversation_history = []
            # Set the question to be processed
            st.session_state.current_question = question
            st.rerun()

else:
    # Chat Interface
    st.subheader("💬 Chat with your Database")
    
    # Display conversation history
    for i, msg in enumerate(st.session_state.conversation_history):
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 You:</strong> {msg["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message agent-message">
                <strong>🤖 Assistant:</strong> {msg["content"]}
            </div>
            """, unsafe_allow_html=True)
            
            # Display any charts
            if "chart" in msg:
                st.plotly_chart(msg["chart"], use_container_width=True)
            
            # Display any data tables with pagination
            if "data" in msg and not msg["data"].empty:
                render_large_dataframe(msg["data"], "📊 Query Results", f"chat_msg_{i}")
    
    # Input area
    question = st.text_input("💭 Ask a question about your database:", key="question_input")
    
    # Handle sample question from session state
    if hasattr(st.session_state, 'current_question'):
        question = st.session_state.current_question
        del st.session_state.current_question
    
    if st.button("🚀 Send", type="primary") or question:
        if question:
            # Add user message to history
            st.session_state.conversation_history.append({
                "role": "user",
                "content": question,
                "timestamp": datetime.now()
            })
            
            # Process the question
            with st.spinner("🤖 Processing your question..."):
                # Add progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("🔍 Analyzing your question...")
                    progress_bar.progress(20)
                    # Get context
                    context = st.session_state.agents["context_agent"].get_relevant_context(
                        st.session_state.session_id, question
                    )
                    
                    status_text.text("🔄 Generating SQL query...")
                    progress_bar.progress(40)
                    
                    # Generate SQL and get data
                    sql_result = st.session_state.agents["sql_agent"].process_question(question, context)
                    
                    progress_bar.progress(60)
                    
                    # Check for rate limit errors
                    if not sql_result.get("success") and ("rate limit" in str(sql_result.get("error", "")).lower() or sql_result.get("rate_limited")):
                        progress_bar.empty()
                        status_text.empty()
                        
                        error_msg = """⏳ **API Rate Limit Reached**
                        
The Together AI API has temporarily limited our requests. Here's what you can do:

**Option 1: Wait & Retry**
- Wait 60-90 seconds for the rate limit to reset
- Then try your question again

**Option 2: Try Simple Queries** (These work with our fallback system)
- "how many tables are there"
- "show me artists" 
- "count albums"
- "list tracks"

**Option 3: Use the Sample Questions**
- Click any of the sample questions in the sidebar"""
                        
                        st.session_state.conversation_history.append({
                            "role": "assistant",
                            "content": error_msg,
                            "timestamp": datetime.now()
                        })
                        st.rerun()
                    
                    if sql_result.get("success"):
                        status_text.text("📊 Processing results...")
                        progress_bar.progress(80)
                        
                        response_parts = []
                        
                        # Add SQL query info
                        if sql_result.get("sql_query"):
                            if sql_result.get("fallback_used"):
                                response_parts.append(f"**SQL Query (Fallback):** `{sql_result['sql_query']}`")
                                response_parts.append("💡 *Using simplified query due to API rate limits*")
                            else:
                                response_parts.append(f"**SQL Query:** `{sql_result['sql_query']}`")
                        
                        # Add data summary
                        if "data" in sql_result and not sql_result["data"].empty:
                            df = sql_result["data"]
                            response_parts.append(f"**Found {len(df)} rows with {len(df.columns)} columns**")
                            
                            # Create visualization if data is suitable
                            try:
                                viz_result = st.session_state.agents["viz_agent"].create_visualizations(
                                    df, question
                                )
                                
                                chart = None
                                if viz_result.get("success") and "charts" in viz_result:
                                    charts = viz_result["charts"]
                                    if charts and "figure" in charts[0]:
                                        chart = charts[0]["figure"]
                                        response_parts.append("**📊 Visualization created**")
                            except Exception as e:
                                st.warning(f"Could not create visualization: {str(e)}")
                                chart = None
                            
                            # Generate insights
                            try:
                                insight_result = st.session_state.agents["insight_agent"].generate_insights(
                                    df, question, {}
                                )
                                
                                if insight_result.get("success") and "insights" in insight_result:
                                    insights = insight_result["insights"]
                                    if insights.get("summary"):
                                        response_parts.append(f"**💡 Insights:** {insights['summary']}")
                            except Exception as e:
                                st.warning(f"Could not generate insights: {str(e)}")
                            
                            # Save conversation
                            st.session_state.agents["context_agent"].save_conversation_turn(
                                st.session_state.session_id,
                                question,
                                "\n".join(response_parts),
                                "multi_agent",
                                {"sql_query": sql_result.get("sql_query")}
                            )
                            
                            # Add assistant message to history
                            assistant_msg = {
                                "role": "assistant",
                                "content": "\n\n".join(response_parts),
                                "timestamp": datetime.now(),
                                "data": df
                            }
                            
                            if chart:
                                assistant_msg["chart"] = chart
                            
                            # Finalize progress
                            progress_bar.progress(100)
                            status_text.text("✅ Complete!")
                            time.sleep(0.5)  # Brief pause to show completion
                            progress_bar.empty()
                            status_text.empty()
                            
                            st.session_state.conversation_history.append(assistant_msg)
                            
                            # Auto-save session
                            auto_save_session()
                        
                        else:
                            progress_bar.empty()
                            status_text.empty()
                            error_msg = "⚠️ **No Data Found**\n\nThe query executed successfully but returned no results. Try:\n- Checking your search criteria\n- Using a broader query\n- Exploring available data with 'show me tables'"
                            st.session_state.conversation_history.append({
                                "role": "assistant",
                                "content": error_msg,
                                "timestamp": datetime.now()
                            })
                    
                    else:
                        progress_bar.empty()
                        status_text.empty()
                        error_details = sql_result.get('error', 'Unknown error occurred')
                        error_msg = f"""❌ **Query Failed**
                        
**Error Details:** {error_details}

**Troubleshooting Tips:**
- Try rephrasing your question
- Use simpler language
- Check if you're asking about the right table/data
- Try one of the sample questions"""
                        st.session_state.conversation_history.append({
                            "role": "assistant",
                            "content": error_msg,
                            "timestamp": datetime.now()
                        })
                
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Enhanced error handling
                    error_type = type(e).__name__
                    error_details = str(e)
                    
                    if "connection" in error_details.lower():
                        error_msg = f"""🔌 **Connection Error**
                        
**Issue:** Unable to connect to the database or API service.
**Details:** {error_details}

**Solutions:**
- Check your internet connection
- Verify the database is accessible
- Wait a moment and try again"""
                    elif "timeout" in error_details.lower():
                        error_msg = f"""⏰ **Timeout Error**
                        
**Issue:** The operation took too long to complete.
**Details:** {error_details}

**Solutions:**
- Try a simpler query
- Check if the database is responding
- Wait and try again"""
                    else:
                        error_msg = f"""💥 **System Error**
                        
**Error Type:** {error_type}
**Details:** {error_details}

**Solutions:**
- Try rephrasing your question
- Use one of the sample questions
- If the problem persists, there may be a system issue"""
                    
                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": error_msg,
                        "timestamp": datetime.now()
                    })
            
            # Clear the input and rerun to show new messages
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>Multi-Agent Conversational Database Assistant v1.0</p>
    <p>Powered by LangGraph, Together AI, and Streamlit</p>
</div>
""", unsafe_allow_html=True) 