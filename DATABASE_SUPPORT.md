# 🗄️ Database Support Guide

Our text-to-SQL tool with **Llama 4** is designed to work with **multiple database types** through SQLAlchemy's powerful engine system. Here's everything you need to know about database compatibility and setup.

## ✅ **Supported Databases**

### **1. SQLite** (Current Default) ⭐
- **Status**: ✅ Fully Working  
- **Use Case**: Development, testing, small applications
- **Advantages**: No server setup, portable, lightweight
- **Connection**: File-based (`chinook.db`)

```python
db_manager = DatabaseManager(
    database_path="chinook.db",
    database_type="sqlite"
)
```

### **2. PostgreSQL** 🐘
- **Status**: ✅ Supported  
- **Use Case**: Production applications, complex queries
- **Advantages**: Advanced SQL features, JSON support, excellent performance
- **Required Driver**: `psycopg2-binary` or `psycopg2`

```python
db_manager = DatabaseManager(
    database_type="postgresql",
    host="localhost",
    port=5432,
    username="your_username", 
    password="your_password",
    database_name="your_database"
)
```

### **3. MySQL/MariaDB** 🐬
- **Status**: ✅ Supported
- **Use Case**: Web applications, WordPress, e-commerce
- **Advantages**: Popular, well-documented, good performance
- **Required Driver**: `pymysql` or `mysqlclient`

```python
db_manager = DatabaseManager(
    database_type="mysql",
    host="localhost",
    port=3306,
    username="your_username",
    password="your_password", 
    database_name="your_database"
)
```

### **4. Microsoft SQL Server** 🏢
- **Status**: ✅ Supported
- **Use Case**: Enterprise applications, .NET environments
- **Advantages**: Enterprise features, Windows integration
- **Required Driver**: `pyodbc` + ODBC Driver

```python
db_manager = DatabaseManager(
    database_type="mssql",
    host="localhost",
    port=1433,
    username="your_username",
    password="your_password",
    database_name="your_database"
)
```

### **5. Oracle Database** 🔮
- **Status**: ✅ Supported
- **Use Case**: Large enterprise systems, complex analytics
- **Advantages**: Enterprise-grade, advanced features
- **Required Driver**: `cx_Oracle`

```python
db_manager = DatabaseManager(
    database_type="oracle",
    host="localhost",
    port=1521,
    username="your_username",
    password="your_password",
    database_name="your_database"
)
```

### **6. Cloud Databases** ☁️
- **AWS RDS**: PostgreSQL, MySQL, SQL Server, Oracle
- **Azure SQL**: SQL Server, PostgreSQL, MySQL
- **Google Cloud SQL**: PostgreSQL, MySQL, SQL Server
- **Heroku Postgres**: PostgreSQL
- **PlanetScale**: MySQL-compatible

```python
# Example: AWS RDS PostgreSQL
db_manager = DatabaseManager.from_connection_string(
    connection_string="postgresql://user:pass@rds-endpoint:5432/dbname",
    database_type="postgresql"
)
```

## 🔧 **Setup Instructions**

### **Step 1: Install Database Driver**

Depending on your target database, install the appropriate driver:

```bash
# PostgreSQL
pip install psycopg2-binary

# MySQL
pip install pymysql

# SQL Server  
pip install pyodbc

# Oracle
pip install cx_Oracle

# For cloud databases
pip install psycopg2-binary pymysql pyodbc
```

### **Step 2: Configure Connection**

Choose one of these methods:

#### **Method A: Direct Parameters**
```python
from database_tools import DatabaseManager

db_manager = DatabaseManager(
    database_type="postgresql",  # or mysql, mssql, oracle
    host="your-host",
    port=5432,
    username="your-username", 
    password="your-password",
    database_name="your-database"
)
```

#### **Method B: Environment Variables**
```bash
export DB_TYPE=postgresql
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=your_username
export DB_PASSWORD=your_password
export DB_NAME=your_database
```

```python
from database_examples import connect_from_environment

db_manager = connect_from_environment()
```

#### **Method C: Connection String**
```python
db_manager = DatabaseManager.from_connection_string(
    connection_string="postgresql://user:pass@host:5432/dbname",
    database_type="postgresql"
)
```

### **Step 3: Test Connection**
```python
result = db_manager.test_connection()
print(result)
# {'success': True, 'message': 'Database connection successful', ...}
```

### **Step 4: Update Your Application**

Update your main application files to use the new database:

```python
# In sql_chain.py or sql_agent_simple.py
chain = SQLChain(
    database_path=db_manager.connection_string,  # Use connection string
    model="meta-llama/Llama-4-Scout-17B-16E-Instruct",
    api_key=your_api_key
)
```

## 📊 **Database-Specific Features**

### **SQL Syntax Differences**

Our tool automatically handles database-specific SQL syntax:

| Feature | SQLite | PostgreSQL | MySQL | SQL Server | Oracle |
|---------|--------|------------|-------|------------|--------|
| **Pagination** | `LIMIT n` | `LIMIT n` | `LIMIT n` | `TOP n` | `ROWNUM <= n` |
| **String Match** | `LIKE` | `ILIKE` | `LIKE` | `LIKE` | `LIKE` |
| **Date Functions** | `datetime()` | `NOW()` | `NOW()` | `GETDATE()` | `SYSDATE` |
| **Identifier Quotes** | `"name"` | `"name"` | `` `name` `` | `[name]` | `"name"` |

### **Llama 4 Optimization**

Llama 4 automatically adapts to different database types with:

- **Database-specific SQL generation**
- **Proper syntax for each engine** 
- **Optimal query patterns**
- **Error handling for each database**

## 🌐 **Cloud Database Examples**

### **AWS RDS**
```python
# PostgreSQL on RDS
db_manager = DatabaseManager(
    database_type="postgresql",
    host="mydb.123456789012.us-east-1.rds.amazonaws.com",
    port=5432,
    username="myuser",
    password="mypassword",
    database_name="mydatabase"
)
```

### **Azure SQL Database**
```python
# Azure SQL Database
db_manager = DatabaseManager(
    database_type="mssql",
    host="myserver.database.windows.net",
    port=1433,
    username="myuser",
    password="mypassword",
    database_name="mydatabase"
)
```

### **Google Cloud SQL**
```python
# Cloud SQL PostgreSQL
db_manager = DatabaseManager(
    database_type="postgresql",
    host="34.56.78.90",  # Public IP
    port=5432,
    username="postgres",
    password="mypassword",
    database_name="mydatabase"
)
```

### **Heroku Postgres**
```python
# From Heroku DATABASE_URL
import os
db_manager = DatabaseManager.from_connection_string(
    connection_string=os.getenv("DATABASE_URL"),
    database_type="postgresql"
)
```

## 🔒 **Security Best Practices**

### **1. Environment Variables**
Never hardcode credentials:

```bash
# .env file
DB_TYPE=postgresql
DB_HOST=your-host
DB_USER=your-username
DB_PASSWORD=your-secure-password
DB_NAME=your-database
TOGETHER_API_KEY=your-api-key
```

### **2. Connection Pooling**
For production, use connection pooling:

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    connection_string,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

### **3. SSL/TLS**
Enable SSL for cloud databases:

```python
# PostgreSQL with SSL
connection_string = "postgresql://user:pass@host:5432/db?sslmode=require"

# MySQL with SSL  
connection_string = "mysql+pymysql://user:pass@host:3306/db?ssl=true"
```

## 🧪 **Testing Different Databases**

Use our test script to verify database compatibility:

```bash
# Test current SQLite setup
python database_examples.py

# Test with environment variables
export DB_TYPE=postgresql
export DB_HOST=localhost
export DB_USER=myuser
export DB_PASSWORD=mypass
export DB_NAME=testdb

python -c "from database_examples import connect_from_environment; connect_from_environment().test_connection()"
```

## 📈 **Performance Considerations**

### **Database Performance Ranking** (for typical text-to-SQL workloads)

1. **PostgreSQL** - Best overall performance and features
2. **MySQL** - Good performance, wide compatibility  
3. **SQL Server** - Excellent for enterprise, Windows environments
4. **SQLite** - Perfect for development, limited concurrency
5. **Oracle** - Powerful but complex setup

### **Optimization Tips**

- **Use indexes** on frequently queried columns
- **Limit result sets** with appropriate LIMIT clauses
- **Consider read replicas** for heavy query workloads
- **Use connection pooling** for production applications

## 🚀 **Next Steps**

1. **Choose your database** based on your use case
2. **Install the appropriate driver**
3. **Configure connection parameters**
4. **Test the connection** before deploying
5. **Update your application** to use the new database
6. **Enjoy Llama 4's intelligent SQL generation**!

---

**Need help with a specific database?** Check our examples in `database_examples.py` or create an issue with your database type and requirements! 