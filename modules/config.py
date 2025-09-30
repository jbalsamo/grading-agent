"""
Configuration module for Azure OpenAI settings.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AzureOpenAIConfig:
    """Configuration class for Azure OpenAI settings."""
    
    def __init__(self):
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self.chat_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o")
        self.embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
        
        # Validate required settings
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate that required configuration values are present."""
        if not self.endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT is required in .env file")
        if not self.api_key:
            raise ValueError("AZURE_OPENAI_API_KEY is required in .env file")
        if not self.chat_deployment:
            raise ValueError("AZURE_OPENAI_CHAT_DEPLOYMENT is required in .env file")
    
    def get_azure_openai_kwargs(self) -> dict:
        """Get keyword arguments for Azure OpenAI initialization."""
        return {
            "azure_endpoint": self.endpoint,
            "api_key": self.api_key,
            "api_version": self.api_version,
            "azure_deployment": self.chat_deployment,
        }
    
    def __str__(self) -> str:
        """String representation of the config (without sensitive data)."""
        return f"AzureOpenAIConfig(endpoint={self.endpoint}, deployment={self.chat_deployment})"

# Global config instance
config = AzureOpenAIConfig()
