"""
Tests for streaming infrastructure and functionality.

Tests:
- StreamingManager
- ChunkBuffer
- StreamingProgressTracker
- MasterAgent.chat_streaming()
- ConversationHistory streaming methods
"""
import pytest
import asyncio
from modules.streaming import StreamingManager, ChunkBuffer, StreamingProgressTracker
from modules.master_agent import MasterAgent
from modules.conversation_history import ConversationHistory


class TestChunkBuffer:
    """Test ChunkBuffer functionality."""
    
    def test_chunk_buffer_initialization(self):
        """Test buffer initializes correctly."""
        buffer = ChunkBuffer(max_chunks=100)
        
        assert len(buffer.chunks) == 0
        assert buffer.total_chunks == 0
        assert buffer.total_chars == 0
        assert buffer.max_chunks == 100
    
    def test_add_chunks(self):
        """Test adding chunks to buffer."""
        buffer = ChunkBuffer()
        
        buffer.add_chunk("Hello ")
        buffer.add_chunk("World")
        
        assert buffer.total_chunks == 2
        assert buffer.total_chars == 11
        assert buffer.get_full_content() == "Hello World"
    
    def test_get_last_n_chunks(self):
        """Test retrieving last N chunks."""
        buffer = ChunkBuffer()
        
        for i in range(10):
            buffer.add_chunk(f"Chunk {i} ")
        
        last_3 = buffer.get_last_n_chunks(3)
        assert len(last_3) == 3
        assert last_3[-1] == "Chunk 9 "
    
    def test_buffer_overflow(self):
        """Test buffer with max size."""
        buffer = ChunkBuffer(max_chunks=5)
        
        for i in range(10):
            buffer.add_chunk(f"Chunk {i}")
        
        # Should only have last 5 chunks
        assert len(buffer.chunks) == 5
        assert buffer.overflow_count > 0
    
    def test_buffer_stats(self):
        """Test getting buffer statistics."""
        buffer = ChunkBuffer()
        buffer.add_chunk("Test 1 ")
        buffer.add_chunk("Test 2 ")
        
        stats = buffer.get_stats()
        
        assert stats['buffered_chunks'] == 2
        assert stats['total_chunks'] == 2
        assert stats['total_chars'] == 14
        assert stats['overflow_count'] == 0
    
    def test_clear_buffer(self):
        """Test clearing buffer."""
        buffer = ChunkBuffer()
        buffer.add_chunk("Test")
        
        buffer.clear()
        
        assert len(buffer.chunks) == 0
        assert buffer.total_chunks == 0
        assert buffer.total_chars == 0


class TestStreamingProgressTracker:
    """Test StreamingProgressTracker functionality."""
    
    def test_tracker_initialization(self):
        """Test tracker initializes correctly."""
        tracker = StreamingProgressTracker(expected_agents=['grading', 'formatting'])
        
        assert 'grading' in tracker.agent_progress
        assert 'formatting' in tracker.agent_progress
        assert tracker.agent_progress['grading']['status'] == 'pending'
    
    def test_start_agent(self):
        """Test starting an agent."""
        tracker = StreamingProgressTracker()
        
        tracker.start_agent('grading')
        
        assert 'grading' in tracker.agent_progress
        assert tracker.agent_progress['grading']['status'] == 'streaming'
        assert tracker.agent_progress['grading']['start_time'] is not None
    
    def test_add_chunk(self):
        """Test adding chunks to agent progress."""
        tracker = StreamingProgressTracker()
        tracker.start_agent('grading')
        
        tracker.add_chunk('grading', 'Chunk 1')
        tracker.add_chunk('grading', 'Chunk 2')
        
        assert tracker.agent_progress['grading']['chunk_count'] == 2
        assert tracker.agent_progress['grading']['char_count'] == 14
    
    def test_complete_agent(self):
        """Test completing an agent."""
        tracker = StreamingProgressTracker()
        tracker.start_agent('grading')
        tracker.add_chunk('grading', 'Test chunk')
        
        tracker.complete_agent('grading')
        
        assert tracker.agent_progress['grading']['status'] == 'complete'
        assert tracker.agent_progress['grading']['end_time'] is not None
    
    def test_error_agent(self):
        """Test handling agent error."""
        tracker = StreamingProgressTracker()
        tracker.start_agent('grading')
        
        tracker.error_agent('grading', 'Test error')
        
        assert tracker.agent_progress['grading']['status'] == 'error'
        assert tracker.agent_progress['grading']['error'] == 'Test error'
    
    def test_overall_progress(self):
        """Test calculating overall progress."""
        tracker = StreamingProgressTracker(expected_agents=['grading', 'formatting', 'chat'])
        
        # No agents complete
        assert tracker.get_overall_progress() == 0.0
        
        # One agent complete
        tracker.start_agent('grading')
        tracker.complete_agent('grading')
        assert tracker.get_overall_progress() == pytest.approx(33.33, 0.1)
        
        # All agents complete
        tracker.start_agent('formatting')
        tracker.complete_agent('formatting')
        tracker.start_agent('chat')
        tracker.complete_agent('chat')
        assert tracker.get_overall_progress() == 100.0
    
    def test_is_complete(self):
        """Test checking if workflow is complete."""
        tracker = StreamingProgressTracker(expected_agents=['grading', 'formatting'])
        
        assert not tracker.is_complete()
        
        tracker.start_agent('grading')
        tracker.complete_agent('grading')
        assert not tracker.is_complete()
        
        tracker.start_agent('formatting')
        tracker.complete_agent('formatting')
        assert tracker.is_complete()
    
    def test_get_metrics(self):
        """Test getting comprehensive metrics."""
        tracker = StreamingProgressTracker(expected_agents=['grading'])
        tracker.start_agent('grading')
        tracker.add_chunk('grading', 'Test ')
        tracker.add_chunk('grading', 'Chunk')
        tracker.complete_agent('grading')
        
        metrics = tracker.get_metrics()
        
        assert metrics['total_agents'] == 1
        assert metrics['completed_agents'] == 1
        assert metrics['total_chunks'] == 2
        assert metrics['total_chars'] == 10
        assert 'duration' in metrics


class TestStreamingManager:
    """Test StreamingManager functionality."""
    
    def test_streaming_manager_initialization(self):
        """Test manager initializes correctly."""
        manager = StreamingManager()
        
        assert len(manager.active_streams) == 0
        assert len(manager.chunk_buffers) == 0
    
    def test_create_stream(self):
        """Test creating a new stream."""
        manager = StreamingManager()
        
        stream_id = manager.create_stream(agent_name='grading')
        
        assert stream_id in manager.active_streams
        assert manager.active_streams[stream_id]['agent_name'] == 'grading'
        assert manager.active_streams[stream_id]['status'] == 'streaming'
    
    def test_add_chunk_to_stream(self):
        """Test adding chunks to a stream."""
        manager = StreamingManager()
        stream_id = manager.create_stream(agent_name='grading')
        
        manager.add_chunk(stream_id, 'Chunk 1 ')
        manager.add_chunk(stream_id, 'Chunk 2')
        
        chunks = manager.get_chunks(stream_id)
        assert len(chunks) == 2
        
        full_content = manager.get_full_content(stream_id)
        assert full_content == 'Chunk 1 Chunk 2'
    
    def test_complete_stream(self):
        """Test completing a stream."""
        manager = StreamingManager()
        stream_id = manager.create_stream(agent_name='grading')
        manager.add_chunk(stream_id, 'Test content')
        
        summary = manager.complete_stream(stream_id)
        
        assert summary['status'] == 'complete'
        assert summary['chunk_count'] == 1
        assert 'duration' in summary
    
    def test_error_stream(self):
        """Test handling stream error."""
        manager = StreamingManager()
        stream_id = manager.create_stream(agent_name='grading')
        
        manager.error_stream(stream_id, 'Test error')
        
        assert manager.active_streams[stream_id]['status'] == 'error'
        assert manager.active_streams[stream_id]['error'] == 'Test error'
    
    def test_get_stream_status(self):
        """Test getting stream status."""
        manager = StreamingManager()
        stream_id = manager.create_stream(agent_name='grading')
        
        status = manager.get_stream_status(stream_id)
        
        assert status['agent_name'] == 'grading'
        assert status['status'] == 'streaming'
    
    def test_cleanup_stream(self):
        """Test cleaning up stream resources."""
        manager = StreamingManager()
        stream_id = manager.create_stream(agent_name='grading')
        
        manager.cleanup_stream(stream_id)
        
        assert stream_id not in manager.active_streams
        assert stream_id not in manager.chunk_buffers
    
    @pytest.mark.asyncio
    async def test_stream_from_agent(self):
        """Test streaming from an agent generator."""
        manager = StreamingManager()
        
        # Mock async generator
        async def mock_generator():
            for i in range(5):
                yield f"Chunk {i} "
        
        content = await manager.stream_from_agent(
            mock_generator(),
            agent_name='test'
        )
        
        assert content == "Chunk 0 Chunk 1 Chunk 2 Chunk 3 Chunk 4 "


class TestConversationHistoryStreaming:
    """Test ConversationHistory streaming methods."""
    
    def test_start_streaming_message(self):
        """Test starting a streaming message."""
        history = ConversationHistory(max_messages=10)
        
        history.start_streaming_message('grading', metadata={'test': 'value'})
        
        assert history.is_streaming()
        assert history.streaming_agent == 'grading'
        assert history.streaming_metadata['test'] == 'value'
    
    def test_add_streaming_chunk(self):
        """Test adding chunks to streaming message."""
        history = ConversationHistory(max_messages=10)
        history.start_streaming_message('grading')
        
        history.add_streaming_chunk('Hello ')
        history.add_streaming_chunk('World')
        
        content = history.get_current_streaming_content()
        assert content == 'Hello World'
    
    def test_finalize_streaming_message(self):
        """Test finalizing a streaming message."""
        history = ConversationHistory(max_messages=10)
        history.start_streaming_message('grading')
        history.add_streaming_chunk('Test ')
        history.add_streaming_chunk('Message')
        
        history.finalize_streaming_message()
        
        assert not history.is_streaming()
        assert len(history.messages) == 1
        assert history.messages[0].content == 'Test Message'
        assert history.messages[0].metadata['was_streamed'] is True
    
    def test_cancel_streaming_message(self):
        """Test canceling a streaming message."""
        history = ConversationHistory(max_messages=10)
        history.start_streaming_message('grading')
        history.add_streaming_chunk('Test')
        
        history.cancel_streaming_message()
        
        assert not history.is_streaming()
        assert len(history.messages) == 0  # Should not add to history
    
    def test_streaming_stats(self):
        """Test getting streaming statistics."""
        history = ConversationHistory(max_messages=10)
        history.start_streaming_message('grading')
        history.add_streaming_chunk('Test ')
        history.add_streaming_chunk('Chunk')
        
        stats = history.get_streaming_stats()
        
        assert stats['is_streaming'] is True
        assert stats['agent'] == 'grading'
        assert stats['chunk_count'] == 2
        assert stats['total_chars'] == 10


class TestMasterAgentStreaming:
    """Test MasterAgent.chat_streaming() method."""
    
    @pytest.mark.asyncio
    async def test_chat_streaming_basic(self):
        """Test basic chat_streaming functionality."""
        agent = MasterAgent()
        
        events = []
        async for event in agent.chat_streaming("Hello, how are you?"):
            events.append(event)
        
        # Should have status and chunk events
        assert len(events) > 0
        
        # Check event types
        event_types = [e['type'] for e in events]
        assert 'status' in event_types or 'chunk' in event_types
    
    @pytest.mark.asyncio
    async def test_chat_streaming_grading_workflow(self):
        """Test chat_streaming with grading request."""
        agent = MasterAgent()
        
        events = []
        async for event in agent.chat_streaming("Grade this assignment: Student work here..."):
            events.append(event)
        
        # Should have events
        assert len(events) > 0
        
        # Should include grading and formatting agents
        agents = [e.get('agent') for e in events if 'agent' in e]
        # May include: master, grading, formatting
        assert len(set(agents)) > 1
    
    @pytest.mark.asyncio
    async def test_chat_streaming_error_handling(self):
        """Test that streaming handles errors gracefully."""
        agent = MasterAgent()
        
        # Test with empty input (should error)
        events = []
        async for event in agent.chat_streaming(""):
            events.append(event)
        
        # Should have error event
        error_events = [e for e in events if e['type'] == 'error']
        assert len(error_events) > 0
    
    @pytest.mark.asyncio
    async def test_chat_streaming_yields_chunks(self):
        """Test that streaming yields multiple chunks."""
        agent = MasterAgent()
        
        chunk_count = 0
        async for event in agent.chat_streaming("Tell me a short story"):
            if event['type'] == 'chunk':
                chunk_count += 1
        
        # Should have received chunks
        assert chunk_count > 0


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
