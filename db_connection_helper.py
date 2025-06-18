"""
Database connection helper for dynamic credential management and connection string parsing.
"""

import re
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional
import streamlit as st

class DatabaseConnectionHelper:
    """Helper class for managing database connections with dynamic credentials."""
    
    @staticmethod
    def parse_connection_string(connection_string: str) -> Dict[str, Any]:
        """Parse a database connection string into components.
        
        Args:
            connection_string: Database connection string
            
        Returns:
            Dictionary with connection parameters
            
        Examples:
            postgresql://user:pass@host:port/db
            mysql://user:pass@host:port/db
            mssql://user:pass@host:port/db
        """
        try:
            parsed = urlparse(connection_string)
            
            # Extract database type from scheme
            db_type = parsed.scheme.lower()
            if db_type == 'postgres':
                db_type = 'postgresql'
            
            # Parse connection components
            config = {
                "type": db_type,
                "host": parsed.hostname,
                "port": parsed.port,
                "username": parsed.username,
                "password": parsed.password,
                "database": parsed.path.lstrip('/') if parsed.path else None
            }
            
            # Handle query parameters (SSL, etc.)
            if parsed.query:
                query_params = parse_qs(parsed.query)
                config["query_params"] = query_params
            
            return config
            
        except Exception as e:
            raise ValueError(f"Invalid connection string format: {e}")
    
    @staticmethod
    def validate_connection_config(config: Dict[str, Any]) -> Dict[str, str]:
        """Validate connection configuration and return validation errors.
        
        Args:
            config: Connection configuration dictionary
            
        Returns:
            Dictionary of validation errors (empty if valid)
        """
        errors = {}
        
        required_fields = ["type", "host", "username", "database"]
        for field in required_fields:
            if not config.get(field):
                errors[field] = f"{field.title()} is required"
        
        # Database type validation
        supported_types = ["postgresql", "mysql", "mssql", "oracle", "sqlite"]
        if config.get("type") and config["type"] not in supported_types:
            errors["type"] = f"Unsupported database type. Supported: {', '.join(supported_types)}"
        
        # Port validation
        if config.get("port"):
            try:
                port = int(config["port"])
                if port < 1 or port > 65535:
                    errors["port"] = "Port must be between 1 and 65535"
            except (ValueError, TypeError):
                errors["port"] = "Port must be a valid number"
        
        return errors
    
    @staticmethod
    def create_connection_config(
        db_type: str,
        host: str,
        port: Optional[int],
        username: str,
        password: str,
        database: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a standardized connection configuration.
        
        Args:
            db_type: Database type (postgresql, mysql, etc.)
            host: Database host
            port: Database port
            username: Username
            password: Password
            database: Database name
            name: Display name for the connection
            description: Description of the connection
            
        Returns:
            Standardized connection configuration
        """
        config = {
            "type": db_type.lower(),
            "name": name or f"{db_type.title()} Connection",
            "description": description or f"Custom {db_type.title()} database connection",
            "connection": {
                "host": host,
                "port": port,
                "username": username,
                "password": password,
                "database": database
            },
            "is_custom": True,
            "status": "configured"
        }
        
        return config

def render_custom_connection_form() -> Optional[Dict[str, Any]]:
    """Render a form for custom database connections in Streamlit.
    
    Returns:
        Connection configuration if form is submitted, None otherwise
    """
    st.subheader("🔗 Custom Database Connection")
    
    # Connection method selection
    connection_method = st.radio(
        "Connection Method:",
        ["📝 Manual Entry", "🔗 Connection String"],
        key="connection_method"
    )
    
    if connection_method == "🔗 Connection String":
        st.write("**Enter Connection String:**")
        st.info("Format: `postgresql://user:password@host:port/database`")
        
        # Use user's Supabase example as placeholder
        supabase_example = "postgresql://postgres.hxxjdvecnhvqkgkscnmv:Sri*9594@aws-0-ap-south-1.pooler.supabase.com:5432/postgres"
        
        connection_string = st.text_input(
            "Connection String:",
            value="",
            placeholder=supabase_example,
            help="Example: postgresql://user:pass@host:port/database\nYou can use the Supabase connection shown above as an example"
        )
        
        if connection_string:
            try:
                # Parse connection string
                parsed_config = DatabaseConnectionHelper.parse_connection_string(connection_string)
                
                # Show parsed details
                with st.expander("📋 Parsed Connection Details", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Type:** {parsed_config['type']}")
                        st.write(f"**Host:** {parsed_config['host']}")
                        st.write(f"**Port:** {parsed_config['port']}")
                    with col2:
                        st.write(f"**Username:** {parsed_config['username']}")
                        st.write(f"**Database:** {parsed_config['database']}")
                        st.write(f"**Password:** {'*' * len(str(parsed_config['password'])) if parsed_config['password'] else 'Not provided'}")
                
                # Test connection button
                if st.button("🔍 Test Connection", key="test_connection_string"):
                    return test_and_create_connection(parsed_config)
                    
            except ValueError as e:
                st.error(f"Invalid connection string: {e}")
                st.info("Make sure your connection string follows the format: `protocol://user:password@host:port/database`")
    
    else:  # Manual Entry
        st.write("**Enter Connection Details:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            db_type = st.selectbox(
                "Database Type:",
                ["postgresql", "mysql", "mssql", "oracle"],
                help="Select your database type"
            )
            
            host = st.text_input(
                "Host:",
                placeholder="localhost or your-server.com",
                help="Database server hostname or IP address"
            )
            
            port = st.number_input(
                "Port:",
                min_value=1,
                max_value=65535,
                value=5432 if db_type == "postgresql" else (3306 if db_type == "mysql" else (1433 if db_type == "mssql" else 1521)),
                help="Database server port"
            )
        
        with col2:
            username = st.text_input(
                "Username:",
                placeholder="your_username",
                help="Database username"
            )
            
            password = st.text_input(
                "Password:",
                type="password",
                placeholder="your_password",
                help="Database password"
            )
            
            database = st.text_input(
                "Database Name:",
                placeholder="your_database",
                help="Name of the database to connect to"
            )
        
        # Optional fields
        with st.expander("📝 Additional Details (Optional)"):
            connection_name = st.text_input(
                "Connection Name:",
                placeholder="My Custom Database",
                help="Friendly name for this connection"
            )
            
            description = st.text_area(
                "Description:",
                placeholder="Description of this database connection",
                help="Optional description"
            )
        
        # Test connection button
        if st.button("🔍 Test Connection", key="test_manual_connection"):
            if not all([host, username, database]):
                st.error("Please fill in all required fields (Host, Username, Database)")
                return None
            
            manual_config = {
                "type": db_type,
                "host": host,
                "port": int(port),
                "username": username,
                "password": password,
                "database": database
            }
            
            return test_and_create_connection(
                manual_config, 
                name=connection_name, 
                description=description
            )
    
    return None

def test_and_create_connection(
    parsed_config: Dict[str, Any], 
    name: Optional[str] = None, 
    description: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Test database connection and create configuration if successful.
    
    Args:
        parsed_config: Parsed connection configuration
        name: Optional custom name
        description: Optional custom description
        
    Returns:
        Connection configuration if successful, None otherwise
    """
    from database_tools import DatabaseManager
    
    with st.spinner("Testing database connection..."):
        try:
            # Create database manager to test connection
            db_manager = DatabaseManager(
                database_type=parsed_config["type"],
                host=parsed_config["host"],
                port=parsed_config["port"],
                username=parsed_config["username"],
                password=parsed_config["password"],
                database_name=parsed_config["database"]
            )
            
            # Test connection
            result = db_manager.test_connection()
            
            if result["success"]:
                st.success("✅ Connection successful!")
                
                # Get table information
                try:
                    tables = db_manager.list_tables()
                    st.info(f"Found {len(tables)} tables in the database")
                    
                    if tables:
                        with st.expander("📋 Available Tables"):
                            for i, table in enumerate(tables[:10]):  # Show first 10 tables
                                st.write(f"• {table}")
                            if len(tables) > 10:
                                st.write(f"... and {len(tables) - 10} more tables")
                except Exception as e:
                    st.warning(f"Could not list tables: {e}")
                
                # Create configuration
                connection_config = DatabaseConnectionHelper.create_connection_config(
                    db_type=parsed_config["type"],
                    host=parsed_config["host"],
                    port=parsed_config["port"],
                    username=parsed_config["username"],
                    password=parsed_config["password"],
                    database=parsed_config["database"],
                    name=name,
                    description=description
                )
                
                # Save connection button
                if st.button("💾 Save This Connection", key="save_connection"):
                    return save_custom_connection(connection_config)
                
                return connection_config
                
            else:
                st.error(f"❌ Connection failed: {result['message']}")
                st.info("Please check your credentials and try again")
                
        except Exception as e:
            st.error(f"❌ Connection error: {str(e)}")
            
    return None

def save_custom_connection(connection_config: Dict[str, Any]) -> Dict[str, Any]:
    """Save a custom connection to the database configurations.
    
    Args:
        connection_config: Connection configuration to save
        
    Returns:
        Updated connection configuration
    """
    import json
    import os
    
    # Load existing configurations
    configs_file = "database_configs.json"
    if os.path.exists(configs_file):
        with open(configs_file, "r") as f:
            existing_configs = json.load(f)
    else:
        existing_configs = {}
    
    # Generate unique key for this connection
    base_key = f"custom_{connection_config['type']}"
    key = base_key
    counter = 1
    while key in existing_configs:
        key = f"{base_key}_{counter}"
        counter += 1
    
    # Add to configurations
    existing_configs[key] = connection_config
    
    # Save back to file
    with open(configs_file, "w") as f:
        json.dump(existing_configs, f, indent=2)
    
    st.success(f"✅ Connection saved as '{connection_config['name']}'")
    st.info("Refresh the page to see the new connection in the database dropdown")
    
    return connection_config 