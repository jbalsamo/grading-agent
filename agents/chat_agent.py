"""
Chat Agent - Specialized for general conversation and assistance.
"""
from typing import Dict, Any, TYPE_CHECKING
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import config
import logging

if TYPE_CHECKING:
    from conversation_history import ConversationHistory

logger = logging.getLogger(__name__)

class ChatAgent:
    """Specialized agent for general chat and conversation."""
    
    def __init__(self):
        """Initialize the chat agent."""
        self.llm = self._create_llm()
        self.agent_type = "chat"
        logger.info("Chat Agent initialized")
    
    def _create_llm(self) -> AzureChatOpenAI:
        """Create Azure OpenAI LLM instance for chat."""
        return AzureChatOpenAI(
            **config.get_azure_openai_kwargs(),
            temperature=1.0,
        )
    
    def process(self, user_input: str) -> str:
        """Process chat requests."""
        try:
            system_message = """You are a helpful and friendly AI assistant. 
            You excel at general conversation, answering questions, providing explanations, 
            and helping users with various tasks. Be conversational, helpful, and engaging."""
            
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=user_input)
            ]
            
            response = self.llm.invoke(messages)
            logger.info("Chat agent processed request successfully")
            return response.content
            
        except Exception as e:
            logger.error(f"Error in chat agent: {e}")
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
    
    def get_status(self) -> str:
        """Get the status of the chat agent."""
        return "active"
    
    def process_with_history(self, user_input: str, conversation_history: 'ConversationHistory') -> str:
        """Process chat requests with conversation history context."""
        try:
            system_message = """You are a helpful and friendly AI assistant. 
            You excel at general conversation, answering questions, providing explanations, 
            and helping users with various tasks. Be conversational, helpful, and engaging.
            
            You have access to the conversation history, so you can reference previous 
            messages and maintain context throughout the conversation. Use this context 
            to provide more relevant and personalized responses."""
            
            # Get conversation history messages
            history_messages = conversation_history.get_langchain_messages()
            
            # Create current message set
            current_messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=user_input)
            ]
            
            # Combine history with current messages
            # Keep system message first, then history, then current user input
            all_messages = [current_messages[0]] + history_messages + [current_messages[1]]
            
            response = self.llm.invoke(all_messages)
            logger.info("Chat agent processed request with conversation history successfully")
            return response.content
            
        except Exception as e:
            logger.error(f"Error in chat agent with history: {e}")
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of the chat agent."""
        return {
            "agent_type": self.agent_type,
            "capabilities": [
                "General conversation",
                "Question answering",
                "Explanations and clarifications",
                "Creative writing assistance",
                "General problem solving",
                "Conversation history awareness"
            ],
            "specialization": "Conversational AI and general assistance with context awareness"
        }
