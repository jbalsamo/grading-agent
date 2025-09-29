"""
Analysis Agent - Specialized for data analysis and computational tasks.
"""
from typing import Dict, Any
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import config
import logging

logger = logging.getLogger(__name__)

class AnalysisAgent:
    """Specialized agent for data analysis and computational tasks."""
    
    def __init__(self):
        """Initialize the analysis agent."""
        self.llm = self._create_llm()
        self.agent_type = "analysis"
        logger.info("Analysis Agent initialized")
    
    def _create_llm(self) -> AzureChatOpenAI:
        """Create Azure OpenAI LLM instance for analysis."""
        return AzureChatOpenAI(
            **config.get_azure_openai_kwargs(),
            temperature=1.0,  # Using supported temperature
        )
    
    def process(self, user_input: str) -> str:
        """Process analysis requests."""
        try:
            system_message = """You are a specialized data analysis and computational AI assistant.
            You excel at:
            - Data analysis and interpretation
            - Statistical analysis and insights
            - Code generation for data processing
            - Mathematical computations
            - File processing and data extraction
            - Visualization recommendations
            - Pattern recognition in data
            
            Provide detailed, accurate, and methodical responses. Include step-by-step approaches
            when appropriate and suggest specific tools or methods for complex tasks."""
            
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=user_input)
            ]
            
            response = self.llm.invoke(messages)
            logger.info("Analysis agent processed request successfully")
            return response.content
            
        except Exception as e:
            logger.error(f"Error in analysis agent: {e}")
            return f"I apologize, but I encountered an error during analysis: {str(e)}"
    
    def get_status(self) -> str:
        """Get the status of the analysis agent."""
        return "active"
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of the analysis agent."""
        return {
            "agent_type": self.agent_type,
            "capabilities": [
                "Data analysis and interpretation",
                "Statistical analysis",
                "Code generation for data processing",
                "Mathematical computations",
                "File processing and data extraction",
                "Data visualization recommendations",
                "Pattern recognition",
                "Research methodology guidance"
            ],
            "specialization": "Data analysis and computational tasks",
            "temperature": 1.0
        }
