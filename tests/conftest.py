"""
Pytest configuration and shared fixtures.
"""
import pytest
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.master_agent import MasterAgent
from modules.conversation_history import ConversationHistory


@pytest.fixture(scope="session")
def project_root_dir():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="function")
def clean_conversation_history():
    """Fixture to clean up conversation history after each test."""
    history_file = Path(__file__).parent.parent / "data" / "conversation_history.json"
    
    # Clean before test
    if history_file.exists():
        history_file.unlink()
    
    yield
    
    # Clean after test
    if history_file.exists():
        history_file.unlink()


@pytest.fixture(scope="function")
def conversation_history(clean_conversation_history):
    """Provide a fresh ConversationHistory instance."""
    return ConversationHistory(max_messages=20)


@pytest.fixture(scope="function")
def master_agent(clean_conversation_history):
    """Provide a fresh MasterAgent instance.
    
    Note: This requires Azure OpenAI credentials to be configured.
    Mark tests using this as @pytest.mark.requires_api
    """
    return MasterAgent()


@pytest.fixture(scope="session")
def sample_test_messages():
    """Provide sample messages for testing."""
    return [
        "Hello! My name is Alice.",
        "Can you help me with Python programming?",
        "What's the difference between a list and a tuple?",
        "Can you remember my name?",
    ]


@pytest.fixture(scope="session")
def sample_analysis_query():
    """Provide a sample analysis query."""
    return "Can you analyze this data: [1, 2, 3, 4, 5] and calculate the mean?"


@pytest.fixture(scope="session")
def sample_grading_query():
    """Provide a sample grading query."""
    return "Grade this essay: The capital of France is Paris. It's a beautiful city."
