# Custom Database Connections Guide

This document explains how to connect to your own databases using the Text-to-SQL application.

## 🎯 Overview

The application now supports connecting to external databases through:

1. **Pre-configured Sample Databases** - SQLite databases that can be downloaded
2. **Docker-based Databases** - MySQL, PostgreSQL, SQL Server, Oracle via Docker
3. **Custom Database Connections** - Connect to your existing databases
4. **Cloud Database Connections** - Connect to cloud providers (AWS RDS, Supabase, etc.)

## 🔗 Connection Methods

### Method 1: Quick Connect (Your Supabase Example)

For your specific Supabase PostgreSQL instance:

```
postgresql://postgres.hxxjdvecnhvqkgkscnmv:Sri*9594@aws-0-ap-south-1.pooler.supabase.com:5432/postgres
```

1. Click **"🚀 Connect to Supabase Example"** in the sidebar
2. The app will automatically parse and test the connection
3. If successful, it will be added to your database list

### Method 2: Connection String

**Format:** `protocol://username:password@host:port/database`

**Examples:**
```bash
# PostgreSQL (like your Supabase)
postgresql://user:password@host:5432/database

# MySQL
mysql://user:password@host:3306/database

# SQL Server
mssql://user:password@host:1433/database

# Oracle
oracle://user:password@host:1521/database
```

**Steps:**
1. Click **"➕ Add Other Custom Database"**
2. Select **"🔗 Connection String"**
3. Paste your connection string
4. Click **"🔍 Test Connection"**
5. If successful, click **"💾 Save This Connection"**

### Method 3: Manual Entry

**Steps:**
1. Click **"➕ Add Other Custom Database"**
2. Select **"📝 Manual Entry"**
3. Fill in the connection details:
   - Database Type (PostgreSQL, MySQL, SQL Server, Oracle)
   - Host (server address)
   - Port (database port)
   - Username
   - Password
   - Database Name
4. Click **"🔍 Test Connection"**
5. If successful, click **"💾 Save This Connection"**

## 🌐 Supported Cloud Providers

### Supabase (PostgreSQL)
- **Format:** `postgresql://[user]:[password]@[host]:5432/postgres`
- **Example:** Your provided connection string
- **Notes:** Supabase uses PostgreSQL with connection pooling

### AWS RDS
```bash
# PostgreSQL
postgresql://username:password@database-1.xyz.us-east-1.rds.amazonaws.com:5432/mydb

# MySQL
mysql://username:password@database-1.xyz.us-east-1.rds.amazonaws.com:3306/mydb
```

### Google Cloud SQL
```bash
# PostgreSQL
postgresql://username:password@123.456.789.0:5432/mydb

# MySQL  
mysql://username:password@123.456.789.0:3306/mydb
```

### Azure Database
```bash
# PostgreSQL
postgresql://username@servername:password@servername.postgres.database.azure.com:5432/mydb

# MySQL
mysql://username@servername:password@servername.mysql.database.azure.com:3306/mydb
```

### Heroku Postgres
```bash
postgresql://user:password@host:5432/database
```

### PlanetScale (MySQL)
```bash
mysql://username:password@host:3306/database
```

## 🔧 Database-Specific Features

### SQLite
- **Pros:** File-based, no server needed, downloadable
- **Cons:** Limited for production use
- **Use Case:** Development, testing, demos

### PostgreSQL
- **Pros:** Advanced SQL features, JSON support, strong consistency
- **Cons:** More complex setup
- **Use Case:** Production applications, complex queries

### MySQL
- **Pros:** Fast, widely supported, easy to use
- **Cons:** Some SQL feature limitations
- **Use Case:** Web applications, general purpose

### SQL Server
- **Pros:** Enterprise features, Windows integration
- **Cons:** Licensing costs, Windows-focused
- **Use Case:** Enterprise applications, Microsoft stack

### Oracle
- **Pros:** Enterprise features, high performance
- **Cons:** Complex, expensive licensing
- **Use Case:** Large enterprise applications

## 🛡️ Security Considerations

### Connection Security
- **SSL/TLS:** Use encrypted connections when possible
- **Credentials:** Never commit passwords to version control
- **Environment Variables:** Store sensitive data in environment variables
- **Network:** Use VPNs or private networks for production

### Best Practices
1. **Test connections** before saving
2. **Use read-only accounts** when possible
3. **Limit database access** to necessary tables
4. **Monitor connection usage**
5. **Rotate credentials** regularly

## 🚀 Quick Start Examples

### Example 1: Your Supabase Connection
1. Use the **"🚀 Connect to Supabase Example"** button
2. Connection will be tested automatically
3. Start querying your PostgreSQL database immediately

### Example 2: Local PostgreSQL
```bash
# If you have PostgreSQL running locally
postgresql://postgres:password@localhost:5432/mydatabase
```

### Example 3: Docker PostgreSQL
```bash
# Start PostgreSQL with Docker
docker run --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres

# Connect using
postgresql://postgres:password@localhost:5432/postgres
```

## 🔍 Troubleshooting

### Common Issues

**Connection Timeout**
- Check if the database server is running
- Verify network connectivity
- Check firewall settings

**Authentication Failed**
- Verify username and password
- Check if user has necessary permissions
- Ensure database exists

**SSL/TLS Errors**
- Try adding `?sslmode=require` to PostgreSQL connections
- For MySQL, use `?ssl=true`
- Check if server requires SSL

**Port Issues**
- Verify the correct port number
- Check if port is open and accessible
- Default ports: PostgreSQL (5432), MySQL (3306), SQL Server (1433), Oracle (1521)

### Testing Connections

The app automatically tests connections when you:
1. Click **"🔍 Test Connection"**
2. Use the quick connect buttons
3. Save a new connection

**Test Results Show:**
- ✅ Connection successful
- 📊 Number of tables found
- 📋 List of available tables
- ❌ Error messages if connection fails

## 📝 Connection Management

### Saving Connections
- Connections are saved to `database_configs.json`
- Automatically appear in the database dropdown
- Persist between app restarts

### Deleting Connections
- Edit `database_configs.json` to remove unwanted connections
- Or restart the app to reload default configurations

### Connection Security
- Passwords are stored in the configuration file
- For production use, consider using environment variables
- Use read-only database accounts when possible

## 🎓 Advanced Usage

### Environment Variables
Set database credentials as environment variables:

```bash
export DB_HOST=your-host.com
export DB_USER=your-username
export DB_PASSWORD=your-password
export DB_NAME=your-database
```

### Custom Sample Queries
The app automatically adjusts sample queries based on your database type:
- **Chinook/Music databases:** Artist and track queries
- **Northwind/Business databases:** Product and order queries
- **Custom databases:** Generic exploration queries

### Multi-Database Workflows
1. Connect to multiple databases
2. Switch between them using the dropdown
3. Compare schemas and data across different systems
4. Use different AI models for different databases

## 🤖 AI Model Integration

All connected databases work with:
- **Llama 4 Scout** (recommended for accuracy)
- **Llama 4 Maverick** (good for complex queries)
- **Llama 3.3 70B** (fast general purpose)
- **Other Llama models** available in the dropdown

The AI automatically adapts to your database schema and generates appropriate SQL queries regardless of the database type.

---

## 🆘 Need Help?

If you encounter issues:
1. Check the connection string format
2. Verify database server is accessible
3. Test with a simple tool like `psql` or `mysql` client
4. Check the app's error messages for specific guidance

Your Supabase connection should work seamlessly with the **"🚀 Connect to Supabase Example"** button! 