"""
Streamlit Frontend for Multi-Agent Conversational Database Assistant
"""
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
import json
import asyncio
import time
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="Multi-Agent Database Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

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
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'database_schema' not in st.session_state:
    st.session_state.database_schema = None

# Utility functions
def make_api_request(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Make API request to backend"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            return {"success": False, "error": f"Unsupported method: {method}"}
        
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_session() -> str:
    """Create a new conversation session"""
    result = make_api_request("/sessions", "POST", {"user_id": "streamlit_user"})
    if result.get("success"):
        return result["session_id"]
    else:
        st.error(f"Failed to create session: {result.get('error')}")
        return None

def get_database_schema() -> Dict:
    """Get database schema information"""
    result = make_api_request("/database/schema")
    if result.get("success"):
        return result["schema"]
    else:
        st.error(f"Failed to get database schema: {result.get('error')}")
        return {}

def process_question(session_id: str, question: str) -> Dict:
    """Process user question through multi-agent system"""
    data = {
        "session_id": session_id,
        "question": question,
        "context": {}
    }
    
    result = make_api_request("/chat", "POST", data)
    return result

# Header
st.markdown("""
<div class="main-header">
    <h1>🤖 Multi-Agent Conversational Database Assistant</h1>
    <p>Powered by LangGraph, Together AI, and specialized agents for SQL, Visualization, and Insights</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🎛️ Control Panel")
    
    # Session Management
    st.subheader("Session Management")
    
    if st.button("🆕 New Session", type="primary"):
        st.session_state.session_id = create_session()
        st.session_state.conversation_history = []
        if st.session_state.session_id:
            st.success(f"New session created: {st.session_state.session_id[:8]}...")
    
    if st.session_state.session_id:
        st.info(f"Current Session: {st.session_state.session_id[:8]}...")
        
        if st.button("🗑️ Clear Session"):
            result = make_api_request(f"/sessions/{st.session_state.session_id}", "DELETE")
            if result.get("success"):
                st.session_state.conversation_history = []
                st.success("Session cleared!")
            else:
                st.error(f"Failed to clear session: {result.get('error')}")
    
    # Database Information
    st.subheader("📊 Database Info")
    
    if st.button("🔄 Refresh Schema"):
        st.session_state.database_schema = get_database_schema()
    
    if st.session_state.database_schema is None:
        st.session_state.database_schema = get_database_schema()
    
    if st.session_state.database_schema:
        schema = st.session_state.database_schema
        st.metric("Total Tables", schema.get("total_tables", 0))
        
        with st.expander("📋 Table Details"):
            for table_name, table_info in schema.get("tables", {}).items():
                st.write(f"**{table_name}**")
                st.write(f"- Columns: {table_info.get('column_count', 0)}")
                if table_info.get('columns'):
                    st.write(f"- Fields: {', '.join(table_info['columns'][:5])}")
    
    # Agent Status
    st.subheader("🤖 Agent Status")
    
    agents = [
        {"name": "SQL Agent", "icon": "🔍", "status": "Active"},
        {"name": "Context Agent", "icon": "🧠", "status": "Active"},
        {"name": "Visualization Agent", "icon": "📊", "status": "Active"},
        {"name": "Insight Agent", "icon": "💡", "status": "Active"},
        {"name": "Memory Agent", "icon": "💾", "status": "Active"},
        {"name": "Export Agent", "icon": "📤", "status": "Active"}
    ]
    
    for agent in agents:
        st.markdown(f"**{agent['icon']} {agent['name']}**: ✅ {agent['status']}")

# Main Content
if not st.session_state.session_id:
    st.warning("⚠️ Please create a new session to start chatting!")
    
    # Sample Questions
    st.subheader("💡 Sample Questions")
    
    sample_questions = [
        "Show me all customers from the USA",
        "What are the top 5 selling artists by total sales?",
        "How many tracks are there in each genre?",
        "Show me the revenue by country",
        "Which albums have the most tracks?"
    ]
    
    cols = st.columns(2)
    for i, question in enumerate(sample_questions):
        with cols[i % 2]:
            if st.button(f"📝 {question}", key=f"sample_{i}"):
                if not st.session_state.session_id:
                    st.session_state.session_id = create_session()
                
                if st.session_state.session_id:
                    # Process the sample question
                    with st.spinner("🤖 Processing your question..."):
                        result = process_question(st.session_state.session_id, question)
                        
                        # Add to conversation history
                        st.session_state.conversation_history.append({
                            "type": "user",
                            "message": question,
                            "timestamp": datetime.now()
                        })
                        
                        st.session_state.conversation_history.append({
                            "type": "agent",
                            "message": result.get("response", "No response generated"),
                            "data": result.get("data"),
                            "charts": result.get("charts", []),
                            "insights": result.get("insights", {}),
                            "sql_query": result.get("sql_query"),
                            "timestamp": datetime.now()
                        })
                    
                    st.rerun()

else:
    # Chat Interface
    st.subheader("💬 Conversation")
    
    # Display conversation history
    for message in st.session_state.conversation_history:
        if message["type"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 You:</strong> {message["message"]}
                <small style="float: right; color: #666;">{message["timestamp"].strftime("%H:%M:%S")}</small>
            </div>
            """, unsafe_allow_html=True)
        
        else:  # agent message
            st.markdown(f"""
            <div class="chat-message agent-message">
                <strong>🤖 Assistant:</strong><br>
                {message["message"]}
                <small style="float: right; color: #666;">{message["timestamp"].strftime("%H:%M:%S")}</small>
            </div>
            """, unsafe_allow_html=True)
            
            # Display SQL query if available
            if message.get("sql_query"):
                with st.expander("🔍 SQL Query"):
                    st.code(message["sql_query"], language="sql")
            
            # Display data if available
            if message.get("data"):
                with st.expander("📊 Data Results"):
                    df = pd.DataFrame(message["data"])
                    st.dataframe(df, use_container_width=True)
            
            # Display charts if available
            if message.get("charts"):
                st.subheader("📈 Visualizations")
                
                for i, chart in enumerate(message["charts"]):
                    if "figure" in chart:
                        st.plotly_chart(chart["figure"], use_container_width=True, key=f"chart_{i}_{message['timestamp']}")
            
            # Display insights if available
            if message.get("insights"):
                with st.expander("💡 Insights"):
                    insights = message["insights"]
                    
                    # AI Insights
                    if insights.get("ai_insights"):
                        st.write("**🤖 AI-Generated Insights:**")
                        for insight in insights["ai_insights"]:
                            st.write(f"• {insight}")
                    
                    # Statistical Insights
                    if insights.get("statistical_insights"):
                        st.write("**📊 Statistical Insights:**")
                        for insight in insights["statistical_insights"]:
                            st.write(f"• {insight}")
    
    # Input area
    st.subheader("✍️ Ask a Question")
    
    user_question = st.text_input(
        "Type your question about the database:",
        placeholder="e.g., Show me the top 10 customers by total purchases",
        key="user_input"
    )
    
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        if st.button("🚀 Send", type="primary"):
            if user_question.strip():
                # Add user message to history
                st.session_state.conversation_history.append({
                    "type": "user",
                    "message": user_question,
                    "timestamp": datetime.now()
                })
                
                # Process question
                with st.spinner("🤖 Processing your question..."):
                    result = process_question(st.session_state.session_id, user_question)
                    
                    # Add agent response to history
                    st.session_state.conversation_history.append({
                        "type": "agent",
                        "message": result.get("response", "No response generated"),
                        "data": result.get("data"),
                        "charts": result.get("charts", []),
                        "insights": result.get("insights", {}),
                        "sql_query": result.get("sql_query"),
                        "timestamp": datetime.now()
                    })
                
                # Clear input and rerun
                st.session_state.user_input = ""
                st.rerun()
    
    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.conversation_history = []
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🤖 Multi-Agent Database Assistant | Powered by LangGraph, Together AI, and Streamlit</p>
</div>
""", unsafe_allow_html=True) 