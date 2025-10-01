"""
Security utilities for input validation and rate limiting.
"""
import time
import re
from typing import Dict, Any, Optional
from functools import wraps
import logging
from .config import config

logger = logging.getLogger(__name__)


class InputValidator:
    """Validates user input for security and safety."""
    
    @staticmethod
    def validate_input(user_input: str) -> Dict[str, Any]:
        """Validate user input and return validation result.
        
        Args:
            user_input: The user's input string
            
        Returns:
            Dict with 'valid' bool and 'error' message if invalid
        """
        if not user_input or not user_input.strip():
            return {"valid": False, "error": "Input cannot be empty"}
        
        # Check length
        if len(user_input) > config.max_input_length:
            return {
                "valid": False, 
                "error": f"Input too long (max {config.max_input_length} characters)"
            }
        
        # Check for suspicious patterns (basic protection)
        suspicious_patterns = [
            r'<script[^>]*>.*?</script>',  # XSS attempts
            r'javascript:',  # JavaScript protocol
            r'on\w+\s*=',  # Event handlers
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                logger.warning(f"Suspicious pattern detected in input: {pattern}")
                return {
                    "valid": False,
                    "error": "Input contains potentially unsafe content"
                }
        
        return {"valid": True, "error": None}
    
    @staticmethod
    def sanitize_input(user_input: str) -> str:
        """Sanitize user input by removing potentially harmful content.
        
        Args:
            user_input: The user's input string
            
        Returns:
            Sanitized input string
        """
        # Strip whitespace
        sanitized = user_input.strip()
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        # Limit consecutive whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        return sanitized


class RateLimiter:
    """Simple in-memory rate limiter for API calls."""
    
    def __init__(self, max_calls: int = None, time_window: int = None):
        """Initialize rate limiter.
        
        Args:
            max_calls: Maximum number of calls allowed in time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls or config.rate_limit_calls
        self.time_window = time_window or config.rate_limit_period
        self.calls: Dict[str, list] = {}
        self.enabled = config.rate_limit_enabled
    
    def check_rate_limit(self, identifier: str = "default") -> Dict[str, Any]:
        """Check if rate limit is exceeded for given identifier.
        
        Args:
            identifier: Unique identifier for the caller (e.g., user_id, session_id)
            
        Returns:
            Dict with 'allowed' bool and 'retry_after' seconds if blocked
        """
        if not self.enabled:
            return {"allowed": True, "retry_after": 0}
        
        now = time.time()
        
        # Initialize or clean old calls
        if identifier not in self.calls:
            self.calls[identifier] = []
        
        # Remove calls outside the time window
        self.calls[identifier] = [
            call_time for call_time in self.calls[identifier]
            if call_time > now - self.time_window
        ]
        
        # Check if limit exceeded
        if len(self.calls[identifier]) >= self.max_calls:
            oldest_call = min(self.calls[identifier])
            retry_after = int(self.time_window - (now - oldest_call))
            logger.warning(f"Rate limit exceeded for {identifier}")
            return {"allowed": False, "retry_after": retry_after}
        
        # Record this call
        self.calls[identifier].append(now)
        return {"allowed": True, "retry_after": 0}
    
    def reset(self, identifier: str = "default"):
        """Reset rate limit for given identifier."""
        if identifier in self.calls:
            del self.calls[identifier]
            logger.info(f"Rate limit reset for {identifier}")


def rate_limit(identifier: str = "default"):
    """Decorator for rate limiting functions.
    
    Args:
        identifier: Unique identifier for rate limiting
    """
    limiter = RateLimiter()
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = limiter.check_rate_limit(identifier)
            if not result["allowed"]:
                raise RateLimitException(
                    f"Rate limit exceeded. Try again in {result['retry_after']} seconds."
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


class RateLimitException(Exception):
    """Exception raised when rate limit is exceeded."""
    pass


class SecurityException(Exception):
    """Base exception for security-related errors."""
    pass


class InputValidationException(SecurityException):
    """Exception raised when input validation fails."""
    pass
