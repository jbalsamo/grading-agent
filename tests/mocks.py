"""
Mock objects for testing without requiring API access.
"""
from typing import List, Dict, Any, Optional
from unittest.mock import Mock


class MockLLMResponse:
    """Mock LLM response object."""
    
    def __init__(self, content: str):
        self.content = content


class MockAzureChatOpenAI:
    """Mock Azure Chat OpenAI client for testing."""
    
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.call_count = 0
        self.call_history: List[List[Any]] = []
    
    def invoke(self, messages: List[Any]) -> MockLLMResponse:
        """Mock invoke method."""
        self.call_count += 1
        self.call_history.append(messages)
        
        # Generate response based on message content
        if not messages:
            return MockLLMResponse("Hello! How can I help you?")
        
        last_message = messages[-1]
        content = getattr(last_message, 'content', str(last_message))
        
        # Simple pattern matching for realistic responses
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['hello', 'hi', 'hey']):
            return MockLLMResponse("Hello! I'm here to help you.")
        elif any(word in content_lower for word in ['name', 'who are you']):
            return MockLLMResponse("I'm a test assistant.")
        elif 'calculate' in content_lower or 'math' in content_lower:
            return MockLLMResponse("Based on the calculation, the answer is 42.")
        elif 'grade' in content_lower or 'assessment' in content_lower:
            return MockLLMResponse("This work shows good understanding. Grade: B+")
        elif 'analyze' in content_lower or 'analysis' in content_lower:
            return MockLLMResponse("Here's my analysis: The data shows a clear trend.")
        else:
            return MockLLMResponse(f"I understand you said: {content[:50]}...")
    
    async def ainvoke(self, messages: List[Any]) -> MockLLMResponse:
        """Mock async invoke method."""
        return self.invoke(messages)


class MockDataManager:
    """Mock data manager for testing."""
    
    def __init__(self):
        self.interactions: List[Dict[str, Any]] = []
        self.context_data: Dict[str, Any] = {}
    
    def store_interaction(self, interaction_data: Dict[str, Any]) -> bool:
        """Mock store interaction."""
        self.interactions.append(interaction_data)
        return True
    
    def get_relevant_context(self, user_input: str, max_context: int = 5) -> Dict[str, Any]:
        """Mock get relevant context."""
        return {
            "relevant_interactions": self.interactions[-max_context:],
            "context_count": len(self.interactions[-max_context:]),
            "search_keywords": user_input.lower().split()
        }
    
    def get_recent_interactions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Mock get recent interactions."""
        return self.interactions[-limit:]
    
    def get_interaction_stats(self) -> Dict[str, Any]:
        """Mock get interaction stats."""
        return {
            "total_interactions": len(self.interactions),
            "task_type_distribution": {},
            "agent_usage": {},
            "recent_activity": len(self.interactions)
        }


class MockConversationHistory:
    """Mock conversation history for testing."""
    
    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self.messages: List[Dict[str, Any]] = []
    
    def add_user_message(self, content: str):
        """Mock add user message."""
        self.messages.append({"role": "user", "content": content})
        self._trim_messages()
    
    def add_assistant_message(self, content: str, agent_type: str = "mock"):
        """Mock add assistant message."""
        self.messages.append({
            "role": "assistant",
            "content": content,
            "agent_type": agent_type
        })
        self._trim_messages()
    
    def _trim_messages(self):
        """Trim messages to max size."""
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_messages_for_llm(self) -> List[Dict[str, str]]:
        """Mock get messages for LLM."""
        return self.messages
    
    def get_langchain_messages(self) -> List[Any]:
        """Mock get langchain messages."""
        return [Mock(content=msg["content"], role=msg["role"]) for msg in self.messages]
    
    def clear_history(self):
        """Mock clear history."""
        self.messages.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Mock get stats."""
        return {
            "total_messages": len(self.messages),
            "user_messages": sum(1 for m in self.messages if m["role"] == "user"),
            "assistant_messages": sum(1 for m in self.messages if m["role"] == "assistant"),
            "agent_usage": {}
        }
    
    def __len__(self):
        return len(self.messages)


class MockSpecializedAgent:
    """Mock specialized agent for testing."""
    
    def __init__(self, agent_type: str = "mock"):
        self.agent_type = agent_type
        self.call_count = 0
    
    def process(self, user_input: str) -> str:
        """Mock process method."""
        self.call_count += 1
        return f"Mock {self.agent_type} agent response to: {user_input[:50]}"
    
    def process_with_history(self, user_input: str, conversation_history: Any) -> str:
        """Mock process with history."""
        self.call_count += 1
        history_len = len(conversation_history) if hasattr(conversation_history, '__len__') else 0
        return f"Mock {self.agent_type} agent (with {history_len} history items) response to: {user_input[:50]}"
    
    def get_status(self) -> str:
        """Mock get status."""
        return "active"


def create_mock_config(**overrides):
    """Create a mock configuration object.
    
    Args:
        **overrides: Configuration values to override
        
    Returns:
        Mock config object
    """
    default_config = {
        "endpoint": "https://mock-endpoint.openai.azure.com/",
        "api_key": "mock-api-key",
        "api_version": "2024-02-15-preview",
        "chat_deployment": "mock-deployment",
        "agent_temperature": 1.0,
        "request_timeout": 30,
        "max_retries": 3,
        "max_conversation_messages": 20,
        "rate_limit_enabled": False,  # Disable for tests
        "max_input_length": 10000,
        "enable_response_cache": False,  # Disable for tests
        "enable_metrics": False  # Disable for tests
    }
    
    default_config.update(overrides)
    
    mock_config = Mock()
    for key, value in default_config.items():
        setattr(mock_config, key, value)
    
    mock_config.get_azure_openai_kwargs = Mock(return_value={
        "azure_endpoint": default_config["endpoint"],
        "api_key": default_config["api_key"],
        "api_version": default_config["api_version"],
        "azure_deployment": default_config["chat_deployment"],
        "timeout": default_config["request_timeout"],
        "max_retries": default_config["max_retries"],
    })
    
    return mock_config
