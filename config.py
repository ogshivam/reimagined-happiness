"""
Configuration settings for the Text-to-SQL tool.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration  
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "text-to-sql-tool")

# Database Configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", "chinook.db")
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite")

# Model Configuration
DEFAULT_MODEL = os.getenv("TOGETHER_MODEL", "meta-llama/Llama-4-Scout-17B-16E-Instruct")
MODEL_TEMPERATURE = 0

# Application Configuration
MAX_QUERY_RESULTS = 20
DEFAULT_LIMIT = 10
MAX_ERROR_RETRIES = 3

# Sample queries for testing
SAMPLE_QUERIES = [
    "What are the top 5 selling artists?",
    "How many customers are from each country?",
    "What is the most popular genre?",
    "Show me the revenue by year.",
    "Which employee has the highest sales?",
    "What are the 10 longest tracks?",
    "How many albums does each artist have?",
    "What is the average track length by genre?",
    "Which customers have spent the most money?",
    "What are the top selling albums?"
]

# Available Together AI models
TOGETHER_MODELS = {
    # Llama 4 Models (Latest!)
    "meta-llama/Llama-4-Scout-17B-16E-Instruct": "🚀 Llama 4 Scout (17Bx16E) - Latest!",
    "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8": "🚀 Llama 4 Maverick (17Bx128E) - Advanced",
    
    # Llama 3 Models  
    "meta-llama/Llama-3.3-70B-Instruct-Turbo": "🔥 Llama 3.3 70B Turbo (Recommended)",
    "meta-llama/Meta-Llama-3-70B-Instruct-Turbo": "🔥 Llama 3 70B Turbo",
    "meta-llama/Llama-3-8b-chat-hf": "⚡ Llama 3 8B (Fast)",
    "meta-llama/Meta-Llama-3-8B-Instruct-Lite": "⚡ Llama 3 8B Lite",
    "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo": "👁️ Llama 3.2 11B Vision",
    
    # Code & Other Models
    "meta-llama/CodeLlama-34b-Instruct-hf": "💻 Code Llama 34B",
    "mistralai/Mixtral-8x7B-Instruct-v0.1": "🌟 Mixtral 8x7B",
}

# Validation
def validate_config():
    """Validate configuration settings."""
    issues = []
    
    if not TOGETHER_API_KEY:
        issues.append("TOGETHER_API_KEY environment variable is required")
    
    if not os.path.exists(DATABASE_PATH):
        issues.append(f"Database file not found at {DATABASE_PATH}")
    
    return issues

def get_config_summary():
    """Get a summary of current configuration."""
    return {
        "api_key_configured": bool(TOGETHER_API_KEY),
        "database_path": DATABASE_PATH,
        "database_exists": os.path.exists(DATABASE_PATH),
        "langsmith_enabled": LANGCHAIN_TRACING_V2,
        "default_model": DEFAULT_MODEL,
        "available_models": list(TOGETHER_MODELS.keys()),
        "sample_queries_count": len(SAMPLE_QUERIES)
    } 