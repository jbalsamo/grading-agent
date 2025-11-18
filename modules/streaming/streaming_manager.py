"""
StreamingManager - Coordinates streaming across agents and workflows.

This manager handles:
- Streaming event coordination
- Agent status tracking
- Chunk buffering and forwarding
- Error handling during streaming
- Progress tracking
"""
from typing import AsyncGenerator, Dict, Any, Optional, List
import time
import logging
from uuid import uuid4

# Enhanced type safety
from modules.types import (
    StreamInfo,
    StreamStatus,
    AgentType,
    StreamingManagerProtocol
)

logger = logging.getLogger(__name__)


class StreamingManager:
    """
    Manages streaming operations across multiple agents.
    
    Coordinates streaming from LangGraph astream_events() and agent
    stream_process() methods, providing unified streaming interface.
    """
    
    def __init__(self):
        """Initialize the streaming manager."""
        self.active_streams: Dict[str, Dict[str, Any]] = {}
        self.chunk_buffers: Dict[str, List[str]] = {}
        self.stream_metadata: Dict[str, Dict[str, Any]] = {}
        logger.info("StreamingManager initialized")
    
    def create_stream(
        self,
        stream_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new streaming session.
        
        Args:
            stream_id: Optional custom stream ID
            agent_name: Name of the agent streaming
            metadata: Additional metadata for the stream
            
        Returns:
            Stream ID for tracking
        """
        if stream_id is None:
            stream_id = str(uuid4())
        
        self.active_streams[stream_id] = {
            'agent_name': agent_name or 'unknown',
            'status': 'streaming',
            'start_time': time.time(),
            'chunk_count': 0,
            'total_chars': 0
        }
        
        self.chunk_buffers[stream_id] = []
        self.stream_metadata[stream_id] = metadata or {}
        
        logger.info(f"Created stream {stream_id} for agent {agent_name}")
        return stream_id
    
    def add_chunk(self, stream_id: str, chunk: str) -> None:
        """
        Add a chunk to the stream buffer.
        
        Args:
            stream_id: Stream identifier
            chunk: Text chunk to add
        """
        if stream_id not in self.active_streams:
            logger.warning(f"Attempt to add chunk to non-existent stream {stream_id}")
            return
        
        self.chunk_buffers[stream_id].append(chunk)
        self.active_streams[stream_id]['chunk_count'] += 1
        self.active_streams[stream_id]['total_chars'] += len(chunk)
    
    def get_chunks(self, stream_id: str) -> List[str]:
        """
        Get all chunks for a stream.
        
        Args:
            stream_id: Stream identifier
            
        Returns:
            List of chunks
        """
        return self.chunk_buffers.get(stream_id, [])
    
    def get_full_content(self, stream_id: str) -> str:
        """
        Get full content by joining all chunks.
        
        Args:
            stream_id: Stream identifier
            
        Returns:
            Complete content string
        """
        return ''.join(self.chunk_buffers.get(stream_id, []))
    
    def complete_stream(self, stream_id: str) -> Dict[str, Any]:
        """
        Mark a stream as complete and return summary.
        
        Args:
            stream_id: Stream identifier
            
        Returns:
            Stream summary with metrics
        """
        if stream_id not in self.active_streams:
            return {}
        
        stream_info = self.active_streams[stream_id]
        stream_info['status'] = 'complete'
        stream_info['end_time'] = time.time()
        stream_info['duration'] = stream_info['end_time'] - stream_info['start_time']
        stream_info['full_content'] = self.get_full_content(stream_id)
        
        logger.info(
            f"Stream {stream_id} complete: "
            f"{stream_info['chunk_count']} chunks, "
            f"{stream_info['total_chars']} chars, "
            f"{stream_info['duration']:.2f}s"
        )
        
        return stream_info
    
    def error_stream(self, stream_id: str, error: str) -> None:
        """
        Mark a stream as errored.
        
        Args:
            stream_id: Stream identifier
            error: Error message
        """
        if stream_id not in self.active_streams:
            return
        
        self.active_streams[stream_id]['status'] = 'error'
        self.active_streams[stream_id]['error'] = error
        self.active_streams[stream_id]['end_time'] = time.time()
        
        logger.error(f"Stream {stream_id} encountered error: {error}")
    
    def get_stream_status(self, stream_id: str) -> Dict[str, Any]:
        """
        Get current status of a stream.
        
        Args:
            stream_id: Stream identifier
            
        Returns:
            Stream status information
        """
        return self.active_streams.get(stream_id, {})
    
    def cleanup_stream(self, stream_id: str) -> None:
        """
        Clean up stream resources.
        
        Args:
            stream_id: Stream identifier
        """
        if stream_id in self.active_streams:
            del self.active_streams[stream_id]
        if stream_id in self.chunk_buffers:
            del self.chunk_buffers[stream_id]
        if stream_id in self.stream_metadata:
            del self.stream_metadata[stream_id]
        
        logger.debug(f"Cleaned up stream {stream_id}")
    
    async def stream_from_agent(
        self,
        agent_generator: AsyncGenerator[str, None],
        agent_name: str,
        on_chunk: Optional[callable] = None
    ) -> str:
        """
        Stream from an agent's stream_process method.
        
        Args:
            agent_generator: Async generator from agent.stream_process()
            agent_name: Name of the agent
            on_chunk: Optional callback for each chunk
            
        Returns:
            Complete content from stream
        """
        stream_id = self.create_stream(agent_name=agent_name)
        
        try:
            async for chunk in agent_generator:
                self.add_chunk(stream_id, chunk)
                
                if on_chunk:
                    on_chunk(chunk)
            
            summary = self.complete_stream(stream_id)
            return summary.get('full_content', '')
            
        except Exception as e:
            self.error_stream(stream_id, str(e))
            logger.error(f"Error streaming from {agent_name}: {e}")
            raise
        
        finally:
            # Don't cleanup immediately - let caller retrieve data first
            pass
    
    async def stream_multi_agent_workflow(
        self,
        workflow_steps: List[Dict[str, Any]],
        on_agent_start: Optional[callable] = None,
        on_agent_complete: Optional[callable] = None,
        on_chunk: Optional[callable] = None
    ) -> Dict[str, str]:
        """
        Stream from a multi-agent workflow.
        
        Args:
            workflow_steps: List of workflow steps with agent info
            on_agent_start: Callback when agent starts
            on_agent_complete: Callback when agent completes
            on_chunk: Callback for each chunk
            
        Returns:
            Dictionary of agent_name -> content
        """
        results = {}
        
        for step in workflow_steps:
            agent_name = step.get('agent_name')
            agent_generator = step.get('generator')
            
            if on_agent_start:
                on_agent_start(agent_name)
            
            content = await self.stream_from_agent(
                agent_generator,
                agent_name,
                on_chunk=on_chunk
            )
            
            results[agent_name] = content
            
            if on_agent_complete:
                on_agent_complete(agent_name, content)
        
        return results
    
    def get_all_active_streams(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all active streams.
        
        Returns:
            Dictionary of stream_id -> stream_info
        """
        return {
            stream_id: info
            for stream_id, info in self.active_streams.items()
            if info.get('status') == 'streaming'
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get overall streaming metrics.
        
        Returns:
            Metrics dictionary
        """
        total_streams = len(self.active_streams)
        active_streams = len(self.get_all_active_streams())
        
        total_chunks = sum(
            info.get('chunk_count', 0)
            for info in self.active_streams.values()
        )
        
        total_chars = sum(
            info.get('total_chars', 0)
            for info in self.active_streams.values()
        )
        
        return {
            'total_streams': total_streams,
            'active_streams': active_streams,
            'total_chunks': total_chunks,
            'total_chars': total_chars
        }
