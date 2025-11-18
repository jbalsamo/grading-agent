"""
Code Review Agent - Specialized for code review and quality analysis.
"""
from typing import Dict, Any, TYPE_CHECKING
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from ..config import config
import logging

if TYPE_CHECKING:
    from ..conversation_history import ConversationHistory

logger = logging.getLogger(__name__)


class CodeReviewAgent:
    """Specialized agent for code review and quality analysis."""
    
    def __init__(self):
        """Initialize the code review agent."""
        self.llm = self._create_llm()
        self.agent_type = "code_review"
        logger.info("Code Review Agent initialized")
    
    def _create_llm(self) -> AzureChatOpenAI:
        """Create Azure OpenAI LLM instance for code review.
        
        Note: Using temperature=1.0 as required by gpt-5 model.
        """
        return AzureChatOpenAI(
            **config.get_azure_openai_kwargs(),
            temperature=1.0,  # Explicitly set to 1.0 as required by gpt-5 model
        )
    
    def process(self, user_input: str) -> str:
        """Process code review requests without history.
        
        Args:
            user_input: User's request containing code to review
            
        Returns:
            Code review feedback and recommendations
        """
        try:
            system_message = """You are a specialized code review AI assistant.
            
            Your expertise includes:
            - Identifying bugs and logic errors
            - Detecting security vulnerabilities (SQL injection, XSS, etc.)
            - Suggesting performance optimizations
            - Enforcing best practices and design patterns
            - Improving code readability and maintainability
            - Checking for proper error handling
            
            When reviewing code:
            1. Be specific - point to exact lines or patterns
            2. Be constructive - explain WHY changes improve the code
            3. Prioritize issues by severity (critical, important, minor)
            4. Provide code examples for suggested fixes
            5. Consider the broader context and architecture
            
            Always be professional and educational in your feedback."""
            
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=user_input)
            ]
            
            response = self.llm.invoke(messages)
            logger.info("Code review agent processed request successfully")
            return response.content
            
        except Exception as e:
            logger.error(f"Error in code review agent: {e}")
            return f"I apologize, but I encountered an error during code review: {str(e)}"
    
    def process_with_history(self, user_input: str,
                            conversation_history: 'ConversationHistory') -> str:
        """Process code review requests with conversation history.
        
        Args:
            user_input: User's request
            conversation_history: Shared conversation history
            
        Returns:
            Code review with context awareness
        """
        try:
            system_message = """You are a specialized code review AI assistant.
            
            Your expertise includes:
            - Identifying bugs and logic errors
            - Detecting security vulnerabilities
            - Suggesting performance optimizations
            - Enforcing best practices and design patterns
            
            You have access to conversation history, which allows you to:
            - Reference previously reviewed code
            - Track improvements over time
            - Maintain consistent coding standards
            - Build on earlier feedback
            
            Use this context to provide more coherent and personalized reviews."""
            
            # Get conversation history messages
            history_messages = conversation_history.get_langchain_messages()
            
            # Create current message set
            current_messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=user_input)
            ]
            
            # Combine: system prompt + history + current input
            all_messages = [current_messages[0]] + history_messages + [current_messages[1]]
            
            response = self.llm.invoke(all_messages)
            logger.info("Code review agent processed with history successfully")
            return response.content
            
        except Exception as e:
            logger.error(f"Error in code review agent with history: {e}")
            return f"I apologize, but I encountered an error during code review: {str(e)}"
    
    def get_status(self) -> str:
        """Get the status of the code review agent.
        
        Returns:
            Status string ("active" if operational)
        """
        return "active"
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of the code review agent.
        
        Returns:
            Dictionary describing agent capabilities
        """
        return {
            "agent_type": self.agent_type,
            "capabilities": [
                "Bug detection and logic error identification",
                "Security vulnerability analysis",
                "Performance optimization suggestions",
                "Best practices enforcement",
                "Code readability improvements",
                "Design pattern recommendations",
                "Error handling review",
                "Conversation history for consistent reviews"
            ],
            "specialization": "Code review and quality analysis with context awareness",
            "temperature": 0.3,
            "supports_history": True
        }