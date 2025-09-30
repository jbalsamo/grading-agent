"""
Conversation History Manager - Manages shared chat history across agents.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

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
    
    def __init__(self, max_messages: int = 20):
        """Initialize conversation history manager.
        
        Args:
            max_messages: Maximum number of messages to keep in history
        """
        self.max_messages = max_messages
        self.messages: List[ChatMessage] = []
        logger.info(f"ConversationHistory initialized with max_messages={max_messages}")
    
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
