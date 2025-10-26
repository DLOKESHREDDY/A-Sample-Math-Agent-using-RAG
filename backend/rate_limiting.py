from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from typing import Dict, Optional
import time
from collections import defaultdict, deque
from logging_config import get_logger

logger = get_logger(__name__)

class AdvancedRateLimiter:
    """Advanced rate limiter with multiple strategies."""
    
    def __init__(self):
        # Store request timestamps per IP
        self.requests: Dict[str, deque] = defaultdict(lambda: deque())
        # Store request counts per IP per minute
        self.minute_counts: Dict[str, int] = defaultdict(int)
        self.last_minute_reset: Dict[str, float] = defaultdict(float)
    
    def is_allowed(self, ip: str, max_requests: int = 60, window_seconds: int = 60) -> bool:
        """Check if request is allowed based on sliding window."""
        current_time = time.time()
        
        # Clean old requests outside the window
        while self.requests[ip] and self.requests[ip][0] < current_time - window_seconds:
            self.requests[ip].popleft()
        
        # Check if under limit
        if len(self.requests[ip]) >= max_requests:
            logger.warning(
                "Rate limit exceeded",
                ip=ip,
                request_count=len(self.requests[ip]),
                max_requests=max_requests
            )
            return False
        
        # Add current request
        self.requests[ip].append(current_time)
        return True
    
    def get_reset_time(self, ip: str, window_seconds: int = 60) -> float:
        """Get when the rate limit will reset for an IP."""
        if not self.requests[ip]:
            return time.time()
        
        oldest_request = self.requests[ip][0]
        return oldest_request + window_seconds

# Global rate limiter instance
rate_limiter = AdvancedRateLimiter()

def get_rate_limit_key(request: Request) -> str:
    """Get rate limit key for request."""
    # Use IP address as primary key
    ip = get_remote_address(request)
    
    # Could be enhanced to use user ID if authentication is added
    return ip

def check_rate_limit(request: Request, max_requests: int = 60) -> bool:
    """Check if request is within rate limits."""
    key = get_rate_limit_key(request)
    return rate_limiter.is_allowed(key, max_requests)

def get_rate_limit_info(request: Request) -> Dict[str, any]:
    """Get rate limit information for client."""
    key = get_rate_limit_key(request)
    current_time = time.time()
    
    # Count requests in current window
    window_seconds = 60
    request_count = len([
        req_time for req_time in rate_limiter.requests[key]
        if req_time > current_time - window_seconds
    ])
    
    reset_time = rate_limiter.get_reset_time(key, window_seconds)
    
    return {
        "requests_remaining": max(0, 60 - request_count),
        "reset_time": reset_time,
        "current_requests": request_count
    }

# SlowAPI limiter for additional protection
limiter = Limiter(key_func=get_remote_address)

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit exceeded handler."""
    logger.warning(
        "Rate limit exceeded",
        ip=get_remote_address(request),
        limit=str(exc.detail)
    )
    
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "type": "RateLimitExceeded",
                "message": "Too many requests. Please slow down.",
                "retry_after": exc.retry_after
            },
            "success": False
        },
        headers={"Retry-After": str(exc.retry_after)}
    )

