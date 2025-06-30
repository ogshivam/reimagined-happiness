#!/usr/bin/env python3
"""
Intelligent Context Manager
===========================

Advanced conversation context management using:
- Semantic similarity for context relevance
- Intelligent state tracking
- Memory attention mechanisms
- Adaptive context compression
- Multi-turn conversation understanding

This is much closer to how ChatGPT manages conversation context.
"""

import numpy as np
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import re

# Import semantic capabilities if available
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False


class ContextRelevance(Enum):
    """Context relevance levels"""
    CRITICAL = "critical"      # Essential for understanding
    HIGH = "high"             # Very relevant  
    MEDIUM = "medium"         # Somewhat relevant
    LOW = "low"              # Minimally relevant
    IRRELEVANT = "irrelevant" # Can be discarded


@dataclass
class IntelligentExchange:
    """Enhanced conversation exchange with intelligence"""
    exchange_id: str
    user_message: str
    assistant_response: str
    timestamp: str
    
    # Semantic features
    embedding: Optional[np.ndarray] = None
    topics: List[str] = None
    entities: List[str] = None  
    metrics: List[str] = None
    intent: str = "unknown"
    
    # Context features
    relevance_score: float = 0.5
    importance_weight: float = 0.5
    access_count: int = 0
    last_accessed: Optional[str] = None
    
    # Relationship features
    references: List[str] = None  # IDs of referenced exchanges
    referenced_by: List[str] = None  # IDs that reference this
    
    def __post_init__(self):
        if self.topics is None:
            self.topics = []
        if self.entities is None:
            self.entities = []
        if self.metrics is None:
            self.metrics = []
        if self.references is None:
            self.references = []
        if self.referenced_by is None:
            self.referenced_by = []


class ConversationGraph:
    """Graph-based conversation structure for intelligent navigation"""
    
    def __init__(self):
        self.nodes: Dict[str, IntelligentExchange] = {}
        self.edges: Dict[str, List[str]] = {}  # exchange_id -> list of connected exchanges
    
    def add_exchange(self, exchange: IntelligentExchange):
        """Add exchange to conversation graph"""
        self.nodes[exchange.exchange_id] = exchange
        self.edges[exchange.exchange_id] = []
    
    def connect_exchanges(self, from_id: str, to_id: str, weight: float = 1.0):
        """Create semantic connection between exchanges"""
        if from_id in self.edges:
            self.edges[from_id].append(to_id)
        if to_id in self.nodes:
            self.nodes[to_id].referenced_by.append(from_id)
    
    def get_connected_context(self, exchange_id: str, max_depth: int = 2) -> List[IntelligentExchange]:
        """Get semantically connected context using graph traversal"""
        visited = set()
        context = []
        
        def dfs(current_id: str, depth: int):
            if depth > max_depth or current_id in visited:
                return
            
            visited.add(current_id)
            if current_id in self.nodes:
                context.append(self.nodes[current_id])
            
            # Traverse connections
            for connected_id in self.edges.get(current_id, []):
                dfs(connected_id, depth + 1)
        
        dfs(exchange_id, 0)
        return context


class IntelligentContextManager:
    """Advanced context manager with semantic understanding"""
    
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2",
                 max_context_length: int = 8,
                 compression_threshold: int = 3000):
        """Initialize intelligent context manager"""
        
        self.model_name = model_name
        self.model = None
        self.max_context_length = max_context_length
        self.compression_threshold = compression_threshold
        
        # Core data structures
        self.conversation_graph = ConversationGraph()
        self.working_memory: List[str] = []  # Exchange IDs in working memory
        self.compressed_summaries: Dict[str, str] = {}
        
        # Intelligence features
        self.topic_tracking: Dict[str, List[str]] = {}  # topic -> exchange_ids
        self.entity_tracking: Dict[str, List[str]] = {}  # entity -> exchange_ids
        self.conversation_flow: List[Tuple[str, str]] = []  # (exchange_id, flow_type)
        
        # Load semantic model
        if SEMANTIC_AVAILABLE:
            try:
                print("🧠 Loading intelligent context model...")
                self.model = SentenceTransformer(model_name)
                print("✅ Intelligent context model loaded")
            except Exception as e:
                print(f"⚠️  Failed to load semantic model: {e}")
                self.model = None
        
        # Session metadata
        self.session_start = datetime.now().isoformat()
        self.total_exchanges = 0
        self.compression_events = 0
    
    def add_exchange(self,
                    user_message: str,
                    assistant_response: str,
                    intent: str = "unknown",
                    importance: float = 0.5) -> str:
        """Add exchange with intelligent analysis"""
        
        # Create exchange ID
        exchange_id = self._generate_exchange_id(user_message)
        
        # Extract intelligence features
        topics = self._extract_topics(user_message, assistant_response)
        entities = self._extract_entities(user_message, assistant_response)
        metrics = self._extract_metrics(assistant_response)
        
        # Create semantic embedding
        embedding = None
        if self.model:
            combined_text = f"{user_message} {assistant_response}"
            embedding = self.model.encode([combined_text])[0]
        
        # Create intelligent exchange
        exchange = IntelligentExchange(
            exchange_id=exchange_id,
            user_message=user_message,
            assistant_response=assistant_response,
            timestamp=datetime.now().isoformat(),
            embedding=embedding,
            topics=topics,
            entities=entities,
            metrics=metrics,
            intent=intent,
            importance_weight=importance
        )
        
        # Add to conversation graph
        self.conversation_graph.add_exchange(exchange)
        
        # Update tracking
        self._update_topic_tracking(exchange_id, topics)
        self._update_entity_tracking(exchange_id, entities)
        
        # Detect references to previous exchanges
        self._detect_and_connect_references(exchange)
        
        # Add to working memory
        self.working_memory.append(exchange_id)
        
        # Manage memory size and compression
        self._manage_memory()
        
        self.total_exchanges += 1
        return exchange_id
    
    def get_intelligent_context(self,
                               current_query: str,
                               max_exchanges: int = 5,
                               include_related: bool = True) -> str:
        """Generate intelligent context using semantic relevance"""
        
        if not self.working_memory:
            return ""
        
        # Get current query embedding for relevance scoring
        query_embedding = None
        if self.model:
            query_embedding = self.model.encode([current_query])[0]
        
        # Score and rank exchanges by relevance
        scored_exchanges = self._score_exchanges_for_relevance(
            current_query, query_embedding
        )
        
        # Select most relevant exchanges
        selected_exchanges = scored_exchanges[:max_exchanges]
        
        # Build context with intelligent formatting
        context_parts = ["📚 Intelligent Conversation Context:"]
        
        for i, (exchange_id, relevance_score) in enumerate(selected_exchanges, 1):
            exchange = self.conversation_graph.nodes[exchange_id]
            
            # Update access tracking
            exchange.access_count += 1
            exchange.last_accessed = datetime.now().isoformat()
            
            # Format exchange with intelligence
            context_parts.append(f"\n{i}. Exchange (Relevance: {relevance_score:.2f})")
            context_parts.append(f"   User: {exchange.user_message}")
            
            # Use compressed summary if available
            response = self.compressed_summaries.get(
                exchange_id, exchange.assistant_response
            )
            context_parts.append(f"   Assistant: {response[:300]}...")
            
            # Add semantic metadata
            if exchange.topics:
                context_parts.append(f"   Topics: {', '.join(exchange.topics[:3])}")
            if exchange.entities:
                context_parts.append(f"   Entities: {', '.join(exchange.entities[:3])}")
            if exchange.metrics:
                context_parts.append(f"   Metrics: {', '.join(exchange.metrics[:3])}")
        
        # Add intelligent instructions
        context_parts.append("\n🤖 Context Intelligence:")
        context_parts.append("- Use this context to understand follow-up questions")
        context_parts.append("- Reference specific previous exchanges when relevant")
        context_parts.append("- Maintain conversation continuity and coherence")
        context_parts.append("- Build upon established topics and entities")
        
        # Add current query
        context_parts.append(f"\n🎯 Current Query: {current_query}")
        
        return "\n".join(context_parts)
    
    def _score_exchanges_for_relevance(self,
                                      current_query: str,
                                      query_embedding: Optional[np.ndarray]) -> List[Tuple[str, float]]:
        """Score exchanges by relevance to current query"""
        
        scored_exchanges = []
        
        for exchange_id in self.working_memory:
            exchange = self.conversation_graph.nodes[exchange_id]
            relevance_score = 0.0
            
            # Semantic similarity (if available)
            if self.model and query_embedding is not None and exchange.embedding is not None:
                semantic_sim = cosine_similarity(
                    [query_embedding], [exchange.embedding]
                )[0][0]
                relevance_score += semantic_sim * 0.4
            
            # Topic overlap
            query_topics = self._extract_topics(current_query, "")
            topic_overlap = len(set(query_topics) & set(exchange.topics))
            relevance_score += (topic_overlap / max(len(query_topics), 1)) * 0.2
            
            # Entity overlap
            query_entities = self._extract_entities(current_query, "")
            entity_overlap = len(set(query_entities) & set(exchange.entities))
            relevance_score += (entity_overlap / max(len(query_entities), 1)) * 0.2
            
            # Recency bonus (recent exchanges are more relevant)
            position = len(self.working_memory) - self.working_memory.index(exchange_id)
            recency_score = position / len(self.working_memory)
            relevance_score += recency_score * 0.1
            
            # Importance weight
            relevance_score += exchange.importance_weight * 0.1
            
            scored_exchanges.append((exchange_id, relevance_score))
        
        # Sort by relevance score (descending)
        scored_exchanges.sort(key=lambda x: x[1], reverse=True)
        return scored_exchanges
    
    def _detect_and_connect_references(self, exchange: IntelligentExchange):
        """Detect semantic references to previous exchanges"""
        
        if not self.model or not exchange.embedding is not None:
            return
        
        # Check similarity to recent exchanges
        for prev_exchange_id in self.working_memory[-5:]:  # Last 5 exchanges
            if prev_exchange_id == exchange.exchange_id:
                continue
            
            prev_exchange = self.conversation_graph.nodes[prev_exchange_id]
            if prev_exchange.embedding is not None:
                similarity = cosine_similarity(
                    [exchange.embedding], [prev_exchange.embedding]
                )[0][0]
                
                # Create connection if high similarity
                if similarity > 0.4:
                    self.conversation_graph.connect_exchanges(
                        exchange.exchange_id, prev_exchange_id, similarity
                    )
                    exchange.references.append(prev_exchange_id)
    
    def _extract_topics(self, user_message: str, assistant_response: str) -> List[str]:
        """Extract main topics from exchange"""
        combined_text = f"{user_message} {assistant_response}".lower()
        
        # Simple topic extraction (can be enhanced with topic models)
        topic_keywords = {
            'sales': ['sales', 'revenue', 'selling', 'sold'],
            'artists': ['artist', 'band', 'musician', 'singer'],
            'customers': ['customer', 'client', 'buyer', 'user'],
            'analysis': ['analyze', 'trend', 'pattern', 'insight'],
            'visualization': ['chart', 'graph', 'plot', 'visual'],
            'comparison': ['compare', 'versus', 'difference', 'contrast']
        }
        
        detected_topics = []
        for topic, keywords in topic_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics
    
    def _extract_entities(self, user_message: str, assistant_response: str) -> List[str]:
        """Extract named entities from exchange"""
        combined_text = f"{user_message} {assistant_response}"
        
        # Extract capitalized words as potential entities
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', combined_text)
        
        # Filter out common words
        common_words = {'The', 'This', 'That', 'SQL', 'SELECT', 'FROM', 'WHERE'}
        entities = [e for e in entities if e not in common_words]
        
        return list(set(entities))[:5]  # Limit to 5 unique entities
    
    def _extract_metrics(self, assistant_response: str) -> List[str]:
        """Extract numerical metrics from response"""
        
        # Extract numbers, percentages, currency
        patterns = [
            r'\b\d+(?:\.\d+)?%\b',           # Percentages
            r'\$\d+(?:,\d{3})*(?:\.\d{2})?\b', # Currency
            r'\b\d+(?:,\d{3})*\b',           # Large numbers
            r'\b\d+\.\d+\b'                   # Decimals
        ]
        
        metrics = []
        for pattern in patterns:
            matches = re.findall(pattern, assistant_response)
            metrics.extend(matches)
        
        return list(set(metrics))[:5]  # Limit to 5 unique metrics
    
    def _update_topic_tracking(self, exchange_id: str, topics: List[str]):
        """Update topic tracking for the exchange"""
        for topic in topics:
            if topic not in self.topic_tracking:
                self.topic_tracking[topic] = []
            self.topic_tracking[topic].append(exchange_id)
    
    def _update_entity_tracking(self, exchange_id: str, entities: List[str]):
        """Update entity tracking for the exchange"""
        for entity in entities:
            if entity not in self.entity_tracking:
                self.entity_tracking[entity] = []
            self.entity_tracking[entity].append(exchange_id)
    
    def _manage_memory(self):
        """Intelligent memory management with compression"""
        
        # Check if compression is needed
        if len(self.working_memory) > self.max_context_length:
            # Compress older exchanges
            self._compress_older_exchanges()
            
            # Remove least relevant exchanges from working memory
            self.working_memory = self.working_memory[-self.max_context_length:]
    
    def _compress_older_exchanges(self):
        """Compress older exchanges to summaries"""
        
        # Compress exchanges that are not in the last 3
        exchanges_to_compress = self.working_memory[:-3]
        
        for exchange_id in exchanges_to_compress:
            if exchange_id not in self.compressed_summaries:
                exchange = self.conversation_graph.nodes[exchange_id]
                
                # Create intelligent summary
                summary = self._create_intelligent_summary(exchange)
                self.compressed_summaries[exchange_id] = summary
                self.compression_events += 1
    
    def _create_intelligent_summary(self, exchange: IntelligentExchange) -> str:
        """Create intelligent summary preserving key information"""
        
        response = exchange.assistant_response
        
        # Extract key sentences (first and last)
        sentences = response.split('.')
        if len(sentences) <= 2:
            return response
        
        summary_parts = [sentences[0]]
        
        # Add key metrics and entities
        if exchange.metrics:
            summary_parts.append(f" Key metrics: {', '.join(exchange.metrics[:3])}")
        
        if exchange.entities:
            summary_parts.append(f" Entities: {', '.join(exchange.entities[:3])}")
        
        # Add last sentence if meaningful
        if sentences[-1].strip():
            summary_parts.append(f" {sentences[-1]}")
        
        return '. '.join(summary_parts)[:200]  # Limit to 200 chars
    
    def _generate_exchange_id(self, user_message: str) -> str:
        """Generate unique exchange ID"""
        import hashlib
        return hashlib.md5(
            f"{user_message}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:8]
    
    def get_conversation_analytics(self) -> Dict[str, Any]:
        """Get intelligent conversation analytics"""
        
        return {
            'session_start': self.session_start,
            'total_exchanges': self.total_exchanges,
            'working_memory_size': len(self.working_memory),
            'compression_events': self.compression_events,
            'unique_topics': list(self.topic_tracking.keys()),
            'unique_entities': list(self.entity_tracking.keys()),
            'conversation_flow_length': len(self.conversation_flow),
            'semantic_capability': 'enabled' if self.model else 'disabled',
            'average_relevance': self._calculate_average_relevance(),
            'memory_efficiency': f"{self.compression_events}/{self.total_exchanges}" if self.total_exchanges > 0 else "0/0"
        }
    
    def _calculate_average_relevance(self) -> float:
        """Calculate average relevance score of exchanges in memory"""
        if not self.working_memory:
            return 0.0
        
        total_relevance = sum(
            self.conversation_graph.nodes[exchange_id].relevance_score 
            for exchange_id in self.working_memory
        )
        
        return total_relevance / len(self.working_memory)


def create_intelligent_context_manager(**kwargs) -> IntelligentContextManager:
    """Factory function to create intelligent context manager"""
    return IntelligentContextManager(**kwargs)


# Example usage and testing
if __name__ == "__main__":
    print("🧠 Testing Intelligent Context Manager")
    print("=" * 60)
    
    # Create manager
    manager = create_intelligent_context_manager()
    
    # Add test exchanges
    exchanges = [
        ("Show me top artists by sales", "The top artists are: 1. AC/DC with 1,000 sales ($50,000), 2. Beatles with 900 sales", "query"),
        ("Tell me more about AC/DC", "AC/DC is a legendary rock band formed in 1973. They have sold over 200 million records worldwide.", "drill_down"),
        ("How do they compare to Beatles?", "AC/DC has 1,000 sales vs Beatles' 900 sales. AC/DC leads by 11.1%. Both are legendary bands.", "comparison"),
        ("Can you make a chart of this?", "I'll create a bar chart showing artist sales. AC/DC: 1,000, Beatles: 900.", "visualization"),
        ("What's the trend over time?", "Sales show consistent growth. AC/DC increased 15% last year, Beatles increased 8%.", "analysis")
    ]
    
    print("Adding exchanges to intelligent context:\n")
    
    for i, (user_msg, assistant_msg, intent) in enumerate(exchanges, 1):
        exchange_id = manager.add_exchange(
            user_message=user_msg,
            assistant_response=assistant_msg,
            intent=intent,
            importance=0.7 + (i * 0.05)  # Increasing importance
        )
        print(f"✅ Exchange {i} added: {exchange_id}")
    
    # Test intelligent context generation
    print(f"\n🧠 Testing Intelligent Context Generation:")
    print("-" * 60)
    
    test_queries = [
        "Show me more details about the sales comparison",
        "What other information do you have about these artists?",
        "Can you create a different type of chart?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        context = manager.get_intelligent_context(query, max_exchanges=3)
        print(f"Context Preview: {context[:200]}...")
    
    # Show analytics
    print(f"\n📊 Conversation Analytics:")
    analytics = manager.get_conversation_analytics()
    for key, value in analytics.items():
        print(f"  {key}: {value}")
    
    print(f"\n🎉 Intelligent Context Manager Test Complete!") 