"""
VAST Services MVP - Python Backend
Main FastAPI application
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
    yield
    logger.info("VAST Services Backend shutting down")


# Create FastAPI app
app = FastAPI(
    title="VAST Services Backend",
    description="Backend API for VAST Services MVP",
    version="1.0.0",
    lifespan=lifespan
)

# Security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.add_middleware(RateLimiterMiddleware, calls=100, period=900)  # 100 requests per 15 minutes

# Exception handlers
setup_exception_handlers(app)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "OK", 
        "timestamp": datetime.utcnow().isoformat()
    }

# API routes
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(schema_router, prefix="/api/schemas", tags=["schemas"])

# 404 handler
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def catch_all(request: Request, path: str):
    """Catch all handler for 404s"""
    return JSONResponse(
        status_code=404,
        content={"error": "Route not found"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.NODE_ENV == "development"
    )