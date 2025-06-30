"""
Enhanced Text-to-SQL Chat Application
A conversational interface using the Enhanced Agent with chat context and memory.
"""

import streamlit as st
import os
import time
import json
from datetime import datetime
from typing import Dict, Any, List
import uuid

# Set API key for easy testing
os.environ["TOGETHER_API_KEY"] = "tgp_v1_XELYRCJuDTY69-ICL7OBEONSAYquezhyLAMfyi5-Cgc"

# Import our enhanced agent
try:
    from sql_agent_enhanced import create_enhanced_sql_agent
    from database_tools import DatabaseManager
    from config import TOGETHER_MODELS
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="SQL Chat Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for chat interface
st.markdown("""
<style>
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 10px;
        border-radius: 10px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        margin: 10px 0;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 15px 15px 5px 15px;
        margin: 10px 0 10px 20%;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 15px;
        border-radius: 15px 15px 15px 5px;
        margin: 10px 20% 10px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .system-message {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 10%;
        text-align: center;
        font-style: italic;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .chat-input {
        position: sticky;
        bottom: 0;
        background: white;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    }
    
    .context-info {
        background: #e8f4f8;
        border-left: 4px solid #4facfe;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
        font-size: 0.9em;
    }
    
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 5px;
        text-align: center;
    }
    
    .visualization-container {
        background: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

class ConversationalSQLAgent:
    """Enhanced SQL Agent with conversational capabilities."""
    
    def __init__(self):
        """Initialize the conversational agent."""
        self.agent = None
        self.conversation_history = []
        self.context_window = 5  # Keep last 5 exchanges for context
        
    def initialize_agent(self, api_key: str, database_path: str = "chinook.db", model: str = None):
        """Initialize the enhanced agent."""
        try:
            # Use the selected model if provided, otherwise use default
            if model:
                self.agent = create_enhanced_sql_agent(database_path, model=model, api_key=api_key)
            else:
                self.agent = create_enhanced_sql_agent(database_path, api_key=api_key)
            return True
        except Exception as e:
            st.error(f"Failed to initialize agent: {str(e)}")
            return False
    
    def add_to_conversation(self, user_message: str, assistant_response: Dict[str, Any]):
        """Add exchange to conversation history."""
        exchange = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "assistant_response": assistant_response,
            "sql_query": assistant_response.get("sql_query", ""),
            "has_charts": len(assistant_response.get("generated_charts", [])) > 0
        }
        self.conversation_history.append(exchange)
        
        # Keep only recent context to avoid token limits
        if len(self.conversation_history) > self.context_window:
            self.conversation_history = self.conversation_history[-self.context_window:]
    
    def get_conversation_context(self) -> str:
        """Generate enhanced context from recent conversation history."""
        if not self.conversation_history:
            return ""
        
        context_parts = ["Previous conversation context:"]
        
        # Use last 5 exchanges (increased from 3) for better context
        recent_exchanges = self.conversation_history[-5:]
        
        for i, exchange in enumerate(recent_exchanges, 1):
            context_parts.append(f"\n{i}. User asked: {exchange['user_message']}")
            
            # Add SQL context if available
            if exchange.get('sql_query'):
                context_parts.append(f"   SQL: {exchange['sql_query']}")
            
            # Add enhanced answer context (increased from 100 to 300 chars)
            answer = exchange['assistant_response'].get('answer', '')
            if answer:
                context_parts.append(f"   Answer: {answer[:300]}...")
            
            # Add visualization context
            if exchange.get('has_charts'):
                chart_count = len(exchange['assistant_response'].get('generated_charts', []))
                context_parts.append(f"   Visualizations: {chart_count} charts generated")
            
            # Add key findings if available
            key_data = self._extract_context_key_data(answer)
            if key_data:
                context_parts.append(f"   Key Data: {key_data}")
        
        # Add context instructions
        context_parts.append("\nContext Instructions:")
        context_parts.append("- Use this context to understand follow-up questions")
        context_parts.append("- Reference previous results when relevant")
        context_parts.append("- Maintain conversation continuity")
        context_parts.append("- Build upon previous insights")
        
        return "\n".join(context_parts)
    
    def _extract_context_key_data(self, text: str) -> str:
        """Extract key data points from response text for context."""
        if not text:
            return ""
        
        import re
        key_points = []
        
        # Extract numbers and percentages
        numbers = re.findall(r'\b\d+(?:\.\d+)?%?\b', text)
        if numbers:
            key_points.extend(numbers[:3])  # Top 3 numbers
        
        # Extract entities (capitalized words)
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        if entities:
            # Filter out common words and keep unique entities
            filtered_entities = [e for e in entities if e not in ['The', 'This', 'That', 'SQL', 'SELECT']]
            key_points.extend(list(set(filtered_entities))[:3])  # Top 3 entities
        
        return ', '.join(key_points) if key_points else ""
    
    def is_followup_question(self, message: str) -> bool:
        """Enhanced follow-up detection with intent classification."""
        return self._detect_enhanced_followup(message)
    
    def _detect_enhanced_followup(self, message: str) -> bool:
        """Advanced follow-up detection with pattern matching and intent analysis."""
        message_lower = message.lower()
        
        # Enhanced pattern categories
        patterns = {
            'pronouns': ['this', 'that', 'these', 'those', 'it', 'they', 'them', 'such', 'similar'],
            'questions': ['what about', 'how about', 'what if', 'can you', 'could you', 'would you', 'why', 'how', 'when', 'where', 'which'],
            'continuations': ['also', 'additionally', 'furthermore', 'moreover', 'and', 'but', 'however', 'although', 'next', 'then', 'after that'],
            'modifications': ['change', 'modify', 'update', 'alter', 'adjust', 'instead', 'rather', 'different', 'another', 'add', 'remove'],
            'comparisons': ['compare', 'contrast', 'versus', 'vs', 'against', 'difference', 'similar', 'same', 'different', 'better', 'worse'],
            'context_refs': ['from the result', 'from that', 'in the query', 'based on', 'according to']
        }
        
        # Intent classification keywords
        intent_keywords = {
            'clarification': ['what does', 'what is', 'explain', 'meaning', 'definition', 'clarify', 'understand'],
            'drill_down': ['more details', 'show me', 'breakdown', 'expand', 'specific', 'tell me about'],
            'visualization': ['chart', 'graph', 'plot', 'visualize', 'show', 'display', 'pie chart', 'bar chart'],
            'analysis': ['trend', 'pattern', 'correlation', 'analyze', 'analysis', 'insight', 'finding'],
            'modification': ['filter', 'sort', 'group by', 'limit', 'where']
        }
        
        # Count pattern matches
        pattern_matches = 0
        for category, words in patterns.items():
            for word in words:
                if word in message_lower:
                    pattern_matches += 1
        
        # Count intent matches (weighted higher)
        intent_matches = 0
        detected_intent = None
        for intent, keywords in intent_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    intent_matches += len(keyword.split()) * 2  # Weight longer phrases
                    detected_intent = intent
        
        # Context reference check
        context_references = 0
        if self.conversation_history:
            last_response = self.conversation_history[-1].get('assistant_response', {})
            response_text = last_response.get('answer', '') if isinstance(last_response, dict) else str(last_response)
            if response_text:
                # Check for content overlap
                response_words = set(response_text.lower().split())
                message_words = set(message_lower.split())
                common_words = response_words & message_words
                context_references = len([w for w in common_words if len(w) > 3])
        
        # Calculate confidence score
        base_confidence = pattern_matches * 0.15
        intent_confidence = intent_matches * 0.1
        context_confidence = context_references * 0.2
        
        # Conversation continuity bonus for short questions
        continuity_bonus = 0.3 if len(message.split()) <= 8 else 0.0
        
        total_confidence = base_confidence + intent_confidence + context_confidence + continuity_bonus
        
        # Store detected intent for potential use
        if hasattr(self, '_last_detected_intent'):
            self._last_detected_intent = detected_intent
        
        return total_confidence >= 0.4  # Enhanced threshold
    
    def enhance_query_with_context(self, user_message: str) -> str:
        """Enhance the user query with conversation context."""
        context = self.get_conversation_context()
        
        if not context or not self.is_followup_question(user_message):
            return user_message
        
        enhanced_query = f"""
        {context}
        
        Current question: {user_message}
        
        Please answer the current question considering the previous conversation context.
        If this is a follow-up question, use the previous results and context appropriately.
        """
        
        return enhanced_query
    
    def query(self, user_message: str) -> Dict[str, Any]:
        """Process a conversational query."""
        if not self.agent:
            return {"success": False, "answer": "Agent not initialized"}
        
        try:
            # Enhance query with conversation context
            enhanced_query = self.enhance_query_with_context(user_message)
            
            # Process with the enhanced agent
            result = self.agent.query(enhanced_query)
            
            # Add conversation metadata
            result["original_message"] = user_message
            result["enhanced_query"] = enhanced_query
            result["is_followup"] = self.is_followup_question(user_message)
            result["conversation_length"] = len(self.conversation_history)
            
            # Add to conversation history
            self.add_to_conversation(user_message, result)
            
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "answer": f"Error processing query: {str(e)}",
                "original_message": user_message
            }
            self.add_to_conversation(user_message, error_result)
            return error_result

def initialize_session_state():
    """Initialize session state for chat interface."""
    if 'chat_agent' not in st.session_state:
        st.session_state.chat_agent = ConversationalSQLAgent()
    
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    if 'agent_initialized' not in st.session_state:
        st.session_state.agent_initialized = False
    
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    if 'current_model' not in st.session_state:
        st.session_state.current_model = None

def display_chat_message(message: Dict[str, Any], is_user: bool = True):
    """Display a chat message with styling."""
    if is_user:
        st.markdown(f"""
        <div class="user-message">
            <strong>You:</strong> {message['content']}
            <br><small>{message['timestamp']}</small>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Assistant message
        st.markdown(f"""
        <div class="assistant-message">
            <strong>SQL Assistant:</strong> {message['content']}
            <br><small>{message['timestamp']}</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Display metrics if available
        if 'metrics' in message:
            display_message_metrics(message['metrics'])
        
        # Display visualizations if available
        if 'visualizations' in message:
            display_message_visualizations(message['visualizations'])

def display_message_metrics(metrics: Dict[str, Any]):
    """Display metrics for a message."""
    cols = st.columns(4)
    
    with cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⏱️ {metrics.get('execution_time', 0):.2f}s</h3>
            <p>Execution Time</p>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 {metrics.get('charts_count', 0)}</h3>
            <p>Charts Generated</p>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💡 {metrics.get('insights_count', 0)}</h3>
            <p>Insights</p>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[3]:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🔄 {metrics.get('conversation_length', 0)}</h3>
            <p>Conversation Length</p>
        </div>
        """, unsafe_allow_html=True)

def display_message_visualizations(visualizations: List[Dict[str, Any]]):
    """Display visualizations for a message."""
    if not visualizations:
        return
    
    st.markdown('<div class="visualization-container">', unsafe_allow_html=True)
    st.subheader("📈 Generated Visualizations")
    
    for i, viz in enumerate(visualizations):
        if 'figure' in viz and viz['figure'] is not None:
            config = viz.get('config', {})
            st.markdown(f"**{config.get('title', f'Chart {i+1}')}**")
            st.plotly_chart(viz['figure'], use_container_width=True, key=f"chat_viz_{i}_{time.time()}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_chat_sidebar():
    """Render the chat sidebar with controls and history."""
    st.sidebar.header("💬 Chat Controls")
    
    # API Key status
    api_key = os.getenv("TOGETHER_API_KEY")
    if api_key:
        st.sidebar.success("✅ API Key Configured")
    else:
        st.sidebar.error("❌ API Key Missing")
        st.sidebar.info("Set TOGETHER_API_KEY environment variable")
    
    # Model selection
    selected_model = st.sidebar.selectbox(
        "🤖 Select Model",
        options=list(TOGETHER_MODELS.keys()),
        index=0,
        format_func=lambda x: TOGETHER_MODELS[x],
        key="selected_model"
    )
    
    # The selected_model is automatically stored in st.session_state.selected_model
    # due to the key="selected_model" parameter
    
    # Chat statistics
    st.sidebar.subheader("📊 Chat Statistics")
    if st.session_state.chat_agent.conversation_history:
        total_messages = len(st.session_state.chat_agent.conversation_history)
        st.sidebar.metric("Total Exchanges", total_messages)
        
        # Show recent topics
        st.sidebar.subheader("🔍 Recent Topics")
        for i, exchange in enumerate(st.session_state.chat_agent.conversation_history[-3:]):
            st.sidebar.write(f"• {exchange['user_message'][:40]}...")
    
    # Sample conversation starters
    st.sidebar.subheader("💡 Conversation Starters")
    starters = [
        "What are the top 5 selling artists?",
        "Show me revenue by country",
        "Analyze customer spending patterns",
        "What's the most popular genre?",
        "Compare sales by media type"
    ]
    
    for starter in starters:
        if st.sidebar.button(f"💬 {starter[:30]}...", key=f"starter_{starter}"):
            return starter
    
    # Clear conversation
    if st.sidebar.button("🗑️ Clear Conversation"):
        st.session_state.chat_messages = []
        st.session_state.chat_agent.conversation_history = []
        st.rerun()
    
    return None

def main():
    """Main chat application."""
    st.title("💬 SQL Chat Assistant")
    st.markdown("Ask questions about your database and get intelligent responses with visualizations!")
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar
    suggested_query = render_chat_sidebar()
    
    # Check if model has changed and reinitialize if needed
    selected_model = st.session_state.get('selected_model', None)
    if (st.session_state.agent_initialized and 
        st.session_state.current_model != selected_model):
        # Model changed, need to reinitialize
        st.session_state.agent_initialized = False
        st.session_state.current_model = selected_model
        st.info(f"🔄 Model changed to {selected_model}. Reinitializing agent...")
    
    # Initialize agent if not done
    if not st.session_state.agent_initialized:
        api_key = os.getenv("TOGETHER_API_KEY")
        if api_key:
            # Get the selected model from session state
            selected_model = st.session_state.get('selected_model', None)
            
            with st.spinner("🤖 Initializing SQL Chat Assistant..."):
                if st.session_state.chat_agent.initialize_agent(api_key, model=selected_model):
                    st.session_state.agent_initialized = True
                    st.session_state.current_model = selected_model
                    
                    # Display which model is being used
                    model_name = selected_model if selected_model else "default"
                    st.success(f"✅ Chat Assistant Ready! (Using: {model_name})")
                    
                    # Add welcome message
                    welcome_msg = {
                        "content": "Hello! I'm your SQL Chat Assistant. I can help you analyze your database with intelligent queries and visualizations. Ask me anything about your data!",
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "type": "assistant"
                    }
                    st.session_state.chat_messages.append(welcome_msg)
                else:
                    st.error("❌ Failed to initialize chat assistant")
                    st.stop()
        else:
            st.error("❌ API key not found. Please set TOGETHER_API_KEY environment variable.")
            st.stop()
    
    # Display chat messages
    st.subheader("💬 Conversation")
    
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_messages:
            if message['type'] == 'user':
                display_chat_message(message, is_user=True)
            else:
                display_chat_message(message, is_user=False)
    
    # Chat input
    st.markdown("---")
    
    # Use suggested query if available
    default_message = suggested_query if suggested_query else ""
    
    user_input = st.text_input(
        "💬 Ask me anything about your database:",
        value=default_message,
        placeholder="e.g., What are the top selling artists? or Tell me more about those results...",
        disabled=st.session_state.processing
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        send_button = st.button("📤 Send", disabled=st.session_state.processing or not user_input.strip())
    
    with col2:
        if st.session_state.processing:
            st.info("🤖 Processing your question...")
    
    # Process user input
    if send_button and user_input.strip():
        st.session_state.processing = True
        
        # Add user message
        user_msg = {
            "content": user_input,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "type": "user"
        }
        st.session_state.chat_messages.append(user_msg)
        
        # Process with chat agent
        start_time = time.time()
        result = st.session_state.chat_agent.query(user_input)
        execution_time = time.time() - start_time
        
        # Create assistant response
        assistant_msg = {
            "content": result.get("answer", "I couldn't process that question."),
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "type": "assistant",
            "metrics": {
                "execution_time": execution_time,
                "charts_count": len(result.get("generated_charts", [])),
                "insights_count": len(result.get("visualization_insights", [])),
                "conversation_length": len(st.session_state.chat_agent.conversation_history)
            }
        }
        
        # Add visualizations if available
        if result.get("generated_charts"):
            assistant_msg["visualizations"] = result["generated_charts"]
        
        st.session_state.chat_messages.append(assistant_msg)
        st.session_state.processing = False
        
        # Rerun to update the interface
        st.rerun()
    
    # Context information
    if st.session_state.chat_agent.conversation_history:
        with st.expander("🔍 Conversation Context", expanded=False):
            st.markdown(f"""
            <div class="context-info">
                <strong>Context Window:</strong> Last {st.session_state.chat_agent.context_window} exchanges<br>
                <strong>Total Exchanges:</strong> {len(st.session_state.chat_agent.conversation_history)}<br>
                <strong>Follow-up Detection:</strong> {'✅ Active' if len(st.session_state.chat_agent.conversation_history) > 0 else '❌ Inactive'}
            </div>
            """, unsafe_allow_html=True)
            
            # Show conversation context
            context = st.session_state.chat_agent.get_conversation_context()
            if context:
                st.text_area("Current Context", context, height=200)

if __name__ == "__main__":
    main() 