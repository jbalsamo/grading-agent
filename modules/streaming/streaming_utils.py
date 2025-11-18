"""
Streaming utilities for buffering and progress tracking.

Provides helper classes for streaming operations:
- ChunkBuffer: Efficient chunk buffering and retrieval
- StreamingProgressTracker: Track streaming progress and metrics
"""
from typing import List, Dict, Any, Optional
import time
from collections import deque
import logging

logger = logging.getLogger(__name__)


class ChunkBuffer:
    """
    Buffer for managing streaming chunks efficiently.
    
    Provides:
    - Efficient chunk storage
    - Memory-bounded buffering
    - Chunk retrieval and joining
    - Buffer statistics
    """
    
    def __init__(self, max_chunks: int = 1000):
        """
        Initialize chunk buffer.
        
        Args:
            max_chunks: Maximum number of chunks to buffer
        """
        self.max_chunks = max_chunks
        self.chunks: deque = deque(maxlen=max_chunks)
        self.total_chunks = 0
        self.total_chars = 0
        self.overflow_count = 0
    
    def add_chunk(self, chunk: str) -> None:
        """
        Add a chunk to the buffer.
        
        Args:
            chunk: Text chunk to add
        """
        if len(self.chunks) >= self.max_chunks:
            self.overflow_count += 1
        
        self.chunks.append(chunk)
        self.total_chunks += 1
        self.total_chars += len(chunk)
    
    def get_chunks(self, start: int = 0, end: Optional[int] = None) -> List[str]:
        """
        Get chunks in range.
        
        Args:
            start: Start index (inclusive)
            end: End index (exclusive), None for all
            
        Returns:
            List of chunks in range
        """
        chunks_list = list(self.chunks)
        if end is None:
            return chunks_list[start:]
        return chunks_list[start:end]
    
    def get_full_content(self) -> str:
        """
        Get all chunks joined as single string.
        
        Returns:
            Complete buffered content
        """
        return ''.join(self.chunks)
    
    def get_last_n_chunks(self, n: int) -> List[str]:
        """
        Get last N chunks.
        
        Args:
            n: Number of recent chunks to retrieve
            
        Returns:
            List of last N chunks
        """
        chunks_list = list(self.chunks)
        return chunks_list[-n:] if n <= len(chunks_list) else chunks_list
    
    def clear(self) -> None:
        """Clear all buffered chunks."""
        self.chunks.clear()
        self.total_chunks = 0
        self.total_chars = 0
        self.overflow_count = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get buffer statistics.
        
        Returns:
            Dictionary with buffer stats
        """
        return {
            'buffered_chunks': len(self.chunks),
            'total_chunks': self.total_chunks,
            'total_chars': self.total_chars,
            'overflow_count': self.overflow_count,
            'max_chunks': self.max_chunks
        }


class StreamingProgressTracker:
    """
    Track progress and metrics during streaming.
    
    Provides:
    - Real-time progress tracking
    - Performance metrics
    - Throughput calculation
    - Status reporting
    """
    
    def __init__(self, expected_agents: Optional[List[str]] = None):
        """
        Initialize progress tracker.
        
        Args:
            expected_agents: List of expected agent names
        """
        self.expected_agents = expected_agents or []
        self.agent_progress: Dict[str, Dict[str, Any]] = {}
        self.global_start_time = time.time()
        self.global_end_time: Optional[float] = None
        
        # Initialize agent tracking
        for agent in self.expected_agents:
            self.agent_progress[agent] = {
                'status': 'pending',
                'start_time': None,
                'end_time': None,
                'chunk_count': 0,
                'char_count': 0,
                'error': None
            }
    
    def start_agent(self, agent_name: str) -> None:
        """
        Mark an agent as started.
        
        Args:
            agent_name: Name of the agent
        """
        if agent_name not in self.agent_progress:
            self.agent_progress[agent_name] = {
                'status': 'streaming',
                'start_time': time.time(),
                'end_time': None,
                'chunk_count': 0,
                'char_count': 0,
                'error': None
            }
        else:
            self.agent_progress[agent_name]['status'] = 'streaming'
            self.agent_progress[agent_name]['start_time'] = time.time()
        
        logger.info(f"Agent {agent_name} started streaming")
    
    def add_chunk(self, agent_name: str, chunk: str) -> None:
        """
        Record a chunk for an agent.
        
        Args:
            agent_name: Name of the agent
            chunk: Text chunk
        """
        if agent_name not in self.agent_progress:
            self.start_agent(agent_name)
        
        self.agent_progress[agent_name]['chunk_count'] += 1
        self.agent_progress[agent_name]['char_count'] += len(chunk)
    
    def complete_agent(self, agent_name: str) -> None:
        """
        Mark an agent as complete.
        
        Args:
            agent_name: Name of the agent
        """
        if agent_name in self.agent_progress:
            self.agent_progress[agent_name]['status'] = 'complete'
            self.agent_progress[agent_name]['end_time'] = time.time()
            
            # Calculate duration only if start_time is set
            start_time = self.agent_progress[agent_name].get('start_time')
            if start_time is not None:
                duration = (
                    self.agent_progress[agent_name]['end_time'] - start_time
                )
                
                logger.info(
                    f"Agent {agent_name} completed: "
                    f"{self.agent_progress[agent_name]['chunk_count']} chunks "
                    f"in {duration:.2f}s"
                )
            else:
                logger.warning(f"Agent {agent_name} completed but was never started")
    
    def error_agent(self, agent_name: str, error: str) -> None:
        """
        Mark an agent as errored.
        
        Args:
            agent_name: Name of the agent
            error: Error message
        """
        if agent_name in self.agent_progress:
            self.agent_progress[agent_name]['status'] = 'error'
            self.agent_progress[agent_name]['error'] = error
            self.agent_progress[agent_name]['end_time'] = time.time()
            
            logger.error(f"Agent {agent_name} error: {error}")
    
    def get_agent_status(self, agent_name: str) -> str:
        """
        Get status of an agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Status string (pending, streaming, complete, error)
        """
        return self.agent_progress.get(agent_name, {}).get('status', 'unknown')
    
    def get_overall_progress(self) -> float:
        """
        Get overall progress percentage.
        
        Returns:
            Progress as percentage (0-100)
        """
        if not self.expected_agents:
            return 0.0
        
        completed = sum(
            1 for agent in self.expected_agents
            if self.get_agent_status(agent) in ('complete', 'error')
        )
        
        return (completed / len(self.expected_agents)) * 100.0
    
    def is_complete(self) -> bool:
        """
        Check if all agents are complete.
        
        Returns:
            True if all expected agents are done
        """
        if not self.expected_agents:
            return False
        
        return all(
            self.get_agent_status(agent) in ('complete', 'error')
            for agent in self.expected_agents
        )
    
    def complete_workflow(self) -> None:
        """Mark the entire workflow as complete."""
        self.global_end_time = time.time()
        logger.info("Workflow streaming complete")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive metrics.
        
        Returns:
            Dictionary with all metrics
        """
        total_chunks = sum(
            info.get('chunk_count', 0)
            for info in self.agent_progress.values()
        )
        
        total_chars = sum(
            info.get('char_count', 0)
            for info in self.agent_progress.values()
        )
        
        completed_agents = sum(
            1 for info in self.agent_progress.values()
            if info.get('status') == 'complete'
        )
        
        errored_agents = sum(
            1 for info in self.agent_progress.values()
            if info.get('status') == 'error'
        )
        
        duration = (
            self.global_end_time or time.time()
        ) - self.global_start_time
        
        return {
            'total_agents': len(self.expected_agents),
            'completed_agents': completed_agents,
            'errored_agents': errored_agents,
            'progress_pct': self.get_overall_progress(),
            'total_chunks': total_chunks,
            'total_chars': total_chars,
            'duration': duration,
            'chunks_per_sec': total_chunks / duration if duration > 0 else 0,
            'chars_per_sec': total_chars / duration if duration > 0 else 0,
            'agent_details': self.agent_progress
        }
    
    def get_summary(self) -> str:
        """
        Get human-readable summary.
        
        Returns:
            Summary string
        """
        metrics = self.get_metrics()
        
        return f"""Streaming Progress:
  Progress: {metrics['progress_pct']:.1f}%
  Agents: {metrics['completed_agents']}/{metrics['total_agents']} complete
  Chunks: {metrics['total_chunks']} ({metrics['chunks_per_sec']:.1f}/sec)
  Chars: {metrics['total_chars']} ({metrics['chars_per_sec']:.1f}/sec)
  Duration: {metrics['duration']:.2f}s
  Errors: {metrics['errored_agents']}"""
