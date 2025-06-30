"""
Memory Agent - Stores and retrieves conversation history using vector embeddings
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from memory.vector_store import ConversationVectorStore

logger = logging.getLogger(__name__)

class MemoryAgent:
    """Manages vector-based memory storage and retrieval"""
    
    def __init__(self):
        self.vector_store = ConversationVectorStore()
    
    def store_conversation(self, session_id: str, user_message: str, 
                          agent_response: str, agent_type: str,
                          metadata: Dict[str, Any] = None) -> bool:
        """Store conversation in vector memory"""
        try:
            doc_id = self.vector_store.add_conversation(
                session_id=session_id,
                user_message=user_message,
                agent_response=agent_response,
                agent_type=agent_type,
                metadata=metadata
            )
            return doc_id is not None
        except Exception as e:
            logger.error(f"Error storing conversation: {str(e)}")
            return False
    
    def find_similar_conversations(self, query: str, session_id: str = None, 
                                  limit: int = 5) -> List[Dict[str, Any]]:
        """Find conversations similar to the query"""
        try:
            return self.vector_store.search_conversations(
                query=query,
                session_id=session_id,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Error finding similar conversations: {str(e)}")
            return []
    
    def get_conversation_context(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation context for a session"""
        try:
            return self.vector_store.get_conversation_context(session_id, limit)
        except Exception as e:
            logger.error(f"Error getting conversation context: {str(e)}")
            return []
    
    def clear_session_memory(self, session_id: str):
        """Clear all memory for a specific session"""
        try:
            self.vector_store.clear_session(session_id)
        except Exception as e:
            logger.error(f"Error clearing session memory: {str(e)}")
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory storage statistics"""
        try:
            return self.vector_store.get_statistics()
        except Exception as e:
            logger.error(f"Error getting memory statistics: {str(e)}")
            return {"error": str(e)} 