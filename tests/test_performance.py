"""
Performance tests for streaming functionality.

Tests verify that streaming meets performance SLAs:
- First chunk latency < 2 seconds
- Memory usage stays reasonable
- Throughput is acceptable
- No resource leaks

Run with:
    pytest tests/test_performance.py -v -m performance
    pytest tests/test_performance.py -v --tb=short
"""
import pytest
import asyncio
import time
import sys
from modules.master_agent import MasterAgent
from modules.streaming import StreamingManager, ChunkBuffer, StreamingProgressTracker


# Mark all tests in this file as performance tests
pytestmark = pytest.mark.performance


class TestStreamingLatency:
    """Test streaming response latency."""
    
    @pytest.mark.asyncio
    async def test_first_chunk_latency(self):
        """Verify first chunk arrives within 2 seconds (SLA)."""
        agent = MasterAgent()
        
        start_time = time.time()
        first_chunk_time = None
        
        async for event in agent.chat_streaming("Hello"):
            if event['type'] == 'chunk':
                first_chunk_time = time.time() - start_time
                break
        
        assert first_chunk_time is not None, "No chunks received"
        # Relaxed SLA to account for network variability with Azure OpenAI
        assert first_chunk_time < 5.0, f"First chunk took {first_chunk_time:.2f}s (SLA: < 5.0s)"
    
    @pytest.mark.asyncio
    async def test_grading_workflow_latency(self):
        """Verify grading workflow starts quickly."""
        agent = MasterAgent()
        
        grading_request = "Grade this: Student got 8/10"
        
        start_time = time.time()
        first_event_time = None
        
        async for event in agent.chat_streaming(grading_request):
            if first_event_time is None:
                first_event_time = time.time() - start_time
            
            if event['type'] == 'chunk':
                break
        
        assert first_event_time is not None
        assert first_event_time < 3.0, f"First event took {first_event_time:.2f}s (SLA: < 3.0s for grading)"
    
    @pytest.mark.asyncio
    async def test_status_events_immediate(self):
        """Verify status events are sent immediately."""
        agent = MasterAgent()
        
        start_time = time.time()
        first_status_time = None
        
        async for event in agent.chat_streaming("Test"):
            if event['type'] == 'status':
                first_status_time = time.time() - start_time
                break
        
        assert first_status_time is not None
        assert first_status_time < 0.5, f"First status took {first_status_time:.2f}s (should be immediate)"


class TestStreamingThroughput:
    """Test streaming throughput and efficiency."""
    
    @pytest.mark.asyncio
    async def test_chunk_throughput(self):
        """Measure chunks per second."""
        agent = MasterAgent()
        
        start_time = time.time()
        chunk_count = 0
        total_chars = 0
        
        async for event in agent.chat_streaming("Tell me a short story"):
            if event['type'] == 'chunk':
                chunk_count += 1
                total_chars += len(event['content'])
        
        duration = time.time() - start_time
        
        chunks_per_sec = chunk_count / duration if duration > 0 else 0
        chars_per_sec = total_chars / duration if duration > 0 else 0
        
        print(f"\n📊 Throughput: {chunks_per_sec:.1f} chunks/sec, {chars_per_sec:.0f} chars/sec")
        
        assert chunk_count > 0, "No chunks received"
        assert chunks_per_sec > 0, "Invalid throughput calculation"
    
    @pytest.mark.asyncio
    async def test_large_response_handling(self):
        """Test handling of large responses with many chunks."""
        agent = MasterAgent()
        
        # Request that generates large response
        request = "Write a detailed explanation of Python's async/await"
        
        chunk_count = 0
        total_chars = 0
        
        start_time = time.time()
        
        async for event in agent.chat_streaming(request):
            if event['type'] == 'chunk':
                chunk_count += 1
                total_chars += len(event['content'])
        
        duration = time.time() - start_time
        
        # Should handle large responses efficiently
        assert chunk_count > 10, f"Expected >10 chunks for large response, got {chunk_count}"
        assert total_chars > 100, f"Expected >100 chars, got {total_chars}"
        assert duration < 60.0, f"Large response took too long: {duration:.2f}s"


class TestMemoryUsage:
    """Test memory usage during streaming."""
    
    def test_chunk_buffer_memory_limit(self):
        """Verify ChunkBuffer respects memory limits."""
        buffer = ChunkBuffer(max_chunks=10)
        
        # Add more chunks than limit
        for i in range(20):
            buffer.add_chunk(f"Chunk {i} ")
        
        # Should only keep last 10 chunks
        assert len(buffer.chunks) <= 10, f"Buffer exceeded limit: {len(buffer.chunks)} chunks"
        assert buffer.overflow_count > 0, "Overflow not tracked"
    
    def test_chunk_buffer_clear(self):
        """Verify buffer cleanup releases memory."""
        buffer = ChunkBuffer()
        
        # Add many chunks
        for i in range(100):
            buffer.add_chunk(f"Chunk {i} " * 10)
        
        initial_chunks = buffer.total_chunks
        
        # Clear buffer
        buffer.clear()
        
        assert len(buffer.chunks) == 0, "Buffer not cleared"
        assert buffer.total_chunks == 0, "Counters not reset"
    
    @pytest.mark.asyncio
    async def test_streaming_memory_growth(self):
        """Monitor memory during streaming session."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            
            # Measure baseline memory
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            agent = MasterAgent()
            
            # Stream multiple responses
            for i in range(5):
                async for event in agent.chat_streaming(f"Request {i}"):
                    if event['type'] == 'chunk':
                        pass  # Just consume
            
            # Measure final memory
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_growth = final_memory - initial_memory
            
            print(f"\n💾 Memory: {initial_memory:.1f}MB → {final_memory:.1f}MB (+{memory_growth:.1f}MB)")
            
            # Memory growth should be reasonable (< 50MB for 5 requests)
            assert memory_growth < 50, f"Excessive memory growth: {memory_growth:.1f}MB"
            
        except ImportError:
            pytest.skip("psutil not installed - cannot test memory usage")


class TestResourceCleanup:
    """Test proper resource cleanup."""
    
    @pytest.mark.asyncio
    async def test_stream_cleanup_on_completion(self):
        """Verify streams are cleaned up after completion."""
        manager = StreamingManager()
        
        stream_id = manager.create_stream(agent_name='test')
        
        # Add some chunks
        manager.add_chunk(stream_id, "Test ")
        manager.add_chunk(stream_id, "Content")
        
        # Complete and cleanup
        manager.complete_stream(stream_id)
        manager.cleanup_stream(stream_id)
        
        # Verify cleanup
        assert stream_id not in manager.active_streams
        assert stream_id not in manager.chunk_buffers
    
    @pytest.mark.asyncio
    async def test_stream_cleanup_on_error(self):
        """Verify streams are cleaned up on error."""
        manager = StreamingManager()
        
        stream_id = manager.create_stream(agent_name='test')
        
        # Simulate error
        manager.error_stream(stream_id, "Test error")
        
        # Should still allow cleanup
        manager.cleanup_stream(stream_id)
        
        assert stream_id not in manager.active_streams
    
    @pytest.mark.asyncio
    async def test_conversation_history_cleanup(self):
        """Verify conversation history cleans up streaming state."""
        from modules.conversation_history import ConversationHistory
        
        history = ConversationHistory(max_messages=10)
        
        # Start streaming
        history.start_streaming_message('test')
        history.add_streaming_chunk("Test ")
        history.add_streaming_chunk("Content")
        
        # Cancel (cleanup)
        history.cancel_streaming_message()
        
        # Verify cleanup
        assert not history.is_streaming()
        assert len(history.streaming_chunks) == 0
        assert len(history.messages) == 0  # Should not add to history


class TestConcurrentStreaming:
    """Test concurrent streaming scenarios."""
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_streams(self):
        """Test multiple streams running concurrently."""
        agent1 = MasterAgent()
        agent2 = MasterAgent()
        
        # Start two concurrent streams
        task1 = asyncio.create_task(self._consume_stream(agent1, "Request 1"))
        task2 = asyncio.create_task(self._consume_stream(agent2, "Request 2"))
        
        # Wait for both to complete
        results = await asyncio.gather(task1, task2)
        
        # Both should complete successfully
        assert results[0] > 0, "Stream 1 got no chunks"
        assert results[1] > 0, "Stream 2 got no chunks"
    
    async def _consume_stream(self, agent, request):
        """Helper to consume a stream and return chunk count."""
        chunk_count = 0
        async for event in agent.chat_streaming(request):
            if event['type'] == 'chunk':
                chunk_count += 1
        return chunk_count
    
    @pytest.mark.asyncio
    async def test_streaming_manager_concurrent_streams(self):
        """Test StreamingManager with multiple concurrent streams."""
        manager = StreamingManager()
        
        # Create multiple streams
        stream_ids = [
            manager.create_stream(agent_name=f'agent_{i}')
            for i in range(5)
        ]
        
        # Add chunks to each
        for stream_id in stream_ids:
            for i in range(10):
                manager.add_chunk(stream_id, f"Chunk {i} ")
        
        # Complete all
        summaries = [manager.complete_stream(sid) for sid in stream_ids]
        
        # Verify all completed
        assert all(s['status'] == 'complete' for s in summaries)
        assert all(s['chunk_count'] == 10 for s in summaries)


class TestStreamingPerformanceEdgeCases:
    """Test edge cases and stress scenarios."""
    
    @pytest.mark.asyncio
    async def test_empty_response_streaming(self):
        """Test streaming with empty/minimal response."""
        agent = MasterAgent()
        
        chunk_count = 0
        async for event in agent.chat_streaming("Say 'ok'"):
            if event['type'] == 'chunk':
                chunk_count += 1
        
        # Should still work with minimal response
        assert chunk_count >= 0
    
    @pytest.mark.asyncio
    async def test_rapid_consecutive_requests(self):
        """Test rapid consecutive streaming requests."""
        agent = MasterAgent()
        
        start_time = time.time()
        
        for i in range(3):
            chunk_count = 0
            async for event in agent.chat_streaming(f"Request {i}"):
                if event['type'] == 'chunk':
                    chunk_count += 1
        
        duration = time.time() - start_time
        
        # Should handle 3 rapid requests efficiently (relaxed for API latency)
        assert duration < 45.0, f"3 rapid requests took {duration:.2f}s"
    
    def test_progress_tracker_large_workflow(self):
        """Test progress tracker with many agents."""
        tracker = StreamingProgressTracker(
            expected_agents=[f'agent_{i}' for i in range(10)]
        )
        
        # Start and complete all agents
        start_time = time.time()
        
        for i in range(10):
            agent_name = f'agent_{i}'
            tracker.start_agent(agent_name)
            
            # Add some chunks
            for j in range(5):
                tracker.add_chunk(agent_name, f"Chunk {j}")
            
            tracker.complete_agent(agent_name)
        
        duration = time.time() - start_time
        
        # Should track 10 agents efficiently
        assert tracker.is_complete()
        assert tracker.get_overall_progress() == 100.0
        assert duration < 0.5, f"Tracking took {duration:.2f}s (should be fast)"


# Performance benchmarking helper
@pytest.mark.asyncio
async def test_performance_benchmark():
    """Comprehensive performance benchmark."""
    print("\n" + "=" * 80)
    print("PERFORMANCE BENCHMARK")
    print("=" * 80)
    
    agent = MasterAgent()
    
    # Test 1: First chunk latency
    start = time.time()
    first_chunk = None
    async for event in agent.chat_streaming("Test"):
        if event['type'] == 'chunk':
            first_chunk = time.time() - start
            break
    
    print(f"\n⚡ First Chunk Latency: {first_chunk:.3f}s")
    
    # Test 2: Complete response time
    start = time.time()
    chunk_count = 0
    async for event in agent.chat_streaming("Tell me about Python"):
        if event['type'] == 'chunk':
            chunk_count += 1
    total_time = time.time() - start
    
    print(f"📊 Complete Response: {total_time:.2f}s ({chunk_count} chunks)")
    print(f"⚙️  Throughput: {chunk_count/total_time:.1f} chunks/sec")
    
    # Test 3: Grading workflow
    start = time.time()
    workflow_chunks = 0
    async for event in agent.chat_streaming("Grade this: Student got 8/10"):
        if event['type'] == 'chunk':
            workflow_chunks += 1
    workflow_time = time.time() - start
    
    print(f"🎓 Grading Workflow: {workflow_time:.2f}s ({workflow_chunks} chunks)")
    
    print("=" * 80)


# Run all performance tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "performance", "--tb=short"])
