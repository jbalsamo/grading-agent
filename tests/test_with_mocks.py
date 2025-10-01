"""
Example tests using mocks to avoid API dependency.
"""
import pytest
import sys
import os
from unittest.mock import patch, Mock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.security import InputValidator, RateLimiter
from modules.performance import ResponseCache, TokenOptimizer
from modules.monitoring import MetricsCollector
from tests.mocks import (
    MockAzureChatOpenAI,
    MockDataManager,
    MockConversationHistory,
    MockSpecializedAgent,
    create_mock_config
)


class TestInputValidation:
    """Test input validation without API calls."""
    
    def test_validate_empty_input(self):
        """Test validation rejects empty input."""
        validator = InputValidator()
        result = validator.validate_input("")
        assert result["valid"] is False
        assert "empty" in result["error"].lower()
    
    def test_validate_too_long_input(self):
        """Test validation rejects too long input."""
        validator = InputValidator()
        # Create input longer than max length
        long_input = "a" * 10001
        result = validator.validate_input(long_input)
        assert result["valid"] is False
        assert "too long" in result["error"].lower()
    
    def test_validate_suspicious_patterns(self):
        """Test validation detects suspicious patterns."""
        validator = InputValidator()
        suspicious_input = "<script>alert('xss')</script>"
        result = validator.validate_input(suspicious_input)
        assert result["valid"] is False
        assert "unsafe" in result["error"].lower()
    
    def test_validate_normal_input(self):
        """Test validation accepts normal input."""
        validator = InputValidator()
        result = validator.validate_input("Hello, how are you?")
        assert result["valid"] is True
        assert result["error"] is None
    
    def test_sanitize_input(self):
        """Test input sanitization."""
        validator = InputValidator()
        dirty_input = "  Hello   World  \x00  "
        clean = validator.sanitize_input(dirty_input)
        # Check that multiple spaces are condensed and null bytes removed
        assert "Hello World" in clean
        assert "\x00" not in clean
        # Verify no multiple consecutive spaces
        assert "  " not in clean


class TestRateLimiting:
    """Test rate limiting without API calls."""
    
    def test_rate_limit_allows_initial_requests(self):
        """Test rate limiter allows requests under limit."""
        limiter = RateLimiter(max_calls=5, time_window=60)
        
        for i in range(5):
            result = limiter.check_rate_limit("test_user")
            assert result["allowed"] is True
    
    def test_rate_limit_blocks_excess_requests(self):
        """Test rate limiter blocks requests over limit."""
        limiter = RateLimiter(max_calls=3, time_window=60)
        
        # Make 3 allowed requests
        for i in range(3):
            limiter.check_rate_limit("test_user")
        
        # 4th request should be blocked
        result = limiter.check_rate_limit("test_user")
        assert result["allowed"] is False
        assert result["retry_after"] > 0
    
    def test_rate_limit_reset(self):
        """Test rate limiter can be reset."""
        limiter = RateLimiter(max_calls=2, time_window=60)
        
        # Use up limit
        limiter.check_rate_limit("test_user")
        limiter.check_rate_limit("test_user")
        
        # Reset
        limiter.reset("test_user")
        
        # Should be allowed again
        result = limiter.check_rate_limit("test_user")
        assert result["allowed"] is True


class TestResponseCache:
    """Test response caching without API calls."""
    
    def test_cache_miss(self):
        """Test cache returns None on miss."""
        cache = ResponseCache()
        result = cache.get("test input")
        assert result is None
    
    def test_cache_hit(self):
        """Test cache returns cached value on hit."""
        cache = ResponseCache()
        cache.set("test input", "test response")
        result = cache.get("test input")
        assert result == "test response"
    
    def test_cache_stats(self):
        """Test cache statistics tracking."""
        cache = ResponseCache()
        
        # Miss
        cache.get("input1")
        
        # Set and hit
        cache.set("input1", "response1")
        cache.get("input1")
        
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["size"] == 1
    
    def test_cache_clear(self):
        """Test cache can be cleared."""
        cache = ResponseCache()
        cache.set("input1", "response1")
        cache.clear()
        
        result = cache.get("input1")
        assert result is None
        assert cache.get_stats()["size"] == 0


class TestTokenOptimizer:
    """Test token optimization without API calls."""
    
    def test_estimate_tokens(self):
        """Test token estimation."""
        text = "Hello world"  # ~11 chars, ~2-3 tokens estimated
        tokens = TokenOptimizer.estimate_tokens(text)
        assert tokens > 0
        assert tokens < len(text)  # Should be less than character count
    
    def test_optimize_history_within_budget(self):
        """Test history optimization stays within budget."""
        messages = [
            {"role": "user", "content": "a" * 100},
            {"role": "assistant", "content": "b" * 100},
            {"role": "user", "content": "c" * 100},
        ]
        
        # Very low budget should only keep recent messages
        optimized = TokenOptimizer.get_optimized_history(messages, max_tokens=50)
        assert len(optimized) < len(messages)
    
    def test_summarize_old_messages(self):
        """Test old message summarization."""
        messages = [
            {"role": "user", "content": f"message {i}"} for i in range(10)
        ]
        
        summarized = TokenOptimizer.summarize_old_messages(messages, keep_recent=3)
        
        # Should have 1 summary + 3 recent messages
        assert len(summarized) == 4
        assert summarized[0]["role"] == "system"
        assert "summary" in summarized[0]["content"].lower()


class TestMetricsCollector:
    """Test metrics collection without API calls."""
    
    def test_record_request(self):
        """Test recording metrics."""
        collector = MetricsCollector()
        collector.record_request("chat", 0.5, success=True)
        
        metrics = collector.get_metrics()
        assert metrics["total_requests"] == 1
        assert metrics["total_errors"] == 0
        assert "chat" in metrics["agents"]
    
    def test_record_error(self):
        """Test recording error metrics."""
        collector = MetricsCollector()
        collector.record_request("chat", 0.5, success=False, error="Test error")
        
        metrics = collector.get_metrics()
        assert metrics["total_errors"] == 1
        assert metrics["agents"]["chat"]["error_count"] == 1
    
    def test_prometheus_format(self):
        """Test Prometheus format export."""
        collector = MetricsCollector()
        collector.record_request("chat", 0.5, success=True)
        
        prometheus = collector.get_prometheus_format()
        assert "agent_uptime_seconds" in prometheus
        assert "agent_requests_total" in prometheus


class TestMockLLM:
    """Test mock LLM responses."""
    
    def test_mock_llm_basic_response(self):
        """Test mock LLM returns responses."""
        llm = MockAzureChatOpenAI()
        response = llm.invoke([Mock(content="Hello")])
        assert response.content is not None
        assert len(response.content) > 0
    
    def test_mock_llm_tracks_calls(self):
        """Test mock LLM tracks call history."""
        llm = MockAzureChatOpenAI()
        llm.invoke([Mock(content="Test 1")])
        llm.invoke([Mock(content="Test 2")])
        
        assert llm.call_count == 2
        assert len(llm.call_history) == 2


class TestMockDataManager:
    """Test mock data manager."""
    
    def test_store_interaction(self):
        """Test storing interactions."""
        manager = MockDataManager()
        result = manager.store_interaction({"test": "data"})
        assert result is True
        assert len(manager.interactions) == 1
    
    def test_get_relevant_context(self):
        """Test getting relevant context."""
        manager = MockDataManager()
        manager.store_interaction({"user_input": "test", "response": "data"})
        
        context = manager.get_relevant_context("test")
        assert context["context_count"] > 0


class TestMockConversationHistory:
    """Test mock conversation history."""
    
    def test_add_messages(self):
        """Test adding messages."""
        history = MockConversationHistory()
        history.add_user_message("Hello")
        history.add_assistant_message("Hi there", "chat")
        
        assert len(history) == 2
    
    def test_trim_messages(self):
        """Test message trimming."""
        history = MockConversationHistory(max_messages=5)
        
        # Add more than max
        for i in range(10):
            history.add_user_message(f"Message {i}")
        
        assert len(history) == 5
    
    def test_get_stats(self):
        """Test getting statistics."""
        history = MockConversationHistory()
        history.add_user_message("Hello")
        history.add_assistant_message("Hi", "chat")
        
        stats = history.get_stats()
        assert stats["total_messages"] == 2
        assert stats["user_messages"] == 1
        assert stats["assistant_messages"] == 1


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
