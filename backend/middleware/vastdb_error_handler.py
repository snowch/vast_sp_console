"""
Error handling utilities for VastDB SDK integration
"""

import logging
from fastapi import HTTPException, status
from typing import Dict, Any

from vastdb.errors import (
    MissingBucket, MissingSchema, MissingTable, MissingProjection,
    SchemaExists, TableExists, NotFound, Forbidden, BadRequest,
    InternalServerError, ServiceUnavailable, ConnectionError,
    NotSupported, NotSupportedSchema, InvalidArgument,
    TooLargeRequest, ImportFilesError
)

logger = logging.getLogger(__name__)


def handle_vastdb_error(error: Exception) -> Dict[str, Any]:
    """
    Convert VastDB SDK exceptions to appropriate HTTP responses
    
    Returns a dict with 'success': False and 'message' for API consistency
    """
    
    # Missing resource errors (404)
    if isinstance(error, (MissingBucket, MissingSchema, MissingTable, MissingProjection)):
        return {
            "success": False,
            "message": str(error),
            "status_code": status.HTTP_404_NOT_FOUND
        }
    
    # Resource already exists errors (409)
    if isinstance(error, (SchemaExists, TableExists)):
        return {
            "success": False,
            "message": str(error),
            "status_code": status.HTTP_409_CONFLICT
        }
    
    # Bad request errors (400)
    if isinstance(error, (BadRequest, InvalidArgument, NotSupportedSchema)):
        return {
            "success": False,
            "message": str(error),
            "status_code": status.HTTP_400_BAD_REQUEST
        }
    
    # Request too large (413)
    if isinstance(error, TooLargeRequest):
        return {
            "success": False,
            "message": str(error),
            "status_code": status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        }
    
    # Forbidden errors (403)
    if isinstance(error, Forbidden):
        return {
            "success": False,
            "message": str(error),
            "status_code": status.HTTP_403_FORBIDDEN
        }
    
    # Not implemented/supported errors (501)
    if isinstance(error, NotSupported):
        return {
            "success": False,
            "message": str(error),
            "status_code": status.HTTP_501_NOT_IMPLEMENTED
        }
    
    # Service unavailable errors (503)
    if isinstance(error, ServiceUnavailable):
        return {
            "success": False,
            "message": str(error),
            "status_code": status.HTTP_503_SERVICE_UNAVAILABLE
        }
    
    # Connection errors (502)
    if isinstance(error, ConnectionError):
        return {
            "success": False,
            "message": "Failed to connect to VAST Database",
            "status_code": status.HTTP_502_BAD_GATEWAY
        }
    
    # Import errors (400)
    if isinstance(error, ImportFilesError):
        return {
            "success": False,
            "message": error.message,
            "status_code": status.HTTP_400_BAD_REQUEST
        }
    
    # Internal server errors (500)
    if isinstance(error, InternalServerError):
        return {
            "success": False,
            "message": str(error),
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
        }
    
    # Generic not found (404)
    if isinstance(error, NotFound):
        return {
            "success": False,
            "message": str(error),
            "status_code": status.HTTP_404_NOT_FOUND
        }
    
    # Default to internal server error for unknown exceptions
    logger.error(f"Unhandled VastDB error: {type(error).__name__}: {str(error)}")
    return {
        "success": False,
        "message": "An unexpected error occurred",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
    }


def raise_http_exception_from_vastdb_error(error: Exception):
    """
    Convert VastDB SDK exception to FastAPI HTTPException
    """
    error_info = handle_vastdb_error(error)
    raise HTTPException(
        status_code=error_info["status_code"],
        detail=error_info["message"]
    )


# Decorator for handling VastDB errors in API endpoints
def handle_vastdb_exceptions(func):
    """
    Decorator to automatically handle VastDB exceptions in API endpoints
    """
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # Check if it's a VastDB exception
            if hasattr(e, '__module__') and 'vastdb' in str(e.__module__):
                raise_http_exception_from_vastdb_error(e)
            else:
                # Re-raise non-VastDB exceptions
                raise e
    
    return wrapper