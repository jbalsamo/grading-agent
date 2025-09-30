"""
Integration tests for the Master Agent System.

These tests require Azure OpenAI API access and test the full system integration.
Run with: pytest -m integration tests/test_integration.py
"""
import pytest
from modules.master_agent import MasterAgent


@pytest.mark.integration
@pytest.mark.requires_api
class TestMasterAgentIntegration:
    """Integration tests for MasterAgent with full agent workflow."""
    
    def test_master_agent_initialization(self, master_agent):
        """Test that master agent initializes correctly."""
        assert master_agent is not None
        assert master_agent.specialized_agents is not None
        assert len(master_agent.specialized_agents) == 3
        assert 'chat' in master_agent.specialized_agents
        assert 'analysis' in master_agent.specialized_agents
        assert 'grading' in master_agent.specialized_agents
    
    def test_chat_with_context(self, master_agent):
        """Test chat maintains context across messages."""
        # First message
        response1 = master_agent.chat("My name is TestUser")
        assert response1 is not None
        assert len(response1) > 0
        
        # Second message testing context
        response2 = master_agent.chat("What's my name?")
        assert response2 is not None
        assert "TestUser" in response2 or "testuser" in response2.lower()
    
    def test_agent_routing(self, master_agent):
        """Test that messages are routed to correct agents."""
        # Chat query
        response1 = master_agent.chat("Hello, how are you?")
        assert response1 is not None
        
        # Analysis query
        response2 = master_agent.chat("Calculate the mean of [1, 2, 3, 4, 5]")
        assert response2 is not None
        
        # Grading query
        response3 = master_agent.chat("Grade this: The Earth is round.")
        assert response3 is not None
    
    def test_conversation_history_persistence(self, master_agent):
        """Test that conversation history is maintained."""
        master_agent.chat("First message")
        master_agent.chat("Second message")
        master_agent.chat("Third message")
        
        history = master_agent.get_conversation_history()
        assert history['stats']['total_messages'] == 6  # 3 user + 3 assistant
        assert history['stats']['user_messages'] == 3
        assert history['stats']['assistant_messages'] == 3
    
    def test_clear_conversation_history(self, master_agent):
        """Test clearing conversation history."""
        master_agent.chat("Test message")
        assert master_agent.get_conversation_history()['stats']['total_messages'] > 0
        
        master_agent.clear_conversation_history()
        assert master_agent.get_conversation_history()['stats']['total_messages'] == 0
    
    def test_save_and_load_conversation(self, master_agent):
        """Test saving and loading conversation across sessions."""
        # Create conversation
        master_agent.chat("My name is Alice")
        master_agent.chat("I like Python")
        
        # Save
        success = master_agent.save_conversation_history()
        assert success is True
        
        # Create new instance and verify it loads
        new_agent = MasterAgent()
        history = new_agent.get_conversation_history()
        
        # Should have loaded 4 messages (2 user + 2 assistant)
        assert history['stats']['total_messages'] == 4


@pytest.mark.integration
@pytest.mark.requires_api
class TestSpecializedAgents:
    """Integration tests for individual specialized agents."""
    
    def test_chat_agent_response(self, master_agent):
        """Test chat agent provides coherent responses."""
        response = master_agent.chat("Tell me a short joke")
        assert response is not None
        assert len(response) > 10  # Should be a reasonable response
    
    def test_analysis_agent_response(self, master_agent):
        """Test analysis agent handles data analysis."""
        response = master_agent.chat("What is 25 + 37? Show your work.")
        assert response is not None
        assert "62" in response or "sixty-two" in response.lower()
    
    def test_grading_agent_response(self, master_agent):
        """Test grading agent provides feedback."""
        response = master_agent.chat(
            "Grade this essay: Python is a programming language. It's easy to learn."
        )
        assert response is not None
        assert len(response) > 20  # Should provide detailed feedback


@pytest.mark.integration
class TestSystemFeatures:
    """Integration tests for system-level features."""
    
    def test_get_agent_status(self, master_agent):
        """Test getting agent status."""
        status = master_agent.get_agent_status()
        assert status['master_agent'] == 'active'
        assert status['data_manager'] == 'active'
        assert len(status['specialized_agents']) == 3
    
    def test_get_performance_stats(self, master_agent):
        """Test getting performance statistics."""
        # Generate some activity
        master_agent.chat("Test message")
        
        stats = master_agent.get_performance_stats()
        assert 'total_requests' in stats
        assert 'uptime_formatted' in stats
        assert stats['total_requests'] >= 1
    
    def test_health_check(self, master_agent):
        """Test system health check."""
        health = master_agent.run_health_check()
        assert 'overall_status' in health
        assert 'checks' in health
        assert health['overall_status'] in ['healthy', 'degraded', 'unhealthy']


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.slow
class TestMultiAgentWorkflow:
    """Integration tests for multi-agent workflows."""
    
    def test_agent_switching_with_context(self, master_agent):
        """Test switching between agents while maintaining context."""
        # Start with chat
        master_agent.chat("My name is Bob and I'm learning math")
        
        # Switch to analysis
        master_agent.chat("What's 15 + 27?")
        
        # Switch to grading
        response = master_agent.chat("Grade my understanding of basic addition")
        
        # Context should be maintained
        history = master_agent.get_conversation_history()
        assert history['stats']['total_messages'] == 6
        
        # Different agents should have been used
        agent_usage = history['stats']['agent_usage']
        assert len(agent_usage) >= 2  # At least 2 different agents used
    
    def test_complex_conversation_flow(self, master_agent):
        """Test a complex multi-turn conversation."""
        messages = [
            "Hello, I need help with a project",
            "I'm analyzing sales data",
            "Can you help me calculate averages?",
            "What's the average of 10, 20, 30, 40, 50?",
            "Great! Can you explain how you calculated that?",
        ]
        
        for msg in messages:
            response = master_agent.chat(msg)
            assert response is not None
            assert len(response) > 0
        
        # Verify full conversation history
        history = master_agent.get_conversation_history()
        assert history['stats']['total_messages'] == len(messages) * 2
    
    def test_data_manager_context_retrieval(self, master_agent):
        """Test that data manager retrieves relevant context."""
        # Create some interactions
        master_agent.chat("I'm working on Python programming")
        master_agent.chat("I need help with functions")
        master_agent.chat("What are lambda functions?")
        
        # Query should retrieve relevant context
        response = master_agent.chat("Can you remind me what we discussed about Python?")
        assert response is not None
        # Response should reference previous Python topics
        assert any(keyword in response.lower() for keyword in ['python', 'function', 'programming'])
