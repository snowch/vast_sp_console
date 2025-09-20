"""
Schema controller for database schema management using real VastDB SDK
"""

from fastapi import APIRouter, HTTPException, Depends, status, Path
from typing import Dict, Any, Optional
import logging
import re

from models import (
    CreateSchemaRequest, 
    CreateTableRequest,
    SchemaResponse,
    ApiResponse,
    ConnectionInfo
)
from services.vastdb_service import vastdb_service
from services.vastdb_error_handler import handle_vastdb_exceptions, raise_http_exception_from_vastdb_error
from middleware.auth_middleware import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/connection")
@handle_vastdb_exceptions
async def get_connection_info(user: Dict[str, Any] = Depends(get_current_user)):
    """Get VAST Database connection status"""
    try:
        connection_info = vastdb_service.get_connection_info()
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
        logger.error(f"Get connection info error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get connection information"
        )


@router.get("/")
@handle_vastdb_exceptions
async def list_schemas(user: Dict[str, Any] = Depends(get_current_user)):
    """List all database schemas"""
    try:
        result = await vastdb_service.list_schemas()
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
        
        return {
            "success": True,
            "schemas": result["schemas"],
            "total": result["total"],
            "connection": vastdb_service.get_connection_info()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List schemas error: {str(e)}")
        # Check if it's a VastDB exception and handle accordingly
        if hasattr(e, '__module__') and 'vastdb' in str(e.__module__):
            raise_http_exception_from_vastdb_error(e)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch schemas"
            )


@router.post("/", status_code=status.HTTP_201_CREATED)
@handle_vastdb_exceptions
async def create_schema(
    request: CreateSchemaRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new database schema"""
    try:
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create schema error: {str(e)}")
        if hasattr(e, '__module__') and 'vastdb' in str(e.__module__):
            raise_http_exception_from_vastdb_error(e)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create schema"
            )


@router.get("/{name}")
@handle_vastdb_exceptions
async def get_schema(
    name: str = Path(..., min_length=1, max_length=64),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a specific schema"""
    try:
        # Validate schema name format
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid schema name format"
            )
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get schema error: {str(e)}")
        if hasattr(e, '__module__') and 'vastdb' in str(e.__module__):
            raise_http_exception_from_vastdb_error(e)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get schema"
            )


@router.delete("/{name}")
@handle_vastdb_exceptions
async def delete_schema(
    name: str = Path(..., min_length=1, max_length=64),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a schema"""
    try:
        # Validate schema name format
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid schema name format"
            )
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete schema error: {str(e)}")
        if hasattr(e, '__module__') and 'vastdb' in str(e.__module__):
            raise_http_exception_from_vastdb_error(e)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete schema"
            )


@router.post("/{name}/tables", status_code=status.HTTP_201_CREATED)
@handle_vastdb_exceptions
async def create_table(
    request: CreateTableRequest,
    name: str = Path(..., min_length=1, max_length=64),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a table in a schema"""
    try:
        # Validate schema name format
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid schema name format"
            )
        
        # Default columns if none provided
        columns = request.columns
        if not columns:
            columns = [
                {"name": "id", "type": "int64", "nullable": False},
                {"name": "created_at", "type": "timestamp", "nullable": False},
                {"name": "updated_at", "type": "timestamp", "nullable": True}
            ]
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create table error: {str(e)}")
        if hasattr(e, '__module__') and 'vastdb' in str(e.__module__):
            raise_http_exception_from_vastdb_error(e)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create table"
            )


@router.get("/{name}/tables")
@handle_vastdb_exceptions
async def list_tables(
    name: str = Path(..., min_length=1, max_length=64),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """List tables in a schema"""
    try:
        # Validate schema name format
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid schema name format"
            )
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List tables error: {str(e)}")
        if hasattr(e, '__module__') and 'vastdb' in str(e.__module__):
            raise_http_exception_from_vastdb_error(e)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list tables"
            )


# Health check for schemas endpoint
@router.get("/health/schemas")
async def schemas_health():
    """Health check for schemas service"""
    try:
        connection_info = vastdb_service.get_connection_info()
        
        if not connection_info["connected"]:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="VAST Database not available"
            )
        
        # Test the connection
        connection_test = await vastdb_service.connect()
        if not connection_test["success"]:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=connection_test["message"]
            )
        
        return {
            "status": "healthy",
            "vast_database": "connected",
            "endpoint": connection_info["endpoint"],
            "bucket": connection_info["bucket"],
            "timestamp": time.time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="VAST Database health check failed"
        )