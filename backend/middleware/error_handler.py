"""
Error handling middleware and exception handlers
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import logging
import traceback

logger = logging.getLogger(__name__)


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
        from config import settings
        if settings.NODE_ENV == "development":
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