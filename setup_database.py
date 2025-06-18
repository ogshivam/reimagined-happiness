"""
Setup script to download and configure the Chinook database.
"""

import os
import urllib.request
import sqlite3

def download_chinook_database():
    """Download the Chinook database from GitHub."""
    
    database_url = "https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"
    database_path = "chinook.db"
    
    if os.path.exists(database_path):
        print(f"Database {database_path} already exists.")
        return database_path
    
    print("Downloading Chinook database...")
    try:
        urllib.request.urlretrieve(database_url, database_path)
        print(f"Database downloaded successfully to {database_path}")
        return database_path
    except Exception as e:
        print(f"Error downloading database: {e}")
        return None

def verify_database(database_path: str):
    """Verify the database is working and show basic info."""
    
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

if __name__ == "__main__":
    print("Setting up Chinook database for Text-to-SQL tool...")
    print("=" * 50)
    
    # Download database
    db_path = download_chinook_database()
    
    if db_path:
        # Verify database
        if verify_database(db_path):
            print("\nSetup completed successfully!")
            print("\nNext steps:")
            print("1. Get your Together AI API key: https://api.together.xyz/settings/api-keys")
            print("2. Set your API key: export TOGETHER_API_KEY=your_key_here")
            print("3. Run: streamlit run app.py")
        else:
            print("Database verification failed.")
    else:
        print("Failed to setup database.") 