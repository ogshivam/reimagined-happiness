# 🤖 Multi-Agent Conversational Database Assistant

A sophisticated conversational AI system that combines multiple specialized agents to provide intelligent database querying, visualization, and insights using **LangGraph**, **Together AI**, and **Streamlit**.

## 🏗️ Architecture

### Core Components

- **🔍 SQL Agent**: Converts natural language to SQL queries using LangChain
- **🧠 Context Agent**: Manages conversation memory and context
- **📊 Visualization Agent**: Creates automatic charts using Plotly
- **💡 Insight Agent**: Provides business intelligence and pattern detection
- **💾 Memory Agent**: Vector-based conversation storage with ChromaDB
- **📤 Export Agent**: Multi-format data export capabilities

### Technology Stack

- **Frontend**: Streamlit with modern UI components
- **Backend**: FastAPI with async support
- **AI/ML**: Together AI (Llama models), OpenAI embeddings, Sentence Transformers
- **Orchestration**: LangGraph for multi-agent workflow
- **Database**: SQLite (Chinook DB) with multi-database support
- **Visualization**: Plotly with automatic chart generation
- **Memory**: ChromaDB for vector storage, SQLite for conversation history
- **Analytics**: Pandas, NumPy, SciPy for data processing

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to the multi_agent_system directory
cd multi_agent_system

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

Copy the environment example and configure your API keys:

```bash
cp env_example.txt .env
```

Edit `.env` with your API keys:

```env
TOGETHER_API_KEY=your_together_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional
```

### 3. Database Setup

Copy the Chinook database from the parent directory:

```bash
cp ../chinook.db .
```

### 4. Run the System

#### Option A: Full System (Recommended)

Terminal 1 - Start Backend:
```bash
cd backend
python api.py
```

Terminal 2 - Start Frontend:
```bash
cd frontend
streamlit run app.py
```

#### Option B: Direct Agent Testing

```python
from agents.orchestrator import MultiAgentOrchestrator
import asyncio

# Initialize orchestrator
orchestrator = MultiAgentOrchestrator()

# Start session
session_id = orchestrator.start_session("test_user")

# Process question
async def test_question():
    result = await orchestrator.process_question(
        session_id=session_id,
        question="Show me the top 5 selling artists"
    )
    print(result)

asyncio.run(test_question())
```

## 🎯 Features

### 🤖 Multi-Agent Intelligence

- **Conversational Memory**: Context-aware responses using vector embeddings
- **Smart SQL Generation**: Natural language to SQL with context and examples
- **Auto-Visualization**: Intelligent chart type selection based on data characteristics
- **Business Insights**: AI-powered pattern detection and recommendations
- **Error Recovery**: Robust error handling and query validation

### 📊 Advanced Visualizations

- **Smart Chart Detection**: Automatic selection of optimal chart types
- **Interactive Charts**: Plotly-powered visualizations with export options
- **Multiple Chart Types**: Bar, line, pie, scatter, histogram, box plots, heatmaps
- **Data Insights**: Statistical analysis and business intelligence

### 💬 Conversational Interface

- **Session Management**: Persistent conversation history
- **Context Awareness**: References to previous queries and results
- **Multi-turn Conversations**: Follow-up questions and clarifications
- **Export Capabilities**: Data and chart export in multiple formats

### 🔧 Technical Features

- **Async Processing**: Non-blocking multi-agent workflow
- **Vector Memory**: Semantic search through conversation history
- **Multi-Database Support**: SQLite, PostgreSQL, MySQL, SQL Server
- **API Integration**: RESTful API for external integrations
- **Scalable Architecture**: Modular design for easy extension

## 📁 Project Structure

```
multi_agent_system/
├── agents/                    # Core agent implementations
│   ├── sql_agent.py          # Natural language to SQL conversion
│   ├── context_agent.py      # Conversation memory management
│   ├── visualization_agent.py # Chart generation and insights
│   ├── insight_agent.py      # Business intelligence
│   ├── memory_agent.py       # Vector-based storage
│   ├── export_agent.py       # Data export functionality
│   └── orchestrator.py       # LangGraph workflow coordinator
├── backend/                   # FastAPI backend
│   └── api.py                # REST API endpoints
├── frontend/                  # Streamlit frontend
│   └── app.py                # Web interface
├── config/                    # Configuration management
│   └── settings.py           # Environment variables and settings
├── database/                  # Database management
│   └── models.py             # Database connections and models
├── memory/                    # Memory storage
│   └── vector_store.py       # ChromaDB vector storage
├── utils/                     # Utility functions
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## 🔄 Workflow

The multi-agent system follows this workflow:

1. **Context Analysis** → Analyze conversation history and context
2. **SQL Generation** → Convert natural language to SQL query
3. **Data Retrieval** → Execute query and retrieve results
4. **Visualization** → Create appropriate charts and visualizations
5. **Insight Generation** → Generate business insights and patterns
6. **Response Synthesis** → Combine all results into coherent response
7. **Memory Storage** → Store conversation for future context

## 🛠️ Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# AI Models
LLM_MODEL=meta-llama/Llama-3-70b-chat-hf
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
TEMPERATURE=0.1
MAX_TOKENS=4000

# Database
DATABASE_URL=sqlite:///chinook.db
VECTOR_DB_PATH=./memory/vector_store

# API Configuration
API_HOST=localhost
API_PORT=8000
FRONTEND_PORT=8501
```

### Model Options

Supported Together AI models:
- `meta-llama/Llama-3-70b-chat-hf` (Recommended)
- `meta-llama/Llama-3-8b-chat-hf`
- `meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo`
- `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo`

## 📊 Sample Queries

Try these example questions:

- **Basic Queries**: "Show me all customers from the USA"
- **Analytics**: "What are the top 5 selling artists by revenue?"
- **Aggregations**: "How many tracks are there in each genre?"
- **Business Intelligence**: "Show me revenue trends by country"
- **Comparisons**: "Which albums have the most tracks?"

## 🔌 API Endpoints

### Core Endpoints

- `POST /sessions` - Create new conversation session
- `POST /chat` - Process user question
- `GET /sessions/{id}/stats` - Get session statistics
- `DELETE /sessions/{id}` - Clear session data

### Database Endpoints

- `GET /database/schema` - Get database schema
- `GET /database/tables` - List all tables
- `GET /database/tables/{name}/sample` - Get sample data

### Utility Endpoints

- `GET /health` - Health check
- `GET /memory/stats` - Memory storage statistics

## 🧪 Testing

Run the comprehensive test suite:

```python
# Test all components
python test_all_components.py

# Test individual agents
from agents.sql_agent import SQLAgent
sql_agent = SQLAgent()
result = sql_agent.process_question("Show me all genres")
```

## 🚀 Deployment

### Local Development

1. Start backend: `python backend/api.py`
2. Start frontend: `streamlit run frontend/app.py`
3. Access at `http://localhost:8501`

### Production Deployment

- Configure environment variables for production
- Use proper database connections (PostgreSQL/MySQL)
- Set up Redis for session management
- Configure CORS and security settings
- Use reverse proxy (nginx) for load balancing

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-agent`
3. Implement changes with tests
4. Submit pull request

### Adding New Agents

1. Create agent class in `agents/` directory
2. Implement required methods
3. Add to orchestrator workflow
4. Update API endpoints
5. Add frontend integration

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section
2. Review configuration settings
3. Check API key validity
4. Verify database connections

## 🔮 Future Enhancements

- **Multi-user Support**: User authentication and session management
- **Advanced Analytics**: Time series analysis and forecasting
- **Custom Dashboards**: Persistent dashboard creation
- **Plugin System**: Custom agent development framework
- **Real-time Collaboration**: Shared sessions and conversations
- **Advanced Exports**: PDF reports and presentations 