"""
Performance optimization utilities including caching and token management.
"""
import hashlib
import time
from typing import Dict, Any, Optional, List
from collections import OrderedDict
import logging
from .config import config

logger = logging.getLogger(__name__)


class ResponseCache:
    """Simple TTL-based cache for agent responses."""
    
    def __init__(self, max_size: int = None, ttl: int = None):
        """Initialize response cache.
        
        Args:
            max_size: Maximum number of cached items
            ttl: Time-to-live in seconds for cached items
        """
        self.max_size = max_size or config.cache_max_size
        self.ttl = ttl or config.cache_ttl
        self.enabled = config.enable_response_cache
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: Dict[str, float] = {}
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, user_input: str, context: Optional[str] = None) -> str:
        """Generate cache key from input and context.
        
        Args:
            user_input: The user's input
            context: Optional context string
            
        Returns:
            Cache key hash
        """
        data = user_input
        if context:
            data += context
        return hashlib.md5(data.encode()).hexdigest()
    
    def get(self, user_input: str, context: Optional[str] = None) -> Optional[str]:
        """Get cached response if available and not expired.
        
        Args:
            user_input: The user's input
            context: Optional context string
            
        Returns:
            Cached response or None
        """
        if not self.enabled:
            return None
        
        key = self._generate_key(user_input, context)
        
        # Check if key exists and not expired
        if key in self.cache:
            timestamp = self.timestamps.get(key, 0)
            if time.time() - timestamp < self.ttl:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                self.hits += 1
                logger.debug(f"Cache hit for key: {key[:8]}...")
                return self.cache[key]
            else:
                # Expired, remove
                del self.cache[key]
                del self.timestamps[key]
        
        self.misses += 1
        return None
    
    def set(self, user_input: str, response: str, context: Optional[str] = None):
        """Cache a response.
        
        Args:
            user_input: The user's input
            response: The agent's response
            context: Optional context string
        """
        if not self.enabled:
            return
        
        key = self._generate_key(user_input, context)
        
        # Remove oldest if at capacity
        if len(self.cache) >= self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]
            logger.debug(f"Cache evicted oldest entry: {oldest_key[:8]}...")
        
        self.cache[key] = response
        self.timestamps[key] = time.time()
        logger.debug(f"Cached response for key: {key[:8]}...")
    
    def clear(self):
        """Clear all cached items."""
        self.cache.clear()
        self.timestamps.clear()
        self.hits = 0
        self.misses = 0
        logger.info("Response cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dict with cache stats
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "enabled": self.enabled,
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 2),
            "ttl": self.ttl
        }


class TokenOptimizer:
    """Utilities for optimizing token usage in conversations."""
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Rough estimation of token count (without tiktoken dependency).
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        # Rough estimation: ~4 characters per token on average
        return len(text) // 4
    
    @staticmethod
    def get_optimized_history(messages: List[Dict[str, str]], max_tokens: int = 2000) -> List[Dict[str, str]]:
        """Get conversation history optimized to fit within token budget.
        
        Args:
            messages: List of message dictionaries
            max_tokens: Maximum tokens to include
            
        Returns:
            Optimized list of messages
        """
        if not messages:
            return []
        
        # Start with most recent messages
        optimized = []
        total_tokens = 0
        
        for message in reversed(messages):
            msg_tokens = TokenOptimizer.estimate_tokens(message.get("content", ""))
            if total_tokens + msg_tokens > max_tokens:
                break
            optimized.insert(0, message)
            total_tokens += msg_tokens
        
        logger.debug(f"Optimized history: {len(optimized)}/{len(messages)} messages, ~{total_tokens} tokens")
        return optimized
    
    @staticmethod
    def summarize_old_messages(messages: List[Dict[str, str]], keep_recent: int = 5) -> List[Dict[str, str]]:
        """Create a summary placeholder for old messages.
        
        Args:
            messages: List of message dictionaries
            keep_recent: Number of recent messages to keep in full
            
        Returns:
            List with summary and recent messages
        """
        if len(messages) <= keep_recent:
            return messages
        
        old_messages = messages[:-keep_recent]
        recent_messages = messages[-keep_recent:]
        
        # Create summary
        summary_content = f"[Previous conversation summary: {len(old_messages)} earlier messages]"
        summary_message = {"role": "system", "content": summary_content}
        
        return [summary_message] + recent_messages


class PerformanceMonitor:
    """Monitor performance metrics for optimization insights."""
    
    def __init__(self):
        self.token_usage: List[int] = []
        self.cache_checks = 0
        self.optimizations_applied = 0
    
    def record_token_usage(self, tokens: int):
        """Record token usage for analysis."""
        self.token_usage.append(tokens)
        
        # Keep only last 1000 records
        if len(self.token_usage) > 1000:
            self.token_usage = self.token_usage[-1000:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self.token_usage:
            return {
                "avg_tokens": 0,
                "max_tokens": 0,
                "total_requests": 0,
                "optimizations_applied": self.optimizations_applied
            }
        
        return {
            "avg_tokens": round(sum(self.token_usage) / len(self.token_usage), 2),
            "max_tokens": max(self.token_usage),
            "min_tokens": min(self.token_usage),
            "total_requests": len(self.token_usage),
            "optimizations_applied": self.optimizations_applied
        }
