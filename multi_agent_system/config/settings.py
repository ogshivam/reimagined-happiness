"""
Configuration settings for Multi-Agent Conversational Database Assistant
"""
import os
from typing import Dict, List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Keys
    together_api_key: Optional[str] = Field(None, env="TOGETHER_API_KEY")
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    
    # Database Configuration
    database_url: str = Field("sqlite:///chinook.db", env="DATABASE_URL")
    vector_db_path: str = Field("./memory/vector_store", env="VECTOR_DB_PATH")
    
    # AI Model Configuration
    llm_model: str = Field("meta-llama/Llama-3-70b-chat-hf", env="LLM_MODEL")
    embedding_model: str = Field("sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    temperature: float = Field(0.1, env="TEMPERATURE")
    max_tokens: int = Field(4000, env="MAX_TOKENS")
    
    # Agent Configuration
    max_iterations: int = Field(10, env="MAX_ITERATIONS")
    memory_window: int = Field(20, env="MEMORY_WINDOW")
    context_limit: int = Field(8000, env="CONTEXT_LIMIT")
    
    # Visualization Settings
    chart_width: int = Field(800, env="CHART_WIDTH")
    chart_height: int = Field(600, env="CHART_HEIGHT")
    export_formats: List[str] = Field(["png", "svg", "html", "json"], env="EXPORT_FORMATS")
    
    # FastAPI Configuration
    api_host: str = Field("localhost", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    api_debug: bool = Field(True, env="API_DEBUG")
    
    # Streamlit Configuration
    frontend_host: str = Field("localhost", env="FRONTEND_HOST")
    frontend_port: int = Field(8501, env="FRONTEND_PORT")
    
    # Redis Configuration (for conversation memory)
    redis_host: str = Field("localhost", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    redis_db: int = Field(0, env="REDIS_DB")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_format: str = Field("%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Available LLM models
AVAILABLE_MODELS = {
    "llama-3-70b": "meta-llama/Llama-3-70b-chat-hf",
    "llama-3-8b": "meta-llama/Llama-3-8b-chat-hf", 
    "llama-3.1-70b": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    "llama-3.1-8b": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    "llama-3.2-90b": "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo"
}

# Database connection templates
DATABASE_CONFIGS = {
    "sqlite": {
        "driver": "sqlite",
        "example": "sqlite:///database.db"
    },
    "postgresql": {
        "driver": "postgresql+psycopg2",
        "example": "postgresql+psycopg2://user:password@localhost:5432/database"
    },
    "mysql": {
        "driver": "mysql+pymysql", 
        "example": "mysql+pymysql://user:password@localhost:3306/database"
    },
    "mssql": {
        "driver": "mssql+pyodbc",
        "example": "mssql+pyodbc://user:password@server:1433/database?driver=ODBC+Driver+17+for+SQL+Server"
    }
}

# Agent types and their descriptions
AGENT_TYPES = {
    "sql_agent": {
        "name": "SQL Agent",
        "description": "Converts natural language to SQL queries",
        "icon": "🔍"
    },
    "context_agent": {
        "name": "Context Agent", 
        "description": "Manages conversation memory and context",
        "icon": "🧠"
    },
    "visualization_agent": {
        "name": "Visualization Agent",
        "description": "Creates charts and visual representations",
        "icon": "📊"
    },
    "insight_agent": {
        "name": "Insight Agent",
        "description": "Provides business intelligence and patterns",
        "icon": "💡"
    },
    "memory_agent": {
        "name": "Memory Agent",
        "description": "Stores and retrieves conversation history",
        "icon": "💾"
    },
    "export_agent": {
        "name": "Export Agent",
        "description": "Handles data export in various formats",
        "icon": "📤"
    }
}

# Chart type configurations
CHART_CONFIGS = {
    "bar": {"suitable_for": ["categorical", "numerical"], "min_categories": 2, "max_categories": 20},
    "line": {"suitable_for": ["time_series", "numerical"], "min_points": 3, "max_points": 1000},
    "pie": {"suitable_for": ["categorical"], "min_categories": 2, "max_categories": 10},
    "scatter": {"suitable_for": ["numerical"], "min_points": 5, "max_points": 1000},
    "histogram": {"suitable_for": ["numerical"], "min_points": 10, "max_points": 1000},
    "box": {"suitable_for": ["numerical", "categorical"], "min_points": 5, "max_points": 1000},
    "heatmap": {"suitable_for": ["correlation", "matrix"], "min_dimensions": 2, "max_dimensions": 20}
}

# Initialize settings
settings = Settings()

def get_database_path() -> Path:
    """Get the database path, creating directory if needed"""
    if settings.database_url.startswith("sqlite"):
        db_path = Path(settings.database_url.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return db_path
    return None

def get_vector_store_path() -> Path:
    """Get vector store path, creating directory if needed"""
    vector_path = Path(settings.vector_db_path)
    vector_path.mkdir(parents=True, exist_ok=True)
    return vector_path 