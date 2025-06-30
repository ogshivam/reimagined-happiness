"""
Rate Limiter and Retry Logic for Together AI API
"""
import time
import logging
from typing import Callable, Any, Optional
from functools import wraps
import random

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter with exponential backoff for API calls"""
    
    def __init__(self, max_requests_per_minute: int = 30, max_retries: int = 4):  # More conservative
        self.max_requests_per_minute = max_requests_per_minute
        self.max_retries = max_retries
        self.request_times = []
        self.min_interval = 60.0 / max_requests_per_minute  # Minimum seconds between requests
        self.last_rate_limit_time = 0
        
    def wait_if_needed(self):
        """Wait if we're approaching rate limits"""
        current_time = time.time()
        
        # If we hit a rate limit recently, wait longer
        if current_time - self.last_rate_limit_time < 60:
            extra_wait = 60 - (current_time - self.last_rate_limit_time)
            logger.info(f"Recent rate limit detected, waiting extra {extra_wait:.1f} seconds")
            time.sleep(extra_wait)
        
        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if current_time - t < 60]
        
        # If we're at the limit, wait
        if len(self.request_times) >= self.max_requests_per_minute:
            wait_time = 60 - (current_time - self.request_times[0]) + 2  # Extra buffer
            logger.info(f"Rate limit approaching, waiting {wait_time:.1f} seconds")
            time.sleep(wait_time)
            
        # Always wait minimum interval to be conservative
        time.sleep(self.min_interval + random.uniform(0.1, 0.5))
        
        # Record this request
        self.request_times.append(time.time())
    
    def retry_with_backoff(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with exponential backoff retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Wait before making the request
                if attempt > 0:  # Don't wait on first attempt
                    self.wait_if_needed()
                
                # Execute the function
                return func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                error_message = str(e).lower()
                
                # Check if it's a rate limit error
                if "rate limit" in error_message or "rate_limit" in error_message:
                    self.last_rate_limit_time = time.time()  # Record when we hit rate limit
                    
                    if attempt < self.max_retries:
                        # More aggressive exponential backoff for rate limits
                        wait_time = min(60, (3 ** attempt) + random.uniform(5, 15))  # Cap at 60s
                        logger.warning(f"Rate limit hit, attempt {attempt + 1}/{self.max_retries + 1}. Waiting {wait_time:.1f}s")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error("Max retries reached for rate limit error")
                        # Instead of raising, return a graceful error
                        return {
                            "success": False,
                            "error": "Rate limit exceeded. Please wait a moment and try again.",
                            "rate_limited": True
                        }
                else:
                    # Not a rate limit error, don't retry
                    raise
        
        # If we get here, all retries failed
        raise last_exception

# Global rate limiter instance with more conservative settings
rate_limiter = RateLimiter(max_requests_per_minute=30, max_retries=4)

def with_rate_limit(func: Callable) -> Callable:
    """Decorator to add rate limiting to functions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        return rate_limiter.retry_with_backoff(func, *args, **kwargs)
    return wrapper 