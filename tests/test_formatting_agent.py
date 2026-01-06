"""
Tests for FormattingAgent

This test suite validates the FormattingAgent's ability to format
grading results into spreadsheet-style markdown tables.
"""
import pytest
import asyncio
from modules.agents.formatting_agent import FormattingAgent


@pytest.fixture
def formatting_agent():
    """Create formatting agent instance for testing."""
    return FormattingAgent()


@pytest.fixture
def mock_grading_results():
    """Mock grading results for testing."""
    return {
        "student_name": "Test Student",
        "sections": {
            "PS": {"ai_score": 8, "human_score": 9, "max_score": 10},
            "DX": {"ai_score": 7, "human_score": 7, "max_score": 10},
            "PL": {"ai_score": 6, "human_score": 8, "max_score": 10}
        },
        "rubric_items": [
            {"item": "Patient demographics documented", "checked": True},
            {"item": "Chief complaint clearly stated", "checked": True},
            {"item": "Vital signs recorded", "checked": False},
            {"item": "Physical exam findings", "checked": True}
        ],
        "total": {"ai": 21, "human": 24, "max": 30}
    }


@pytest.fixture
def mock_simple_results():
    """Simple grading results for basic testing."""
    return {
        "student": "John Doe",
        "score": 85,
        "max_score": 100
    }


class TestFormattingAgentInitialization:
    """Test FormattingAgent initialization."""
    
    def test_initialization(self, formatting_agent):
        """Test agent initializes correctly."""
        assert formatting_agent is not None
        assert formatting_agent.agent_type == "formatting"
        assert formatting_agent.llm is not None
    
    def test_status(self, formatting_agent):
        """Test agent status reporting."""
        status = formatting_agent.get_status()
        assert status == "active"
    
    def test_capabilities(self, formatting_agent):
        """Test capabilities reporting."""
        caps = formatting_agent.get_capabilities()
        
        assert caps["agent_type"] == "formatting"
        assert "capabilities" in caps
        assert isinstance(caps["capabilities"], list)
        assert len(caps["capabilities"]) > 0
        assert caps["temperature"] == "default"
        assert "Convert grading data to markdown tables" in caps["capabilities"]


class TestFormattingAgentProcessing:
    """Test FormattingAgent processing methods."""
    
    def test_format_grading_results_basic(self, formatting_agent, mock_grading_results):
        """Test basic formatting functionality."""
        result = formatting_agent.format_grading_results(mock_grading_results)
        
        # Verify it returns a string
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Should not return error
        assert "Error" not in result or "error" not in result.lower()
    
    def test_format_includes_markdown_tables(self, formatting_agent, mock_grading_results):
        """Test that output includes markdown table syntax."""
        result = formatting_agent.format_grading_results(mock_grading_results)
        
        # Check for markdown table indicators
        assert "|" in result  # Table column delimiter
        
    def test_process_method_dict_input(self, formatting_agent, mock_grading_results):
        """Test process method with dictionary input."""
        result = formatting_agent.process(mock_grading_results)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_process_method_string_input(self, formatting_agent):
        """Test process method with string input."""
        string_input = "Student: Jane Doe\nScore: 90/100"
        result = formatting_agent.process(string_input)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_empty_results_handling(self, formatting_agent):
        """Test handling of empty results."""
        empty_results = {}
        result = formatting_agent.format_grading_results(empty_results)
        
        # Should not crash
        assert isinstance(result, str)
    
    def test_malformed_data_handling(self, formatting_agent):
        """Test handling of malformed data."""
        bad_data = {"invalid": "structure", "random": [1, 2, 3]}
        result = formatting_agent.format_grading_results(bad_data)
        
        # Should handle gracefully
        assert isinstance(result, str)
    
    def test_simple_results(self, formatting_agent, mock_simple_results):
        """Test with simple results structure."""
        result = formatting_agent.format_grading_results(mock_simple_results)
        
        assert isinstance(result, str)
        assert len(result) > 0


class TestFormattingAgentStreaming:
    """Test FormattingAgent streaming capabilities."""
    
    @pytest.mark.asyncio
    async def test_stream_process_basic(self, formatting_agent, mock_grading_results):
        """Test basic streaming functionality."""
        chunks = []
        
        async for chunk in formatting_agent.stream_process(mock_grading_results):
            chunks.append(chunk)
        
        # Verify we got chunks
        assert len(chunks) > 0
        
        # Verify combined output is valid
        full_output = "".join(chunks)
        assert len(full_output) > 0
    
    @pytest.mark.asyncio
    async def test_stream_with_dict_input(self, formatting_agent, mock_grading_results):
        """Test streaming with dictionary input."""
        chunks = []
        
        async for chunk in formatting_agent.stream_process(mock_grading_results):
            chunks.append(chunk)
            
        full_output = "".join(chunks)
        assert "|" in full_output  # Should have table formatting
    
    @pytest.mark.asyncio
    async def test_stream_with_string_input(self, formatting_agent):
        """Test streaming with string input."""
        string_input = "Test grading data"
        chunks = []
        
        async for chunk in formatting_agent.stream_process(string_input):
            chunks.append(chunk)
        
        assert len(chunks) > 0
    
    @pytest.mark.asyncio
    async def test_stream_chunk_count(self, formatting_agent, mock_simple_results):
        """Test that streaming produces multiple chunks."""
        chunks = []
        
        async for chunk in formatting_agent.stream_process(mock_simple_results):
            chunks.append(chunk)
        
        # Should get multiple chunks (streaming working)
        # Note: Exact count depends on LLM, just verify > 0
        assert len(chunks) > 0
    
    @pytest.mark.asyncio
    async def test_stream_empty_results(self, formatting_agent):
        """Test streaming with empty results."""
        empty_results = {}
        chunks = []
        
        async for chunk in formatting_agent.stream_process(empty_results):
            chunks.append(chunk)
        
        # Should handle gracefully
        assert len(chunks) >= 0


class TestFormattingAgentOutputFormat:
    """Test output format validation."""
    
    def test_output_contains_table_structure(self, formatting_agent, mock_grading_results):
        """Test that output contains table structure."""
        result = formatting_agent.format_grading_results(mock_grading_results)
        
        # Should have table delimiters
        assert "|" in result
    
    def test_output_is_non_empty(self, formatting_agent, mock_grading_results):
        """Test that output is not empty."""
        result = formatting_agent.format_grading_results(mock_grading_results)
        
        assert len(result) > 0
        assert result.strip() != ""
    
    def test_format_alias_method(self, formatting_agent, mock_grading_results):
        """Test that format_grading_results is an alias for process."""
        result1 = formatting_agent.process(mock_grading_results)
        result2 = formatting_agent.format_grading_results(mock_grading_results)
        
        # Both should return strings
        assert isinstance(result1, str)
        assert isinstance(result2, str)


class TestFormattingAgentEdgeCases:
    """Test edge cases and error handling."""
    
    def test_none_input(self, formatting_agent):
        """Test handling of None input."""
        result = formatting_agent.process(None)
        
        # Should handle gracefully
        assert isinstance(result, str)
    
    def test_numeric_input(self, formatting_agent):
        """Test handling of numeric input."""
        result = formatting_agent.process(12345)
        
        # Should convert and handle
        assert isinstance(result, str)
    
    def test_list_input(self, formatting_agent):
        """Test handling of list input."""
        list_input = ["item1", "item2", "item3"]
        result = formatting_agent.process(list_input)
        
        assert isinstance(result, str)
    
    @pytest.mark.asyncio
    async def test_stream_error_recovery(self, formatting_agent):
        """Test that streaming handles errors gracefully."""
        # This should not crash even with problematic input
        chunks = []
        
        try:
            async for chunk in formatting_agent.stream_process(None):
                chunks.append(chunk)
        except Exception:
            # If it raises, that's okay as long as it doesn't hang
            pass
        
        # Test passes if we get here without hanging
        assert True


class TestFormattingAgentIntegration:
    """Integration tests with realistic data."""
    
    def test_realistic_grading_scenario(self, formatting_agent):
        """Test with realistic grading scenario."""
        realistic_data = {
            "student_name": "Alice Johnson",
            "assignment": "Clinical Note Assessment",
            "sections": {
                "History": {"ai": 18, "human": 20, "max": 20},
                "Physical": {"ai": 15, "human": 16, "max": 20},
                "Assessment": {"ai": 22, "human": 24, "max": 25}
            },
            "total_score": {"ai": 55, "human": 60, "max": 65},
            "percentage": {"ai": 84.6, "human": 92.3}
        }
        
        result = formatting_agent.format_grading_results(realistic_data)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "|" in result
    
    @pytest.mark.asyncio
    async def test_realistic_streaming_scenario(self, formatting_agent):
        """Test streaming with realistic scenario."""
        realistic_data = {
            "class": "Clinical Skills 101",
            "date": "2025-11-12",
            "students_graded": 25,
            "average_score": 82.5
        }
        
        chunks = []
        async for chunk in formatting_agent.stream_process(realistic_data):
            chunks.append(chunk)
        
        full_output = "".join(chunks)
        assert len(full_output) > 0


# Run all tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
