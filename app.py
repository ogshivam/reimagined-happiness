"""
Streamlit web interface for the Text-to-SQL tool.
Provides an interactive UI for testing both chain and agent approaches.
"""

import streamlit as st
import os
import pandas as pd
from typing import Dict, Any
import time
import json

# Import our modules
try:
    from sql_chain import SQLChain
    from sql_agent_simple import SimpleSQLAgent
    from database_tools import DatabaseManager, get_chinook_schema_description
    from setup_databases import DatabaseSetup
    from db_connection_helper import render_custom_connection_form, DatabaseConnectionHelper
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Text-to-SQL Generator",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #1f77b4;
    }
    .approach-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ddd;
        margin: 1rem 0;
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
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'chain' not in st.session_state:
        st.session_state.chain = None
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = None
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    if 'selected_database' not in st.session_state:
        st.session_state.selected_database = None
    if 'database_configs' not in st.session_state:
        st.session_state.database_configs = {}
    if 'current_db_connection' not in st.session_state:
        st.session_state.current_db_connection = None

def load_database_configs():
    """Load database configurations from file."""
    if os.path.exists("database_configs.json"):
        try:
            with open("database_configs.json", "r") as f:
                all_configs = json.load(f)
                # Filter out sample databases, keep only Chinook and custom ones
                st.session_state.database_configs = {}
                for key, config in all_configs.items():
                    if (key == "chinook_sqlite" or 
                        config.get("is_custom", False) or 
                        "custom_" in key):
                        st.session_state.database_configs[key] = config
        except Exception as e:
            st.warning(f"Error loading database configs: {e}")
            st.session_state.database_configs = {}
    else:
        # Create default config for Chinook only
        st.session_state.database_configs = {
            "chinook_sqlite": {
                "type": "sqlite",
                "name": "Chinook (Music Store)",
                "description": "Digital music store with artists, albums, tracks, customers, and sales",
                "file_path": "chinook.db",
                "status": "ready" if os.path.exists("chinook.db") else "not_downloaded"
            }
        }

def get_database_connection(db_config: Dict[str, Any]) -> DatabaseManager:
    """Create a database connection based on configuration."""
    db_type = db_config["type"]
    
    if db_type == "sqlite":
        file_path = db_config["file_path"]
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"SQLite database file not found: {file_path}")
        return DatabaseManager(database_path=file_path, database_type="sqlite")
    
    elif db_type in ["postgresql", "mysql", "mssql", "oracle"]:
        connection_info = db_config.get("connection", {})
        return DatabaseManager(
            database_type=db_type,
            host=connection_info.get("host", "localhost"),
            port=connection_info.get("port"),
            username=connection_info.get("username"),
            password=connection_info.get("password"),
            database_name=connection_info.get("database")
        )
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

def test_database_connection(db_config: Dict[str, Any]) -> Dict[str, Any]:
    """Test database connection and return status."""
    try:
        db_manager = get_database_connection(db_config)
        result = db_manager.test_connection()
        if result["success"]:
            # Also check if we can list tables
            tables = db_manager.list_tables()
            result["table_count"] = len(tables)
            result["tables"] = tables[:5]  # Show first 5 tables
        return result
    except Exception as e:
        return {
            "success": False,
            "message": f"Connection failed: {str(e)}",
            "error": str(e)
        }

def load_models():
    """Load the SQL chain and database manager for selected database."""
    try:
        # Get selected database config
        if not st.session_state.selected_database:
            st.error("No database selected! Please select a database from the sidebar.")
            return False
        
        db_config = st.session_state.database_configs.get(st.session_state.selected_database)
        if not db_config:
            st.error("Selected database configuration not found!")
            return False
        
        # Test database connection
        connection_test = test_database_connection(db_config)
        if not connection_test["success"]:
            st.error(f"Database connection failed: {connection_test['message']}")
            return False
        
        # Create database manager
        db_manager = get_database_connection(db_config)
        
        # Get connection string for chains/agents
        if db_config["type"] == "sqlite":
            connection_string = db_config["file_path"]
        else:
            connection_string = db_manager.connection_string
        
        # Load models if not loaded or database changed
        if (st.session_state.chain is None or 
            st.session_state.current_db_connection != st.session_state.selected_database):
            
            with st.spinner("Loading SQL Chain..."):
                model = st.session_state.get('selected_model', "meta-llama/Llama-4-Scout-17B-16E-Instruct")
                api_key = os.getenv("TOGETHER_API_KEY")
                st.session_state.chain = SQLChain(connection_string, model=model, api_key=api_key)
        
        if (st.session_state.agent is None or 
            st.session_state.current_db_connection != st.session_state.selected_database):
            
            with st.spinner("Loading SQL Agent..."):
                model = st.session_state.get('selected_model', "meta-llama/Llama-4-Scout-17B-16E-Instruct")
                api_key = os.getenv("TOGETHER_API_KEY")
                st.session_state.agent = SimpleSQLAgent(connection_string, model=model, api_key=api_key)
        
        # Update session state
        st.session_state.db_manager = db_manager
        st.session_state.current_db_connection = st.session_state.selected_database
        
        return True
        
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return False

def display_database_info():
    """Display information about the database."""
    if st.session_state.db_manager:
        with st.expander("📊 Database Information", expanded=False):
            db_manager = st.session_state.db_manager
            
            # Show database details
            db_config = st.session_state.database_configs.get(st.session_state.selected_database, {})
            st.write(f"**Database:** {db_config.get('name', 'Unknown')}")
            st.write(f"**Type:** {db_config.get('type', 'Unknown').upper()}")
            st.write(f"**Description:** {db_config.get('description', 'No description available')}")
            
            # Show tables
            tables = db_manager.list_tables()
            st.write(f"**Available Tables ({len(tables)}):**")
            cols = st.columns(3)
            for i, table in enumerate(tables):
                with cols[i % 3]:
                    if st.button(f"📋 {table}", key=f"table_{table}"):
                        show_table_info(table)
            
            # Show schema information
            st.write("**Schema Information:**")
            if "chinook" in st.session_state.selected_database.lower():
                # Show Chinook-specific schema description
                st.info(get_chinook_schema_description())
            else:
                # For other databases, show general schema info
                try:
                    schema_info = db_manager.get_schema()
                    if schema_info:
                        # Format schema info nicely
                        st.text_area(
                            "Database Schema:",
                            value=schema_info[:1000] + "..." if len(schema_info) > 1000 else schema_info,
                            height=200,
                            disabled=True
                        )
                    else:
                        st.info("Schema information not available. Click on individual tables above to explore the structure.")
                except Exception as e:
                    st.warning(f"Could not retrieve schema: {e}")
                    st.info("Try clicking on individual tables above to explore the database structure.")

def show_table_info(table_name: str):
    """Show detailed information about a specific table."""
    db_manager = st.session_state.db_manager
    
    with st.expander(f"Table: {table_name}", expanded=True):
        try:
            # Get table statistics
            stats = db_manager.get_table_statistics(table_name)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Rows", stats.get("row_count", "N/A"))
            with col2:
                st.metric("Total Columns", stats.get("column_count", "N/A"))
            
            # Show sample data
            st.write("**Sample Data:**")
            sample_data = db_manager.get_sample_data(table_name)
            st.dataframe(sample_data)
            
        except Exception as e:
            st.error(f"Error loading table info: {e}")

def process_query_chain(question: str, show_intermediate: bool = False):
    """Process a query using the chain approach."""
    chain = st.session_state.chain
    
    with st.spinner("Processing with SQL Chain..."):
        start_time = time.time()
        result = chain.query(question, return_intermediate=True)
        processing_time = time.time() - start_time
    
    # Display results
    if result["success"]:
        st.markdown('<div class="success-box">✅ Query processed successfully!</div>', unsafe_allow_html=True)
        
        # Show answer
        st.write("**Answer:**")
        st.write(result["answer"])
        
        if show_intermediate:
            # Show SQL query
            st.write("**Generated SQL Query:**")
            st.code(result["sql_query"], language="sql")
            
            # Show raw results
            if "raw_results" in result and not result["raw_results"].empty:
                st.write("**Raw Results:**")
                st.dataframe(result["raw_results"])
                st.caption(f"Showing {len(result['raw_results'])} rows")
        
        st.caption(f"Processing time: {processing_time:.2f} seconds")
        
    else:
        st.markdown('<div class="error-box">❌ Query failed</div>', unsafe_allow_html=True)
        st.error(result.get("error", "Unknown error"))
    
    return result

def process_query_agent(question: str, show_intermediate: bool = False):
    """Process a query using the agent approach."""
    agent = st.session_state.agent
    
    with st.spinner("Processing with SQL Agent..."):
        start_time = time.time()
        result = agent.query(question)
        processing_time = time.time() - start_time
    
    # Display results
    if result["success"]:
        st.markdown('<div class="success-box">✅ Query processed successfully!</div>', unsafe_allow_html=True)
        
        # Show answer
        st.write("**Answer:**")
        st.write(result["answer"])
        
        st.caption(f"Processing time: {processing_time:.2f} seconds")
        st.caption(f"Approach: {result.get('approach', 'Agent')}")
        
    else:
        st.markdown('<div class="error-box">❌ Query failed</div>', unsafe_allow_html=True)
        st.error(result.get("error", "Unknown error"))
    
    return result

def render_database_sidebar():
    """Render database selection and management in sidebar."""
    st.header("🗄️ Database Selection")
    
    # Load database configurations
    load_database_configs()
    
    if not st.session_state.database_configs:
        st.warning("No databases configured!")
        if st.button("🚀 Setup Sample Databases"):
            with st.spinner("Setting up databases..."):
                setup = DatabaseSetup()
                configs = setup.setup_all_sample_databases()
                st.session_state.database_configs = configs
                st.success("Databases setup complete!")
                st.rerun()
        return False
    
    # Database selection dropdown
    db_names = list(st.session_state.database_configs.keys())
    db_labels = [st.session_state.database_configs[name]["name"] for name in db_names]
    
    # Find current selection index
    current_index = 0
    if st.session_state.selected_database in db_names:
        current_index = db_names.index(st.session_state.selected_database)
    
    selected_db_index = st.selectbox(
        "Choose database:",
        range(len(db_names)),
        format_func=lambda x: db_labels[x],
        index=current_index,
        key="db_selector"
    )
    
    selected_db_name = db_names[selected_db_index]
    
    # Update selection if changed
    if st.session_state.selected_database != selected_db_name:
        st.session_state.selected_database = selected_db_name
        # Clear cached models when database changes
        st.session_state.chain = None
        st.session_state.agent = None
        st.session_state.db_manager = None
        st.session_state.current_db_connection = None
    
    # Show selected database info
    db_config = st.session_state.database_configs[selected_db_name]
    
    st.write("**Selected Database:**")
    st.info(f"**{db_config['name']}** ({db_config['type'].upper()})")
    st.caption(db_config['description'])
    
    # Database status and actions
    if db_config["type"] == "sqlite":
        file_path = db_config["file_path"]
        if os.path.exists(file_path):
            st.success("✅ Database ready")
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            st.caption(f"File size: {file_size:.1f} MB")
        else:
            st.error("❌ Database file not found")
            if db_config.get("download_available"):
                if st.button(f"📥 Download {db_config['name']}", key=f"download_{selected_db_name}"):
                    with st.spinner(f"Downloading {db_config['name']}..."):
                        setup = DatabaseSetup()
                        if "chinook" in selected_db_name:
                            result = setup.download_sqlite_database("chinook", "chinook.db")
                        elif "northwind" in selected_db_name:
                            result = setup.download_sqlite_database("northwind", "northwind.db")
                        
                        if result:
                            st.success("Download complete!")
                            st.rerun()
                        else:
                            st.error("Download failed!")
            return False
    else:
        # For non-SQLite databases, test connection
        with st.spinner("Testing connection..."):
            connection_test = test_database_connection(db_config)
        
        if connection_test["success"]:
            st.success("✅ Connection successful")
            if "table_count" in connection_test:
                st.caption(f"Found {connection_test['table_count']} tables")
        else:
            st.error("❌ Connection failed")
            st.error(connection_test["message"])
            
            # Show connection setup instructions
            if "setup_instructions" in db_config:
                with st.expander("Setup Instructions"):
                    for instruction in db_config["setup_instructions"]:
                        st.write(f"• {instruction}")
            return False
    
    # Custom connection section
    st.divider()
    
    # Add custom connection toggle
    if st.button("➕ Add Custom Database", key="add_custom_db"):
        st.session_state.show_custom_form = True
    
    # Show custom connection form if toggled
    if st.session_state.get('show_custom_form', False):
        with st.container():
            custom_config = render_custom_connection_form()
            
            if custom_config:
                # Add the custom connection to session state
                custom_key = f"custom_{custom_config['type']}_{int(time.time())}"
                st.session_state.database_configs[custom_key] = custom_config
                st.session_state.selected_database = custom_key
                st.session_state.show_custom_form = False
                
                # Clear cached models to force reload with new database
                st.session_state.chain = None
                st.session_state.agent = None
                st.session_state.db_manager = None
                st.session_state.current_db_connection = None
                
                st.rerun()
            
            # Close form button
            if st.button("❌ Cancel", key="cancel_custom_form"):
                st.session_state.show_custom_form = False
                st.rerun()
    
    return True

def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">🗄️ Text-to-SQL Generator</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Database selection (must be first)
        database_ready = render_database_sidebar()
        
        if not database_ready:
            st.stop()
        
        st.divider()
        
        # Together AI API key check
        api_key = os.getenv("TOGETHER_API_KEY")
        if api_key:
            st.success("✅ Together AI API Key found")
        else:
            st.error("❌ Together AI API Key not found")
            st.info("Set TOGETHER_API_KEY environment variable")
            st.info("Get your API key from: https://api.together.xyz/settings/api-keys")
            st.stop()
        
        # Model selection
        st.header("🤖 Model Selection")
        from config import TOGETHER_MODELS
        
        model_options = list(TOGETHER_MODELS.keys())
        model_labels = [f"{TOGETHER_MODELS[model]} ({model.split('/')[-1]})" for model in model_options]
        
        selected_model_index = st.selectbox(
            "Choose Llama model:",
            range(len(model_options)),
            format_func=lambda x: model_labels[x],
            index=0,
            help="Different models offer trade-offs between speed and accuracy"
        )
        
        selected_model = model_options[selected_model_index]
        
        # Store selected model in session state
        if 'selected_model' not in st.session_state or st.session_state.selected_model != selected_model:
            st.session_state.selected_model = selected_model
            # Clear cached models when selection changes
            st.session_state.chain = None
            st.session_state.agent = None
        
        # Approach selection
        st.header("📊 Approach")
        approach = st.radio(
            "Select approach:",
            ["Chain (Fast & Predictable)", "Agent (Advanced & Iterative)"],
            help="Chain: Direct question→SQL→answer. Agent: Multi-step reasoning with error recovery."
        )
        
        # Display options
        st.header("🎛️ Display Options")
        show_sql = st.checkbox("Show generated SQL", value=True)
        show_raw_results = st.checkbox("Show raw results", value=False)
        show_intermediate = show_sql or show_raw_results
        
        # Sample queries
        st.header("💡 Sample Queries")
        # Dynamic sample queries based on selected database
        db_config = st.session_state.database_configs.get(st.session_state.selected_database, {})
        db_name = db_config.get("name", "").lower()
        
        if "chinook" in db_name or "music" in db_name:
            sample_queries = [
                "What are the top 5 selling artists?",
                "How many customers are from each country?",
                "What is the most popular genre?",
                "Show me the revenue by year",
                "Which employee has the highest sales?"
            ]
        elif "northwind" in db_name or "business" in db_name:
            sample_queries = [
                "What are the top 5 selling products?",
                "How many orders per customer?",
                "What is the total revenue by category?",
                "Show me orders by month",
                "Which employee processed the most orders?"
            ]
        else:
            sample_queries = [
                "Show me the first 10 rows from any table",
                "How many rows are in each table?",
                "What are the column names in the largest table?",
                "Show me some sample data",
                "What is the structure of this database?"
            ]
        
        selected_sample = st.selectbox("Choose a sample query:", [""] + sample_queries)
    
    # Load models after database is selected
    if not load_models():
        st.stop()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Query input
        st.header("💬 Ask a Question")
        
        # Use selected sample query or let user type
        if selected_sample:
            question = st.text_area(
                "Enter your question about the music store database:",
                value=selected_sample,
                height=100,
                help="Ask questions about artists, albums, tracks, customers, sales, etc."
            )
        else:
            question = st.text_area(
                "Enter your question about the music store database:",
                height=100,
                help="Ask questions about artists, albums, tracks, customers, sales, etc."
            )
        
        # Process button
        if st.button("🚀 Generate SQL & Answer", type="primary", use_container_width=True):
            if not question.strip():
                st.warning("Please enter a question!")
            elif not api_key:
                st.error("Please set your Together AI API key!")
            else:
                # Add to history
                st.session_state.query_history.append({
                    "question": question,
                    "timestamp": time.time(),
                    "approach": approach
                })
                
                # Process based on selected approach
                if approach.startswith("Chain"):
                    result = process_query_chain(question, show_intermediate)
                else:
                    result = process_query_agent(question, show_intermediate)
    
    with col2:
        # Database info
        display_database_info()
        
        # Query history
        if st.session_state.query_history:
            st.header("📝 Query History")
            
            for i, entry in enumerate(reversed(st.session_state.query_history[-5:])):
                with st.expander(f"Query {len(st.session_state.query_history) - i}", expanded=False):
                    st.write(f"**Question:** {entry['question']}")
                    st.write(f"**Approach:** {entry['approach']}")
                    st.write(f"**Time:** {time.ctime(entry['timestamp'])}")
            
            if st.button("🗑️ Clear History"):
                st.session_state.query_history = []
                st.experimental_rerun()

if __name__ == "__main__":
    main() 