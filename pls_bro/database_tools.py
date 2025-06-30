"""
Database tools and utilities for the text-to-SQL tool.
Includes SQLDatabaseToolkit setup and custom database utilities.
"""

import os
from typing import List, Dict, Any, Optional
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_together import ChatTogether
from sqlalchemy import create_engine, text
import pandas as pd
from urllib.parse import quote_plus

class DatabaseManager:
    """Manager class for database operations and tool setup."""
    
    def __init__(self, database_path: str = "chinook.db", database_type: str = "sqlite", 
                 host: Optional[str] = None, port: Optional[int] = None, 
                 username: Optional[str] = None, password: Optional[str] = None, 
                 database_name: Optional[str] = None):
        """Initialize the database manager with flexible connection options.
        
        Args:
            database_path: Path to the database file (for SQLite) or connection string
            database_type: Type of database ('sqlite', 'postgresql', 'mysql', 'mssql', 'oracle')
            host: Database host (for non-SQLite databases)
            port: Database port (for non-SQLite databases)
            username: Database username (for non-SQLite databases)
            password: Database password (for non-SQLite databases) 
            database_name: Database name (for non-SQLite databases)
        """
        self.database_type = database_type.lower()
        
        # Create connection string based on database type
        if self.database_type == "sqlite":
            self.database_path = database_path
            connection_string = f"sqlite:///{database_path}"
        elif self.database_type == "postgresql":
            connection_string = self._build_postgresql_connection(host, port, username, password, database_name)
        elif self.database_type == "mysql":
            connection_string = self._build_mysql_connection(host, port, username, password, database_name)
        elif self.database_type == "mssql":
            connection_string = self._build_mssql_connection(host, port, username, password, database_name)
        elif self.database_type == "oracle":
            connection_string = self._build_oracle_connection(host, port, username, password, database_name)
        else:
            # Allow custom connection string
            connection_string = database_path
            
        self.connection_string = connection_string
        self.engine = create_engine(connection_string)
        self.db = SQLDatabase(engine=self.engine)
    
    def _build_postgresql_connection(self, host: str, port: int, username: str, password: str, database_name: str) -> str:
        """Build PostgreSQL connection string."""
        port = port or 5432
        password_encoded = quote_plus(password) if password else ""
        return f"postgresql://{username}:{password_encoded}@{host}:{port}/{database_name}"
    
    def _build_mysql_connection(self, host: str, port: int, username: str, password: str, database_name: str) -> str:
        """Build MySQL connection string."""
        port = port or 3306
        password_encoded = quote_plus(password) if password else ""
        return f"mysql+pymysql://{username}:{password_encoded}@{host}:{port}/{database_name}"
    
    def _build_mssql_connection(self, host: str, port: int, username: str, password: str, database_name: str) -> str:
        """Build SQL Server connection string."""
        port = port or 1433
        password_encoded = quote_plus(password) if password else ""
        return f"mssql+pyodbc://{username}:{password_encoded}@{host}:{port}/{database_name}?driver=ODBC+Driver+17+for+SQL+Server"
    
    def _build_oracle_connection(self, host: str, port: int, username: str, password: str, database_name: str) -> str:
        """Build Oracle connection string."""
        port = port or 1521
        password_encoded = quote_plus(password) if password else ""
        return f"oracle+cx_oracle://{username}:{password_encoded}@{host}:{port}/{database_name}"
    
    @classmethod
    def from_connection_string(cls, connection_string: str, database_type: str = "custom"):
        """Create DatabaseManager from a custom connection string.
        
        Args:
            connection_string: Full SQLAlchemy connection string
            database_type: Type identifier for the database
            
        Returns:
            DatabaseManager instance
        """
        instance = cls.__new__(cls)
        instance.database_type = database_type
        instance.connection_string = connection_string
        instance.engine = create_engine(connection_string)
        instance.db = SQLDatabase(engine=instance.engine)
        return instance
    
    def get_toolkit(self, llm: ChatTogether) -> SQLDatabaseToolkit:
        """Get the SQL database toolkit with all necessary tools.
        
        Args:
            llm: The language model to use for the toolkit
            
        Returns:
            SQLDatabaseToolkit configured with the database
        """
        return SQLDatabaseToolkit(db=self.db, llm=llm)
    
    def get_table_info(self, table_names: List[str] = None) -> str:
        """Get detailed information about database tables.
        
        Args:
            table_names: Optional list of specific tables to get info for
            
        Returns:
            String containing table schema information
        """
        if table_names:
            return self.db.get_table_info_no_throw(table_names)
        return self.db.get_table_info()
    
    def list_tables(self) -> List[str]:
        """Get list of all tables in the database.
        
        Returns:
            List of table names
        """
        return self.db.get_usable_table_names()
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a SQL query and return results as DataFrame.
        
        Args:
            query: SQL query to execute
            
        Returns:
            pandas DataFrame with query results
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))
                columns = result.keys()
                data = result.fetchall()
                return pd.DataFrame(data, columns=columns)
        except Exception as e:
            raise Exception(f"Error executing query: {str(e)}")
    
    def validate_query(self, query: str) -> Dict[str, Any]:
        """Validate a SQL query without executing it.
        
        Args:
            query: SQL query to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            # Different validation approaches for different databases
            if self.database_type == "sqlite":
                explain_query = f"EXPLAIN QUERY PLAN {query}"
            elif self.database_type in ["postgresql", "mysql"]:
                explain_query = f"EXPLAIN {query}"
            elif self.database_type == "mssql":
                explain_query = f"SET SHOWPLAN_ALL ON; {query}"
            else:
                # Generic approach - try to prepare the statement
                explain_query = query
                
            with self.engine.connect() as connection:
                result = connection.execute(text(explain_query))
                plan = result.fetchall()
                return {
                    "valid": True,
                    "message": "Query is valid",
                    "execution_plan": plan
                }
        except Exception as e:
            return {
                "valid": False,
                "message": f"Query validation failed: {str(e)}",
                "execution_plan": None
            }
    
    def get_sample_data(self, table_name: str, limit: int = 5) -> pd.DataFrame:
        """Get sample data from a specific table.
        
        Args:
            table_name: Name of the table
            limit: Number of rows to return
            
        Returns:
            pandas DataFrame with sample data
        """
        # Handle different LIMIT syntax for different databases
        if self.database_type == "mssql":
            query = f"SELECT TOP {limit} * FROM {table_name}"
        elif self.database_type == "oracle":
            query = f"SELECT * FROM {table_name} WHERE ROWNUM <= {limit}"
        else:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            
        return self.execute_query(query)
    
    def get_table_statistics(self, table_name: str) -> Dict[str, Any]:
        """Get basic statistics about a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with table statistics
        """
        try:
            # Get row count
            count_query = f"SELECT COUNT(*) as row_count FROM {table_name}"
            row_count = self.execute_query(count_query)['row_count'].iloc[0]
            
            # Get column info - different for each database type
            if self.database_type == "sqlite":
                info_query = f"PRAGMA table_info({table_name})"
            elif self.database_type == "postgresql":
                info_query = f"""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                """
            elif self.database_type == "mysql":
                info_query = f"DESCRIBE {table_name}"
            elif self.database_type == "mssql":
                info_query = f"""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '{table_name}'
                """
            else:
                # Generic approach
                info_query = f"SELECT * FROM {table_name} LIMIT 0"
            
            columns_info = self.execute_query(info_query)
            
            return {
                "table_name": table_name,
                "row_count": row_count,
                "column_count": len(columns_info),
                "columns": columns_info.to_dict('records'),
                "database_type": self.database_type
            }
        except Exception as e:
            return {
                "table_name": table_name,
                "error": f"Failed to get statistics: {str(e)}",
                "database_type": self.database_type
            }
    
    def get_schema(self) -> str:
        """Get the database schema information.
        
        Returns:
            String containing the complete database schema
        """
        return self.db.get_table_info()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the database connection.
        
        Returns:
            Dictionary with connection test results
        """
        try:
            with self.engine.connect() as connection:
                # Simple test query for different databases
                if self.database_type == "sqlite":
                    test_query = "SELECT 1"
                elif self.database_type in ["postgresql", "mysql"]:
                    test_query = "SELECT 1"
                elif self.database_type == "mssql":
                    test_query = "SELECT 1"
                elif self.database_type == "oracle":
                    test_query = "SELECT 1 FROM DUAL"
                else:
                    test_query = "SELECT 1"
                
                result = connection.execute(text(test_query))
                result.fetchone()
                
                return {
                    "success": True,
                    "message": "Database connection successful",
                    "database_type": self.database_type,
                    "connection_string": self.connection_string
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Database connection failed: {str(e)}",
                "database_type": self.database_type,
                "error": str(e)
            }

def create_database_tools(database_path: str = "chinook.db", model: str = "meta-llama/Llama-3-70b-chat-hf", api_key: str = None) -> tuple:
    """Create database manager and toolkit for use in agents/chains.
    
    Args:
        database_path: Path to the SQLite database
        model: Together AI model name
        api_key: Together AI API key
        
    Returns:
        Tuple of (DatabaseManager, SQLDatabaseToolkit)
    """
    # Initialize the language model
    llm = ChatTogether(
        model=model,
        together_api_key=api_key,
        temperature=0
    )
    
    # Create database manager
    db_manager = DatabaseManager(database_path)
    
    # Get the toolkit
    toolkit = db_manager.get_toolkit(llm)
    
    return db_manager, toolkit

def get_chinook_schema_description() -> str:
    """Get a human-readable description of the Chinook database schema.
    
    Returns:
        String description of the database schema
    """
    return """
    The Chinook database is a sample database that represents a digital media store.
    
    Key Tables:
    - Artist: Information about music artists
    - Album: Music albums with artist references
    - Track: Individual songs/tracks with album, media type, and genre references
    - Customer: Customer information including contact details
    - Employee: Employee information and hierarchy
    - Invoice: Sales invoices with customer references
    - InvoiceLine: Individual items within invoices
    - Genre: Music genres
    - MediaType: Types of media (MP3, AAC, etc.)
    - Playlist: User-created playlists
    - PlaylistTrack: Many-to-many relationship between playlists and tracks
    
    Common Relationships:
    - Artists have many Albums
    - Albums have many Tracks
    - Customers have many Invoices
    - Invoices have many Invoice Items
    - Tracks belong to Genres and Media Types
    - Tracks can be in multiple Playlists
    """ 