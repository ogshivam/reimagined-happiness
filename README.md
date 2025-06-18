# Text-to-SQL Query Generation Tool

A comprehensive text-to-SQL query generation tool built with LangChain and LangGraph, featuring both chain and agent approaches for converting natural language questions into SQL queries. Now powered by advanced Llama 3 and Llama 4 models via Together AI's high-performance API.

## Features

- **Dual Approach**: Supports both predictable chain-based and flexible agent-based SQL generation
- **Interactive Agent**: Uses LangGraph to create a sophisticated SQL agent with error recovery
- **Multiple Tools**: Includes schema inspection, query validation, and execution capabilities
- **Security**: Built-in safety measures and human-in-the-loop capabilities
- **Database Support**: Works with SQLite (Chinook database included)
- **Streamlit UI**: User-friendly web interface for testing queries
- **LangSmith Integration**: Comprehensive tracing and debugging support

## Architecture

### Chain Approach
- Predictable sequence: Question → SQL → Execute → Answer
- Fast and reliable for straightforward queries
- Uses `create_sql_query_chain` for structured generation

### Agent Approach  
- Flexible workflow with iterative querying
- Can handle complex multi-step questions
- Automatic error recovery and query refinement
- Schema exploration capabilities

## Setup

1. Get your Together AI API key:
   - Visit [Together AI](https://api.together.xyz/settings/api-keys)
   - Sign up and get your API key

2. Clone the repository and install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API key:
```bash
export TOGETHER_API_KEY=your_together_ai_api_key_here
# Optional: choose a specific model
export TOGETHER_MODEL=meta-llama/Llama-3-70b-chat-hf
```

4. Download the Chinook database:
```bash
python setup_database.py
```

5. Run the Streamlit app:
```bash
streamlit run app.py
```

## Usage

### Command Line Interface
```python
from sql_agent_simple import SimpleSQLAgent
from sql_chain import SQLChain

# Using the agent approach with Llama 3
agent = SimpleSQLAgent("chinook.db", 
                      model="meta-llama/Llama-3-70b-chat-hf",
                      api_key="your_together_api_key")
result = agent.query("What are the top 5 selling artists?")

# Using the chain approach with Llama 3
chain = SQLChain("chinook.db", 
                model="meta-llama/Llama-3-70b-chat-hf",
                api_key="your_together_api_key")
result = chain.query("How many customers are from each country?")
```

### Web Interface
Access the Streamlit interface at `http://localhost:8501` for an interactive experience.

## Security Considerations

- Always review generated SQL queries before execution
- Use read-only database connections when possible
- Implement proper access controls in production
- Consider human approval workflows for sensitive operations
- **API Security**: Together AI provides enterprise-grade security with API key authentication

## Components

- `sql_agent.py`: LangGraph-based SQL agent implementation
- `sql_chain.py`: Chain-based SQL query generation
- `database_tools.py`: SQL database toolkit and utilities
- `app.py`: Streamlit web interface
- `setup_database.py`: Database setup and sample data loader 