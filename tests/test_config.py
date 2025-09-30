"""
Unit tests for configuration module.
"""
import pytest
import os
from modules.config import AzureOpenAIConfig


@pytest.mark.unit
class TestAzureOpenAIConfig:
    """Test Azure OpenAI configuration."""
    
    def test_config_has_required_attributes(self):
        """Test that config has all required attributes."""
        from modules.config import config
        
        assert hasattr(config, 'endpoint')
        assert hasattr(config, 'api_key')
        assert hasattr(config, 'api_version')
        assert hasattr(config, 'chat_deployment')
    
    def test_config_endpoint_not_none(self):
        """Test that endpoint is configured."""
        from modules.config import config
        
        # Should be set from .env file
        assert config.endpoint is not None
        assert len(config.endpoint) > 0
    
    def test_config_api_key_not_none(self):
        """Test that API key is configured."""
        from modules.config import config
        
        # Should be set from .env file
        assert config.api_key is not None
        assert len(config.api_key) > 0
    
    def test_get_azure_openai_kwargs(self):
        """Test getting Azure OpenAI kwargs."""
        from modules.config import config
        
        kwargs = config.get_azure_openai_kwargs()
        
        assert 'azure_endpoint' in kwargs
        assert 'api_key' in kwargs
        assert 'api_version' in kwargs
        assert 'azure_deployment' in kwargs
        
        assert kwargs['azure_endpoint'] == config.endpoint
        assert kwargs['azure_deployment'] == config.chat_deployment
    
    def test_config_validation(self):
        """Test that config validates required fields."""
        # This should not raise an error if .env is properly configured
        from modules.config import config
        
        # If we got this far without exception, validation passed
        assert config is not None
