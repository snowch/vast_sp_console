"""
Rate limiting middleware
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict, deque
from typing import Dict, Deque


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app, calls: int = 100, period: int = 900):
        """
        Initialize rate limiter
        :param calls: Maximum number of calls allowed
        :param period: Time period in seconds
        """
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.requests: Dict[str, Deque[float]] = defaultdict(deque)
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        client_ip = self.get_client_ip(request)
        current_time = time.time()
        
        # Clean old requests
        self.clean_old_requests(client_ip, current_time)
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.calls:
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"}
            )
        
        # Add current request
        self.requests[client_ip].append(current_time)
        
        response = await call_next(request)
        return response
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def clean_old_requests(self, client_ip: str, current_time: float):
        """Clean requests older than the period"""
        cutoff_time = current_time - self.period
        while (self.requests[client_ip] and 
               self.requests[client_ip][0] < cutoff_time):
            self.requests[client_ip].popleft()