"""
Database models and connection management for Multi-Agent System
"""
import sqlite3
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy import create_engine, text, MetaData, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from pathlib import Path
import logging

from config.settings import settings, DATABASE_CONFIGS

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Enhanced database manager with multi-database support"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or settings.database_url
        self.engine = None
        self.session_maker = None
        self.metadata = None
        self._connection_pool = {}
        
        # Initialize connection synchronously
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize database connection synchronously"""
        try:
            self.engine = create_engine(
                self.database_url,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=settings.log_level == "DEBUG"
            )
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                
            self.session_maker = sessionmaker(bind=self.engine)
            self.metadata = MetaData()
            self.metadata.reflect(bind=self.engine)
            
            logger.info(f"Connected to database: {self.database_url}")
            
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            self.engine = None
        
    async def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.engine = create_engine(
                self.database_url,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=settings.log_level == "DEBUG"
            )
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                
            self.session_maker = sessionmaker(bind=self.engine)
            self.metadata = MetaData()
            self.metadata.reflect(bind=self.engine)
            
            logger.info(f"Connected to database: {self.database_url}")
            return True
            
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            return False
    
    async def disconnect(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")
    
    def get_tables(self) -> List[str]:
        """Get list of all tables in the database"""
        try:
            inspector = inspect(self.engine)
            return inspector.get_table_names()
        except Exception as e:
            logger.error(f"Error getting tables: {str(e)}")
            return []
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get detailed schema information for a table"""
        try:
            inspector = inspect(self.engine)
            columns = inspector.get_columns(table_name)
            primary_keys = inspector.get_pk_constraint(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            indexes = inspector.get_indexes(table_name)
            
            return {
                "table_name": table_name,
                "columns": columns,
                "primary_keys": primary_keys,
                "foreign_keys": foreign_keys,
                "indexes": indexes
            }
        except Exception as e:
            logger.error(f"Error getting schema for {table_name}: {str(e)}")
            return {}
    
    def get_sample_data(self, table_name: str, limit: int = 5) -> pd.DataFrame:
        """Get sample data from a table"""
        try:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            return pd.read_sql(query, self.engine)
        except Exception as e:
            logger.error(f"Error getting sample data from {table_name}: {str(e)}")
            return pd.DataFrame()
    
    def execute_query(self, query: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Execute SQL query and return results with metadata"""
        try:
            # Execute query and get results
            df = pd.read_sql(query, self.engine)
            
            # Generate metadata
            metadata = {
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": list(df.columns),
                "data_types": df.dtypes.to_dict(),
                "memory_usage": df.memory_usage(deep=True).sum(),
                "query": query
            }
            
            logger.info(f"Query executed successfully: {metadata['row_count']} rows returned")
            return df, metadata
            
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise SQLAlchemyError(f"Query execution failed: {str(e)}")
    
    def get_database_summary(self) -> Dict[str, Any]:
        """Get comprehensive database summary"""
        try:
            tables = self.get_tables()
            summary = {
                "database_url": self.database_url,
                "total_tables": len(tables),
                "tables": {}
            }
            
            for table in tables:
                try:
                    sample_df = self.get_sample_data(table, 3)
                    schema = self.get_table_schema(table)
                    
                    summary["tables"][table] = {
                        "column_count": len(sample_df.columns) if not sample_df.empty else 0,
                        "sample_rows": len(sample_df),
                        "columns": list(sample_df.columns) if not sample_df.empty else [],
                        "schema": schema
                    }
                except Exception as e:
                    logger.warning(f"Could not get summary for table {table}: {str(e)}")
                    summary["tables"][table] = {"error": str(e)}
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting database summary: {str(e)}")
            return {"error": str(e)}

class ConversationMemory:
    """Manages conversation history and context storage"""
    
    def __init__(self, db_path: str = "memory/conversations.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()
    
    def _init_tables(self):
        """Initialize conversation storage tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_message TEXT,
                    agent_response TEXT,
                    agent_type TEXT,
                    metadata TEXT,
                    sql_query TEXT,
                    results_summary TEXT
                );
                
                CREATE TABLE IF NOT EXISTS conversation_context (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    context_key TEXT NOT NULL,
                    context_value TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_session_id ON conversations(session_id);
                CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations(timestamp);
                CREATE INDEX IF NOT EXISTS idx_context_session ON conversation_context(session_id);
            """)
    
    def save_conversation(self, session_id: str, user_message: str, 
                         agent_response: str, agent_type: str,
                         metadata: Dict[str, Any] = None,
                         sql_query: str = None,
                         results_summary: str = None):
        """Save conversation turn to memory"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO conversations 
                    (session_id, user_message, agent_response, agent_type, metadata, sql_query, results_summary)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (session_id, user_message, agent_response, agent_type, 
                     str(metadata) if metadata else None, sql_query, results_summary))
                
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")
    
    def get_conversation_history(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve conversation history for a session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM conversations 
                    WHERE session_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (session_id, limit))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}")
            return []
    
    def save_context(self, session_id: str, context_key: str, context_value: str):
        """Save context information for a session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO conversation_context 
                    (session_id, context_key, context_value)
                    VALUES (?, ?, ?)
                """, (session_id, context_key, context_value))
                
        except Exception as e:
            logger.error(f"Error saving context: {str(e)}")
    
    def get_context(self, session_id: str, context_key: str = None) -> Dict[str, Any]:
        """Retrieve context for a session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if context_key:
                    cursor = conn.execute("""
                        SELECT context_value FROM conversation_context 
                        WHERE session_id = ? AND context_key = ?
                        ORDER BY timestamp DESC LIMIT 1
                    """, (session_id, context_key))
                    result = cursor.fetchone()
                    return {"value": result["context_value"] if result else None}
                else:
                    cursor = conn.execute("""
                        SELECT context_key, context_value FROM conversation_context 
                        WHERE session_id = ?
                        ORDER BY timestamp DESC
                    """, (session_id,))
                    return {row["context_key"]: row["context_value"] for row in cursor.fetchall()}
                    
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return {}

# Global database manager instance
db_manager = DatabaseManager()
conversation_memory = ConversationMemory() 