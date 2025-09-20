"""
VAST Database service using the actual vastdb Python SDK with lazy connection
"""

import logging
import time
from typing import Dict, Optional, Any, List
from datetime import datetime

from config import settings, validate_vast_config

logger = logging.getLogger(__name__)


class VastDbService:
    """Service that provides vastdb functionality using the official Python SDK"""
    
    def __init__(self):
        """Initialize service but don't connect until needed"""
        self.session = None
        self._connection_attempted = False
        self._connection_error = None
        
        try:
            validate_vast_config()
            self.endpoint = settings.VAST_ENDPOINT
            self.access_key_id = settings.VAST_ACCESS_KEY_ID
            self.secret_access_key = settings.VAST_SECRET_ACCESS_KEY
            self.bucket_name = settings.VAST_BUCKET_NAME
            self.verify_ssl = settings.VAST_VERIFY_SSL
            self.region = settings.VAST_REGION
            
            logger.info(f"VastDB service configured with endpoint: {self.endpoint}, bucket: {self.bucket_name}")
            
        except ValueError as e:
            logger.error(f"VAST configuration error: {e}")
            self._connection_error = str(e)
    
    def _ensure_connection(self):
        """Ensure we have a valid connection, create if needed"""
        if self.session is not None:
            return True
            
        if self._connection_error:
            return False
            
        if self._connection_attempted:
            return False
            
        try:
            import vastdb
            logger.info("Attempting to connect to VAST Database...")
            
            self.session = vastdb.connect(
                endpoint=self.endpoint,
                access=self.access_key_id,
                secret=self.secret_access_key,
                ssl_verify=self.verify_ssl
            )
            
            logger.info("Successfully connected to VAST Database")
            self._connection_attempted = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to VAST Database: {str(e)}")
            self._connection_error = str(e)
            self._connection_attempted = True
            return False
    
    async def connect(self) -> Dict[str, Any]:
        """Test connection to VAST endpoint"""
        if self._connection_error:
            return {
                "success": False,
                "message": f"VAST Database configuration error: {self._connection_error}"
            }
        
        if not self._ensure_connection():
            return {
                "success": False,
                "message": self._connection_error or "Failed to establish VAST Database connection"
            }
        
        try:
            # Test the connection by attempting to access the bucket
            with self.session.transaction() as tx:
                bucket = tx.bucket(self.bucket_name)
                # If we can access the bucket, connection is successful
                return {
                    "success": True,
                    "endpoint": self.endpoint,
                    "bucket": self.bucket_name,
                    "message": "Connected to VAST Database"
                }
                
        except Exception as e:
            # Handle specific VastDB exceptions
            import vastdb.errors as vastdb_errors
            
            if isinstance(e, vastdb_errors.MissingBucket):
                error_msg = f"Bucket '{self.bucket_name}' not found"
            elif isinstance(e, vastdb_errors.ConnectionError):
                error_msg = f"Failed to connect to VAST Database: {str(e)}"
            else:
                error_msg = f"VAST Database error: {str(e)}"
                
            logger.error(f"VAST DB connection test error: {error_msg}")
            return {
                "success": False,
                "message": error_msg
            }
    
    async def create_schema(self, schema_name: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a database schema"""
        if not self._ensure_connection():
            return {
                "success": False,
                "message": self._connection_error or "VAST Database not available"
            }
        
        try:
            import vastdb.errors as vastdb_errors
            
            options = options or {}
            fail_if_exists = options.get("failIfExists", True)
            
            with self.session.transaction() as tx:
                bucket = tx.bucket(self.bucket_name)
                
                try:
                    schema = bucket.create_schema(schema_name, fail_if_exists=fail_if_exists)
                    
                    return {
                        "success": True,
                        "schema": {
                            "name": schema_name,
                            "bucket": self.bucket_name,
                            "path": f"/{self.bucket_name}/{schema_name}",
                            "protocols": ["DATABASE", "S3"],
                            "created": datetime.utcnow().isoformat(),
                            "id": self._generate_schema_id(schema_name)
                        },
                        "message": f"Schema '{schema_name}' created successfully"
                    }
                    
                except vastdb_errors.SchemaExists:
                    if fail_if_exists:
                        return {
                            "success": False,
                            "message": f"Schema '{schema_name}' already exists"
                        }
                    else:
                        # Schema exists but we don't fail, return existing schema info
                        return {
                            "success": True,
                            "schema": {
                                "name": schema_name,
                                "bucket": self.bucket_name,
                                "path": f"/{self.bucket_name}/{schema_name}",
                                "protocols": ["DATABASE", "S3"],
                                "created": datetime.utcnow().isoformat(),
                                "id": self._generate_schema_id(schema_name)
                            },
                            "message": f"Schema '{schema_name}' already exists"
                        }
            
        except Exception as e:
            logger.error(f"Create schema error: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }
    
    async def list_schemas(self) -> Dict[str, Any]:
        """List all schemas in the bucket"""
        if not self._ensure_connection():
            return {
                "success": False,
                "message": self._connection_error or "VAST Database not available",
                "schemas": []
            }
        
        try:
            with self.session.transaction() as tx:
                bucket = tx.bucket(self.bucket_name)
                schemas = bucket.schemas()
                
                schema_list = []
                for schema in schemas:
                    schema_list.append({
                        "name": schema.name,
                        "bucket": self.bucket_name,
                        "path": f"/{self.bucket_name}/{schema.name}",
                        "protocols": ["DATABASE", "S3"],
                        "created": datetime.utcnow().isoformat(),
                        "id": self._generate_schema_id(schema.name)
                    })
                
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
        if not self._ensure_connection():
            return {
                "success": False,
                "message": self._connection_error or "VAST Database not available"
            }
        
        try:
            import vastdb.errors as vastdb_errors
            
            with self.session.transaction() as tx:
                bucket = tx.bucket(self.bucket_name)
                
                try:
                    schema = bucket.schema(schema_name)
                    tables = schema.tables()
                    
                    table_list = []
                    for table in tables:
                        table_list.append({
                            "name": table.name,
                            "schema": schema_name,
                            "columns": [{"name": f.name, "type": str(f.type)} for f in table.columns()],
                            "rows": table.stats.num_rows if hasattr(table, 'stats') else 0,
                            "created": datetime.utcnow().isoformat()
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
                    
                except vastdb_errors.MissingSchema:
                    return {
                        "success": False,
                        "message": f"Schema '{schema_name}' not found"
                    }
            
        except Exception as e:
            logger.error(f"Get schema error: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }
    
    async def delete_schema(self, schema_name: str) -> Dict[str, Any]:
        """Delete a schema"""
        if not self._ensure_connection():
            return {
                "success": False,
                "message": self._connection_error or "VAST Database not available"
            }
        
        try:
            import vastdb.errors as vastdb_errors
            
            with self.session.transaction() as tx:
                bucket = tx.bucket(self.bucket_name)
                
                try:
                    schema = bucket.schema(schema_name)
                    schema.drop()
                    
                    return {
                        "success": True,
                        "message": f"Schema '{schema_name}' deleted successfully"
                    }
                    
                except vastdb_errors.MissingSchema:
                    return {
                        "success": False,
                        "message": f"Schema '{schema_name}' not found"
                    }
            
        except Exception as e:
            logger.error(f"Delete schema error: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }
    
    async def create_table(self, schema_name: str, table_name: str, columns: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a table in a schema"""
        if not self._ensure_connection():
            return {
                "success": False,
                "message": self._connection_error or "VAST Database not available"
            }
        
        try:
            import pyarrow as pa
            import vastdb.errors as vastdb_errors
            
            # Convert columns to PyArrow schema
            if not columns:
                columns = [
                    {"name": "id", "type": "int64", "nullable": False},
                    {"name": "created_at", "type": "timestamp", "nullable": False},
                    {"name": "updated_at", "type": "timestamp", "nullable": True}
                ]
            
            # Convert to PyArrow schema
            pa_fields = []
            for col in columns:
                col_type = self._map_to_arrow_type(col["type"])
                nullable = col.get("nullable", True)
                pa_fields.append(pa.field(col["name"], col_type, nullable=nullable))
            
            arrow_schema = pa.schema(pa_fields)
            
            with self.session.transaction() as tx:
                bucket = tx.bucket(self.bucket_name)
                schema = bucket.schema(schema_name)
                
                try:
                    table = schema.create_table(table_name, arrow_schema)
                    
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
                    
                except vastdb_errors.TableExists:
                    return {
                        "success": False,
                        "message": f"Table '{table_name}' already exists"
                    }
            
        except Exception as e:
            logger.error(f"Create table error: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }
    
    def _map_to_arrow_type(self, type_name: str):
        """Map type name to PyArrow type"""
        import pyarrow as pa
        
        type_map = {
            'string': pa.string(),
            'utf8': pa.string(),
            'int': pa.int64(),
            'int64': pa.int64(),
            'int32': pa.int32(),
            'integer': pa.int64(), 
            'float': pa.float64(),
            'float64': pa.float64(),
            'double': pa.float64(),
            'boolean': pa.bool_(),
            'bool': pa.bool_(),
            'date': pa.date32(),
            'date32': pa.date32(),
            'timestamp': pa.timestamp('us')
        }
        
        return type_map.get(type_name, pa.string())
    
    def _generate_schema_id(self, schema_name: str) -> str:
        """Generate a deterministic ID for the schema"""
        import base64
        source = f"{self.bucket_name}-{schema_name}"
        return base64.b64encode(source.encode()).decode()[:16]
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information"""
        return {
            "endpoint": getattr(self, 'endpoint', None),
            "bucket": getattr(self, 'bucket_name', None),
            "connected": self.session is not None,
            "configuration_error": self._connection_error
        }


# Global service instance - now safe to create at module level
vastdb_service = VastDbService()