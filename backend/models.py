"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import re


class LoginRequest(BaseModel):
    """Login request model"""
    vastHost: str = Field(..., description="VAST cluster IP address")
    vastPort: int = Field(..., ge=1, le=65535, description="VAST cluster port")
    username: str = Field(..., min_length=1, description="Username")
    password: str = Field(..., min_length=1, description="Password")
    tenant: str = Field(default="default", description="Tenant name")
    
    @validator('vastHost')
    def validate_ip_address(cls, v):
        # Simple IP validation
        ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
        if not re.match(ip_pattern, v):
            raise ValueError('Invalid IP address format')
        return v


class LoginResponse(BaseModel):
    """Login response model"""
    success: bool
    token: Optional[str] = None
    user: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class TokenVerifyResponse(BaseModel):
    """Token verification response model"""
    valid: bool
    user: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class CreateSchemaRequest(BaseModel):
    """Create schema request model"""
    name: str = Field(..., min_length=1, max_length=64, description="Schema name")
    description: Optional[str] = Field(None, max_length=255, description="Optional description")
    
    @validator('name')
    def validate_schema_name(cls, v):
        # Schema name validation: must start with letter, contain only letters, numbers, underscore
        pattern = r'^[a-zA-Z][a-zA-Z0-9_]*$'
        if not re.match(pattern, v):
            raise ValueError('Schema name must start with letter and contain only letters, numbers, and underscores')
        return v


class CreateTableRequest(BaseModel):
    """Create table request model"""
    tableName: str = Field(..., min_length=1, max_length=64, description="Table name")
    columns: Optional[List[Dict[str, Any]]] = Field(default=[], description="Table columns")
    
    @validator('tableName')
    def validate_table_name(cls, v):
        # Table name validation: must start with letter, contain only letters, numbers, underscore
        pattern = r'^[a-zA-Z][a-zA-Z0-9_]*$'
        if not re.match(pattern, v):
            raise ValueError('Table name must start with letter and contain only letters, numbers, and underscores')
        return v


class SchemaResponse(BaseModel):
    """Schema response model"""
    name: str
    bucket: str
    path: str
    protocols: List[str]
    created: str
    id: str
    tables: Optional[List[Dict[str, Any]]] = None


class TableResponse(BaseModel):
    """Table response model"""
    name: str
    schema: str
    columns: List[Dict[str, Any]]
    rows: int
    created: str


class ConnectionInfo(BaseModel):
    """Connection information model"""
    endpoint: Optional[str]
    bucket: Optional[str]
    status: str
    message: Optional[str]


class ApiResponse(BaseModel):
    """Generic API response model"""
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    message: Optional[str] = None
    details: Optional[Any] = None
