"""
Simplified SQL Agent implementation using LangChain's create_react_agent.
"""

from langchain_together import ChatTogether
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.prompts import PromptTemplate
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts.chat import ChatPromptTemplate
from database_tools import DatabaseManager, create_database_tools
from typing import Dict, Any

class SimpleSQLAgent:
    """A simplified SQL agent using LangChain's create_react_agent."""
    
    def __init__(self, database_path: str = "chinook.db", model: str = "meta-llama/Llama-3-70b-chat-hf", api_key: str = None):
        """Initialize the SQL agent.
        
        Args:
            database_path: Path to the SQLite database
            model: Together AI model to use
            api_key: Together AI API key
        """
        self.database_path = database_path
        self.llm = ChatTogether(
            model=model,
            together_api_key=api_key,
            temperature=0
        )
        
        # Get database tools  
        self.db_manager, self.toolkit = create_database_tools(database_path, model, api_key)
        self.tools = self.toolkit.get_tools()
        
        # Create the agent
        self.agent_executor = self._create_agent()
    
    def _create_agent(self) -> AgentExecutor:
        """Create the React agent with SQL tools."""
        
        # Custom prompt for SQL agent
        system_message = """You are an agent designed to interact with a SQL database.
        Given an input question, create a syntactically correct SQLite query to run, then look at the results of the query and return the answer.
        Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 10 results.
        You can order the results by a relevant column to return the most interesting examples in the database.
        Never query for all the columns from a specific table, only ask for the relevant columns given the question.
        You have access to tools for interacting with the database.
        Only use the given tools. Only use the information returned by the tools to construct your final answer.
        You MUST double check your query before executing it. If you get an error back, rewrite the query and try again.

        DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

        If the question does not seem related to the database, just return "I don't know" as the answer.

        Here are some examples of user inputs and their corresponding SQL queries:

        Question: How many employees are there?
        SQL Query: SELECT COUNT(*) FROM Employee;

        Question: What are the names of all customers?
        SQL Query: SELECT FirstName, LastName FROM Customer LIMIT 10;

        Question: What is the total sales amount?
        SQL Query: SELECT SUM(Total) FROM Invoice;
        """
        
        # Create the React agent prompt template
        template = f"""{system_message}

You have access to the following tools:

{{tools}}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{{tool_names}}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {{input}}
Thought:{{agent_scratchpad}}"""

        prompt = PromptTemplate.from_template(template)
        
        # Create the react agent
        agent = create_react_agent(self.llm, self.tools, prompt)
        
        # Create agent executor
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10
        )
    
    def query(self, question: str) -> Dict[str, Any]:
        """Process a text-to-SQL query using the agent.
        
        Args:
            question: Natural language question
            
        Returns:
            Dictionary with query results and metadata
        """
        try:
            # Execute the agent
            result = self.agent_executor.invoke({"input": question})
            
            return {
                "question": question,
                "answer": result["output"],
                "success": True,
                "approach": "React Agent"
            }
            
        except Exception as e:
            return {
                "question": question,
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "success": False,
                "error": str(e),
                "approach": "React Agent"
            }

def create_simple_sql_agent(database_path: str = "chinook.db") -> SimpleSQLAgent:
    """Create a simple SQL agent.
    
    Args:
        database_path: Path to the SQLite database
        
    Returns:
        Configured SimpleSQLAgent instance
    """
    return SimpleSQLAgent(database_path)

# Example usage
if __name__ == "__main__":
    # Create the agent
    agent = SimpleSQLAgent()
    
    # Test queries
    test_questions = [
        "How many artists are in the database?",
        "What are the top 5 selling tracks?",
        "Which country has the most customers?",
    ]
    
    print("Testing Simple SQL Agent...")
    print("=" * 50)
    
    for question in test_questions:
        print(f"\nQuestion: {question}")
        result = agent.query(question)
        
        if result["success"]:
            print(f"Answer: {result['answer']}")
        else:
            print(f"Error: {result['error']}")
        
        print("-" * 30) 