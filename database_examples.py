"""
Examples of how to connect to different database types with our text-to-SQL tool.
"""

import os
from database_tools import DatabaseManager
from sql_chain import SQLChain  
from sql_agent_simple import SimpleSQLAgent

# Example 1: SQLite (Current Default)
def connect_to_sqlite():
    """Connect to SQLite database (current setup)."""
    
    db_manager = DatabaseManager(
        database_path="chinook.db",
        database_type="sqlite"
    )
    
    # Test connection
    result = db_manager.test_connection()
    print(f"SQLite Connection: {result}")
    
    return db_manager

# Example 2: PostgreSQL
def connect_to_postgresql():
    """Connect to PostgreSQL database."""
    
    db_manager = DatabaseManager(
        database_type="postgresql",
        host="localhost",
        port=5432,
        username="your_username",
        password="your_password", 
        database_name="your_database"
    )
    
    # Test connection
    result = db_manager.test_connection()
    print(f"PostgreSQL Connection: {result}")
    
    return db_manager

# Example 3: MySQL
def connect_to_mysql():
    """Connect to MySQL database."""
    
    db_manager = DatabaseManager(
        database_type="mysql",
        host="localhost",
        port=3306,
        username="your_username",
        password="your_password",
        database_name="your_database"
    )
    
    # Test connection
    result = db_manager.test_connection()
    print(f"MySQL Connection: {result}")
    
    return db_manager

# Example 4: SQL Server
def connect_to_sql_server():
    """Connect to Microsoft SQL Server."""
    
    db_manager = DatabaseManager(
        database_type="mssql",
        host="localhost",
        port=1433,
        username="your_username",
        password="your_password",
        database_name="your_database"
    )
    
    # Test connection
    result = db_manager.test_connection()
    print(f"SQL Server Connection: {result}")
    
    return db_manager

# Example 5: Oracle
def connect_to_oracle():
    """Connect to Oracle database."""
    
    db_manager = DatabaseManager(
        database_type="oracle",
        host="localhost", 
        port=1521,
        username="your_username",
        password="your_password",
        database_name="your_database"
    )
    
    # Test connection
    result = db_manager.test_connection()
    print(f"Oracle Connection: {result}")
    
    return db_manager

# Example 6: Custom Connection String
def connect_with_custom_string():
    """Connect using a custom connection string."""
    
    # Example for cloud databases
    connection_strings = {
        "postgresql_cloud": "postgresql://user:pass@cloud-host:5432/dbname?sslmode=require",
        "mysql_cloud": "mysql+pymysql://user:pass@cloud-host:3306/dbname?charset=utf8mb4",
        "azure_sql": "mssql+pyodbc://user:pass@server.database.windows.net:1433/dbname?driver=ODBC+Driver+17+for+SQL+Server",
        "sqlite_memory": "sqlite:///:memory:",
        "cockroachdb": "cockroachdb://user:pass@host:26257/dbname?sslmode=require"
    }
    
    # Use any connection string
    db_manager = DatabaseManager.from_connection_string(
        connection_string=connection_strings["postgresql_cloud"],
        database_type="postgresql"
    )
    
    return db_manager

# Example 7: Environment-based Configuration
def connect_from_environment():
    """Connect using environment variables."""
    
    db_type = os.getenv("DB_TYPE", "sqlite")
    
    if db_type == "sqlite":
        return DatabaseManager(
            database_path=os.getenv("DB_PATH", "chinook.db"),
            database_type="sqlite"
        )
    elif db_type == "postgresql":
        return DatabaseManager(
            database_type="postgresql",
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            username=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database_name=os.getenv("DB_NAME")
        )
    elif db_type == "mysql":
        return DatabaseManager(
            database_type="mysql",
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            username=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database_name=os.getenv("DB_NAME")
        )
    else:
        # Use connection string from environment
        return DatabaseManager.from_connection_string(
            connection_string=os.getenv("DATABASE_URL"),
            database_type=db_type
        )

# Example 8: Using Different Databases with SQL Chain
def create_sql_chain_for_database(database_type: str = "sqlite"):
    """Create SQL chain for different database types."""
    
    if database_type == "sqlite":
        db_manager = connect_to_sqlite()
    elif database_type == "postgresql":
        db_manager = connect_to_postgresql()
    elif database_type == "mysql":
        db_manager = connect_to_mysql()
    else:
        raise ValueError(f"Unsupported database type: {database_type}")
    
    # Create SQL chain with the database
    chain = SQLChain(
        database_path=db_manager.connection_string,
        model="meta-llama/Llama-4-Scout-17B-16E-Instruct",
        api_key=os.getenv("TOGETHER_API_KEY")
    )
    
    return chain, db_manager

# Example 9: Database-Specific Optimization
def get_database_specific_prompt(database_type: str) -> str:
    """Get database-specific prompts for better SQL generation."""
    
    prompts = {
        "postgresql": """
        You are a PostgreSQL expert. Use PostgreSQL-specific features:
        - Use LIMIT for pagination
        - Use ILIKE for case-insensitive search
        - Use array operators when appropriate
        - Use window functions for analytics
        - Remember PostgreSQL is case-sensitive for identifiers
        """,
        
        "mysql": """
        You are a MySQL expert. Use MySQL-specific features:
        - Use LIMIT for pagination
        - Use backticks for identifiers if needed
        - Use MySQL functions like CONCAT, DATE_FORMAT
        - Remember MySQL has specific date handling
        """,
        
        "mssql": """
        You are a SQL Server expert. Use SQL Server-specific features:
        - Use TOP instead of LIMIT
        - Use square brackets for identifiers
        - Use SQL Server functions like FORMAT, STRING_AGG
        - Use OFFSET/FETCH for pagination in newer versions
        """,
        
        "oracle": """
        You are an Oracle expert. Use Oracle-specific features:
        - Use ROWNUM or ROW_NUMBER() for pagination
        - Use Oracle functions like TO_CHAR, TO_DATE
        - Remember Oracle is case-sensitive for identifiers
        - Use DUAL for single-row selects
        """,
        
        "sqlite": """
        You are a SQLite expert. Use SQLite-specific features:
        - Use LIMIT for pagination
        - Remember SQLite has dynamic typing
        - Use SQLite functions like datetime, strftime
        - Be careful with data types
        """
    }
    
    return prompts.get(database_type, prompts["sqlite"])

# Example 10: Multi-Database Support
class MultiDatabaseManager:
    """Manager for multiple database connections."""
    
    def __init__(self):
        self.connections = {}
    
    def add_database(self, name: str, db_manager: DatabaseManager):
        """Add a database connection."""
        self.connections[name] = db_manager
    
    def query_all_databases(self, question: str):
        """Query all connected databases."""
        results = {}
        
        for name, db_manager in self.connections.items():
            try:
                # Create chain for each database
                chain = SQLChain(
                    database_path=db_manager.connection_string,
                    model="meta-llama/Llama-4-Scout-17B-16E-Instruct",
                    api_key=os.getenv("TOGETHER_API_KEY")
                )
                
                result = chain.query(question)
                results[name] = result
                
            except Exception as e:
                results[name] = {"error": str(e), "success": False}
        
        return results

if __name__ == "__main__":
    # Test SQLite connection (current setup)
    print("Testing SQLite connection...")
    sqlite_db = connect_to_sqlite()
    
    # Show how to connect to other databases
    print("\n🗄️ Database Connection Examples:")
    print("=" * 50)
    
    print("1. SQLite (Current): ✅ Working")
    print("2. PostgreSQL: Configure with your credentials")
    print("3. MySQL: Configure with your credentials") 
    print("4. SQL Server: Configure with your credentials")
    print("5. Oracle: Configure with your credentials")
    print("6. Custom Connection: Use any SQLAlchemy URL")
    
    print("\n📝 To use a different database:")
    print("1. Update the connection parameters in database_tools.py")
    print("2. Install the appropriate database driver (e.g., psycopg2, pymysql)")
    print("3. Set environment variables or update the connection string")
    print("4. Test the connection before running queries") 