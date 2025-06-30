"""
Context Agent - Manages conversation memory and context
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from memory.vector_store import ConversationVectorStore
from database.models import ConversationMemory

logger = logging.getLogger(__name__)

class ContextAgent:
    """Manages conversation context and memory"""
    
    def __init__(self):
        self.current_session = None
        self.context_cache = {}
        self.vector_store = ConversationVectorStore()
        self.conversation_memory = ConversationMemory()
    
    def start_session(self, user_id: str = None) -> str:
        """Start a new conversation session"""
        session_id = f"{user_id or 'anonymous'}_{uuid.uuid4().hex[:8]}"
        self.current_session = session_id
        
        # Initialize session context
        self.context_cache[session_id] = {
            "started_at": datetime.now().isoformat(),
            "user_id": user_id,
            "conversation_count": 0,
            "active_tables": [],
            "recent_queries": [],
            "preferences": {}
        }
        
        logger.info(f"Started new session: {session_id}")
        return session_id
    
    def save_conversation_turn(self, session_id: str, user_message: str, 
                              agent_response: str, agent_type: str,
                              metadata: Dict[str, Any] = None) -> bool:
        """Save a conversation turn"""
        try:
            # Save to traditional memory
            self.conversation_memory.save_conversation(
                session_id=session_id,
                user_message=user_message,
                agent_response=agent_response,
                agent_type=agent_type,
                metadata=metadata,
                sql_query=metadata.get("sql_query") if metadata else None,
                results_summary=metadata.get("results_summary") if metadata else None
            )
            
            # Save to vector store for semantic search
            self.vector_store.add_conversation(
                session_id=session_id,
                user_message=user_message,
                agent_response=agent_response,
                agent_type=agent_type,
                metadata=metadata
            )
            
            # Update context cache
            if session_id in self.context_cache:
                self.context_cache[session_id]["conversation_count"] += 1
                
                # Update recent queries if SQL query present
                if metadata and "sql_query" in metadata:
                    recent_queries = self.context_cache[session_id]["recent_queries"]
                    recent_queries.append({
                        "query": metadata["sql_query"],
                        "question": user_message,
                        "timestamp": datetime.now().isoformat()
                    })
                    # Keep only last 5 queries
                    self.context_cache[session_id]["recent_queries"] = recent_queries[-5:]
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving conversation turn: {str(e)}")
            return False
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        try:
            return self.conversation_memory.get_conversation_history(session_id, limit)
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return []
    
    def get_relevant_context(self, session_id: str, current_question: str) -> Dict[str, Any]:
        """Get relevant context for the current question"""
        try:
            context = {
                "session_info": self.context_cache.get(session_id, {}),
                "recent_conversations": [],
                "similar_conversations": [],
                "recent_queries": []
            }
            
            # Get recent conversation history
            recent_history = self.get_conversation_history(session_id, limit=5)
            context["recent_conversations"] = recent_history
            
            # Search for similar conversations
            similar_convs = self.vector_store.search_conversations(
                query=current_question,
                session_id=session_id,
                limit=3
            )
            context["similar_conversations"] = similar_convs
            
            # Get recent SQL queries
            if session_id in self.context_cache:
                context["recent_queries"] = self.context_cache[session_id]["recent_queries"]
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting relevant context: {str(e)}")
            return {}
    
    def update_session_context(self, session_id: str, key: str, value: Any):
        """Update session context information"""
        try:
            if session_id not in self.context_cache:
                self.context_cache[session_id] = {}
            
            self.context_cache[session_id][key] = value
            
            # Also save to persistent storage
            self.conversation_memory.save_context(session_id, key, str(value))
            
        except Exception as e:
            logger.error(f"Error updating session context: {str(e)}")
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get current session context"""
        return self.context_cache.get(session_id, {})
    
    def clear_session(self, session_id: str):
        """Clear session data"""
        try:
            # Clear from cache
            if session_id in self.context_cache:
                del self.context_cache[session_id]
            
            # Clear from vector store
            self.vector_store.clear_session(session_id)
            
            logger.info(f"Cleared session: {session_id}")
            
        except Exception as e:
            logger.error(f"Error clearing session: {str(e)}")
    
    def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session"""
        try:
            context = self.context_cache.get(session_id, {})
            history = self.get_conversation_history(session_id, limit=100)
            
            stats = {
                "session_id": session_id,
                "started_at": context.get("started_at"),
                "conversation_count": len(history),
                "total_queries": len([h for h in history if h.get("sql_query")]),
                "active_tables": context.get("active_tables", []),
                "session_duration": self._calculate_session_duration(context.get("started_at"))
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting session statistics: {str(e)}")
            return {}
    
    def _calculate_session_duration(self, started_at: str) -> Optional[str]:
        """Calculate session duration"""
        try:
            if not started_at:
                return None
            
            start_time = datetime.fromisoformat(started_at)
            duration = datetime.now() - start_time
            
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            
            return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            
        except Exception:
            return None 