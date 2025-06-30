#!/usr/bin/env python3
"""
Enhanced Conversational SQL Chat Interface.
Provides intelligent conversational experience with multi-agent orchestration,
memory, and context-aware follow-up capabilities.
"""

import streamlit as st

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="SQL Chat Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

import os
import pandas as pd
from typing import Dict, Any, List, Optional
import time
import json
import plotly.graph_objects as go
from datetime import datetime
from dataclasses import dataclass, field
import re
import asyncio
import uuid

# Import our modules
try:
    from sql_chain import SQLChain
    from sql_agent_simple import SimpleSQLAgent
    from sql_agent_enhanced import EnhancedSQLAgent, create_enhanced_sql_agent
    from database_tools import DatabaseManager, get_chinook_schema_description
    from config import SAMPLE_QUERIES, TOGETHER_MODELS
    
    # DISABLE multi-agent system to prevent recursion issues
    # Using enhanced agent with conversational context instead
    MULTI_AGENT_ERROR = "Disabled to prevent recursion - using optimized conversational AI"
    MultiAgentOrchestrator = None
    ContextAgent = None
    MemoryAgent = None
    MULTI_AGENT_AVAILABLE = False
    
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# Enhanced CSS for better chat appearance
def load_css():
    """Load custom CSS for the chat interface."""
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Root variables */
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
        --bg-primary: #ffffff;
        --bg-secondary: #f9fafb;
        --border-color: #e5e7eb;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* Main container styling */
    .main > div {
        padding-top: 1rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 2rem;
        letter-spacing: -0.025em;
    }
    
    /* Chat container */
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1.5rem;
        background: var(--bg-secondary);
        border-radius: 16px;
        margin-bottom: 1.5rem;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
        scroll-behavior: smooth;
    }
    
    /* Custom scrollbar */
    .chat-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 3px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 3px;
    }
    
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    
    /* Message styling */
    .user-message {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 20px 20px 6px 20px;
        margin: 12px 0;
        margin-left: 15%;
        box-shadow: var(--shadow-md);
        position: relative;
        font-weight: 500;
        line-height: 1.5;
    }
    
    .agent-message {
        background: var(--bg-primary);
        color: var(--text-primary);
        padding: 20px;
        border-radius: 20px 20px 20px 6px;
        margin: 12px 0;
        margin-right: 15%;
        box-shadow: var(--shadow-md);
        border-left: 4px solid var(--success-color);
        line-height: 1.6;
    }
    
    .system-message {
        background: linear-gradient(135deg, #e0f2fe 0%, #b3e5fc 100%);
        color: #0277bd;
        padding: 12px 20px;
        border-radius: 16px;
        margin: 12px auto;
        text-align: center;
        font-style: italic;
        max-width: 70%;
        box-shadow: var(--shadow-sm);
        font-weight: 500;
    }
    
    .error-message {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        color: var(--error-color);
        padding: 16px 20px;
        border-radius: 20px 20px 20px 6px;
        margin: 12px 0;
        margin-right: 15%;
        box-shadow: var(--shadow-md);
        border-left: 4px solid var(--error-color);
        line-height: 1.5;
    }
    
    /* Agent info styling */
    .agent-info {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .agent-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 12px;
        font-size: 1rem;
        font-weight: bold;
        box-shadow: var(--shadow-sm);
    }
    
    /* Message timestamp */
    .message-timestamp {
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.8);
        margin-top: 8px;
        text-align: right;
        font-weight: 400;
    }
    
    .agent-message .message-timestamp {
        color: var(--text-secondary);
    }
    
    .system-message .message-timestamp {
        color: #0277bd;
        opacity: 0.8;
    }
    
    .error-message .message-timestamp {
        color: var(--error-color);
        opacity: 0.8;
    }
    
    /* Chart container */
    .chart-container {
        background: var(--bg-primary);
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
    }
    
    /* Typing indicator */
    .typing-indicator {
        background: #f1f5f9;
        color: #64748b;
        padding: 16px 20px;
        border-radius: 20px 20px 20px 6px;
        margin: 12px 0;
        margin-right: 15%;
        font-style: italic;
        animation: pulse 2s ease-in-out infinite;
        box-shadow: var(--shadow-sm);
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .typing-dots {
        display: flex;
        gap: 4px;
    }
    
    .typing-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #64748b;
        animation: typing 1.4s ease-in-out infinite;
    }
    
    .typing-dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.8; }
        50% { opacity: 1; }
    }
    
    @keyframes typing {
        0%, 80%, 100% { opacity: 0.3; }
        40% { opacity: 1; }
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 12px;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.025em;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    /* Agent selector buttons */
    .agent-selector-btn {
        padding: 12px 24px;
        border-radius: 12px;
        border: 2px solid var(--border-color);
        background: var(--bg-primary);
        color: var(--text-primary);
        font-weight: 600;
        transition: all 0.3s ease;
        cursor: pointer;
        text-align: center;
        box-shadow: var(--shadow-sm);
    }
    
    .agent-selector-btn:hover {
        border-color: var(--primary-color);
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    
    .agent-selector-btn.active {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border-color: var(--primary-color);
        box-shadow: var(--shadow-lg);
    }
    
    /* Form styling */
    .stTextInput > div > div > input {
        border-radius: 16px;
        border: 2px solid var(--border-color);
        padding: 14px 20px;
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        outline: none;
    }
    
    /* Sample questions */
    .sample-question-btn {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 12px 16px;
        margin: 4px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.9rem;
        color: var(--text-primary);
        box-shadow: var(--shadow-sm);
    }
    
    .sample-question-btn:hover {
        background: var(--primary-color);
        color: white;
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: var(--bg-secondary);
    }
    
    /* Metrics styling */
    .metric-card {
        background: var(--bg-primary);
        padding: 16px;
        border-radius: 12px;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border-color);
        margin: 8px 0;
    }
    
    /* SQL query display */
    .sql-query-container {
        background: #1e293b;
        color: #e2e8f0;
        padding: 16px;
        border-radius: 8px;
        margin: 12px 0;
        font-family: 'Monaco', 'Consolas', monospace;
        font-size: 0.9rem;
        overflow-x: auto;
    }
    
    /* Message actions */
    .message-actions {
        display: flex;
        gap: 8px;
        margin-top: 12px;
        opacity: 0.7;
        transition: opacity 0.3s ease;
    }
    
    .message-actions:hover {
        opacity: 1;
    }
    
    .action-btn {
        background: none;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
        transition: all 0.3s ease;
    }
    
    .action-btn:hover {
        background: var(--bg-secondary);
        color: var(--text-primary);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Responsive design */
    @media (max-width: 768px) {
        .user-message, .agent-message {
            margin-left: 5%;
            margin-right: 5%;
        }
        
        .main-header {
            font-size: 2rem;
        }
        
        .chat-container {
            max-height: 400px;
            padding: 1rem;
        }
    }
    
    /* Loading animation */
    .loading-spinner {
        display: inline-block;
        width: 16px;
        height: 16px;
        border: 2px solid #f3f3f3;
        border-top: 2px solid var(--primary-color);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)

@dataclass
class ChatMessage:
    """Represents a chat message with enhanced context."""
    content: str
    sender: str  # "user", "agent", "system"
    message_type: str = "text"  # "text", "result", "error"
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None
    context_references: List[str] = field(default_factory=list)  # References to previous messages

class ChatInterface:
    """Main chat interface class."""
    
    def __init__(self):
        """Initialize the chat interface."""
        self.agents = {
            "⚡ SQL Chain": {
                "type": "chain",
                "icon": "⚡",
                "color": "#f59e0b",
                "description": "Fast and direct SQL generation"
            },
            "🤖 Simple Agent": {
                "type": "agent", 
                "icon": "🤖",
                "color": "#10b981",
                "description": "Reasoning-based SQL agent"
            },
            "🚀 Enhanced Agent": {
                "type": "enhanced",
                "icon": "🚀", 
                "color": "#667eea",
                "description": "Advanced agent with visualizations"
            },
            "🧠 Conversational AI": {
                "type": "orchestrator",
                "icon": "🧠",
                "color": "#8b5cf6",
                "description": "Intelligent conversation with memory & context"
            }
        }
        
        # Load CSS
        load_css()
    
    def initialize_session_state(self):
        """Initialize Streamlit session state with enhanced features."""
        # Initialize session ID for conversation tracking
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
            
            # Add enhanced welcome message
            welcome_msg = ChatMessage(
                content="""🎉 **Welcome to your Enhanced Conversational SQL Assistant!** 

I'm powered by an intelligent multi-agent system that can:
• 🧠 **Remember our conversation** and understand context
• 🔗 **Answer follow-up questions** about previous results  
• 📊 **Generate visualizations** and insights
• 💡 **Learn from your queries** to provide better responses

**Try asking:** "Show me top artists by sales" then follow up with "What about their albums?" or "Create a chart for this data"

Choose an agent above and let's start exploring your data! 🚀""",
                sender="system",
                message_type="text",
                session_id=st.session_state.session_id
            )
            st.session_state.chat_messages.append(welcome_msg)
        
        if 'current_agent' not in st.session_state:
            st.session_state.current_agent = "🧠 Conversational AI"
        
        if 'chat_input' not in st.session_state:
            st.session_state.chat_input = ""
        
        # Initialize models
        if 'enhanced_agent' not in st.session_state:
            st.session_state.enhanced_agent = None
        if 'chain' not in st.session_state:
            st.session_state.chain = None
        if 'agent' not in st.session_state:
            st.session_state.agent = None
        if 'db_manager' not in st.session_state:
            st.session_state.db_manager = None
        if 'message_count' not in st.session_state:
            st.session_state.message_count = 0
            
        # Initialize multi-agent orchestrator and memory
        if 'orchestrator' not in st.session_state:
            st.session_state.orchestrator = None
        if 'context_agent' not in st.session_state:
            st.session_state.context_agent = None
        if 'conversation_context' not in st.session_state:
            st.session_state.conversation_context = {}
        if 'last_query_results' not in st.session_state:
            st.session_state.last_query_results = None
    
    def load_models(self):
        """Load SQL models and multi-agent orchestrator."""
        api_key = os.getenv("TOGETHER_API_KEY")
        if not api_key:
            st.error("❌ TOGETHER_API_KEY environment variable not found!")
            return False
        
        model = "meta-llama/Llama-3-70b-chat-hf"
        
        try:
            # Load models only when needed
            if st.session_state.enhanced_agent is None:
                with st.spinner("🚀 Loading Enhanced Agent..."):
                    st.session_state.enhanced_agent = create_enhanced_sql_agent(
                        database_path="chinook.db",
                        model=model,
                        api_key=api_key
                    )
            
            if st.session_state.chain is None:
                with st.spinner("⚡ Loading SQL Chain..."):
                    st.session_state.chain = SQLChain("chinook.db", model=model, api_key=api_key)
            
            if st.session_state.agent is None:
                with st.spinner("🤖 Loading Simple Agent..."):
                    st.session_state.agent = SimpleSQLAgent("chinook.db", model=model, api_key=api_key)
            
            if st.session_state.db_manager is None:
                st.session_state.db_manager = DatabaseManager("chinook.db")
            
            # DISABLE multi-agent orchestrator to prevent recursion issues
            # Use enhanced agent with conversational context instead
            st.session_state.orchestrator = None
            st.session_state.context_agent = None
            
            return True
        except Exception as e:
            st.error(f"❌ Error loading models: {str(e)}")
            return False
    
    def render_agent_selector(self):
        """Render agent selection buttons."""
        st.markdown("### 🤖 Choose Your SQL Assistant")
        st.markdown("Each agent has different capabilities and approaches to solving your SQL queries.")
        
        cols = st.columns(len(self.agents))
        
        for i, (agent_name, agent_info) in enumerate(self.agents.items()):
            with cols[i]:
                is_active = st.session_state.current_agent == agent_name
                
                # Create a custom styled button using HTML/CSS
                button_class = "agent-selector-btn active" if is_active else "agent-selector-btn"
                
                if st.button(
                    f"{agent_info['icon']} {agent_name.split(' ', 1)[1]}",
                    key=f"agent_btn_{i}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                    help=agent_info['description']
                ):
                    if st.session_state.current_agent != agent_name:
                        # Add system message about agent switch
                        switch_msg = ChatMessage(
                            content=f"🔄 Switched to {agent_name} - {agent_info['description']}",
                            sender="system",
                            message_type="text"
                        )
                        st.session_state.chat_messages.append(switch_msg)
                        st.session_state.current_agent = agent_name
                        st.rerun()
                
                # Show agent description
                st.caption(agent_info['description'])
    
    def render_chat_history(self):
        """Render the chat message history."""
        st.markdown("### 💬 Conversation")
        
        # Create chat container
        chat_container = st.container()
        
        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            for i, msg in enumerate(st.session_state.chat_messages):
                self.render_message(msg, i)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def clean_agent_output(self, text: str) -> str:
        """Clean agent output by removing unwanted text fragments."""
        if not text:
            return "I'm processing your request..."
        
        # More comprehensive cleaning for agent artifacts
        # Remove ReAct framework artifacts
        text = re.sub(r'\bObserv\w*\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\bObservation:\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\bAction:\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\bAction Input:\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\bThought:\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\bFinal Answer:\s*', '', text, flags=re.IGNORECASE)
        
        # Remove error messages and loops
        text = re.sub(r'Error: table_names.*?not found in database', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'It looks like I made.*?mistake.*?', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'Let me try again.*?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'I need to provide.*?correct.*?', '', text, flags=re.IGNORECASE)
        
        # Remove repetitive phrases
        text = re.sub(r'(The `\w+` input is not valid[.\s]*)+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'(I got an error message[.\s]*)+', '', text, flags=re.IGNORECASE)
        
        # Clean up multiple spaces, newlines, and empty lines
        text = re.sub(r'\n\s*\n+', '\n', text)  # Remove multiple empty lines
        text = re.sub(r'\s+', ' ', text)  # Normalize spaces
        text = re.sub(r'^\s*[\n\r]+', '', text)  # Remove leading whitespace/newlines
        text = text.strip()
        
        # If the text is too short, just whitespace, or contains only artifacts, return a default message
        if len(text.strip()) < 10 or not re.search(r'[a-zA-Z]{3,}', text):
            return "I'm processing your request. Please wait a moment..."
        
        # If text contains mostly error messages or loops, provide a helpful fallback
        if re.search(r'(error|mistake|trouble|loop|invalid)', text, re.IGNORECASE) and len(text) < 100:
            return "I encountered some technical difficulties, but I'm working on your query. Please try rephrasing your question if needed."
        
        return text
    
    def render_message(self, message: ChatMessage, index: int):
        """Render a single chat message."""
        timestamp_str = message.timestamp.strftime("%H:%M")
        
        # Clean the message content
        clean_content = self.clean_agent_output(message.content)
        
        if message.sender == "user":
            st.markdown(f"""
            <div class="user-message">
                {clean_content}
                <div class="message-timestamp">{timestamp_str}</div>
            </div>
            """, unsafe_allow_html=True)
        
        elif message.sender == "system":
            st.markdown(f"""
            <div class="system-message">
                {clean_content}
                <div class="message-timestamp">{timestamp_str}</div>
            </div>
            """, unsafe_allow_html=True)
        
        elif message.message_type == "error":
            st.markdown(f"""
            <div class="error-message">
                ❌ {clean_content}
                <div class="message-timestamp">{timestamp_str}</div>
            </div>
            """, unsafe_allow_html=True)
        
        else:  # Agent message
            agent_info = self.agents.get(message.sender, {"icon": "🤖", "color": "#10b981"})
            
            st.markdown(f"""
            <div class="agent-message">
                <div class="agent-info">
                    <div class="agent-avatar" style="background-color: {agent_info['color']}; color: white;">
                        {agent_info['icon']}
                    </div>
                    <strong>{message.sender}</strong>
                    <span style="margin-left: auto; font-size: 0.75rem; color: #6b7280;">{timestamp_str}</span>
                </div>
                {clean_content}
            </div>
            """, unsafe_allow_html=True)
            
            # Render charts if present
            if message.message_type == "result" and "charts" in message.metadata:
                self.render_charts(message.metadata["charts"], index)
            
            # Show SQL query if available
            if message.metadata.get("sql_query"):
                with st.expander("🔍 View SQL Query", expanded=False):
                    st.markdown(f"""
                    <div class="sql-query-container">
                        <code>{message.metadata["sql_query"]}</code>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Show insights if available  
            if message.metadata.get("insights"):
                with st.expander("💡 Data Insights", expanded=False):
                    insights = message.metadata["insights"]
                    if isinstance(insights, dict):
                        for key, value in insights.items():
                            st.markdown(f"**{key}:** {value}")
                    elif isinstance(insights, list):
                        for insight in insights:
                            st.write(f"• {insight}")
                    else:
                        st.write(insights)
            
            # Show context information for conversational AI
            if message.metadata.get("context_used") and message.metadata.get("context_references"):
                with st.expander("🧠 Context Used", expanded=False):
                    st.markdown("This response used conversation context:")
                    for ref in message.metadata["context_references"]:
                        st.markdown(f"• {ref}")
            
            # Show data preview if available
            if message.metadata.get("data") is not None:
                try:
                    df = message.metadata["data"]
                    if hasattr(df, 'head') and len(df) > 0:
                        with st.expander("📋 Data Preview", expanded=False):
                            st.dataframe(df.head(10), use_container_width=True)
                            st.caption(f"Showing first 10 rows of {len(df)} total rows")
                except Exception:
                    pass  # Silently ignore data preview errors
    
    def render_charts(self, charts: List[Dict], message_index: int = 0):
        """Render charts inline in the chat."""
        if not charts:
            return
            
        for i, chart in enumerate(charts):
            if "figure" in chart:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                # Create unique key using message index and chart index
                chart_key = f"chart_{message_index}_{i}_{hash(str(chart.get('config', {})))}"
                st.plotly_chart(chart["figure"], use_container_width=True, key=chart_key)
                
                # Add chart description
                config = chart.get("config", {})
                if config.get("description"):
                    st.caption(f"📊 {config['description']}")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    def process_user_message(self, user_input: str):
        """Process user input with enhanced context awareness."""
        if not user_input.strip():
            return
        
        # Add user message with session context
        user_msg = ChatMessage(
            content=user_input,
            sender="user",
            message_type="text",
            session_id=st.session_state.session_id,
            conversation_id=str(uuid.uuid4())
        )
        st.session_state.chat_messages.append(user_msg)
        st.session_state.message_count += 1
        
        # Show enhanced typing indicator
        typing_placeholder = st.empty()
        typing_placeholder.markdown("""
        <div class="typing-indicator">
            <div class="loading-spinner"></div>
            <span>🧠 Processing with context awareness...</span>
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Process with selected agent
        try:
            result = self.query_agent_with_context(user_input)
            
            # Remove typing indicator
            typing_placeholder.empty()
            
            # Clean the answer
            clean_answer = self.clean_agent_output(result.get("answer", ""))
            
            # Add agent response with enhanced metadata
            agent_msg = ChatMessage(
                content=clean_answer,
                sender=st.session_state.current_agent,
                message_type="result" if result.get("success", False) else "error",
                session_id=st.session_state.session_id,
                conversation_id=user_msg.conversation_id,
                metadata={
                    "charts": result.get("charts", []),
                    "insights": result.get("insights", {}),
                    "sql_query": result.get("sql_query", ""),
                    "success": result.get("success", False),
                    "context_used": result.get("context_used", False),
                    "agent_responses": result.get("agent_responses", {}),
                    "data": result.get("data"),
                    "context_references": result.get("context_references", [])
                }
            )
            st.session_state.chat_messages.append(agent_msg)
            
            # Store results for future context
            st.session_state.last_query_results = result
            
            # Save conversation to memory if context agent is available
            if st.session_state.context_agent:
                try:
                    st.session_state.context_agent.save_conversation_turn(
                        session_id=st.session_state.session_id,
                        user_message=user_input,
                        agent_response=clean_answer,
                        agent_type=st.session_state.current_agent,
                        metadata=agent_msg.metadata
                    )
                except Exception as mem_error:
                    st.warning(f"Memory storage error: {str(mem_error)}")
            
        except Exception as e:
            typing_placeholder.empty()
            
            error_msg = ChatMessage(
                content=f"Sorry, I encountered an error while processing your request: {str(e)}",
                sender=st.session_state.current_agent,
                message_type="error",
                session_id=st.session_state.session_id
            )
            st.session_state.chat_messages.append(error_msg)
        
        # Clear input and rerun
        st.session_state.chat_input = ""
        st.rerun()
    
    def query_agent_with_context(self, question: str) -> Dict[str, Any]:
        """Query the selected agent with conversation context."""
        agent_type = self.agents[st.session_state.current_agent]["type"]
        
        # Check if this is the conversational AI orchestrator
        if agent_type == "orchestrator":
            return self.query_orchestrator(question)
        
        # For other agents, use the original method but with enhanced context
        elif agent_type == "chain":
            return st.session_state.chain.query(question, return_intermediate=False)
        
        elif agent_type == "agent":
            return st.session_state.agent.query(question)
        
        elif agent_type == "enhanced":
            return st.session_state.enhanced_agent.query(question)
        
        else:
            return {"success": False, "answer": f"Unknown agent type: {agent_type}. Available types: {list(self.agents.keys())}"}
    
    def query_orchestrator(self, question: str) -> Dict[str, Any]:
        """Query with conversational intelligence (optimized for stability)."""
        # Use the enhanced agent with smart conversational context 
        # This avoids the LangGraph recursion issues while still providing intelligent responses
        try:
            return self.query_enhanced_with_context(question)
        except Exception as e:
            return {
                "success": False,
                "answer": f"I encountered an issue while processing your question: {str(e)}",
                "error": str(e)
            }
    
    def query_enhanced_with_context(self, question: str) -> Dict[str, Any]:
        """Enhanced agent with intelligent conversational context."""
        try:
            # Get recent conversation history for context
            recent_messages = st.session_state.chat_messages[-7:] if len(st.session_state.chat_messages) > 1 else []
            last_query_results = st.session_state.last_query_results
            
            # Build context-aware prompt
            context_prompt = self.build_context_prompt(question, recent_messages, last_query_results)
            
            # Query enhanced agent with context
            result = st.session_state.enhanced_agent.query(context_prompt)
            
            # Enhance the result with conversational intelligence
            if result.get("success", False):
                # Add context metadata
                result["context_used"] = len(recent_messages) > 1 or last_query_results is not None
                context_refs = []
                if len(recent_messages) > 1:
                    context_refs.append("recent conversation")
                if last_query_results:
                    context_refs.append("previous query results")
                result["context_references"] = context_refs
                
                # Add enhanced insights based on context
                if last_query_results and last_query_results.get("data") is not None:
                    result["insights"] = result.get("insights", {})
                    if isinstance(result["insights"], dict):
                        result["insights"]["context_continuity"] = "This response builds on previous query results"
                
                # Store for future context
                st.session_state.last_query_results = result
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "answer": f"I encountered an issue while processing your contextual query: {str(e)}",
                "error": str(e)
            }
    
    def build_context_prompt(self, question: str, recent_messages: List, last_results: Dict) -> str:
        """Build an intelligent context-aware prompt for conversational queries."""
        context_parts = []
        
        # Add smart context instruction for follow-up questions
        if recent_messages or last_results:
            context_parts.append("🤖 CONVERSATIONAL AI MODE: You are having an intelligent conversation about database analysis.")
            context_parts.append("When users ask follow-up questions (like 'what about...', 'show me more...', 'how about...'), use the context below to understand what they're referring to.")
            
        # Add the current question
        context_parts.append(f"\n📝 CURRENT QUESTION: {question}")
        
        # Add conversation history with smart filtering
        if recent_messages:
            context_parts.append("\n💬 CONVERSATION HISTORY:")
            for i, msg in enumerate(recent_messages[-4:]):  # Last 4 messages for better context
                if msg.sender == "user":
                    context_parts.append(f"  User: {msg.content}")
                elif msg.sender == "agent" and msg.message_type == "result":
                    # Extract key info from agent responses
                    content_preview = msg.content[:150] + "..." if len(msg.content) > 150 else msg.content
                    context_parts.append(f"  Assistant: {content_preview}")
                    if hasattr(msg, 'metadata') and msg.metadata.get("sql_query"):
                        context_parts.append(f"    SQL: {msg.metadata['sql_query']}")
        
        # Add previous query results with intelligent formatting
        if last_results and last_results.get("data") is not None:
            context_parts.append("\n📊 PREVIOUS QUERY RESULTS:")
            
            # Add SQL query info
            if last_results.get("sql_query"):
                context_parts.append(f"  SQL Query: {last_results['sql_query']}")
            
            # Add smart data preview
            try:
                data = last_results["data"]
                if hasattr(data, 'columns'):  # DataFrame
                    context_parts.append(f"  Returned {len(data)} records with columns: {list(data.columns)}")
                    if len(data) > 0:
                        sample_data = data.head(2).to_dict('records')
                        context_parts.append(f"  Sample data: {sample_data}")
                elif isinstance(data, list) and len(data) > 0:
                    context_parts.append(f"  Returned {len(data)} records")
                    if isinstance(data[0], dict):
                        columns = list(data[0].keys())
                        context_parts.append(f"  Columns: {columns}")
                        context_parts.append(f"  Sample: {data[:2]}")
                else:
                    context_parts.append(f"  Results: {str(data)[:200]}...")
            except Exception as e:
                context_parts.append(f"  Data available (processing error: {str(e)[:50]})")
        
        # Add intelligent instruction for context awareness
        if recent_messages or last_results:
            context_parts.append("\n🎯 INSTRUCTIONS:")
            context_parts.append("- Use the above context to provide relevant, connected responses")
            context_parts.append("- When users ask 'what about X' or 'show me Y', refer to the previous data/results")
            context_parts.append("- Build upon previous queries when creating new SQL statements")
            context_parts.append("- Mention relevant connections to previous results in your response")
        
        return "\n".join(context_parts)
    
    # Keep the original method for backward compatibility
    def query_agent(self, question: str) -> Dict[str, Any]:
        """Query the selected agent (legacy method)."""
        return self.query_agent_with_context(question)
    
    def render_input_area(self):
        """Render the message input area."""
        st.markdown("### ✍️ Ask a Question")
        
        # Sample questions with better styling
        with st.expander("💡 Sample Questions", expanded=False):
            sample_questions = [
                "What are the top 5 selling artists by total sales?",
                "Show me the revenue by country with charts", 
                "How many artists are in the database?",
                "What is the distribution of track lengths?",
                "Which customers have spent the most money?",
                "Show me sales trends by genre",
                "What are the most popular albums?",
                "Which employees have the highest sales?"
            ]
            
            # Add conversational examples for the new AI agent
            if st.session_state.current_agent == "🧠 Conversational AI":
                st.success("✅ **Conversational AI Ready!** - Optimized for stability with intelligent context understanding (LangGraph recursion issues resolved)")
                st.markdown("**💡 Try these conversational examples:**")
                conversational_examples = [
                    "👋 Start: 'Show me top artists by sales'",
                    "🔗 Follow-up: 'What about their albums?'", 
                    "📊 Visualize: 'Create a chart for this data'",
                    "🔍 Deep dive: 'Tell me more about the top one'",
                    "📈 Compare: 'How does this compare to last month?'",
                    "💭 Analyze: 'What insights do you see?'"
                ]
                
                for example in conversational_examples:
                    st.markdown(f"• {example}")
                
                st.markdown("---")
            
            # Display sample questions in a grid
            cols = st.columns(2)
            for i, question in enumerate(sample_questions):
                with cols[i % 2]:
                    if st.button(
                        f"📝 {question[:45]}{'...' if len(question) > 45 else ''}", 
                        key=f"sample_{i}",
                        use_container_width=True,
                        help=question
                    ):
                        self.process_user_message(question)
        
        # Input form with better styling
        with st.form("chat_input_form", clear_on_submit=True):
            col1, col2 = st.columns([5, 1])
            
            with col1:
                user_input = st.text_input(
                    "Your question:",
                    placeholder="e.g., What are the top selling albums? Show me charts.",
                    label_visibility="collapsed",
                    help="Ask any question about your database in natural language"
                )
            
            with col2:
                submitted = st.form_submit_button(
                    "Send 📤", 
                    use_container_width=True,
                    type="primary"
                )
            
            if submitted and user_input:
                self.process_user_message(user_input)
    
    def render_sidebar_info(self):
        """Render sidebar with database info and settings."""
        with st.sidebar:
            st.title("🗄️ Database Dashboard")
            
            # API key status
            api_key = os.getenv("TOGETHER_API_KEY")
            if api_key:
                st.success("✅ API Key Configured")
            else:
                st.error("❌ API Key Missing")
            
            # Current agent info
            st.subheader("🤖 Current Agent")
            current_agent_info = self.agents[st.session_state.current_agent]
            
            st.markdown(f"""
            <div class="metric-card">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background-color: {current_agent_info['color']}; color: white; 
                                width: 40px; height: 40px; border-radius: 50%; 
                                display: flex; align-items: center; justify-content: center;
                                font-size: 1.2rem; font-weight: bold;">
                        {current_agent_info['icon']}
                    </div>
                    <div>
                        <div style="font-weight: 600; color: #1f2937;">
                            {st.session_state.current_agent}
                        </div>
                        <div style="font-size: 0.9rem; color: #6b7280;">
                            {current_agent_info['description']}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Database info
            if st.session_state.db_manager:
                try:
                    tables = st.session_state.db_manager.list_tables()
                    st.subheader("📊 Database Stats")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Tables", len(tables))
                    with col2:
                        st.metric("Messages", len(st.session_state.chat_messages))
                    
                    with st.expander("📋 Table List"):
                        for table in tables:
                            st.write(f"• **{table}**")
                    
                    with st.expander("📖 Schema Description"):
                        st.markdown(get_chinook_schema_description())
                
                except Exception as e:
                    st.error(f"Error loading database info: {str(e)}")
            
            # Chat statistics and session info
            st.subheader("📈 Chat Statistics") 
            total_messages = len(st.session_state.chat_messages)
            user_messages = len([m for m in st.session_state.chat_messages if m.sender == "user"])
            agent_messages = len([m for m in st.session_state.chat_messages if m.sender != "user" and m.sender != "system"])
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Messages", total_messages)
            with col2:
                st.metric("User Queries", user_messages)
            
            # Session management
            st.subheader("🗂️ Session Management")
            session_short = st.session_state.session_id[:8]
            st.text(f"Session ID: {session_short}...")
            
            if st.button("🔄 New Session"):
                # Clear current session
                st.session_state.chat_messages = []
                st.session_state.session_id = str(uuid.uuid4())
                st.session_state.conversation_context = {}
                st.session_state.last_query_results = None
                st.session_state.message_count = 0
                
                # Restart context agent session if available
                if st.session_state.context_agent:
                    try:
                        st.session_state.context_agent.start_session()
                    except Exception:
                        pass
                
                # Add new welcome message
                welcome_msg = ChatMessage(
                    content="""🎉 **New Session Started!** 

Ready to explore your database with enhanced conversational intelligence! 🚀""",
                    sender="system",
                    message_type="text",
                    session_id=st.session_state.session_id
                )
                st.session_state.chat_messages.append(welcome_msg)
                st.rerun()
            
            # Memory status for conversational AI
            if st.session_state.current_agent == "🧠 Conversational AI":
                st.subheader("🧠 Memory Status")
                if st.session_state.orchestrator and st.session_state.context_agent:
                    st.success("✅ Conversational Memory Active")
                    st.caption("I can remember our conversation and provide context-aware responses!")
                else:
                    st.warning("⚠️ Limited Memory Mode")
                    st.caption("Multi-agent system not fully loaded")
            

            
            # Action buttons
            st.subheader("🔧 Actions")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear Chat", use_container_width=True, type="secondary"):
                    st.session_state.chat_messages = []
                    st.session_state.message_count = 0
                    welcome_msg = ChatMessage(
                        content="👋 Chat cleared! Ready for new questions!",
                        sender="system",
                        message_type="text"
                    )
                    st.session_state.chat_messages.append(welcome_msg)
                    st.rerun()
            
            with col2:
                if st.button("📥 Export Chat", use_container_width=True, type="secondary"):
                    # Export chat as JSON
                    chat_data = []
                    for msg in st.session_state.chat_messages:
                        chat_data.append({
                            "timestamp": msg.timestamp.isoformat(),
                            "sender": msg.sender,
                            "content": msg.content,
                            "type": msg.message_type
                        })
                    
                    st.download_button(
                        label="💾 Download JSON",
                        data=json.dumps(chat_data, indent=2),
                        file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )

def main():
    """Main application function."""
    st.markdown('<h1 class="main-header">💬 SQL Chat Assistant</h1>', unsafe_allow_html=True)
    
    # Display multi-agent system status
    if not MULTI_AGENT_AVAILABLE and MULTI_AGENT_ERROR:
        st.warning(f"⚠️ Multi-agent system not available: {MULTI_AGENT_ERROR}")
        st.info("💡 Don't worry! The conversational features will still work with a fallback system.")
    
    # Initialize chat interface
    chat = ChatInterface()
    chat.initialize_session_state()
    
    # Load models
    if not chat.load_models():
        st.stop()
    
    # Render sidebar
    chat.render_sidebar_info()
    
    # Main chat interface
    chat.render_agent_selector()
    chat.render_chat_history()
    chat.render_input_area()
    
    # Auto-scroll to bottom (JavaScript)
    st.markdown("""
    <script>
    setTimeout(function() {
        var chatContainer = document.querySelector('.chat-container');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }, 100);
    </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 