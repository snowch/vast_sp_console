"""
VAST Services MVP - Python Backend
Main FastAPI application with proper CORS configuration
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from datetime import datetime
import os
from contextlib import asynccontextmanager

from config import settings
from controllers.auth_controller import router as auth_router
from controllers.schema_controller import router as schema_router
from middleware.rate_limiter import RateLimiterMiddleware
from middleware.error_handler import setup_exception_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info(f"VAST Services Backend starting on port {settings.PORT}")
    logger.info(f"Environment: {settings.NODE_ENV}")
    logger.info(f"Frontend URL: {settings.FRONTEND_URL}")
    yield
    logger.info("VAST Services Backend shutting down")


# Create FastAPI app
app = FastAPI(
    title="VAST Services Backend",
    description="Backend API for VAST Services MVP",
    version="1.0.0",
    lifespan=lifespan
)

# Security middleware - keep this minimal for development
if settings.NODE_ENV == "production":
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# CORS middleware - VERY IMPORTANT: This must be added BEFORE other middlewares
# that might handle the request
origins = [
    settings.FRONTEND_URL,
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",  # Alternative localhost
]

if settings.NODE_ENV == "development":
    origins.extend([
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ])

logger.info(f"CORS origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Rate limiting middleware - add after CORS
app.add_middleware(RateLimiterMiddleware, calls=100, period=900)  # 100 requests per 15 minutes

# Exception handlers
setup_exception_handlers(app)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "OK", 
        "timestamp": datetime.utcnow().isoformat(),
        "service": "VAST Services Backend",
        "version": "1.0.0"
    }

# CORS preflight handler - explicit OPTIONS handling
@app.options("/{full_path:path}")
async def options_handler(request: Request, full_path: str):
    """Handle CORS preflight requests"""
    return JSONResponse(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )

# API routes
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(schema_router, prefix="/api/schemas", tags=["schemas"])

# 404 handler
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def catch_all(request: Request, path: str):
    """Catch all handler for 404s"""
    logger.warning(f"404 - Path not found: {request.method} {path}")
    return JSONResponse(
        status_code=404,
        content={"error": "Route not found", "path": path, "method": request.method}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.NODE_ENV == "development",
        log_level="info"
    )