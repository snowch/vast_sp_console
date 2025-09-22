"""
VAST Services MVP - Python Backend
Main FastAPI application with improved routing and error handling
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from datetime import datetime
import os
from contextlib import asynccontextmanager

from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info(f"🚀 VAST Services Backend starting on port {settings.PORT}")
    logger.info(f"🌍 Environment: {settings.NODE_ENV}")
    logger.info(f"🔗 Frontend URL: {settings.FRONTEND_URL}")
    
    # Check VAST configuration at startup but don't fail if missing
    from config import get_vast_connection_info
    vast_info = get_vast_connection_info()
    if vast_info.get("configured"):
        logger.info(f"✅ VAST Database configured: {vast_info['endpoint']}")
    else:
        logger.warning(f"⚠️  VAST Database not configured: {vast_info.get('error', 'Missing configuration')}")
        logger.warning("   Some features will be unavailable until VAST is configured")
    
    yield
    logger.info("👋 VAST Services Backend shutting down")


# Create FastAPI app
app = FastAPI(
    title="VAST Services Backend",
    description="Backend API for VAST Services MVP",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000", 
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

if settings.FRONTEND_URL and settings.FRONTEND_URL not in origins:
    origins.append(settings.FRONTEND_URL)

if settings.NODE_ENV == "development":
    origins.extend([
        "http://localhost:*",
        "http://127.0.0.1:*",
    ])

logger.info(f"🔧 CORS origins configured: {origins}")

# CORS middleware - MUST be first
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.NODE_ENV == "development" else origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Other middleware
if settings.NODE_ENV == "production":
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Import middleware after app creation to avoid circular imports
try:
    from middleware.rate_limiter import RateLimiterMiddleware
    from middleware.error_handler import setup_exception_handlers
    
    app.add_middleware(RateLimiterMiddleware, calls=100, period=900)
    setup_exception_handlers(app)
except ImportError as e:
    logger.warning(f"Could not import middleware: {e}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from config import get_vast_connection_info
    vast_info = get_vast_connection_info()
    
    return {
        "status": "OK", 
        "timestamp": datetime.utcnow().isoformat(),
        "service": "VAST Services Backend",
        "version": "1.0.0",
        "cors_enabled": True,
        "vast_configured": vast_info.get("configured", False)
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "VAST Services Backend API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "auth": "/api/auth/*", 
            "database_schemas": "/api/database/schemas/*"
        }
    }

# CORS test endpoint
@app.get("/cors-test")
async def cors_test():
    """CORS test endpoint"""
    return {
        "message": "CORS is working! ✅",
        "timestamp": datetime.utcnow().isoformat(),
        "origin_allowed": True
    }

# Preflight handlers
@app.options("/api/{full_path:path}")
async def api_options_handler(request: Request, full_path: str):
    """Handle CORS preflight requests for API routes"""
    return JSONResponse(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*" if settings.NODE_ENV == "development" else request.headers.get("origin", "*"),
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "3600",
        }
    )

@app.options("/{full_path:path}")
async def options_handler(request: Request, full_path: str):
    """Handle CORS preflight requests"""
    return JSONResponse(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*" if settings.NODE_ENV == "development" else request.headers.get("origin", "*"),
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "3600",
        }
    )

# Import and include routers with improved error handling
try:
    from controllers.auth_controller import router as auth_router
    app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
    logger.info("✅ Auth controller loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load auth controller: {e}")

# Try to load schema controller with better error handling
schema_router_loaded = False
try:
    from controllers.schema_controller import router as schema_router
    app.include_router(schema_router, prefix="/api/database/schemas", tags=["database", "schemas"])
    logger.info("✅ Schema controller loaded at /api/database/schemas")
    schema_router_loaded = True
except ImportError as e:
    logger.error(f"❌ Failed to load schema controller: {e}")
except Exception as e:
    logger.error(f"❌ Error loading schema controller: {e}")

# Create fallback routes if schema controller failed to load
if not schema_router_loaded:
    from fastapi import APIRouter
    from config import get_vast_connection_info
    
    # Create minimal schema router
    minimal_router = APIRouter()
    
    @minimal_router.get("/connection")
    async def get_connection_status():
        """Get VAST Database connection status"""
        vast_info = get_vast_connection_info()
        return {
            "success": vast_info.get("configured", False),
            "connection": {
                "endpoint": vast_info.get("endpoint"),
                "bucket": vast_info.get("bucket"),
                "status": "configured" if vast_info.get("configured") else "not_configured",
                "message": vast_info.get("error", "VAST Database not configured")
            }
        }
    
    @minimal_router.get("/")
    async def list_schemas_minimal():
        """List schemas - minimal implementation"""
        vast_info = get_vast_connection_info()
        if not vast_info.get("configured"):
            return {
                "success": False,
                "message": "VAST Database not configured. Please check environment variables.",
                "schemas": [],
                "total": 0
            }
        
        return {
            "success": False,
            "message": "VAST Database service not available - schema controller failed to load",
            "schemas": [],
            "total": 0
        }
    
    @minimal_router.post("/")
    async def create_schema_minimal():
        """Create schema - minimal implementation"""
        return {
            "success": False,
            "message": "Schema creation not available - schema controller failed to load"
        }
    
    @minimal_router.get("/health")
    async def schemas_health_minimal():
        """Health check - minimal implementation"""
        vast_info = get_vast_connection_info()
        return {
            "status": "service_unavailable",
            "vast_database": "not_available",
            "message": "Schema service not available",
            "vast_configured": vast_info.get("configured", False)
        }
    
    # Include minimal router
    app.include_router(minimal_router, prefix="/api/database/schemas", tags=["database", "schemas"])
    logger.info("⚠️  Minimal schema controller loaded at /api/database/schemas")

# Add a debug route to show all registered routes
@app.get("/debug/routes")
async def debug_routes():
    """Debug endpoint to show all registered routes"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else ["GET"]
            })
    
    return {
        "total_routes": len(routes),
        "routes": sorted(routes, key=lambda x: x["path"])
    }

# Improved 404 handler
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    """Custom 404 handler with better error information"""
    logger.warning(f"404 - Path not found: {request.method} {request.url.path}")
    
    # Provide helpful suggestions for common mistakes
    suggestions = []
    path = request.url.path
    
    if path.startswith("/api/schemas"):
        suggestions.append("Try /api/database/schemas instead")
    elif path.startswith("/database/schemas"):
        suggestions.append("Try /api/database/schemas instead")
    elif not path.startswith("/api/") and path not in ["/", "/health", "/docs", "/openapi.json"]:
        suggestions.append(f"Try /api{path} instead")
    
    return JSONResponse(
        status_code=404,
        content={
            "error": "Route not found",
            "path": path,
            "method": request.method,
            "suggestions": suggestions,
            "available_endpoints": [
                "/health",
                "/api/auth/login",
                "/api/auth/verify", 
                "/api/database/schemas/connection",
                "/api/database/schemas",
                "/debug/routes"
            ]
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.NODE_ENV == "development",
        log_level="info"
    )