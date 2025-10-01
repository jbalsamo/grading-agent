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
        # Azure OpenAI settings
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self.chat_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o")
        self.embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
        
        # Agent settings (now configurable)
        self.agent_temperature = float(os.getenv("AGENT_TEMPERATURE", "1.0"))
        self.request_timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        
        # Conversation history settings
        self.max_conversation_messages = int(os.getenv("MAX_CONVERSATION_MESSAGES", "20"))
        self.conversation_history_file = os.getenv("CONVERSATION_HISTORY_FILE", "data/conversation_history.json")
        
        # Rate limiting settings
        self.rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
        self.rate_limit_calls = int(os.getenv("RATE_LIMIT_CALLS", "10"))
        self.rate_limit_period = int(os.getenv("RATE_LIMIT_PERIOD", "60"))
        
        # Input validation settings
        self.max_input_length = int(os.getenv("MAX_INPUT_LENGTH", "10000"))
        
        # Performance settings
        self.enable_response_cache = os.getenv("ENABLE_RESPONSE_CACHE", "true").lower() == "true"
        self.cache_ttl = int(os.getenv("CACHE_TTL", "300"))
        self.cache_max_size = int(os.getenv("CACHE_MAX_SIZE", "100"))
        
        # Monitoring settings
        self.enable_metrics = os.getenv("ENABLE_METRICS", "true").lower() == "true"
        self.metrics_port = int(os.getenv("METRICS_PORT", "9090"))
        
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
        
        # Validate ranges
        if self.agent_temperature < 0 or self.agent_temperature > 2:
            raise ValueError("AGENT_TEMPERATURE must be between 0 and 2")
        if self.max_conversation_messages < 1:
            raise ValueError("MAX_CONVERSATION_MESSAGES must be at least 1")
        if self.request_timeout < 1:
            raise ValueError("REQUEST_TIMEOUT must be at least 1 second")
    
    def get_azure_openai_kwargs(self) -> dict:
        """Get keyword arguments for Azure OpenAI initialization."""
        return {
            "azure_endpoint": self.endpoint,
            "api_key": self.api_key,
            "api_version": self.api_version,
            "azure_deployment": self.chat_deployment,
            "timeout": self.request_timeout,
            "max_retries": self.max_retries,
        }
    
    def __str__(self) -> str:
        """String representation of the config (without sensitive data)."""
        return f"AzureOpenAIConfig(endpoint={self.endpoint}, deployment={self.chat_deployment})"

# Global config instance
config = AzureOpenAIConfig()
