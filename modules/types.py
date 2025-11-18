"""
Type definitions for the grading agent system.

This module provides enhanced type safety using:
- Protocol for agent interfaces
- Literal for constrained string values
- TypedDict for structured data
- Generic types for better IDE support

Usage:
    from modules.types import AgentProtocol, EventType, StreamEvent
"""
from typing import Protocol, Literal, TypedDict, AsyncGenerator, Optional, Dict, Any, List
from typing_extensions import NotRequired


# ========== Literal Types ==========

# Event types for streaming
EventType = Literal['status', 'chunk', 'complete', 'error']

# Agent types
AgentType = Literal['chat', 'grading', 'analysis', 'formatting', 'master']

# Stream status
StreamStatus = Literal['pending', 'streaming', 'complete', 'error']

# Workflow types
WorkflowType = Literal['standard_workflow', 'grading_workflow']


# ========== TypedDict Definitions ==========

class StreamEvent(TypedDict):
    """Type-safe streaming event structure."""
    type: EventType
    content: str
    agent: NotRequired[str]  # Optional field


class AgentMetadata(TypedDict):
    """Agent metadata structure."""
    name: str
    type: AgentType
    temperature: float
    capabilities: List[str]


class StreamingMetrics(TypedDict):
    """Streaming performance metrics."""
    duration: float
    chunk_count: int
    total_chars: int
    chars_per_sec: float
    total_agents: int
    completed_agents: int


class StreamInfo(TypedDict):
    """Stream information structure."""
    stream_id: str
    agent_name: str
    status: StreamStatus
    chunk_count: int
    start_time: float
    end_time: NotRequired[float]
    error: NotRequired[str]


# ========== Protocol Definitions ==========

class AgentProtocol(Protocol):
    """
    Protocol defining the interface that all agents must implement.
    
    This provides type checking without requiring inheritance.
    """
    
    def process(self, user_input: str) -> str:
        """
        Process a user request and return a response.
        
        Args:
            user_input: The user's request
            
        Returns:
            The agent's response
        """
        ...
    
    async def stream_process(
        self, 
        user_input: str,
        conversation_history: Optional[Any] = None
    ) -> AsyncGenerator[str, None]:
        """
        Process a request with streaming output.
        
        Args:
            user_input: The user's request
            conversation_history: Optional conversation history
            
        Yields:
            Content chunks as they are generated
        """
        ...
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get agent capabilities and metadata.
        
        Returns:
            Dictionary describing agent capabilities
        """
        ...
    
    def get_status(self) -> str:
        """
        Get current agent status.
        
        Returns:
            Status string (e.g., 'active', 'busy', 'error')
        """
        ...


class StreamingManagerProtocol(Protocol):
    """Protocol for streaming manager implementations."""
    
    def create_stream(self, agent_name: str) -> str:
        """Create a new stream and return its ID."""
        ...
    
    def add_chunk(self, stream_id: str, chunk: str) -> None:
        """Add a chunk to an active stream."""
        ...
    
    def complete_stream(self, stream_id: str) -> StreamInfo:
        """Mark a stream as complete and return summary."""
        ...
    
    def get_stream_status(self, stream_id: str) -> StreamInfo:
        """Get current stream status."""
        ...
    
    def cleanup_stream(self, stream_id: str) -> None:
        """Clean up stream resources."""
        ...


class ChunkBufferProtocol(Protocol):
    """Protocol for chunk buffer implementations."""
    
    def add_chunk(self, chunk: str) -> None:
        """Add a chunk to the buffer."""
        ...
    
    def get_full_content(self) -> str:
        """Get all buffered content as a single string."""
        ...
    
    def get_last_n_chunks(self, n: int) -> List[str]:
        """Get the last N chunks."""
        ...
    
    def clear(self) -> None:
        """Clear all buffered content."""
        ...
    
    def get_stats(self) -> Dict[str, int]:
        """Get buffer statistics."""
        ...


class ConversationHistoryProtocol(Protocol):
    """Protocol for conversation history implementations."""
    
    def add_user_message(self, content: str) -> None:
        """Add a user message to history."""
        ...
    
    def add_assistant_message(
        self, 
        content: str, 
        agent_type: str = "master",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add an assistant message to history."""
        ...
    
    def get_messages_for_llm(self, include_system: bool = True) -> List[Dict[str, str]]:
        """Get messages formatted for LLM consumption."""
        ...
    
    def start_streaming_message(
        self, 
        agent_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Start a new streaming message."""
        ...
    
    def add_streaming_chunk(self, chunk: str) -> None:
        """Add a chunk to the streaming message."""
        ...
    
    def finalize_streaming_message(self) -> None:
        """Finalize and save the streaming message."""
        ...
    
    def is_streaming(self) -> bool:
        """Check if currently streaming."""
        ...


# ========== Type Aliases ==========

# Common type aliases for better readability
MessageList = List[Dict[str, str]]
AgentResponses = Dict[str, str]
DataContext = Dict[str, Any]
StateDict = Dict[str, Any]


# ========== Type Guards ==========

def is_stream_event(obj: Any) -> bool:
    """
    Type guard to check if an object is a valid StreamEvent.
    
    Args:
        obj: Object to check
        
    Returns:
        True if object matches StreamEvent structure
    """
    if not isinstance(obj, dict):
        return False
    
    if 'type' not in obj or 'content' not in obj:
        return False
    
    if obj['type'] not in ('status', 'chunk', 'complete', 'error'):
        return False
    
    return True


def is_agent(obj: Any) -> bool:
    """
    Type guard to check if an object implements AgentProtocol.
    
    Args:
        obj: Object to check
        
    Returns:
        True if object has required agent methods
    """
    required_methods = ['process', 'stream_process', 'get_capabilities', 'get_status']
    return all(hasattr(obj, method) for method in required_methods)


# ========== Validation Functions ==========

def validate_event_type(event_type: str) -> EventType:
    """
    Validate and return an event type.
    
    Args:
        event_type: Event type string to validate
        
    Returns:
        Validated EventType
        
    Raises:
        ValueError: If event_type is invalid
    """
    valid_types: tuple[EventType, ...] = ('status', 'chunk', 'complete', 'error')
    
    if event_type not in valid_types:
        raise ValueError(
            f"Invalid event type: {event_type}. "
            f"Must be one of: {', '.join(valid_types)}"
        )
    
    return event_type  # type: ignore


def validate_agent_type(agent_type: str) -> AgentType:
    """
    Validate and return an agent type.
    
    Args:
        agent_type: Agent type string to validate
        
    Returns:
        Validated AgentType
        
    Raises:
        ValueError: If agent_type is invalid
    """
    valid_types: tuple[AgentType, ...] = ('chat', 'grading', 'analysis', 'formatting', 'master')
    
    if agent_type not in valid_types:
        raise ValueError(
            f"Invalid agent type: {agent_type}. "
            f"Must be one of: {', '.join(valid_types)}"
        )
    
    return agent_type  # type: ignore


# ========== Exports ==========

__all__ = [
    # Literal types
    'EventType',
    'AgentType',
    'StreamStatus',
    'WorkflowType',
    # TypedDict
    'StreamEvent',
    'AgentMetadata',
    'StreamingMetrics',
    'StreamInfo',
    # Protocols
    'AgentProtocol',
    'StreamingManagerProtocol',
    'ChunkBufferProtocol',
    'ConversationHistoryProtocol',
    # Type aliases
    'MessageList',
    'AgentResponses',
    'DataContext',
    'StateDict',
    # Type guards
    'is_stream_event',
    'is_agent',
    # Validation
    'validate_event_type',
    'validate_agent_type',
]
