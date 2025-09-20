"""
VAST Database service that mimics the vastdb Python SDK
"""

import httpx
import time
import hashlib
import base64
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from config import settings, validate_vast_config

logger = logging.getLogger(__name__)


class VastDbService:
    """Service that provides vastdb-like functionality using environment variables"""
    
    def __init__(self):
        try:
            validate_vast_config()
            self.endpoint = settings.VAST_ENDPOINT
            self.access_key_id = settings.VAST_ACCESS_KEY_ID
            self.secret_access_key = settings.VAST_SECRET_ACCESS_KEY
            self.bucket_name = settings.VAST_BUCKET_NAME
            self.verify_ssl = settings.VAST_VERIFY_SSL
            self.region = settings.VAST_REGION
            self.client = self._create_client()
            self.sessions: Dict[str, Dict[str, Any]] = {}
        except ValueError as e:
            logger.error(f"VAST configuration error: {e}")
            self.endpoint = None
            self.client = None
    
    def _create_client(self) -> Optional[httpx.AsyncClient]:
        """Create HTTP client for VAST endpoint"""
        if not self.endpoint:
            return None
            
        if not self.verify_ssl:
            disable_warnings(InsecureRequestWarning)
        
        return httpx.AsyncClient(
            base_url=self.endpoint,
            timeout=30.0,
            verify=self.verify_ssl,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'VAST-Services-MVP/1.0'
            }
        )
    
    async def connect(self) -> Dict[str, Any]:
        """Test connection to VAST endpoint"""
        if not self.client:
            return {
                "success": False,
                "message": "VAST Database not configured - missing environment variables"
            }
        
        try:
            async with self.client as c:
                # Test connection with a simple health check
                response = await c.get("/health")
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "endpoint": self.endpoint,
                        "bucket": self.bucket_name,
                        "message": "Connected to VAST Database"
                    }
                else:
                    return {
                        "success": False,
                        "message": f"VAST Database connection failed: HTTP {response.status_code}"
                    }
        except Exception as e:
            logger.error(f"VAST DB connection error: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to connect to VAST Database: {str(e)}"
            }
    
    async def create_schema(self, schema_name: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a database schema"""
        if not self.client:
            return {
                "success": False,
                "message": "VAST Database not configured"
            }
        
        try:
            session_key = f"{self.endpoint}:{self.bucket_name}:{schema_name}"
            
            # Simulate vastdb.connect() -> tx.bucket() -> create_schema() pattern
            transaction = await self._begin_transaction()
            bucket = transaction["bucket"](self.bucket_name)
            
            schema = await bucket["create_schema"](schema_name, options or {})
            
            # Cache the session
            self.sessions[session_key] = {
                "schema_name": schema_name,
                "bucket": self.bucket_name,
                "endpoint": self.endpoint,
                "transaction": transaction,
                "created": time.time()
            }
            
            await transaction["commit"]()
            
            return {
                "success": True,
                "schema": {
                    "name": schema_name,
                    "bucket": self.bucket_name,
                    "path": f"/{self.bucket_name}/{schema_name}",
                    "protocols": ["DATABASE", "S3"],  # Default protocols for database schemas
                    "created": datetime.utcnow().isoformat(),
                    "id": self._generate_schema_id(schema_name)
                },
                "message": f"Schema '{schema_name}' created successfully"
            }
            
        except Exception as e:
            logger.error(f"Create schema error: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }
    
    async def list_schemas(self) -> Dict[str, Any]:
        """List all schemas in the bucket"""
        if not self.client:
            return {
                "success": False,
                "message": "VAST Database not configured",
                "schemas": []
            }
        
        try:
            transaction = await self._begin_transaction()
            bucket = transaction["bucket"](self.bucket_name)
            
            schemas = await bucket["schemas"]()
            
            schema_list = []
            for schema in schemas:
                schema_list.append({
                    "name": schema["name"],
                    "bucket": self.bucket_name,
                    "path": f"/{self.bucket_name}/{schema['name']}",
                    "protocols": ["DATABASE", "S3"],
                    "created": datetime.utcnow().isoformat(),
                    "id": self._generate_schema_id(schema["name"])
                })
            
            await transaction["commit"]()
            
            return {
                "success": True,
                "schemas": schema_list,
                "total": len(schema_list)
            }
            
        except Exception as e:
            logger.error(f"List schemas error: {str(e)}")
            return {
                "success": False,
                "message": str(e),
                "schemas": []
            }
    
    async def get_schema(self, schema_name: str) -> Dict[str, Any]:
        """Get a specific schema"""
        if not self.client:
            return {
                "success": False,
                "message": "VAST Database not configured"
            }
        
        try:
            transaction = await self._begin_transaction()
            bucket = transaction["bucket"](self.bucket_name)
            schema = await bucket["schema"](schema_name, {"fail_if_missing": False})
            
            if not schema:
                return {
                    "success": False,
                    "message": f"Schema '{schema_name}' not found"
                }
            
            # Get tables in this schema
            tables = await schema["tables"]()
            
            await transaction["commit"]()
            
            table_list = []
            for table in tables:
                table_list.append({
                    "name": table["name"],
                    "schema": schema_name,
                    "columns": table.get("columns", []),
                    "rows": table.get("rowCount", 0),
                    "created": table.get("created", datetime.utcnow().isoformat())
                })
            
            return {
                "success": True,
                "schema": {
                    "name": schema_name,
                    "bucket": self.bucket_name,
                    "path": f"/{self.bucket_name}/{schema_name}",
                    "protocols": ["DATABASE", "S3"],
                    "created": datetime.utcnow().isoformat(),
                    "id": self._generate_schema_id(schema_name),
                    "tables": table_list
                }
            }
            
        except Exception as e:
            logger.error(f"Get schema error: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }
    
    async def delete_schema(self, schema_name: str) -> Dict[str, Any]:
        """Delete a schema"""
        if not self.client:
            return {
                "success": False,
                "message": "VAST Database not configured"
            }
        
        try:
            transaction = await self._begin_transaction()
            bucket = transaction["bucket"](self.bucket_name)
            schema = await bucket["schema"](schema_name)
            
            await schema["drop"]()
            await transaction["commit"]()
            
            # Clean up cached session
            session_key = f"{self.endpoint}:{self.bucket_name}:{schema_name}"
            if session_key in self.sessions:
                del self.sessions[session_key]
            
            return {
                "success": True,
                "message": f"Schema '{schema_name}' deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Delete schema error: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }
    
    async def create_table(self, schema_name: str, table_name: str, columns: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a table in a schema"""
        if not self.client:
            return {
                "success": False,
                "message": "VAST Database not configured"
            }
        
        try:
            transaction = await self._begin_transaction()
            bucket = transaction["bucket"](self.bucket_name)
            schema = await bucket["schema"](schema_name)
            
            # Convert columns to PyArrow-like schema format
            columns = columns or []
            if not columns:
                columns = [
                    {"name": "id", "type": "int64", "nullable": False},
                    {"name": "created_at", "type": "timestamp", "nullable": False},
                    {"name": "updated_at", "type": "timestamp", "nullable": True}
                ]
            
            pa_schema = self._convert_to_pyarrow_schema(columns)
            
            table = await schema["create_table"](table_name, pa_schema, {"fail_if_exists": False})
            
            await transaction["commit"]()
            
            return {
                "success": True,
                "table": {
                    "name": table_name,
                    "schema": schema_name,
                    "columns": columns,
                    "created": datetime.utcnow().isoformat(),
                    "rows": 0
                },
                "message": f"Table '{table_name}' created successfully"
            }
            
        except Exception as e:
            logger.error(f"Create table error: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }
    
    async def _begin_transaction(self) -> Dict[str, Any]:
        """Simulate vastdb transaction pattern"""
        return {
            "bucket": lambda bucket_name: {
                "create_schema": lambda schema_name, options: {
                    "name": schema_name,
                    "bucket": bucket_name
                },
                "schemas": lambda: [
                    {"name": "analytics"},
                    {"name": "users"}, 
                    {"name": "events"}
                ],
                "schema": lambda schema_name, options=None: {
                    "name": schema_name,
                    "bucket": bucket_name,
                    "tables": lambda: [
                        {"name": "users", "columns": [], "rowCount": 0},
                        {"name": "events", "columns": [], "rowCount": 0}
                    ],
                    "create_table": lambda table_name, schema, options=None: {
                        "name": table_name,
                        "schema": schema_name,
                        "columns": schema
                    },
                    "drop": lambda: True
                }
            },
            "commit": lambda: True
        }
    
    def _convert_to_pyarrow_schema(self, columns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert JavaScript column definitions to PyArrow-like schema"""
        arrow_columns = []
        for col in columns:
            arrow_columns.append({
                "name": col["name"],
                "type": self._map_to_arrow_type(col["type"]),
                "nullable": col.get("nullable", True)
            })
        return arrow_columns
    
    def _map_to_arrow_type(self, js_type: str) -> str:
        """Map JavaScript types to Arrow types"""
        type_map = {
            'string': 'utf8',
            'int': 'int64',
            'integer': 'int64', 
            'float': 'float64',
            'double': 'float64',
            'boolean': 'bool',
            'date': 'date32',
            'timestamp': 'timestamp'
        }
        return type_map.get(js_type, 'utf8')
    
    def _generate_schema_id(self, schema_name: str) -> str:
        """Generate a deterministic ID for the schema"""
        source = f"{self.bucket_name}-{schema_name}"
        return base64.b64encode(source.encode()).decode()[:16]
    
    def cleanup_sessions(self):
        """Clean up expired sessions"""
        now = time.time()
        expired_keys = []
        
        for key, session in self.sessions.items():
            age_hours = (now - session["created"]) / 3600
            if age_hours > 8:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.sessions[key]
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information"""
        return {
            "endpoint": self.endpoint,
            "bucket": self.bucket_name,
            "sessions_count": len(self.sessions),
            "connected": self.client is not None
        }


# Global service instance
vastdb_service = VastDbService()
