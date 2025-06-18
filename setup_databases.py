"""
Enhanced database setup script to download and configure multiple database types.
Supports SQLite, PostgreSQL, MySQL sample databases for easy testing.
"""

import os
import urllib.request
import sqlite3
import json
import zipfile
import tempfile
from typing import Dict, Any, Optional
import pandas as pd

class DatabaseSetup:
    """Setup and configure multiple database types with sample data."""
    
    def __init__(self):
        self.databases = {}
        self.sample_data_urls = {
            "chinook": {
                "sqlite": "https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite",
                "description": "Digital music store database with artists, albums, tracks, customers, and sales data"
            },
            "northwind": {
                "sqlite": "https://raw.githubusercontent.com/jpwhite3/northwind-SQLite3/master/Northwind_large.sqlite",
                "description": "Classic business database with customers, orders, products, and employees"
            },
            "sakila": {
                "description": "DVD rental store database with films, actors, customers, and rentals"
            }
        }
    
    def download_sqlite_database(self, db_name: str = "chinook", target_path: str = None) -> str:
        """Download a SQLite sample database.
        
        Args:
            db_name: Name of the database to download ('chinook' or 'northwind')
            target_path: Target file path (optional)
            
        Returns:
            Path to the downloaded database
        """
        if db_name not in self.sample_data_urls:
            raise ValueError(f"Unknown database: {db_name}")
        
        db_info = self.sample_data_urls[db_name]
        if "sqlite" not in db_info:
            raise ValueError(f"No SQLite version available for: {db_name}")
        
        database_url = db_info["sqlite"]
        if target_path is None:
            target_path = f"{db_name}.db"
        
        if os.path.exists(target_path):
            print(f"Database {target_path} already exists.")
            return target_path
        
        print(f"Downloading {db_name} database...")
        try:
            urllib.request.urlretrieve(database_url, target_path)
            print(f"Database downloaded successfully to {target_path}")
            
            # Verify the database
            if self.verify_sqlite_database(target_path):
                print(f"✅ {db_name} database is ready to use!")
                return target_path
            else:
                print(f"❌ Database verification failed for {target_path}")
                return None
                
        except Exception as e:
            print(f"Error downloading database: {e}")
            return None
    
    def verify_sqlite_database(self, database_path: str) -> bool:
        """Verify a SQLite database is working and show basic info.
        
        Args:
            database_path: Path to the SQLite database
            
        Returns:
            True if database is valid, False otherwise
        """
        if not os.path.exists(database_path):
            print(f"Database {database_path} not found.")
            return False
        
        try:
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
            
            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            print(f"\nDatabase verification successful!")
            print(f"Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table[0]}")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error verifying database: {e}")
            return False
    
    def create_sample_mysql_database(self, database_name: str = "sample_mysql") -> Dict[str, Any]:
        """Create configuration for a sample MySQL database.
        
        Args:
            database_name: Name of the database
            
        Returns:
            Configuration dictionary
        """
        config = {
            "type": "mysql",
            "name": database_name,
            "description": "Sample MySQL database configuration",
            "connection": {
                "host": "localhost",
                "port": 3306,
                "username": "root",
                "password": "",
                "database": database_name
            },
            "setup_instructions": [
                "1. Install MySQL server",
                "2. Create database: CREATE DATABASE sample_mysql;",
                "3. Import sample data or use existing database",
                "4. Update credentials in the configuration"
            ],
            "sample_data_script": self._get_mysql_sample_script()
        }
        return config
    
    def create_sample_postgresql_database(self, database_name: str = "sample_postgres") -> Dict[str, Any]:
        """Create configuration for a sample PostgreSQL database.
        
        Args:
            database_name: Name of the database
            
        Returns:
            Configuration dictionary
        """
        config = {
            "type": "postgresql",
            "name": database_name,
            "description": "Sample PostgreSQL database configuration",
            "connection": {
                "host": "localhost",
                "port": 5432,
                "username": "postgres",
                "password": "",
                "database": database_name
            },
            "setup_instructions": [
                "1. Install PostgreSQL server",
                "2. Create database: CREATE DATABASE sample_postgres;",
                "3. Import sample data or use existing database",
                "4. Update credentials in the configuration"
            ],
            "sample_data_script": self._get_postgresql_sample_script()
        }
        return config
    
    def create_sample_mssql_database(self, database_name: str = "sample_mssql") -> Dict[str, Any]:
        """Create configuration for a sample Microsoft SQL Server database.
        
        Args:
            database_name: Name of the database
            
        Returns:
            Configuration dictionary
        """
        config = {
            "type": "mssql",
            "name": database_name,
            "description": "Sample Microsoft SQL Server database configuration",
            "connection": {
                "host": "localhost",
                "port": 1433,
                "username": "sa",
                "password": "",
                "database": database_name
            },
            "setup_instructions": [
                "1. Install SQL Server (Developer/Express edition is free)",
                "2. Enable SQL Server Authentication mode",
                "3. Create database: CREATE DATABASE sample_mssql;",
                "4. Import sample data or use existing database",
                "5. Update credentials in the configuration"
            ],
            "sample_data_script": self._get_mssql_sample_script(),
            "docker_command": "docker run -e 'ACCEPT_EULA=Y' -e 'SA_PASSWORD=YourStrong@Passw0rd' -p 1433:1433 --name sqlserver -d mcr.microsoft.com/mssql/server:2019-latest"
        }
        return config
    
    def create_sample_oracle_database(self, database_name: str = "sample_oracle") -> Dict[str, Any]:
        """Create configuration for a sample Oracle database.
        
        Args:
            database_name: Name of the database
            
        Returns:
            Configuration dictionary
        """
        config = {
            "type": "oracle",
            "name": database_name,
            "description": "Sample Oracle database configuration",
            "connection": {
                "host": "localhost",
                "port": 1521,
                "username": "system",
                "password": "",
                "database": "XE"  # Oracle Express Edition default
            },
            "setup_instructions": [
                "1. Install Oracle Database XE (Express Edition is free)",
                "2. Create user: CREATE USER sample_user IDENTIFIED BY password;",
                "3. Grant privileges: GRANT ALL PRIVILEGES TO sample_user;",
                "4. Import sample data or use existing database",
                "5. Update credentials in the configuration"
            ],
            "sample_data_script": self._get_oracle_sample_script(),
            "docker_command": "docker run -d -p 1521:1521 -e ORACLE_PASSWORD=mypassword gvenzl/oracle-xe:21-slim"
        }
        return config
    
    def _get_mysql_sample_script(self) -> str:
        """Get MySQL sample data creation script."""
        return """
-- Sample MySQL Database Script
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2),
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    city VARCHAR(100),
    country VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    product_id INT,
    quantity INT,
    order_date DATE,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Sample data
INSERT INTO products (name, price, category) VALUES
('Laptop', 999.99, 'Electronics'),
('Mouse', 29.99, 'Electronics'),
('Coffee Mug', 12.50, 'Kitchen'),
('Book', 19.99, 'Books'),
('Phone', 699.99, 'Electronics');

INSERT INTO customers (first_name, last_name, email, city, country) VALUES
('John', 'Doe', 'john@example.com', 'New York', 'USA'),
('Jane', 'Smith', 'jane@example.com', 'London', 'UK'),
('Bob', 'Johnson', 'bob@example.com', 'Toronto', 'Canada');

INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES
(1, 1, 1, '2024-01-15'),
(2, 2, 2, '2024-01-16'),
(3, 3, 1, '2024-01-17');
"""
    
    def _get_postgresql_sample_script(self) -> str:
        """Get PostgreSQL sample data creation script."""
        return """
-- Sample PostgreSQL Database Script
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2),
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    city VARCHAR(100),
    country VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    product_id INT REFERENCES products(id),
    quantity INT,
    order_date DATE
);

-- Sample data
INSERT INTO products (name, price, category) VALUES
('Laptop', 999.99, 'Electronics'),
('Mouse', 29.99, 'Electronics'),
('Coffee Mug', 12.50, 'Kitchen'),
('Book', 19.99, 'Books'),
('Phone', 699.99, 'Electronics');

INSERT INTO customers (first_name, last_name, email, city, country) VALUES
('John', 'Doe', 'john@example.com', 'New York', 'USA'),
('Jane', 'Smith', 'jane@example.com', 'London', 'UK'),
('Bob', 'Johnson', 'bob@example.com', 'Toronto', 'Canada');

INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES
(1, 1, 1, '2024-01-15'),
(2, 2, 2, '2024-01-16'),
(3, 3, 1, '2024-01-17');
"""
    
    def _get_mssql_sample_script(self) -> str:
        """Get Microsoft SQL Server sample data creation script."""
        return """
-- Sample Microsoft SQL Server Database Script
CREATE TABLE products (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    price DECIMAL(10,2),
    category NVARCHAR(100),
    created_at DATETIME DEFAULT GETDATE()
);

CREATE TABLE customers (
    id INT IDENTITY(1,1) PRIMARY KEY,
    first_name NVARCHAR(100),
    last_name NVARCHAR(100),
    email NVARCHAR(255) UNIQUE,
    city NVARCHAR(100),
    country NVARCHAR(100)
);

CREATE TABLE orders (
    id INT IDENTITY(1,1) PRIMARY KEY,
    customer_id INT,
    product_id INT,
    quantity INT,
    order_date DATE,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Sample data
INSERT INTO products (name, price, category) VALUES
('Laptop', 999.99, 'Electronics'),
('Mouse', 29.99, 'Electronics'),
('Coffee Mug', 12.50, 'Kitchen'),
('Book', 19.99, 'Books'),
('Phone', 699.99, 'Electronics');

INSERT INTO customers (first_name, last_name, email, city, country) VALUES
('John', 'Doe', 'john@example.com', 'New York', 'USA'),
('Jane', 'Smith', 'jane@example.com', 'London', 'UK'),
('Bob', 'Johnson', 'bob@example.com', 'Toronto', 'Canada');

INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES
(1, 1, 1, '2024-01-15'),
(2, 2, 2, '2024-01-16'),
(3, 3, 1, '2024-01-17');
"""
    
    def _get_oracle_sample_script(self) -> str:
        """Get Oracle sample data creation script."""
        return """
-- Sample Oracle Database Script
CREATE TABLE products (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    name VARCHAR2(255) NOT NULL,
    price NUMBER(10,2),
    category VARCHAR2(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customers (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    first_name VARCHAR2(100),
    last_name VARCHAR2(100),
    email VARCHAR2(255) UNIQUE,
    city VARCHAR2(100),
    country VARCHAR2(100)
);

CREATE TABLE orders (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    customer_id NUMBER,
    product_id NUMBER,
    quantity NUMBER,
    order_date DATE,
    CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
    CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Sample data
INSERT INTO products (name, price, category) VALUES ('Laptop', 999.99, 'Electronics');
INSERT INTO products (name, price, category) VALUES ('Mouse', 29.99, 'Electronics');
INSERT INTO products (name, price, category) VALUES ('Coffee Mug', 12.50, 'Kitchen');
INSERT INTO products (name, price, category) VALUES ('Book', 19.99, 'Books');
INSERT INTO products (name, price, category) VALUES ('Phone', 699.99, 'Electronics');

INSERT INTO customers (first_name, last_name, email, city, country) VALUES ('John', 'Doe', 'john@example.com', 'New York', 'USA');
INSERT INTO customers (first_name, last_name, email, city, country) VALUES ('Jane', 'Smith', 'jane@example.com', 'London', 'UK');
INSERT INTO customers (first_name, last_name, email, city, country) VALUES ('Bob', 'Johnson', 'bob@example.com', 'Toronto', 'Canada');

INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES (1, 1, 1, DATE '2024-01-15');
INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES (2, 2, 2, DATE '2024-01-16');
INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES (3, 3, 1, DATE '2024-01-17');

COMMIT;
"""
    
    def save_database_configs(self, configs_path: str = "database_configs.json"):
        """Save database configurations to a JSON file.
        
        Args:
            configs_path: Path to save the configurations
        """
        configs = {
            "chinook_sqlite": {
                "type": "sqlite",
                "name": "Chinook (Music Store)",
                "description": "Digital music store with artists, albums, tracks, customers, and sales",
                "file_path": "chinook.db",
                "download_available": True,
                "status": "ready" if os.path.exists("chinook.db") else "not_downloaded"
            },
            "northwind_sqlite": {
                "type": "sqlite", 
                "name": "Northwind (Business)",
                "description": "Classic business database with customers, orders, products, and employees",
                "file_path": "northwind.db",
                "download_available": True,
                "status": "ready" if os.path.exists("northwind.db") else "not_downloaded"
            },
            "sample_mysql": self.create_sample_mysql_database(),
            "sample_postgresql": self.create_sample_postgresql_database(),
            "sample_mssql": self.create_sample_mssql_database(),
            "sample_oracle": self.create_sample_oracle_database()
        }
        
        with open(configs_path, 'w') as f:
            json.dump(configs, f, indent=2)
        
        print(f"Database configurations saved to {configs_path}")
        return configs
    
    def setup_all_sample_databases(self):
        """Set up all available sample databases."""
        print("🗄️ Setting up sample databases...")
        print("=" * 50)
        
        # Download SQLite databases
        print("📥 Downloading SQLite databases...")
        
        # Chinook (music store)
        chinook_path = self.download_sqlite_database("chinook", "chinook.db")
        if chinook_path:
            self.databases["chinook"] = chinook_path
        
        # Northwind (business)
        northwind_path = self.download_sqlite_database("northwind", "northwind.db")
        if northwind_path:
            self.databases["northwind"] = northwind_path
        
        # Save configurations
        configs = self.save_database_configs()
        
        print("\n✅ Database setup complete!")
        print("\nAvailable databases:")
        for db_name, config in configs.items():
            status = "✅" if config.get("status") == "ready" else "⚠️"
            print(f"  {status} {config['name']} ({config['type'].upper()})")
        
        print(f"\n📋 Total databases configured: {len(configs)}")
        print("🚀 Ready to use in the Streamlit app!")
        
        return configs
    
    def create_docker_compose(self):
        """Create a docker-compose.yml for easy database testing."""
        docker_compose_content = """
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: sample_postgres
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./sql_scripts:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 5

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password123
      MYSQL_DATABASE: sample_mysql
      MYSQL_USER: testuser
      MYSQL_PASSWORD: password123
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./sql_scripts:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 30s
      timeout: 10s
      retries: 5

  sqlserver:
    image: mcr.microsoft.com/mssql/server:2019-latest
    environment:
      ACCEPT_EULA: Y
      SA_PASSWORD: YourStrong@Passw0rd
      MSSQL_DATABASE: sample_mssql
    ports:
      - "1433:1433"
    volumes:
      - mssql_data:/var/opt/mssql
    healthcheck:
      test: ["CMD-SHELL", "/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P YourStrong@Passw0rd -Q 'SELECT 1'"]
      interval: 30s
      timeout: 10s
      retries: 5

  oracle:
    image: gvenzl/oracle-xe:21-slim
    environment:
      ORACLE_PASSWORD: mypassword
      APP_USER: sample_user
      APP_USER_PASSWORD: sample_password
    ports:
      - "1521:1521"
    volumes:
      - oracle_data:/opt/oracle/oradata
    healthcheck:
      test: ["CMD", "healthcheck.sh"]
      interval: 30s
      timeout: 10s
      retries: 5

volumes:
  postgres_data:
  mysql_data:
  mssql_data:
  oracle_data:
"""
        
        with open("docker-compose.yml", "w") as f:
            f.write(docker_compose_content)
        
        # Create SQL scripts directory
        os.makedirs("sql_scripts", exist_ok=True)
        
        # Save SQL scripts
        with open("sql_scripts/01_mysql_sample.sql", "w") as f:
            f.write(self._get_mysql_sample_script())
        
        with open("sql_scripts/01_postgres_sample.sql", "w") as f:
            f.write(self._get_postgresql_sample_script())
        
        with open("sql_scripts/01_mssql_sample.sql", "w") as f:
            f.write(self._get_mssql_sample_script())
        
        with open("sql_scripts/01_oracle_sample.sql", "w") as f:
            f.write(self._get_oracle_sample_script())
        
        print("✅ Docker Compose configuration created!")
        print("🐳 Run 'docker-compose up -d' to start all database servers")
        print("   - PostgreSQL on port 5432")
        print("   - MySQL on port 3306") 
        print("   - SQL Server on port 1433")
        print("   - Oracle on port 1521")

def main():
    """Main setup function."""
    setup = DatabaseSetup()
    
    print("🗄️ Text-to-SQL Database Setup")
    print("=" * 40)
    print("Setting up sample databases for testing...")
    
    # Setup all databases
    configs = setup.setup_all_sample_databases()
    
    # Create Docker Compose for easy testing
    setup.create_docker_compose()
    
    print("\n🎯 Next steps:")
    print("1. SQLite databases are ready to use immediately")
    print("2. For other databases: run 'docker-compose up -d'")
    print("3. Or configure your own database connections")
    print("4. Run 'streamlit run app.py' to start the app")
    print("5. Select your preferred database from the dropdown!")
    print("\n💡 Why different approaches:")
    print("  • SQLite: File-based, downloadable, no server needed")
    print("  • Others: Server-based, need installation + configuration")

if __name__ == "__main__":
    main() 