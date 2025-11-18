"""
Integration tests for the grading workflow.

Tests the complete grading workflow:
Master → Grading Agent → Formatting Agent → (optional) Chat Agent
"""
import pytest
import asyncio
from modules.master_agent import MasterAgent
from modules.agents.grading_agent import GradingAgent
from modules.agents.formatting_agent import FormattingAgent
from modules.conversation_history import ConversationHistory


@pytest.fixture
def master_agent():
    """Create MasterAgent instance for testing."""
    return MasterAgent()


@pytest.fixture
def conversation_history():
    """Create ConversationHistory instance."""
    return ConversationHistory(max_messages=20)


@pytest.fixture
def sample_grading_request():
    """Sample grading request."""
    return """Grade this student's clinical note:

Patient: John Doe
Chief Complaint: Chest pain
History: 45-year-old male with sudden onset chest pain radiating to left arm.
Vital Signs: BP 140/90, HR 95, RR 18, Temp 98.6°F
Physical Exam: Heart sounds regular, lungs clear
Assessment: Possible angina
Plan: EKG, cardiac enzymes, cardiology consult

Please grade against the rubric."""


class TestGradingWorkflowIntegration:
    """Test the complete grading workflow integration."""
    
    def test_grading_workflow_exists(self, master_agent):
        """Test that grading workflow nodes exist in graph."""
        # Verify new nodes are registered
        assert hasattr(master_agent, '_grading_workflow_entry')
        assert hasattr(master_agent, '_route_to_grading')
        assert hasattr(master_agent, '_route_to_formatting')
        assert hasattr(master_agent, '_route_to_chat_notes')
    
    def test_workflow_conditional_routing(self, master_agent):
        """Test that grading requests route to grading workflow."""
        assert hasattr(master_agent, '_should_use_grading_workflow')
        
        # Test grading classification
        state = {
            'agent_type': 'grading',
            'error': ''
        }
        route = master_agent._should_use_grading_workflow(state)
        assert route == 'grading_workflow'
        
        # Test non-grading classification
        state = {
            'agent_type': 'chat',
            'error': ''
        }
        route = master_agent._should_use_grading_workflow(state)
        assert route == 'standard_workflow'
    
    def test_grading_workflow_entry_initializes_state(self, master_agent):
        """Test that workflow entry initializes grading-specific state."""
        state = {
            'user_input': 'Grade this assignment',
            'agent_type': 'grading'
        }
        
        result = master_agent._grading_workflow_entry(state)
        
        assert 'workflow_path' in result
        assert 'grading_workflow_entry' in result['workflow_path']
        assert result['current_agent'] == 'grading'
        assert 'grading_results' in result
        assert 'formatted_output' in result
    
    def test_route_to_grading_executes_agent(self, master_agent, sample_grading_request):
        """Test that route_to_grading executes the grading agent."""
        state = {
            'user_input': sample_grading_request,
            'agent_type': 'grading',
            'workflow_path': [],
            'agent_responses': {}
        }
        
        result = master_agent._route_to_grading(state)
        
        # Verify grading executed
        assert 'route_to_grading' in result['workflow_path']
        assert 'grading' in result['agent_responses']
        assert len(result['agent_responses']['grading']) > 0
    
    def test_route_to_formatting_formats_results(self, master_agent):
        """Test that route_to_formatting creates formatted output."""
        state = {
            'workflow_path': [],
            'agent_responses': {
                'grading': 'Student: John Doe\nScore: 85/100'
            }
        }
        
        result = master_agent._route_to_formatting(state)
        
        # Verify formatting executed
        assert 'route_to_formatting' in result['workflow_path']
        assert 'formatted_output' in result
        assert len(result['formatted_output']) > 0


class TestGradingAgentStreaming:
    """Test grading agent streaming capabilities."""
    
    @pytest.mark.asyncio
    async def test_grading_agent_stream_process(self):
        """Test grading agent stream_process method."""
        agent = GradingAgent()
        
        chunks = []
        async for chunk in agent.stream_process("Grade this test assignment"):
            chunks.append(chunk)
        
        # Verify streaming worked
        assert len(chunks) > 0
        full_output = ''.join(chunks)
        assert len(full_output) > 0
    
    @pytest.mark.asyncio
    async def test_grading_agent_stream_with_history(self):
        """Test grading agent streaming with conversation history."""
        agent = GradingAgent()
        history = ConversationHistory(max_messages=5)
        
        # Add some history
        history.add_user_message("What is the grading rubric?")
        history.add_assistant_message("The rubric includes...", "grading")
        
        chunks = []
        async for chunk in agent.stream_process("Grade student A", history):
            chunks.append(chunk)
        
        assert len(chunks) > 0


class TestFormattingAgentIntegration:
    """Test formatting agent in the workflow."""
    
    def test_formatting_agent_processes_grading_output(self):
        """Test that formatting agent can process grading output."""
        agent = FormattingAgent()
        
        grading_output = """
        Student: Jane Doe
        Section PS: 8/10
        Section DX: 7/10
        Total: 15/20
        """
        
        formatted = agent.format_grading_results(grading_output)
        
        assert isinstance(formatted, str)
        assert len(formatted) > 0
        # Should have table formatting
        assert '|' in formatted
    
    @pytest.mark.asyncio
    async def test_formatting_agent_streaming(self):
        """Test formatting agent streaming capability."""
        agent = FormattingAgent()
        
        grading_data = {
            "student": "Test Student",
            "score": 90,
            "max_score": 100
        }
        
        chunks = []
        async for chunk in agent.stream_process(grading_data):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        full_output = ''.join(chunks)
        assert '|' in full_output  # Should have table formatting


class TestEndToEndGradingWorkflow:
    """End-to-end tests for complete grading workflow."""
    
    def test_grading_request_classification(self, master_agent):
        """Test that grading requests are classified correctly."""
        grading_inputs = [
            "Grade this assignment",
            "Score this student's work",
            "Evaluate this clinical note against the rubric",
            "Assessment of student performance"
        ]
        
        for input_text in grading_inputs:
            state = {'user_input': input_text}
            result = master_agent._classify_task(state)
            
            # Should classify as grading
            assert result.get('agent_type') == 'grading'
    
    def test_non_grading_requests_use_standard_workflow(self, master_agent):
        """Test that non-grading requests use standard workflow."""
        state = {
            'agent_type': 'chat',
            'error': ''
        }
        
        route = master_agent._should_use_grading_workflow(state)
        assert route == 'standard_workflow'
    
    def test_workflow_handles_missing_agents_gracefully(self, master_agent):
        """Test that workflow handles missing agents without crashing."""
        # Test with minimal state
        state = {
            'user_input': 'Grade this',
            'workflow_path': [],
            'agent_responses': {}
        }
        
        # Should not crash even if some agents are missing
        result = master_agent._route_to_grading(state)
        assert 'error' in result or 'grading' in result.get('agent_responses', {})


class TestConversationHistoryWithWorkflow:
    """Test conversation history integration with grading workflow."""
    
    def test_workflow_adds_to_history(self, master_agent, sample_grading_request):
        """Test that workflow results are added to conversation history."""
        initial_count = len(master_agent.conversation_history.messages)
        
        # Run a grading request
        response = master_agent.chat(sample_grading_request)
        
        # History should have been updated
        final_count = len(master_agent.conversation_history.messages)
        assert final_count > initial_count
    
    def test_streaming_history_integration(self):
        """Test that streaming integrates with conversation history."""
        history = ConversationHistory(max_messages=10)
        
        # Start streaming
        history.start_streaming_message('grading')
        assert history.is_streaming()
        
        # Add chunks
        history.add_streaming_chunk("Chunk 1 ")
        history.add_streaming_chunk("Chunk 2 ")
        history.add_streaming_chunk("Chunk 3")
        
        # Get current content
        content = history.get_current_streaming_content()
        assert content == "Chunk 1 Chunk 2 Chunk 3"
        
        # Finalize
        history.finalize_streaming_message()
        assert not history.is_streaming()
        
        # Should be in history now
        assert len(history.messages) == 1
        assert history.messages[0].content == "Chunk 1 Chunk 2 Chunk 3"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
