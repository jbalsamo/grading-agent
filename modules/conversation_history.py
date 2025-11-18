"""
Conversation History Manager - Manages shared chat history across agents.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import json
import os

logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """Represents a single chat message in the conversation."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime
    agent_type: Optional[str] = None  # Which agent generated this response
    metadata: Optional[Dict[str, Any]] = None

class ConversationHistory:
    """Manages conversation history with a rolling window of messages."""
    
    def __init__(self, max_messages: int = 20, storage_file: str = "data/conversation_history.json"):
        """Initialize conversation history manager.
        
        Args:
            max_messages: Maximum number of messages to keep in history
            storage_file: Path to file for persisting conversation history
        """
        self.max_messages = max_messages
        self.storage_file = storage_file
        self.messages: List[ChatMessage] = []
        
        # Streaming support
        self.streaming_chunks: List[str] = []
        self.streaming_agent: Optional[str] = None
        self.streaming_metadata: Dict[str, Any] = {}
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(storage_file), exist_ok=True)
        
        logger.info(f"ConversationHistory initialized with max_messages={max_messages}, storage_file={storage_file}")
    
    def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation history."""
        message = ChatMessage(
            role="user",
            content=content,
            timestamp=datetime.now()
        )
        self._add_message(message)
        logger.debug(f"Added user message: {content[:50]}...")
    
    def add_assistant_message(self, content: str, agent_type: str = "master", metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add an assistant message to the conversation history.
        
        Args:
            content: The assistant's response
            agent_type: Which agent generated this response
            metadata: Additional metadata about the response
        """
        message = ChatMessage(
            role="assistant",
            content=content,
            timestamp=datetime.now(),
            agent_type=agent_type,
            metadata=metadata or {}
        )
        self._add_message(message)
        logger.debug(f"Added assistant message from {agent_type}: {content[:50]}...")
    
    def add_system_message(self, content: str) -> None:
        """Add a system message to the conversation history."""
        message = ChatMessage(
            role="system",
            content=content,
            timestamp=datetime.now()
        )
        self._add_message(message)
        logger.debug(f"Added system message: {content[:50]}...")
    
    def _add_message(self, message: ChatMessage) -> None:
        """Add a message and maintain the rolling window."""
        self.messages.append(message)
        
        # Maintain rolling window - keep only the last max_messages
        if len(self.messages) > self.max_messages:
            removed_count = len(self.messages) - self.max_messages
            self.messages = self.messages[-self.max_messages:]
            logger.debug(f"Trimmed {removed_count} old messages from history")
    
    def get_messages_for_llm(self, include_system: bool = True) -> List[Dict[str, str]]:
        """Get messages formatted for LLM consumption.
        
        Args:
            include_system: Whether to include system messages
            
        Returns:
            List of message dictionaries with 'role' and 'content' keys
        """
        formatted_messages = []
        
        for message in self.messages:
            if not include_system and message.role == "system":
                continue
                
            formatted_message = {
                "role": message.role,
                "content": message.content
            }
            
            # Add agent context for assistant messages
            if message.role == "assistant" and message.agent_type:
                formatted_message["content"] = f"[{message.agent_type} agent]: {message.content}"
            
            formatted_messages.append(formatted_message)
        
        return formatted_messages
    
    def get_langchain_messages(self):
        """Get messages formatted for LangChain consumption."""
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        
        langchain_messages = []
        
        for message in self.messages:
            content = message.content
            
            # Add agent context for assistant messages
            if message.role == "assistant" and message.agent_type:
                content = f"[{message.agent_type} agent]: {content}"
            
            if message.role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif message.role == "assistant":
                langchain_messages.append(AIMessage(content=content))
            elif message.role == "system":
                langchain_messages.append(SystemMessage(content=content))
        
        return langchain_messages
    
    def get_recent_context(self, num_messages: int = 10) -> str:
        """Get recent conversation context as a formatted string.
        
        Args:
            num_messages: Number of recent messages to include
            
        Returns:
            Formatted conversation context
        """
        recent_messages = self.messages[-num_messages:] if num_messages > 0 else self.messages
        
        if not recent_messages:
            return "No previous conversation context."
        
        context_lines = ["Recent conversation context:"]
        
        for message in recent_messages:
            timestamp_str = message.timestamp.strftime("%H:%M")
            
            if message.role == "user":
                context_lines.append(f"[{timestamp_str}] User: {message.content}")
            elif message.role == "assistant":
                agent_info = f" ({message.agent_type})" if message.agent_type else ""
                context_lines.append(f"[{timestamp_str}] Assistant{agent_info}: {message.content}")
        
        return "\n".join(context_lines)
    
    def clear_history(self) -> None:
        """Clear all conversation history."""
        message_count = len(self.messages)
        self.messages.clear()
        logger.info(f"Cleared {message_count} messages from conversation history")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the conversation history."""
        if not self.messages:
            return {
                "total_messages": 0,
                "user_messages": 0,
                "assistant_messages": 0,
                "system_messages": 0,
                "agent_usage": {},
                "oldest_message": None,
                "newest_message": None
            }
        
        stats = {
            "total_messages": len(self.messages),
            "user_messages": sum(1 for m in self.messages if m.role == "user"),
            "assistant_messages": sum(1 for m in self.messages if m.role == "assistant"),
            "system_messages": sum(1 for m in self.messages if m.role == "system"),
            "agent_usage": {},
            "oldest_message": self.messages[0].timestamp.isoformat(),
            "newest_message": self.messages[-1].timestamp.isoformat()
        }
        
        # Count usage by agent type
        for message in self.messages:
            if message.role == "assistant" and message.agent_type:
                agent_type = message.agent_type
                stats["agent_usage"][agent_type] = stats["agent_usage"].get(agent_type, 0) + 1
        
        return stats
    
    def __len__(self) -> int:
        """Return the number of messages in history."""
        return len(self.messages)
    
    def __str__(self) -> str:
        """String representation of the conversation history."""
        return f"ConversationHistory({len(self.messages)} messages, max={self.max_messages})"
    
    def save_to_disk(self) -> bool:
        """Save conversation history to disk.
        
        Returns:
            True if save was successful, False otherwise
        """
        try:
            # Convert messages to serializable format
            serializable_messages = []
            for message in self.messages:
                msg_dict = {
                    "role": message.role,
                    "content": message.content,
                    "timestamp": message.timestamp.isoformat(),
                    "agent_type": message.agent_type,
                    "metadata": message.metadata
                }
                serializable_messages.append(msg_dict)
            
            # Save to file
            data = {
                "max_messages": self.max_messages,
                "saved_at": datetime.now().isoformat(),
                "messages": serializable_messages
            }
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(self.messages)} messages to {self.storage_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving conversation history: {e}")
            return False
    
    def load_from_disk(self) -> bool:
        """Load conversation history from disk.
        
        Returns:
            True if load was successful, False otherwise
        """
        try:
            if not os.path.exists(self.storage_file):
                logger.info(f"No conversation history file found at {self.storage_file}")
                return False
            
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Clear current messages
            self.messages.clear()
            
            # Restore messages
            for msg_dict in data.get("messages", []):
                message = ChatMessage(
                    role=msg_dict["role"],
                    content=msg_dict["content"],
                    timestamp=datetime.fromisoformat(msg_dict["timestamp"]),
                    agent_type=msg_dict.get("agent_type"),
                    metadata=msg_dict.get("metadata")
                )
                self.messages.append(message)
            
            # Update max_messages if it changed
            if "max_messages" in data:
                self.max_messages = data["max_messages"]
            
            logger.info(f"Loaded {len(self.messages)} messages from {self.storage_file}")
            logger.info(f"Last saved at: {data.get('saved_at', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading conversation history: {e}")
            return False
    
    def delete_saved_history(self) -> bool:
        """Delete the saved conversation history file.
        
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            if os.path.exists(self.storage_file):
                os.remove(self.storage_file)
                logger.info(f"Deleted conversation history file: {self.storage_file}")
                return True
            else:
                logger.info(f"No conversation history file to delete at {self.storage_file}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting conversation history file: {e}")
            return False
    
    # ========== Streaming Support Methods ==========
    
    def start_streaming_message(self, agent_type: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Start a new streaming message.
        
        Args:
            agent_type: The agent that will stream the message
            metadata: Optional metadata for the streaming message
        """
        self.streaming_chunks = []
        self.streaming_agent = agent_type
        self.streaming_metadata = metadata or {}
        logger.debug(f"Started streaming message for {agent_type}")
    
    def add_streaming_chunk(self, chunk: str) -> None:
        """
        Add a chunk to the current streaming message.
        
        Args:
            chunk: Text chunk to add
        """
        self.streaming_chunks.append(chunk)
    
    def get_current_streaming_content(self) -> str:
        """
        Get the current accumulated streaming content.
        
        Returns:
            Concatenated streaming chunks
        """
        return ''.join(self.streaming_chunks)
    
    def is_streaming(self) -> bool:
        """
        Check if currently streaming a message.
        
        Returns:
            True if streaming is active
        """
        return len(self.streaming_chunks) > 0 or self.streaming_agent is not None
    
    def finalize_streaming_message(self) -> None:
        """
        Finalize the streaming message and add it to conversation history.
        
        Converts accumulated chunks into a complete message and adds
        it to the conversation history.
        """
        if not self.streaming_chunks:
            logger.warning("Attempted to finalize empty streaming message")
            return
        
        # Combine all chunks into final content
        content = ''.join(self.streaming_chunks)
        
        # Create the assistant message
        message = ChatMessage(
            role="assistant",
            content=content,
            timestamp=datetime.now(),
            agent_type=self.streaming_agent or "unknown",
            metadata={
                **self.streaming_metadata,
                'was_streamed': True,
                'chunk_count': len(self.streaming_chunks)
            }
        )
        
        # Add to history
        self._add_message(message)
        
        logger.info(
            f"Finalized streaming message from {self.streaming_agent}: "
            f"{len(self.streaming_chunks)} chunks, {len(content)} chars"
        )
        
        # Clear streaming state
        self.streaming_chunks = []
        self.streaming_agent = None
        self.streaming_metadata = {}
    
    def cancel_streaming_message(self) -> None:
        """
        Cancel the current streaming message without adding to history.
        """
        if self.is_streaming():
            logger.info(f"Cancelled streaming message from {self.streaming_agent}")
            self.streaming_chunks = []
            self.streaming_agent = None
            self.streaming_metadata = {}
    
    def get_streaming_stats(self) -> Dict[str, Any]:
        """
        Get statistics about current streaming message.
        
        Returns:
            Dictionary with streaming stats
        """
        return {
            'is_streaming': self.is_streaming(),
            'agent': self.streaming_agent,
            'chunk_count': len(self.streaming_chunks),
            'total_chars': len(self.get_current_streaming_content()),
            'metadata': self.streaming_metadata
        }
