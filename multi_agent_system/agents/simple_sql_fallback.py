"""
Simple SQL Fallback Generator
Used when API rate limits are hit to provide basic functionality
"""
import re
from typing import Dict, Any, Optional

class SimpleSQLFallback:
    """Simple SQL generator for common queries when API is rate limited"""
    
    def __init__(self):
        self.table_map = {
            'artist': 'Artist',
            'artists': 'Artist', 
            'album': 'Album',
            'albums': 'Album',
            'track': 'Track',
            'tracks': 'Track',
            'customer': 'Customer',
            'customers': 'Customer',
            'invoice': 'Invoice',
            'invoices': 'Invoice',
            'genre': 'Genre',
            'genres': 'Genre',
            'employee': 'Employee',
            'employees': 'Employee'
        }
    
    def generate_simple_sql(self, question: str) -> Optional[str]:
        """Generate basic SQL for common questions"""
        question_lower = question.lower()
        
        # Count queries
        if 'how many' in question_lower or 'count' in question_lower:
            if 'table' in question_lower:
                return "SELECT COUNT(*) as table_count FROM sqlite_master WHERE type='table'"
            
            for word, table in self.table_map.items():
                if word in question_lower:
                    return f"SELECT COUNT(*) as count FROM {table}"
        
        # Show all / list queries
        if any(phrase in question_lower for phrase in ['show me', 'list all', 'get all', 'display']):
            for word, table in self.table_map.items():
                if word in question_lower:
                    return f"SELECT * FROM {table} LIMIT 10"
        
        # Top/best queries
        if any(phrase in question_lower for phrase in ['top', 'best', 'highest']):
            if 'artist' in question_lower:
                return "SELECT * FROM Artist LIMIT 10"
            elif 'album' in question_lower:
                return "SELECT * FROM Album LIMIT 10"
        
        # Table listing
        if 'tables' in question_lower:
            return "SELECT name FROM sqlite_master WHERE type='table'"
        
        # Schema queries
        if 'schema' in question_lower or 'structure' in question_lower:
            return "SELECT name, sql FROM sqlite_master WHERE type='table'"
        
        return None
    
    def can_handle_query(self, question: str) -> bool:
        """Check if this query can be handled by the fallback"""
        question_lower = question.lower()
        
        # Special cases that don't need table names
        if 'table' in question_lower and ('how many' in question_lower or 'count' in question_lower):
            return True
        
        if any(word in question_lower for word in ['tables', 'schema', 'structure']):
            return True
        
        # Can handle basic counting, listing, and schema queries
        return any(phrase in question_lower for phrase in [
            'how many', 'count', 'show me', 'list all', 'top', 'best'
        ]) and any(word in question_lower for word in self.table_map.keys())

fallback_generator = SimpleSQLFallback() 