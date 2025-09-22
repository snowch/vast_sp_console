"""
Schema controller for database schema management - FIXED ROUTES VERSION
Addresses the 405 Method Not Allowed error by fixing route order and conflicts
"""

from fastapi import APIRouter, HTTPException, Depends, status, Path
from typing import Dict, Any, Optional
import logging
import re
import time

from models import (
    CreateSchemaRequest, 
    CreateTableRequest,
    SchemaResponse,
    ApiResponse,
    ConnectionInfo
)
from middleware.auth_middleware import get_current_user

# Create router - IMPORTANT: No prefix here since it's added in main.py
router = APIRouter(tags=["schemas", "database"])
logger = logging.getLogger(__name__)


# CRITICAL: Connection endpoint MUST come before parameterized routes
@router.get("/connection", summary="Get VAST Database connection status")
async def get_connection_info(user: Dict[str, Any] = Depends(get_current_user)):
    """Get VAST Database connection status and configuration"""
    try:
        from config import get_vast_connection_info
        connection_info = get_vast_connection_info()
        
        # Try to test the actual connection if configured
        if connection_info.get("configured"):
            try:
                from services.vastdb_service import vastdb_service
                connection_test = await vastdb_service.connect()
                
                return {
                    "success": True,
                    "connection": {
                        **connection_info,
                        "status": "connected" if connection_test["success"] else "disconnected",
                        "message": connection_test["message"]
                    }
                }
            except Exception as e:
                logger.error(f"VAST DB connection test failed: {str(e)}")
                return {
                    "success": True,
                    "connection": {
                        **connection_info,
                        "status": "disconnected",
                        "message": f"Connection test failed: {str(e)}"
                    }
                }
        else:
            return {
                "success": True,
                "connection": {
                    **connection_info,
                    "status": "not_configured",
                    "message": connection_info.get("error", "VAST Database not configured")
                }
            }
        
    except Exception as e:
        logger.error(f"Get connection info error: {str(e)}")
        return {
            "success": False,
            "connection": {
                "endpoint": None,
                "bucket": None,
                "status": "error",
                "message": f"Failed to get connection information: {str(e)}"
            }
        }


# Health endpoint - MUST come before parameterized routes
@router.get("/health/schemas", summary="Health check for schemas service")
async def schemas_health():
    """Health check endpoint for the database schemas service"""
    try:
        from config import get_vast_connection_info
        connection_info = get_vast_connection_info()
        
        if not connection_info.get("configured"):
            return {
                "status": "service_unavailable",
                "vast_database": "not_configured",
                "message": "VAST Database not configured",
                "timestamp": time.time()
            }
        
        # Test the connection if VastDB service is available
        try:
            from services.vastdb_service import vastdb_service
            connection_test = await vastdb_service.connect()
            
            return {
                "status": "healthy" if connection_test["success"] else "unhealthy",
                "vast_database": "connected" if connection_test["success"] else "disconnected",
                "endpoint": connection_info["endpoint"],
                "bucket": connection_info["bucket"],
                "message": connection_test["message"],
                "timestamp": time.time()
            }
            
        except ImportError as e:
            logger.error(f"VastDB service not available: {e}")
            return {
                "status": "service_unavailable",
                "vast_database": "service_not_available",
                "endpoint": connection_info["endpoint"],
                "bucket": connection_info["bucket"],
                "message": "VastDB service not available",
                "timestamp": time.time()
            }
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            "status": "unhealthy",
            "vast_database": "error",
            "message": f"Health check failed: {str(e)}",
            "timestamp": time.time()
        }


# CRITICAL: Root endpoints - MUST use trailing slash to match exactly
@router.get("/", summary="List all database schemas")
async def list_schemas(user: Dict[str, Any] = Depends(get_current_user)):
    """List all database schemas in the configured bucket"""
    try:
        from config import get_vast_connection_info
        connection_info = get_vast_connection_info()
        
        if not connection_info.get("configured"):
            return {
                "success": False,
                "message": "VAST Database not configured. Please check environment variables.",
                "schemas": [],
                "total": 0,
                "connection": connection_info
            }
        
        # Try to import and use the VAST DB service
        try:
            from services.vastdb_service import vastdb_service
            result = await vastdb_service.list_schemas()
            
            if not result["success"]:
                return {
                    "success": False,
                    "message": result["message"],
                    "schemas": [],
                    "total": 0,
                    "connection": connection_info
                }
            
            return {
                "success": True,
                "schemas": result["schemas"],
                "total": result["total"],
                "connection": connection_info
            }
            
        except ImportError as e:
            logger.error(f"Failed to import vastdb_service: {e}")
            return {
                "success": False,
                "message": "VAST Database service not available - missing dependencies",
                "schemas": [],
                "total": 0,
                "connection": connection_info
            }
        except Exception as e:
            logger.error(f"VastDB service error: {str(e)}")
            return {
                "success": False,
                "message": f"VAST Database error: {str(e)}",
                "schemas": [],
                "total": 0,
                "connection": connection_info
            }
        
    except Exception as e:
        logger.error(f"List schemas error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch schemas"
        )


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create a new database schema")
async def create_schema(
    request: CreateSchemaRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new database schema with the given name and optional description"""
    try:
        from config import get_vast_connection_info
        connection_info = get_vast_connection_info()
        
        if not connection_info.get("configured"):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="VAST Database not configured"
            )
        
        try:
            from services.vastdb_service import vastdb_service
            result = await vastdb_service.create_schema(
                schema_name=request.name,
                options={
                    "description": request.description,
                    "failIfExists": True
                }
            )
            
            if not result["success"]:
                if "already exists" in result["message"].lower():
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=result["message"]
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=result["message"]
                    )
            
            return {
                "success": True,
                "schema": result["schema"],
                "message": result["message"]
            }
            
        except ImportError as e:
            logger.error(f"Failed to import vastdb_service: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="VAST Database service not available"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"VastDB service error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"VAST Database error: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create schema error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create schema"
        )


# Parameterized routes MUST come after static routes
@router.get("/{name}", summary="Get a specific schema")
async def get_schema(
    name: str = Path(..., min_length=1, max_length=64, description="Schema name"),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Get detailed information about a specific schema including its tables"""
    try:
        # Validate schema name format
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid schema name format"
            )
        
        from config import get_vast_connection_info
        connection_info = get_vast_connection_info()
        
        if not connection_info.get("configured"):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="VAST Database not configured"
            )
        
        try:
            from services.vastdb_service import vastdb_service
            result = await vastdb_service.get_schema(name)
            
            if not result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result["message"]
                )
            
            return {
                "success": True,
                "schema": result["schema"]
            }
            
        except ImportError as e:
            logger.error(f"Failed to import vastdb_service: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="VAST Database service not available"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"VastDB service error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"VAST Database error: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get schema error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get schema"
        )


@router.delete("/{name}", summary="Delete a schema")
async def delete_schema(
    name: str = Path(..., min_length=1, max_length=64, description="Schema name"),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a schema and all its tables (irreversible operation)"""
    try:
        # Validate schema name format
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid schema name format"
            )
        
        from config import get_vast_connection_info
        connection_info = get_vast_connection_info()
        
        if not connection_info.get("configured"):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="VAST Database not configured"
            )
        
        try:
            from services.vastdb_service import vastdb_service
            result = await vastdb_service.delete_schema(name)
            
            if not result["success"]:
                if "not found" in result["message"].lower():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=result["message"]
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=result["message"]
                    )
            
            return {
                "success": True,
                "message": result["message"]
            }
            
        except ImportError as e:
            logger.error(f"Failed to import vastdb_service: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="VAST Database service not available"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"VastDB service error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"VAST Database error: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete schema error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete schema"
        )


@router.post("/{name}/tables", status_code=status.HTTP_201_CREATED, summary="Create a table in a schema")
async def create_table(
    request: CreateTableRequest,
    name: str = Path(..., min_length=1, max_length=64, description="Schema name"),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a table in the specified schema with given columns"""
    try:
        # Validate schema name format
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid schema name format"
            )
        
        from config import get_vast_connection_info
        connection_info = get_vast_connection_info()
        
        if not connection_info.get("configured"):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="VAST Database not configured"
            )
        
        # Default columns if none provided
        columns = request.columns
        if not columns:
            columns = [
                {"name": "id", "type": "int64", "nullable": False},
                {"name": "created_at", "type": "timestamp", "nullable": False},
                {"name": "updated_at", "type": "timestamp", "nullable": True}
            ]
        
        try:
            from services.vastdb_service import vastdb_service
            result = await vastdb_service.create_table(name, request.tableName, columns)
            
            if not result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result["message"]
                )
            
            return {
                "success": True,
                "table": result["table"],
                "message": result["message"]
            }
            
        except ImportError as e:
            logger.error(f"Failed to import vastdb_service: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="VAST Database service not available"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"VastDB service error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"VAST Database error: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create table error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create table"
        )


@router.get("/{name}/tables", summary="List tables in a schema")
async def list_tables(
    name: str = Path(..., min_length=1, max_length=64, description="Schema name"),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """List all tables in the specified schema"""
    try:
        # Validate schema name format
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid schema name format"
            )
        
        from config import get_vast_connection_info
        connection_info = get_vast_connection_info()
        
        if not connection_info.get("configured"):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="VAST Database not configured"
            )
        
        try:
            from services.vastdb_service import vastdb_service
            result = await vastdb_service.get_schema(name)
            
            if not result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result["message"]
                )
            
            return {
                "success": True,
                "tables": result["schema"].get("tables", []),
                "schema": name
            }
            
        except ImportError as e:
            logger.error(f"Failed to import vastdb_service: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="VAST Database service not available"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"VastDB service error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"VAST Database error: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List tables error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list tables"
        )
    
@router.get("")  # No trailing slash
async def list_schemas_no_slash(user: Dict[str, Any] = Depends(get_current_user)):
    return await list_schemas(user)

@router.post("")  # No trailing slash  
async def create_schema_no_slash(request: CreateSchemaRequest, user: Dict[str, Any] = Depends(get_current_user)):
    return await create_schema(request, user)