"""
Middleware components for error handling and rate limiting
"""

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from collections import defaultdict, deque
from typing import Dict, Deque
import traceback

logger = logging.getLogger(__name__)


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


def setup_exception_handlers(app: FastAPI):
    """Setup global exception handlers"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions"""
        logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.method} {request.url}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail}
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle validation errors"""
        logger.error(f"ValueError: {str(exc)} - {request.method} {request.url}")
        return JSONResponse(
            status_code=400,
            content={"error": "Validation error", "details": str(exc)}
        )
    
    @app.exception_handler(ConnectionError)
    async def connection_error_handler(request: Request, exc: ConnectionError):
        """Handle connection errors"""
        logger.error(f"ConnectionError: {str(exc)} - {request.method} {request.url}")
        return JSONResponse(
            status_code=502,
            content={"error": "Connection error", "details": "Cannot connect to VAST server"}
        )
    
    @app.exception_handler(TimeoutError)
    async def timeout_error_handler(request: Request, exc: TimeoutError):
        """Handle timeout errors"""
        logger.error(f"TimeoutError: {str(exc)} - {request.method} {request.url}")
        return JSONResponse(
            status_code=408,
            content={"error": "Request timeout"}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions"""
        logger.error(f"Unhandled exception: {str(exc)} - {request.method} {request.url}")
        logger.error(traceback.format_exc())
        
        # Don't expose internal errors in production
        if app.debug:
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "details": str(exc),
                    "traceback": traceback.format_exc()
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error"}
            )


class LoggingMiddleware(BaseHTTPMiddleware):
    """Request logging middleware"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - "
            f"{response.status_code} - {process_time:.3f}s"
        )
        
        return response
