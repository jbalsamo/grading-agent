"""
Grading Agent - Specialized for educational assessment and grading tasks.
"""
from typing import Dict, Any, TYPE_CHECKING
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from ..config import config
import logging

if TYPE_CHECKING:
    from ..conversation_history import ConversationHistory

logger = logging.getLogger(__name__)

class GradingAgent:
    """Specialized agent for educational assessment and grading."""
    
    def __init__(self):
        """Initialize the grading agent."""
        self.llm = self._create_llm()
        self.agent_type = "grading"
        logger.info("Grading Agent initialized")
    
    def _create_llm(self) -> AzureChatOpenAI:
        """Create Azure OpenAI LLM instance for grading."""
        return AzureChatOpenAI(
            **config.get_azure_openai_kwargs(),
            temperature=config.agent_temperature,
        )
    
    def process(self, user_input: str) -> str:
        """Process grading and assessment requests."""
        try:
            system_message = """You are a specialized educational assessment and grading AI assistant.
            You excel at:
            - Grading assignments, essays, and exams
            - Providing detailed feedback on student work
            - Creating rubrics and assessment criteria
            - Analyzing learning outcomes
            - Identifying areas for improvement
            - Suggesting educational resources
            - Maintaining consistency in grading standards
            - Providing constructive and encouraging feedback
            
            Always be fair, objective, and constructive in your assessments. Provide specific
            examples and actionable feedback. Consider different learning styles and levels."""
            
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=user_input)
            ]
            
            response = self.llm.invoke(messages)
            logger.info("Grading agent processed request successfully")
            return response.content
            
        except Exception as e:
            logger.error(f"Error in grading agent: {e}")
            return f"I apologize, but I encountered an error during grading assessment: {str(e)}"
    
    def get_status(self) -> str:
        """Get the status of the grading agent."""
        return "active"
    
    def process_with_history(self, user_input: str, conversation_history: 'ConversationHistory') -> str:
        """Process grading and assessment requests with conversation history context."""
        try:
            system_message = """You are a specialized educational assessment and grading AI assistant.
            You excel at:
            - Grading assignments, essays, and exams
            - Providing detailed feedback on student work
            - Creating rubrics and assessment criteria
            - Analyzing learning outcomes
            - Identifying areas for improvement
            - Suggesting educational resources
            - Maintaining consistency in grading standards
            - Providing constructive and encouraging feedback
            
            You have access to the conversation history, so you can reference previous 
            grading sessions, maintain consistency across multiple assessments, and 
            build upon earlier feedback. Use this context to provide more coherent 
            and consistent educational assessments.
            
            Always be fair, objective, and constructive in your assessments. Provide specific
            examples and actionable feedback. Consider different learning styles and levels."""
            
            # Get conversation history messages
            history_messages = conversation_history.get_langchain_messages()
            
            # Create current message set
            current_messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=user_input)
            ]
            
            # Combine history with current messages
            all_messages = [current_messages[0]] + history_messages + [current_messages[1]]
            
            response = self.llm.invoke(all_messages)
            logger.info("Grading agent processed request with conversation history successfully")
            return response.content
            
        except Exception as e:
            logger.error(f"Error in grading agent with history: {e}")
            return f"I apologize, but I encountered an error during grading assessment: {str(e)}"
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of the grading agent."""
        return {
            "agent_type": self.agent_type,
            "capabilities": [
                "Assignment and essay grading",
                "Detailed feedback generation",
                "Rubric creation and application",
                "Learning outcome analysis",
                "Educational assessment design",
                "Student progress tracking",
                "Constructive feedback delivery",
                "Academic integrity checking",
                "Curriculum alignment assessment",
                "Conversation history awareness for consistent grading"
            ],
            "specialization": "Educational assessment and grading with context awareness",
            "temperature": 1.0
        }
