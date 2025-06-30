"""
SQL Chain implementation for text-to-SQL conversion.
Uses LangChain's create_sql_query_chain for predictable SQL generation.
"""

import os
from typing import Dict, Any, List
from langchain_together import ChatTogether
from langchain.chains import create_sql_query_chain
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from database_tools import DatabaseManager, get_chinook_schema_description
import pandas as pd

class SQLChain:
    """Chain-based approach for text-to-SQL conversion."""
    
    def __init__(self, database_path: str = "chinook.db", model: str = "meta-llama/Llama-3-70b-chat-hf", api_key: str = None):
        """Initialize the SQL chain.
        
        Args:
            database_path: Path to the SQLite database
            model: Together AI model to use
            api_key: Together AI API key
        """
        self.database_path = database_path
        self.db_manager = DatabaseManager(database_path)
        self.llm = ChatTogether(
            model=model,
            together_api_key=api_key,
            temperature=0
        )
        
        # Create the SQL query chain with custom prompt
        self.sql_chain = self._create_sql_query_chain()
        
        # Create the answer chain
        self.answer_chain = self._create_answer_chain()
        
        # Create the full chain (question -> SQL -> execute -> answer)
        self.full_chain = self._create_full_chain()
    
    def _create_sql_query_chain(self):
        """Create a custom SQL query generation chain."""
        
        # Get the database schema
        schema_info = self.db_manager.get_schema()
        
        sql_prompt = PromptTemplate.from_template(
            """You are a SQL expert. Given a question about a music store database, write ONLY the SQL query.

Database Schema:
{schema}

Rules:
- Return ONLY the SQL query, no explanations or extra text
- Use double quotes for column and table names
- The database uses SQLite syntax
- Do not include any text before or after the SQL query

Question: {question}

SQL Query:"""
        )
        
        def extract_sql(response):
            """Extract just the SQL from the response with improved robustness."""
            sql = response.strip()
            
            # Remove common prefixes
            prefixes_to_remove = [
                "Here is the SQL query:",
                "Here's the SQL query:",
                "SQL Query:",
                "Here is the answer:",
                "Question:",
                "SQLQuery:",
                "Here is the",
                "```sql",
                "```"
            ]
            
            for prefix in prefixes_to_remove:
                if sql.lower().startswith(prefix.lower()):
                    sql = sql[len(prefix):].strip()
            
            # Remove markdown code blocks
            if sql.startswith('```'):
                sql = sql[3:].strip()
                if sql.lower().startswith('sql'):
                    sql = sql[3:].strip()
            
            if sql.endswith('```'):
                sql = sql[:-3].strip()
            
            # Simple approach: find the SQL statement by looking for SELECT to semicolon
            # This avoids the complex parsing that was causing truncation
            import re
            
            # Look for a complete SQL statement (more permissive pattern)
            sql_pattern = r'(SELECT\s+.*?;)'
            match = re.search(sql_pattern, sql, re.IGNORECASE | re.DOTALL)
            
            if match:
                result = match.group(1).strip()
            else:
                # Fallback: take everything and ensure it ends with semicolon
                # Remove obvious non-SQL lines (explanatory text)
                lines = sql.split('\n')
                sql_lines = []
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Skip obvious explanation lines
                    if (line.lower().startswith(('this query', 'the query', 'explanation:', 'note:')) or
                        'explanation' in line.lower() or
                        line.startswith('--') or line.startswith('#')):
                        continue
                    
                    sql_lines.append(line)
                
                result = ' '.join(sql_lines).strip()
            
            # Clean up and validate
            if result:
                # Remove extra semicolons
                while result.endswith(';;'):
                    result = result[:-1]
                
                # Ensure ends with semicolon
                if not result.endswith(';'):
                    result += ';'
                
                # Basic validation - should start with SELECT, INSERT, UPDATE, DELETE, or WITH
                result_lower = result.lower().strip()
                if not result_lower.startswith(('select', 'with', 'insert', 'update', 'delete')):
                    # Try to find the actual SQL part
                    for line in result.split():
                        if line.lower().startswith(('select', 'with', 'insert', 'update', 'delete')):
                            # Reconstruct from this point
                            start_idx = result.lower().find(line.lower())
                            result = result[start_idx:]
                            break
            
            return result if result else sql
        
        # Create a partial chain with schema already bound
        from langchain_core.runnables import RunnableLambda
        
        def add_schema_and_invoke(input_dict):
            input_dict = dict(input_dict)  # Make a copy
            input_dict["schema"] = schema_info
            return (sql_prompt | self.llm | StrOutputParser() | extract_sql).invoke(input_dict)
        
        return RunnableLambda(add_schema_and_invoke)
    
    def _create_answer_chain(self):
        """Create a chain to generate natural language answers from SQL results."""
        
        answer_prompt = PromptTemplate.from_template(
            """Given the following user question, corresponding SQL query, and SQL result, 
            answer the user question in a natural and helpful way.

            Question: {question}
            SQL Query: {query}
            SQL Result: {result}
            
            Answer: """
        )
        
        return answer_prompt | self.llm | StrOutputParser()
    
    def _create_full_chain(self):
        """Create the full chain that goes from question to natural language answer."""
        
        def execute_query(inputs):
            """Execute the SQL query and add results to the inputs."""
            try:
                query = inputs["query"]
                result = self.db_manager.execute_query(query)
                
                # Convert DataFrame to a readable format
                if result.empty:
                    result_str = "No results found."
                else:
                    # Limit results for readability
                    if len(result) > 10:
                        result_str = f"First 10 of {len(result)} results:\n{result.head(10).to_string(index=False)}"
                    else:
                        result_str = result.to_string(index=False)
                
                inputs["result"] = result_str
                return inputs
            except Exception as e:
                inputs["result"] = f"Error executing query: {str(e)}"
                return inputs
        
        return (
            RunnablePassthrough.assign(query=self.sql_chain) 
            | RunnablePassthrough.assign(result=execute_query)
            | self.answer_chain
        )
    
    def query(self, question: str, return_intermediate: bool = False) -> Dict[str, Any]:
        """Execute a text-to-SQL query.
        
        Args:
            question: Natural language question
            return_intermediate: Whether to return intermediate results (SQL query, raw results)
            
        Returns:
            Dictionary with query results and metadata
        """
        try:
            # Generate SQL query
            sql_query = self.sql_chain.invoke({"question": question})
            
            # Execute query
            raw_results = self.db_manager.execute_query(sql_query)
            
            # Generate natural language answer
            if raw_results.empty:
                result_str = "No results found."
            else:
                if len(raw_results) > 10:
                    result_str = f"First 10 of {len(raw_results)} results:\n{raw_results.head(10).to_string(index=False)}"
                else:
                    result_str = raw_results.to_string(index=False)
            
            answer = self.answer_chain.invoke({
                "question": question,
                "query": sql_query,
                "result": result_str
            })
            
            result = {
                "question": question,
                "answer": answer,
                "success": True
            }
            
            if return_intermediate:
                result.update({
                    "sql_query": sql_query,
                    "raw_results": raw_results,
                    "num_results": len(raw_results)
                })
            
            return result
            
        except Exception as e:
            return {
                "question": question,
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    def generate_sql_only(self, question: str) -> str:
        """Generate SQL query without executing it.
        
        Args:
            question: Natural language question
            
        Returns:
            Generated SQL query
        """
        try:
            return self.sql_chain.invoke({"question": question})
        except Exception as e:
            return f"Error generating SQL: {str(e)}"
    
    def validate_and_explain_query(self, question: str) -> Dict[str, Any]:
        """Generate SQL query and validate it without executing.
        
        Args:
            question: Natural language question
            
        Returns:
            Dictionary with SQL query and validation results
        """
        try:
            # Generate SQL query
            sql_query = self.sql_chain.invoke({"question": question})
            
            # Validate the query
            validation = self.db_manager.validate_query(sql_query)
            
            return {
                "question": question,
                "sql_query": sql_query,
                "validation": validation,
                "success": True
            }
            
        except Exception as e:
            return {
                "question": question,
                "sql_query": None,
                "validation": {"valid": False, "message": f"Error: {str(e)}"},
                "success": False,
                "error": str(e)
            }
    
    def get_table_context(self, question: str) -> Dict[str, Any]:
        """Analyze question and provide relevant table context.
        
        Args:
            question: Natural language question
            
        Returns:
            Dictionary with relevant table information
        """
        # Simple keyword-based table relevance (could be enhanced with embeddings)
        tables = self.db_manager.list_tables()
        question_lower = question.lower()
        
        relevant_tables = []
        
        # Basic keyword matching for table relevance
        table_keywords = {
            "artists": ["artist", "band", "musician"],
            "albums": ["album", "record", "release"],
            "tracks": ["track", "song", "music"],
            "customers": ["customer", "client", "buyer"],
            "employees": ["employee", "staff", "worker"],
            "invoices": ["invoice", "sale", "purchase", "order"],
            "invoice_items": ["item", "line item"],
            "genres": ["genre", "style", "type of music"],
            "media_types": ["media", "format", "mp3", "aac"],
            "playlists": ["playlist", "collection"],
        }
        
        for table, keywords in table_keywords.items():
            if table in tables and any(keyword in question_lower for keyword in keywords):
                relevant_tables.append(table)
        
        # If no specific tables found, include main tables
        if not relevant_tables:
            relevant_tables = ["artists", "albums", "tracks", "customers", "invoices"]
        
        # Get detailed info for relevant tables
        table_info = {}
        for table in relevant_tables:
            if table in tables:
                table_info[table] = {
                    "sample_data": self.db_manager.get_sample_data(table),
                    "statistics": self.db_manager.get_table_statistics(table)
                }
        
        return {
            "relevant_tables": relevant_tables,
            "table_info": table_info,
            "schema_description": get_chinook_schema_description()
        }

def create_enhanced_sql_chain(database_path: str = "chinook.db") -> SQLChain:
    """Create an enhanced SQL chain with additional capabilities.
    
    Args:
        database_path: Path to the SQLite database
        
    Returns:
        Configured SQLChain instance
    """
    return SQLChain(database_path)

# Example usage and testing
if __name__ == "__main__":
    # Create the SQL chain
    chain = SQLChain()
    
    # Test queries
    test_questions = [
        "What are the top 5 selling artists?",
        "How many customers are from each country?",
        "What is the most popular genre?",
        "Show me the revenue by year.",
        "Which employee has the highest sales?"
    ]
    
    print("Testing SQL Chain...")
    print("=" * 50)
    
    for question in test_questions:
        print(f"\nQuestion: {question}")
        result = chain.query(question, return_intermediate=True)
        
        if result["success"]:
            print(f"SQL Query: {result['sql_query']}")
            print(f"Answer: {result['answer']}")
            print(f"Number of results: {result['num_results']}")
        else:
            print(f"Error: {result['error']}")
        
        print("-" * 30) 