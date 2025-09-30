"""
Unit tests for ConversationHistory class.
"""
import pytest
from datetime import datetime
from modules.conversation_history import ConversationHistory, ChatMessage


class TestChatMessage:
    """Test ChatMessage dataclass."""
    
    def test_create_chat_message(self):
        """Test creating a chat message."""
        msg = ChatMessage(
            role="user",
            content="Hello",
            timestamp=datetime.now(),
            agent_type=None
        )
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.agent_type is None


class TestConversationHistory:
    """Test ConversationHistory functionality."""
    
    def test_initialization(self, conversation_history):
        """Test ConversationHistory initialization."""
        assert len(conversation_history) == 0
        assert conversation_history.max_messages == 20
    
    def test_add_user_message(self, conversation_history):
        """Test adding a user message."""
        conversation_history.add_user_message("Hello")
        assert len(conversation_history) == 1
        assert conversation_history.messages[0].role == "user"
        assert conversation_history.messages[0].content == "Hello"
    
    def test_add_assistant_message(self, conversation_history):
        """Test adding an assistant message."""
        conversation_history.add_assistant_message("Hi there!", "chat")
        assert len(conversation_history) == 1
        assert conversation_history.messages[0].role == "assistant"
        assert conversation_history.messages[0].content == "Hi there!"
        assert conversation_history.messages[0].agent_type == "chat"
    
    def test_rolling_window(self, conversation_history):
        """Test that history maintains rolling window."""
        # Add more messages than max_messages
        for i in range(25):
            conversation_history.add_user_message(f"Message {i}")
        
        # Should only keep last 20
        assert len(conversation_history) == 20
        # First message should be "Message 5" (25 - 20 = 5)
        assert "Message 5" in conversation_history.messages[0].content
    
    def test_clear_history(self, conversation_history):
        """Test clearing conversation history."""
        conversation_history.add_user_message("Test")
        conversation_history.add_assistant_message("Response", "chat")
        assert len(conversation_history) == 2
        
        conversation_history.clear_history()
        assert len(conversation_history) == 0
    
    def test_get_langchain_messages(self, conversation_history):
        """Test converting to LangChain message format."""
        conversation_history.add_user_message("Hello")
        conversation_history.add_assistant_message("Hi", "chat")
        
        messages = conversation_history.get_langchain_messages()
        assert len(messages) == 2
        assert messages[0].content == "Hello"
        # Assistant messages include agent type prefix
        assert "[chat agent]:" in messages[1].content
        assert "Hi" in messages[1].content
    
    def test_get_recent_context(self, conversation_history):
        """Test getting recent context as string."""
        conversation_history.add_user_message("Question 1")
        conversation_history.add_assistant_message("Answer 1", "chat")
        conversation_history.add_user_message("Question 2")
        conversation_history.add_assistant_message("Answer 2", "analysis")
        
        context = conversation_history.get_recent_context(2)
        assert "Question 2" in context
        assert "Answer 2" in context
        assert "analysis" in context.lower()
    
    def test_get_stats(self, conversation_history):
        """Test getting conversation statistics."""
        conversation_history.add_user_message("Q1")
        conversation_history.add_assistant_message("A1", "chat")
        conversation_history.add_user_message("Q2")
        conversation_history.add_assistant_message("A2", "analysis")
        conversation_history.add_assistant_message("A3", "grading")
        
        stats = conversation_history.get_stats()
        assert stats['total_messages'] == 5
        assert stats['user_messages'] == 2
        assert stats['assistant_messages'] == 3
        assert stats['agent_usage']['chat'] == 1
        assert stats['agent_usage']['analysis'] == 1
        assert stats['agent_usage']['grading'] == 1


@pytest.mark.unit
class TestConversationPersistence:
    """Test conversation history persistence."""
    
    def test_save_to_disk(self, conversation_history):
        """Test saving conversation history to disk."""
        conversation_history.add_user_message("Test message")
        conversation_history.add_assistant_message("Test response", "chat")
        
        success = conversation_history.save_to_disk()
        assert success is True
    
    def test_load_from_disk(self, conversation_history):
        """Test loading conversation history from disk."""
        # Save some data first
        conversation_history.add_user_message("Saved message")
        conversation_history.add_assistant_message("Saved response", "chat")
        conversation_history.save_to_disk()
        
        # Create new instance and load
        new_history = ConversationHistory(max_messages=20)
        success = new_history.load_from_disk()
        
        assert success is True
        assert len(new_history) == 2
        assert new_history.messages[0].content == "Saved message"
        assert new_history.messages[1].content == "Saved response"
    
    def test_delete_saved_history(self, conversation_history):
        """Test deleting saved history file."""
        conversation_history.add_user_message("Test")
        conversation_history.save_to_disk()
        
        success = conversation_history.delete_saved_history()
        assert success is True
        
        # Loading should fail now
        new_history = ConversationHistory(max_messages=20)
        success = new_history.load_from_disk()
        assert success is False
