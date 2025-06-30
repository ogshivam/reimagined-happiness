"""
Enhanced Context Manager
=======================

This module provides advanced context management capabilities including:
- Extended memory retention (5 exchanges, 500 char answers)
- Metadata extraction and storage
- Smart context compression
- Token usage monitoring
- Key findings preservation

Key Features:
- 5x larger context window
- Structured metadata storage
- Intelligent compression algorithms
- Performance monitoring
- Backward compatibility
"""

import json
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class ExchangeType(Enum):
    """Type of conversation exchange"""
    QUERY = "query"
    FOLLOWUP = "followup"
    CLARIFICATION = "clarification"
    ANALYSIS = "analysis"


@dataclass
class ExchangeMetadata:
    """Metadata for a conversation exchange"""
    timestamp: str
    exchange_type: ExchangeType
    query_length: int
    response_length: int
    sql_query: Optional[str] = None
    visualization_type: Optional[str] = None
    key_metrics: List[str] = None
    entities_mentioned: List[str] = None
    intent: Optional[str] = None
    confidence: float = 0.0
    
    def __post_init__(self):
        if self.key_metrics is None:
            self.key_metrics = []
        if self.entities_mentioned is None:
            self.entities_mentioned = []


@dataclass
class ConversationExchange:
    """Enhanced conversation exchange with metadata"""
    user_message: str
    assistant_response: str
    metadata: ExchangeMetadata
    exchange_id: str
    compressed_response: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'user_message': self.user_message,
            'assistant_response': self.assistant_response,
            'metadata': asdict(self.metadata),
            'exchange_id': self.exchange_id,
            'compressed_response': self.compressed_response
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConversationExchange':
        """Create from dictionary"""
        metadata_dict = data['metadata']
        metadata = ExchangeMetadata(
            timestamp=metadata_dict['timestamp'],
            exchange_type=ExchangeType(metadata_dict['exchange_type']),
            query_length=metadata_dict['query_length'],
            response_length=metadata_dict['response_length'],
            sql_query=metadata_dict.get('sql_query'),
            visualization_type=metadata_dict.get('visualization_type'),
            key_metrics=metadata_dict.get('key_metrics', []),
            entities_mentioned=metadata_dict.get('entities_mentioned', []),
            intent=metadata_dict.get('intent'),
            confidence=metadata_dict.get('confidence', 0.0)
        )
        
        return cls(
            user_message=data['user_message'],
            assistant_response=data['assistant_response'],
            metadata=metadata,
            exchange_id=data['exchange_id'],
            compressed_response=data.get('compressed_response')
        )


class EnhancedContextManager:
    """Advanced context management with extended memory and compression"""
    
    def __init__(self, 
                 max_exchanges: int = 5,
                 max_response_chars: int = 500,
                 compression_threshold: int = 2000):
        """
        Initialize enhanced context manager
        
        Args:
            max_exchanges: Maximum number of exchanges to keep
            max_response_chars: Maximum characters per response
            compression_threshold: Token threshold for compression
        """
        self.max_exchanges = max_exchanges
        self.max_response_chars = max_response_chars
        self.compression_threshold = compression_threshold
        
        self.conversation_history: List[ConversationExchange] = []
        self.session_metadata = {
            'session_id': self._generate_session_id(),
            'start_time': datetime.now().isoformat(),
            'total_exchanges': 0,
            'total_tokens_estimated': 0,
            'compression_events': 0
        }
    
    def add_exchange(self,
                    user_message: str,
                    assistant_response: str,
                    exchange_type: ExchangeType = ExchangeType.QUERY,
                    sql_query: Optional[str] = None,
                    visualization_type: Optional[str] = None,
                    intent: Optional[str] = None,
                    confidence: float = 0.0) -> str:
        """
        Add a new exchange to conversation history
        
        Args:
            user_message: User's message
            assistant_response: Assistant's response
            exchange_type: Type of exchange
            sql_query: SQL query if applicable
            visualization_type: Type of visualization if created
            intent: Detected intent
            confidence: Confidence score
            
        Returns:
            Exchange ID
        """
        # Extract metadata
        metadata = self._extract_metadata(
            user_message, assistant_response, exchange_type,
            sql_query, visualization_type, intent, confidence
        )
        
        # Create exchange
        exchange_id = self._generate_exchange_id(user_message)
        exchange = ConversationExchange(
            user_message=user_message,
            assistant_response=assistant_response[:self.max_response_chars],
            metadata=metadata,
            exchange_id=exchange_id
        )
        
        # Add to history
        self.conversation_history.append(exchange)
        
        # Update session metadata
        self.session_metadata['total_exchanges'] += 1
        self.session_metadata['total_tokens_estimated'] += self._estimate_tokens(
            user_message + assistant_response
        )
        
        # Check if compression is needed
        if self._should_compress():
            self._compress_history()
        
        # Maintain max history size
        if len(self.conversation_history) > self.max_exchanges:
            self.conversation_history = self.conversation_history[-self.max_exchanges:]
        
        return exchange_id
    
    def get_context_for_query(self, 
                             current_query: str,
                             context_window: int = 3,
                             include_metadata: bool = True) -> str:
        """
        Get formatted context for query enhancement
        
        Args:
            current_query: Current user query
            context_window: Number of recent exchanges to include
            include_metadata: Whether to include metadata in context
            
        Returns:
            Formatted context string
        """
        if not self.conversation_history:
            return ""
        
        # Get recent exchanges
        recent_exchanges = self.conversation_history[-context_window:]
        
        context_parts = []
        
        # Add conversation history
        for i, exchange in enumerate(recent_exchanges, 1):
            context_parts.append(f"Previous Exchange {i}:")
            context_parts.append(f"User: {exchange.user_message}")
            
            # Use compressed response if available and shorter
            response = exchange.compressed_response or exchange.assistant_response
            context_parts.append(f"Assistant: {response}")
            
            # Add metadata if requested
            if include_metadata and exchange.metadata:
                metadata_info = []
                if exchange.metadata.sql_query:
                    metadata_info.append(f"SQL: {exchange.metadata.sql_query}")
                if exchange.metadata.key_metrics:
                    metadata_info.append(f"Key Metrics: {', '.join(exchange.metadata.key_metrics)}")
                if exchange.metadata.visualization_type:
                    metadata_info.append(f"Visualization: {exchange.metadata.visualization_type}")
                
                if metadata_info:
                    context_parts.append(f"Context: {' | '.join(metadata_info)}")
            
            context_parts.append("")  # Empty line for separation
        
        # Add current query context
        context_parts.append(f"Current Query: {current_query}")
        
        return "\n".join(context_parts)
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of conversation for analytics"""
        if not self.conversation_history:
            return {}
        
        # Extract key information
        query_types = [ex.metadata.exchange_type.value for ex in self.conversation_history]
        intents = [ex.metadata.intent for ex in self.conversation_history if ex.metadata.intent]
        sql_queries = [ex.metadata.sql_query for ex in self.conversation_history if ex.metadata.sql_query]
        visualizations = [ex.metadata.visualization_type for ex in self.conversation_history if ex.metadata.visualization_type]
        
        # Get all key metrics
        all_metrics = []
        for ex in self.conversation_history:
            all_metrics.extend(ex.metadata.key_metrics)
        
        # Get all entities
        all_entities = []
        for ex in self.conversation_history:
            all_entities.extend(ex.metadata.entities_mentioned)
        
        return {
            'session_info': self.session_metadata,
            'total_exchanges': len(self.conversation_history),
            'query_types': list(set(query_types)),
            'intents': list(set(intents)),
            'sql_queries_count': len(sql_queries),
            'visualizations_created': list(set(visualizations)),
            'key_metrics': list(set(all_metrics)),
            'entities_mentioned': list(set(all_entities)),
            'avg_confidence': sum(ex.metadata.confidence for ex in self.conversation_history) / len(self.conversation_history),
            'compression_ratio': self.session_metadata['compression_events'] / max(1, len(self.conversation_history))
        }
    
    def _extract_metadata(self,
                         user_message: str,
                         assistant_response: str,
                         exchange_type: ExchangeType,
                         sql_query: Optional[str],
                         visualization_type: Optional[str],
                         intent: Optional[str],
                         confidence: float) -> ExchangeMetadata:
        """Extract metadata from exchange"""
        
        # Extract key metrics from response
        key_metrics = self._extract_key_metrics(assistant_response)
        
        # Extract entities mentioned
        entities = self._extract_entities(user_message, assistant_response)
        
        return ExchangeMetadata(
            timestamp=datetime.now().isoformat(),
            exchange_type=exchange_type,
            query_length=len(user_message),
            response_length=len(assistant_response),
            sql_query=sql_query,
            visualization_type=visualization_type,
            key_metrics=key_metrics,
            entities_mentioned=entities,
            intent=intent,
            confidence=confidence
        )
    
    def _extract_key_metrics(self, response: str) -> List[str]:
        """Extract key metrics and numbers from response"""
        import re
        
        metrics = []
        
        # Look for number patterns
        number_patterns = [
            r'\b\d+%\b',  # Percentages
            r'\$\d+(?:,\d{3})*(?:\.\d{2})?\b',  # Currency
            r'\b\d+(?:,\d{3})*\b',  # Large numbers
            r'\b\d+\.\d+\b'  # Decimals
        ]
        
        for pattern in number_patterns:
            matches = re.findall(pattern, response)
            metrics.extend(matches)
        
        # Look for common metric keywords
        metric_keywords = [
            'total', 'average', 'maximum', 'minimum', 'count', 'sum',
            'revenue', 'sales', 'profit', 'loss', 'growth', 'increase', 'decrease'
        ]
        
        words = response.lower().split()
        for word in words:
            if word in metric_keywords:
                metrics.append(word)
        
        return list(set(metrics))[:10]  # Limit to 10 metrics
    
    def _extract_entities(self, user_message: str, assistant_response: str) -> List[str]:
        """Extract entities (proper nouns) from messages"""
        import re
        
        entities = []
        
        # Simple approach: find capitalized words that might be entities
        text = user_message + " " + assistant_response
        
        # Find potential entities (capitalized words)
        potential_entities = re.findall(r'\b[A-Z][a-z]+\b', text)
        
        # Filter out common words
        common_words = {
            'The', 'This', 'That', 'These', 'Those', 'What', 'Where', 'When', 
            'How', 'Why', 'SQL', 'SELECT', 'FROM', 'WHERE', 'GROUP', 'ORDER'
        }
        
        for entity in potential_entities:
            if entity not in common_words and len(entity) > 2:
                entities.append(entity)
        
        return list(set(entities))[:10]  # Limit to 10 entities
    
    def _should_compress(self) -> bool:
        """Check if compression is needed"""
        estimated_tokens = self.session_metadata['total_tokens_estimated']
        return estimated_tokens > self.compression_threshold
    
    def _compress_history(self):
        """Compress older exchanges to save space"""
        if len(self.conversation_history) <= 2:
            return
        
        # Compress all but the last 2 exchanges
        for i in range(len(self.conversation_history) - 2):
            exchange = self.conversation_history[i]
            
            if not exchange.compressed_response:
                # Create compressed version
                exchange.compressed_response = self._compress_response(
                    exchange.assistant_response
                )
                
                # Update token estimate
                original_tokens = self._estimate_tokens(exchange.assistant_response)
                compressed_tokens = self._estimate_tokens(exchange.compressed_response)
                
                self.session_metadata['total_tokens_estimated'] -= (original_tokens - compressed_tokens)
                self.session_metadata['compression_events'] += 1
    
    def _compress_response(self, response: str) -> str:
        """Compress a response while preserving key information"""
        # Simple compression: keep first and last sentences, add key metrics
        sentences = response.split('.')
        
        if len(sentences) <= 2:
            return response
        
        # Keep first sentence
        compressed = sentences[0] + '.'
        
        # Add key information from middle
        middle_text = ' '.join(sentences[1:-1])
        key_info = self._extract_key_info(middle_text)
        
        if key_info:
            compressed += f" Key findings: {key_info}."
        
        # Keep last sentence if meaningful
        if sentences[-1].strip():
            compressed += ' ' + sentences[-1]
        
        return compressed[:200]  # Hard limit
    
    def _extract_key_info(self, text: str) -> str:
        """Extract key information from text"""
        # Look for numbers, percentages, and important keywords
        import re
        
        key_elements = []
        
        # Find numbers and percentages
        numbers = re.findall(r'\d+(?:\.\d+)?%?', text)
        key_elements.extend(numbers[:3])  # Top 3 numbers
        
        # Find important keywords
        important_words = ['increased', 'decreased', 'highest', 'lowest', 'total', 'average']
        words = text.lower().split()
        
        for word in important_words:
            if word in words:
                key_elements.append(word)
        
        return ', '.join(key_elements[:5])  # Top 5 elements
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        # Simple estimation: ~4 characters per token
        return len(text) // 4
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return hashlib.md5(
            f"{datetime.now().isoformat()}_{id(self)}".encode()
        ).hexdigest()[:8]
    
    def _generate_exchange_id(self, user_message: str) -> str:
        """Generate unique exchange ID"""
        return hashlib.md5(
            f"{user_message}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:8]
    
    def export_conversation(self) -> Dict:
        """Export conversation history for persistence"""
        return {
            'session_metadata': self.session_metadata,
            'conversation_history': [ex.to_dict() for ex in self.conversation_history]
        }
    
    def import_conversation(self, data: Dict):
        """Import conversation history from persistence"""
        self.session_metadata = data.get('session_metadata', self.session_metadata)
        
        conversation_data = data.get('conversation_history', [])
        self.conversation_history = [
            ConversationExchange.from_dict(ex_data) 
            for ex_data in conversation_data
        ]


def create_enhanced_context_manager(max_exchanges: int = 5,
                                  max_response_chars: int = 500) -> EnhancedContextManager:
    """Factory function to create enhanced context manager"""
    return EnhancedContextManager(
        max_exchanges=max_exchanges,
        max_response_chars=max_response_chars
    )


# Example usage and testing
if __name__ == "__main__":
    # Test the enhanced context manager
    context_manager = create_enhanced_context_manager()
    
    print("🧪 Testing Enhanced Context Manager\n")
    
    # Add some test exchanges
    test_exchanges = [
        ("Show me top artists by sales", "Here are the top artists: 1. AC/DC (1000 sales), 2. Beatles (900 sales), 3. Led Zeppelin (800 sales). Total revenue: $50,000.", ExchangeType.QUERY),
        ("Tell me more about AC/DC", "AC/DC is a legendary rock band formed in 1973. They have sold over 200 million records worldwide, making them one of the best-selling music artists of all time.", ExchangeType.FOLLOWUP),
        ("What about their album sales?", "AC/DC's highest-selling album is 'Back in Black' with 50 million copies sold. Their total album sales increased by 15% last year.", ExchangeType.FOLLOWUP),
        ("Can you make a chart of this?", "I'll create a bar chart showing artist sales. The chart displays sales data with AC/DC leading at 1000 units, followed by Beatles at 900 units.", ExchangeType.ANALYSIS),
        ("How does this compare to industry average?", "The top artists perform 300% above industry average. Industry average is 250 sales per artist, while our top 3 average 900 sales.", ExchangeType.ANALYSIS)
    ]
    
    # Add exchanges
    for user_msg, assistant_msg, ex_type in test_exchanges:
        exchange_id = context_manager.add_exchange(
            user_message=user_msg,
            assistant_response=assistant_msg,
            exchange_type=ex_type,
            sql_query="SELECT * FROM artists ORDER BY sales DESC",
            visualization_type="bar_chart" if "chart" in user_msg.lower() else None,
            intent="followup" if ex_type == ExchangeType.FOLLOWUP else "query",
            confidence=0.8
        )
        print(f"✅ Added exchange: {exchange_id}")
    
    # Test context generation
    print(f"\n📝 Context for new query:")
    context = context_manager.get_context_for_query("What are the latest trends?")
    print(context[:500] + "..." if len(context) > 500 else context)
    
    # Test conversation summary
    print(f"\n📊 Conversation Summary:")
    summary = context_manager.get_conversation_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Test export/import
    print(f"\n💾 Export/Import Test:")
    exported = context_manager.export_conversation()
    print(f"  Exported {len(exported['conversation_history'])} exchanges")
    
    # Create new manager and import
    new_manager = create_enhanced_context_manager()
    new_manager.import_conversation(exported)
    print(f"  Imported {len(new_manager.conversation_history)} exchanges")
    
    print(f"\n🎉 Enhanced Context Manager Test Complete!") 