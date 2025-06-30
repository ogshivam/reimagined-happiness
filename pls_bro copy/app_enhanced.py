"""
Enhanced Streamlit web interface for the Text-to-SQL tool with Advanced Visualization.
Provides an interactive UI for testing the enhanced agent with automatic chart generation.
"""

import streamlit as st
import os
import pandas as pd
from typing import Dict, Any
import time
import json
import plotly.graph_objects as go
from datetime import datetime
import base64
from io import BytesIO

# Import our modules
try:
    from sql_chain import SQLChain
    from sql_agent_simple import SimpleSQLAgent
    from sql_agent_enhanced import EnhancedSQLAgent, create_enhanced_sql_agent
    from database_tools import DatabaseManager, get_chinook_schema_description
    from config import SAMPLE_QUERIES, TOGETHER_MODELS
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Enhanced Text-to-SQL Generator with Visualizations",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #1f77b4;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .approach-card {
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 2px solid #ddd;
        margin: 1rem 0;
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
    .viz-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 0.5rem 0;
    }
    .insight-item {
        padding: 0.75rem;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
        border-left: 4px solid #007bff;
        border-radius: 0.25rem;
        color: #212529 !important;
        font-weight: 500;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    .metric-container {
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        margin: 1rem 0;
    }
    /* Fix for data insights visibility */
    .stMarkdown .insight-item {
        color: #212529 !important;
        background-color: #f8f9fa !important;
    }
    /* Ensure text in expanders is visible */
    .streamlit-expanderContent {
        color: #212529 !important;
    }
    /* Fix JSON display in expanders */
    .streamlit-expanderContent pre {
        color: #212529 !important;
        background-color: #f8f9fa !important;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'enhanced_agent' not in st.session_state:
        st.session_state.enhanced_agent = None
    if 'chain' not in st.session_state:
        st.session_state.chain = None
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = None
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    if 'visualization_results' not in st.session_state:
        st.session_state.visualization_results = {}

def load_models():
    """Load the enhanced SQL agent and other models."""
    try:
        api_key = os.getenv("TOGETHER_API_KEY")
        if not api_key:
            st.error("TOGETHER_API_KEY environment variable not found!")
            st.info("Please set your Together AI API key in the environment")
            return False
        
        model = st.session_state.get('selected_model', "meta-llama/Llama-3-70b-chat-hf")
        
        # Load enhanced agent if not loaded
        if st.session_state.enhanced_agent is None:
            with st.spinner("Loading Enhanced SQL Agent with Visualization..."):
                try:
                    st.session_state.enhanced_agent = create_enhanced_sql_agent(
                        database_path="chinook.db",
                        model=model,
                        api_key=api_key
                    )
                    st.sidebar.success("✅ Enhanced Agent Loaded")
                except Exception as e:
                    st.sidebar.error(f"❌ Enhanced Agent Failed: {str(e)}")
                    st.session_state.enhanced_agent = None
        
        # Load other models if not loaded
        if st.session_state.chain is None:
            with st.spinner("Loading SQL Chain..."):
                try:
                    st.session_state.chain = SQLChain("chinook.db", model=model, api_key=api_key)
                    st.sidebar.success("✅ SQL Chain Loaded")
                except Exception as e:
                    st.sidebar.error(f"❌ SQL Chain Failed: {str(e)}")
                    st.session_state.chain = None
        
        if st.session_state.agent is None:
            with st.spinner("Loading Simple SQL Agent..."):
                try:
                    st.session_state.agent = SimpleSQLAgent("chinook.db", model=model, api_key=api_key)
                    st.sidebar.success("✅ Simple Agent Loaded")
                except Exception as e:
                    st.sidebar.error(f"❌ Simple Agent Failed: {str(e)}")
                    st.session_state.agent = None
        
        if st.session_state.db_manager is None:
            try:
                st.session_state.db_manager = DatabaseManager("chinook.db")
                st.sidebar.success("✅ Database Manager Loaded")
            except Exception as e:
                st.sidebar.error(f"❌ Database Manager Failed: {str(e)}")
                st.session_state.db_manager = None
        
        # Return True if at least one component loaded successfully
        return any([
            st.session_state.enhanced_agent is not None,
            st.session_state.chain is not None,
            st.session_state.agent is not None,
            st.session_state.db_manager is not None
        ])
        
    except Exception as e:
        st.error(f"Error loading models: {str(e)}")
        return False

def display_database_info():
    """Display database information and schema."""
    if st.session_state.db_manager is None:
        return
    
    with st.expander("📊 Database Information", expanded=False):
        try:
            tables = st.session_state.db_manager.list_tables()
            st.write("**Available Tables:**")
            
            cols = st.columns(3)
            for i, table in enumerate(tables):
                with cols[i % 3]:
                    if st.button(table, key=f"table_{table}"):
                        show_table_info(table)
            
            st.write("**Database Schema Overview:**")
            st.info(get_chinook_schema_description())
            
        except Exception as e:
            st.error(f"Error loading database info: {str(e)}")

def show_table_info(table_name: str):
    """Show detailed information about a specific table."""
    try:
        # Get sample data
        sample_data = st.session_state.db_manager.get_sample_data(table_name, limit=5)
        
        st.subheader(f"Table: {table_name}")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("**Sample Data:**")
            st.dataframe(sample_data, use_container_width=True)
        
        with col2:
            st.write("**Statistics:**")
            stats = st.session_state.db_manager.get_table_statistics(table_name)
            for key, value in stats.items():
                st.metric(key, value)
                
    except Exception as e:
        st.error(f"Error loading table info: {str(e)}")

def process_query_enhanced(question: str, show_intermediate: bool = False):
    """Process query using the enhanced agent with visualizations."""
    if not st.session_state.enhanced_agent:
        st.error("Enhanced agent not loaded!")
        return
    
    start_time = time.time()
    
    try:
        with st.spinner("🤖 Processing with Enhanced Agent (including visualizations)..."):
            result = st.session_state.enhanced_agent.query(question)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Store result for persistence
        st.session_state.visualization_results = result
        
        if result.get("success", False):
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.success("✅ Query processed successfully with visualizations!")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("⏱️ Execution Time", f"{execution_time:.2f}s")
            with col2:
                chart_count = len(result.get("generated_charts", []))
                st.metric("📊 Charts Generated", chart_count)
            with col3:
                insight_count = len(result.get("visualization_insights", []))
                st.metric("💡 Insights", insight_count)
            with col4:
                export_count = len(result.get("export_options", []))
                st.metric("📤 Export Options", export_count)
            
            # Display answer
            st.subheader("📝 Answer")
            st.write(result.get("answer", "No answer provided"))
            
            # Display visualizations
            display_visualizations(result, "query_result")
            
            # Display insights
            display_insights(result)
            
            # Display intermediate results if requested
            if show_intermediate:
                display_intermediate_results(result)
            
            # Add to history
            st.session_state.query_history.append({
                "timestamp": datetime.now(),
                "question": question,
                "result": result,
                "execution_time": execution_time,
                "approach": "Enhanced Agent"
            })
            
        else:
            st.markdown('<div class="error-box">', unsafe_allow_html=True)
            st.error("❌ Query failed!")
            st.write(result.get("answer", "Unknown error occurred"))
            
            # Show debug information
            if show_intermediate:
                with st.expander("🔍 Debug Information", expanded=False):
                    st.json(result)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        
        st.error(f"❌ Error processing query: {str(e)}")
        st.write(f"Execution time: {execution_time:.2f}s")
        
        # Show debug information
        if show_intermediate:
            with st.expander("🔍 Debug Information", expanded=True):
                st.write("**Error Details:**")
                st.code(str(e))
                st.write("**Question:**")
                st.code(question)

def display_visualizations(result: Dict[str, Any], context: str = "main"):
    """Display generated visualizations."""
    generated_charts = result.get("generated_charts", [])
    
    if not generated_charts:
        st.info("🎨 No visualizations were generated for this query.")
        return
    
    st.subheader("📈 Generated Visualizations")
    
    # Display charts
    for i, chart_data in enumerate(generated_charts):
        try:
            config = chart_data["config"]
            fig = chart_data.get("figure")
            
            if fig is None:
                st.warning(f"⚠️ Chart {i+1} figure not available")
                continue
            
            with st.container():
                st.markdown(f'<div class="viz-card">', unsafe_allow_html=True)
                
                # Chart header
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{config['title']}**")
                    st.caption(config['description'])
                with col2:
                    # Export options for individual chart - use unique keys with timestamp
                    import time
                    timestamp = int(time.time() * 1000)  # millisecond precision
                    chart_id = f"chart_{context}_{i}_{timestamp}_{hash(config['title']) % 1000}"
                    export_format = st.selectbox(
                        "Export as:",
                        ["png", "html", "svg", "json"],
                        key=f"export_format_{chart_id}"
                    )
                    if st.button("💾 Export", key=f"export_btn_{chart_id}"):
                        export_chart(fig, export_format, config['title'])
                
                # Display the chart
                st.plotly_chart(fig, use_container_width=True, key=f"plotly_chart_{chart_id}")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"❌ Error displaying chart {i+1}: {str(e)}")
            st.write(f"Chart config: {chart_data.get('config', {})}")
    
    # Dashboard export options
    if len(generated_charts) > 1:
        st.subheader("📊 Dashboard Export")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info("💡 You can export all visualizations as a combined dashboard")
        with col2:
            if st.button("📋 Export Dashboard", key=f"dashboard_export_btn_{context}"):
                export_dashboard(result)

def display_insights(result: Dict[str, Any]):
    """Display data insights."""
    insights = result.get("visualization_insights", [])
    
    if not insights:
        return
    
    st.subheader("💡 Data Insights")
    
    for i, insight in enumerate(insights):
        # Use HTML with proper styling for better visibility
        st.markdown(
            f'<div class="insight-item">🔍 {insight}</div>', 
            unsafe_allow_html=True
        )
    
    # Additional analysis
    data_analysis = result.get("data_analysis", {})
    if data_analysis and "error" not in data_analysis:
        with st.expander("📊 Detailed Data Analysis", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Data Characteristics:**")
                characteristics = {
                    "Rows": data_analysis.get("num_rows", 0),
                    "Columns": data_analysis.get("num_columns", 0),
                    "Numeric Columns": len(data_analysis.get("numeric_columns", [])),
                    "Categorical Columns": len(data_analysis.get("categorical_columns", []))
                }
                # Display as formatted text instead of JSON for better visibility
                for key, value in characteristics.items():
                    st.write(f"• **{key}**: {value}")
            
            with col2:
                st.markdown("**Column Types:**")
                column_types = data_analysis.get("column_types", {})
                if column_types:
                    # Display as formatted text instead of JSON
                    for col_name, col_type in column_types.items():
                        st.write(f"• **{col_name}**: {col_type}")
                else:
                    st.write("No column type information available")

def display_intermediate_results(result: Dict[str, Any]):
    """Display intermediate results like SQL query and raw data."""
    with st.expander("🔍 Intermediate Results", expanded=False):
        # SQL Query
        if result.get("sql_query"):
            st.write("**Generated SQL Query:**")
            st.code(result["sql_query"], language="sql")
        
        # Raw Data
        raw_data_dict = result.get("raw_data")
        if raw_data_dict is not None:
            st.write("**Raw Query Results:**")
            if isinstance(raw_data_dict, dict) and "data" in raw_data_dict:
                # Convert back to DataFrame for display
                raw_data = pd.DataFrame(raw_data_dict["data"])
                st.dataframe(raw_data, use_container_width=True)
            else:
                # Handle legacy format or direct DataFrame
                st.dataframe(raw_data_dict, use_container_width=True)
        
        # Chart Suggestions
        suggested_charts = result.get("suggested_charts", [])
        if suggested_charts:
            st.write("**Chart Suggestions:**")
            for suggestion in suggested_charts:
                st.write(f"- **{suggestion['type']}**: {suggestion.get('description', 'No description')}")

def export_chart(fig: go.Figure, format_type: str, title: str):
    """Export individual chart."""
    try:
        if format_type == "png":
            img_bytes = fig.to_image(format="png")
            st.download_button(
                label=f"Download {title}.png",
                data=img_bytes,
                file_name=f"{title}.png",
                mime="image/png"
            )
            st.success(f"✅ {title}.png ready for download!")
        elif format_type == "html":
            html_content = fig.to_html(include_plotlyjs='cdn')
            st.download_button(
                label=f"Download {title}.html",
                data=html_content,
                file_name=f"{title}.html",
                mime="text/html"
            )
            st.success(f"✅ {title}.html ready for download!")
        elif format_type == "svg":
            svg_content = fig.to_image(format="svg")
            st.download_button(
                label=f"Download {title}.svg",
                data=svg_content,
                file_name=f"{title}.svg",
                mime="image/svg+xml"
            )
            st.success(f"✅ {title}.svg ready for download!")
        elif format_type == "json":
            json_content = fig.to_json()
            st.download_button(
                label=f"Download {title}.json",
                data=json_content,
                file_name=f"{title}.json",
                mime="application/json"
            )
            st.success(f"✅ {title}.json ready for download!")
    except Exception as e:
        st.error(f"❌ Export failed: {str(e)}")
        st.info("💡 Try a different export format or check your chart data")

def export_dashboard(result: Dict[str, Any]):
    """Export complete dashboard."""
    try:
        generated_charts = result.get("generated_charts", [])
        insights = result.get("visualization_insights", [])
        
        # Create HTML dashboard
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SQL Analysis Dashboard</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; color: #1f77b4; }}
                .chart-container {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
                .insights {{ background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .insight-item {{ margin: 5px 0; padding: 5px; background-color: white; border-left: 4px solid #007bff; }}
            </style>
        </head>
        <body>
            <h1 class="header">📊 SQL Analysis Dashboard</h1>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Question:</strong> {result.get('question', 'N/A')}</p>
            
            <div class="insights">
                <h2>💡 Key Insights</h2>
        """
        
        for insight in insights:
            html_content += f'<div class="insight-item">🔍 {insight}</div>'
        
        html_content += "</div>"
        
        # Add charts
        for i, chart_data in enumerate(generated_charts):
            config = chart_data["config"]
            fig_html = chart_data["html"]
            
            html_content += f"""
            <div class="chart-container">
                <h3>{config['title']}</h3>
                <p>{config['description']}</p>
                {fig_html}
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        # Provide download
        st.download_button(
            label="📋 Download Complete Dashboard",
            data=html_content,
            file_name=f"sql_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html"
        )
        
        st.success("✅ Dashboard export ready for download!")
        
    except Exception as e:
        st.error(f"Dashboard export failed: {str(e)}")

def process_query_chain(question: str, show_intermediate: bool = False):
    """Process query using the chain approach."""
    if not st.session_state.chain:
        st.error("Chain not loaded!")
        return
    
    start_time = time.time()
    
    with st.spinner("⚡ Processing with SQL Chain..."):
        result = st.session_state.chain.query(question, return_intermediate=show_intermediate)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    if result["success"]:
        st.success("✅ Query processed successfully!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("⏱️ Execution Time", f"{execution_time:.2f}s")
        with col2:
            if show_intermediate and "num_results" in result:
                st.metric("📊 Results", result["num_results"])
        
        st.subheader("📝 Answer")
        st.write(result["answer"])
        
        if show_intermediate:
            with st.expander("🔍 Intermediate Results", expanded=False):
                if "sql_query" in result:
                    st.write("**Generated SQL Query:**")
                    st.code(result["sql_query"], language="sql")
                if "raw_results" in result:
                    st.write("**Raw Results:**")
                    st.dataframe(result["raw_results"], use_container_width=True)
    else:
        st.error("❌ Query failed!")
        st.write(result["answer"])

def process_query_agent(question: str, show_intermediate: bool = False):
    """Process query using the simple agent approach."""
    if not st.session_state.agent:
        st.error("Agent not loaded!")
        return
    
    start_time = time.time()
    
    with st.spinner("🤖 Processing with SQL Agent..."):
        result = st.session_state.agent.query(question)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    if result["success"]:
        st.success("✅ Query processed successfully!")
        st.metric("⏱️ Execution Time", f"{execution_time:.2f}s")
        
        st.subheader("📝 Answer")
        st.write(result["answer"])
    else:
        st.error("❌ Query failed!")
        st.write(result["answer"])

def render_sidebar():
    """Render the sidebar with model selection and sample queries."""
    st.sidebar.title("🛠️ Configuration")
    
    # Model selection
    st.sidebar.subheader("🤖 Model Selection")
    selected_model = st.sidebar.selectbox(
        "Choose AI Model:",
        options=list(TOGETHER_MODELS.keys()),
        format_func=lambda x: TOGETHER_MODELS[x],
        key="selected_model"
    )
    
    # API key status
    api_key = os.getenv("TOGETHER_API_KEY")
    if api_key:
        st.sidebar.success("✅ API Key Configured")
    else:
        st.sidebar.error("❌ API Key Missing")
        st.sidebar.info("Set TOGETHER_API_KEY environment variable")
    
    # Sample queries
    st.sidebar.subheader("💡 Sample Queries")
    sample_queries = [
        "What are the top 10 selling artists by total sales?",
        "Show me the revenue by country",
        "What is the distribution of track lengths?",
        "How do album sales vary by genre?",
        "Which customers have spent the most money?",
        "Show sales trends over time",
        "What are the most popular music genres?",
        "Compare sales performance by media type"
    ]
    
    for i, query in enumerate(sample_queries):
        if st.sidebar.button(f"📝 {query[:40]}...", key=f"sample_{i}"):
            return query
    
    # Query history
    if st.session_state.query_history:
        st.sidebar.subheader("📚 Query History")
        for i, entry in enumerate(reversed(st.session_state.query_history[-5:])):
            if st.sidebar.button(f"🔄 {entry['question'][:30]}...", key=f"history_{i}"):
                return entry['question']
    
    return None

def main():
    """Main application function."""
    st.markdown('<h1 class="main-header">📊 Enhanced Text-to-SQL Generator</h1>', unsafe_allow_html=True)
    
    # Info about the optimized interface
    st.info("🎯 **Streamlined Interface**: Intermediate results are always shown, and Enhanced Agent includes automatic visualizations!")
    
    # Initialize session state
    initialize_session_state()
    
    # Initialize button state
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'last_query' not in st.session_state:
        st.session_state.last_query = ""
    if 'last_approach' not in st.session_state:
        st.session_state.last_approach = ""
    
    # Sidebar
    sidebar_query = render_sidebar()
    
    # Check if models are loaded
    if not load_models():
        st.stop()
    
    # Display database info
    display_database_info()
    
    # Main interface
    st.subheader("💬 Ask a Question About Your Database")
    
    # Use sidebar query if selected
    default_query = sidebar_query if sidebar_query else ""
    question = st.text_area(
        "Enter your question:",
        value=default_query,
        height=100,
        placeholder="e.g., What are the top 5 selling artists by revenue?"
    )
    
    # Set optimal defaults - no UI clutter needed
    # These were previously user-configurable checkboxes but are now hardcoded for better UX
    show_intermediate = True  # Always show intermediate results (SQL queries, debug info)
    
    # Always show approach selection if there's a question
    if question.strip():
        # Approach selection
        st.subheader("🎯 Choose Processing Approach")
        
        approach_cols = st.columns(3)
        
        with approach_cols[0]:
            st.markdown('<div class="approach-card">', unsafe_allow_html=True)
            st.markdown("### ⚡ SQL Chain")
            st.write("Fast, predictable SQL generation")
            st.caption("✓ Shows SQL query & execution details")
            if st.button("Use Chain", use_container_width=True, key="btn_chain", disabled=st.session_state.processing):
                st.session_state.processing = True
                st.session_state.last_query = question
                st.session_state.last_approach = "chain"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        with approach_cols[1]:
            st.markdown('<div class="approach-card">', unsafe_allow_html=True)
            st.markdown("### 🤖 Simple Agent")
            st.write("Tool-based reasoning with retry")
            st.caption("✓ Shows reasoning steps & SQL query")
            if st.button("Use Agent", use_container_width=True, key="btn_agent", disabled=st.session_state.processing):
                st.session_state.processing = True
                st.session_state.last_query = question
                st.session_state.last_approach = "agent"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        with approach_cols[2]:
            st.markdown('<div class="approach-card">', unsafe_allow_html=True)
            st.markdown("### 🚀 Enhanced Agent")
            st.write("Advanced workflow with visualizations")
            st.caption("✓ Auto charts, insights, dashboard & export")
            if st.button("Use Enhanced Agent", use_container_width=True, key="btn_enhanced", disabled=st.session_state.processing):
                st.session_state.processing = True
                st.session_state.last_query = question
                st.session_state.last_approach = "enhanced"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Process the query if we have a pending request
        if st.session_state.processing and st.session_state.last_query:
            st.markdown("---")  # Add separator
            
            query_to_process = st.session_state.last_query
            approach = st.session_state.last_approach
            
            try:
                if approach == "chain":
                    st.info("🔄 Processing with SQL Chain...")
                    process_query_chain(query_to_process, show_intermediate)
                elif approach == "agent":
                    st.info("🔄 Processing with Simple Agent...")
                    process_query_agent(query_to_process, show_intermediate)
                elif approach == "enhanced":
                    st.info("🔄 Processing with Enhanced Agent...")
                    process_query_enhanced(query_to_process, show_intermediate)
                
                # Reset processing state after completion
                st.session_state.processing = False
                st.session_state.last_query = ""
                st.session_state.last_approach = ""
                
            except Exception as e:
                st.error(f"❌ Processing failed: {str(e)}")
                st.session_state.processing = False
                st.session_state.last_query = ""
                st.session_state.last_approach = ""
    
    else:
        st.info("💡 Enter a question above to get started, or select a sample query from the sidebar.")
    
    # Display persistent visualizations if available
    if st.session_state.visualization_results:
        st.markdown("---")
        st.subheader("📊 Recent Visualizations")
        with st.expander("View Recent Charts", expanded=False):
            display_visualizations(st.session_state.visualization_results, "recent")
    
    # Debug section (can be removed in production)
    with st.expander("🔍 Debug Information", expanded=False):
        st.write("**Session State Status:**")
        st.write(f"- Enhanced Agent: {'✅ Loaded' if st.session_state.enhanced_agent else '❌ Not loaded'}")
        st.write(f"- SQL Chain: {'✅ Loaded' if st.session_state.chain else '❌ Not loaded'}")
        st.write(f"- Simple Agent: {'✅ Loaded' if st.session_state.agent else '❌ Not loaded'}")
        st.write(f"- Database Manager: {'✅ Loaded' if st.session_state.db_manager else '❌ Not loaded'}")
        st.write(f"- Query History: {len(st.session_state.query_history)} entries")
        st.write(f"- Processing: {'✅ Active' if st.session_state.processing else '❌ Idle'}")
        st.write(f"- Last Query: {st.session_state.last_query[:50]}..." if st.session_state.last_query else "- Last Query: None")
        
        api_key = os.getenv("TOGETHER_API_KEY")
        st.write(f"- API Key: {'✅ Present' if api_key else '❌ Missing'}")
        
        if st.button("🔄 Reload All Models", key="debug_reload"):
            # Clear session state and reload
            st.session_state.enhanced_agent = None
            st.session_state.chain = None
            st.session_state.agent = None
            st.session_state.db_manager = None
            st.session_state.processing = False
            st.session_state.last_query = ""
            st.session_state.last_approach = ""
            st.rerun()

if __name__ == "__main__":
    main()