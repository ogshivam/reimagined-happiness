"""
Vector store for conversation memory and semantic search
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import logging
from pathlib import Path
import json
import hashlib
from datetime import datetime

from config.settings import settings

logger = logging.getLogger(__name__)

class ConversationVectorStore:
    """Vector store for managing conversation embeddings and semantic search"""
    
    def __init__(self, persist_directory: str = None):
        self.persist_directory = persist_directory or settings.vector_db_path
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(settings.embedding_model)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Create collections
        self.conversations_collection = self._get_or_create_collection("conversations")
        self.queries_collection = self._get_or_create_collection("sql_queries")
        self.insights_collection = self._get_or_create_collection("insights")
        
    def _get_or_create_collection(self, name: str):
        """Get or create a ChromaDB collection"""
        try:
            return self.client.get_collection(name)
        except:
            return self.client.create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
    
    def _generate_id(self, text: str, timestamp: str = None) -> str:
        """Generate unique ID for a document"""
        content = f"{text}_{timestamp or datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def add_conversation(self, session_id: str, user_message: str, 
                        agent_response: str, agent_type: str,
                        metadata: Dict[str, Any] = None) -> str:
        """Add conversation to vector store"""
        try:
            # Combine user message and agent response for embedding
            combined_text = f"User: {user_message}\nAgent ({agent_type}): {agent_response}"
            
            # Generate embedding
            embedding = self.embedding_model.encode(combined_text).tolist()
            
            # Create document ID
            doc_id = self._generate_id(combined_text)
            
            # Prepare metadata
            doc_metadata = {
                "session_id": session_id,
                "user_message": user_message,
                "agent_response": agent_response,
                "agent_type": agent_type,
                "timestamp": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            # Add to collection
            self.conversations_collection.add(
                embeddings=[embedding],
                documents=[combined_text],
                metadatas=[doc_metadata],
                ids=[doc_id]
            )
            
            logger.info(f"Added conversation to vector store: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error adding conversation to vector store: {str(e)}")
            return None
    
    def add_sql_query(self, query: str, description: str, 
                     results_summary: str, metadata: Dict[str, Any] = None) -> str:
        """Add SQL query and results to vector store"""
        try:
            # Combine query, description, and results for embedding
            combined_text = f"Query: {query}\nDescription: {description}\nResults: {results_summary}"
            
            # Generate embedding
            embedding = self.embedding_model.encode(combined_text).tolist()
            
            # Create document ID
            doc_id = self._generate_id(combined_text)
            
            # Prepare metadata
            doc_metadata = {
                "query": query,
                "description": description,
                "results_summary": results_summary,
                "timestamp": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            # Add to collection
            self.queries_collection.add(
                embeddings=[embedding],
                documents=[combined_text],
                metadatas=[doc_metadata],
                ids=[doc_id]
            )
            
            logger.info(f"Added SQL query to vector store: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error adding SQL query to vector store: {str(e)}")
            return None
    
    def add_insight(self, insight_text: str, insight_type: str,
                   data_context: str, metadata: Dict[str, Any] = None) -> str:
        """Add data insight to vector store"""
        try:
            # Combine insight with context for embedding
            combined_text = f"Insight ({insight_type}): {insight_text}\nContext: {data_context}"
            
            # Generate embedding
            embedding = self.embedding_model.encode(combined_text).tolist()
            
            # Create document ID
            doc_id = self._generate_id(combined_text)
            
            # Prepare metadata
            doc_metadata = {
                "insight_text": insight_text,
                "insight_type": insight_type,
                "data_context": data_context,
                "timestamp": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            # Add to collection
            self.insights_collection.add(
                embeddings=[embedding],
                documents=[combined_text],
                metadatas=[doc_metadata],
                ids=[doc_id]
            )
            
            logger.info(f"Added insight to vector store: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error adding insight to vector store: {str(e)}")
            return None
    
    def search_conversations(self, query: str, session_id: str = None, 
                           limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar conversations"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Prepare where clause
            where_clause = {}
            if session_id:
                where_clause["session_id"] = session_id
            
            # Search
            results = self.conversations_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause if where_clause else None
            )
            
            # Format results
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    formatted_results.append({
                        "id": results["ids"][0][i],
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i] if "distances" in results else None
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching conversations: {str(e)}")
            return []
    
    def search_sql_queries(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar SQL queries"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search
            results = self.queries_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
            )
            
            # Format results
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    formatted_results.append({
                        "id": results["ids"][0][i],
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i] if "distances" in results else None
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching SQL queries: {str(e)}")
            return []
    
    def search_insights(self, query: str, insight_type: str = None, 
                       limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar insights"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Prepare where clause
            where_clause = {}
            if insight_type:
                where_clause["insight_type"] = insight_type
            
            # Search
            results = self.insights_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause if where_clause else None
            )
            
            # Format results
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    formatted_results.append({
                        "id": results["ids"][0][i],
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i] if "distances" in results else None
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching insights: {str(e)}")
            return []
    
    def get_conversation_context(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation context for a session"""
        try:
            results = self.conversations_collection.get(
                where={"session_id": session_id},
                limit=limit
            )
            
            # Format and sort by timestamp
            formatted_results = []
            if results["documents"]:
                for i in range(len(results["documents"])):
                    formatted_results.append({
                        "id": results["ids"][i],
                        "document": results["documents"][i],
                        "metadata": results["metadatas"][i]
                    })
                
                # Sort by timestamp (most recent first)
                formatted_results.sort(
                    key=lambda x: x["metadata"].get("timestamp", ""),
                    reverse=True
                )
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error getting conversation context: {str(e)}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            stats = {
                "conversations_count": self.conversations_collection.count(),
                "queries_count": self.queries_collection.count(),
                "insights_count": self.insights_collection.count(),
                "embedding_model": settings.embedding_model,
                "persist_directory": self.persist_directory
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {"error": str(e)}
    
    def clear_session(self, session_id: str):
        """Clear all data for a specific session"""
        try:
            # Get all documents for the session
            results = self.conversations_collection.get(
                where={"session_id": session_id}
            )
            
            if results["ids"]:
                self.conversations_collection.delete(ids=results["ids"])
                logger.info(f"Cleared {len(results['ids'])} conversations for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error clearing session: {str(e)}")

# Global vector store instance
vector_store = ConversationVectorStore() 