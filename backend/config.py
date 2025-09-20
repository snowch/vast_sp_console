"""
Configuration settings for VAST Services backend
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings"""
    
    # Application Configuration
    NODE_ENV: str = "development"
    PORT: int = 3001
    JWT_SECRET: str = "your-secure-secret-key-change-this"
    JWT_EXPIRES_IN: str = "8h"
    FRONTEND_URL: str = "http://localhost:3000"
    
    # VAST Database Configuration (Optional - will be checked when needed)
    VAST_ENDPOINT: Optional[str] = None
    VAST_ACCESS_KEY_ID: Optional[str] = None
    VAST_SECRET_ACCESS_KEY: Optional[str] = None
    VAST_BUCKET_NAME: Optional[str] = None
    
    # Optional VAST Configuration
    VAST_REGION: str = "africa-east-1"
    VAST_VERIFY_SSL: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def validate_vast_config():
    """Validate VAST configuration - raises ValueError if invalid"""
    required_vars = [
        "VAST_ENDPOINT",
        "VAST_ACCESS_KEY_ID", 
        "VAST_SECRET_ACCESS_KEY",
        "VAST_BUCKET_NAME"
    ]
    
    missing_vars = []
    placeholder_vars = []
    
    for var in required_vars:
        value = getattr(settings, var)
        if not value:
            missing_vars.append(var)
        elif value in ["your-vast-endpoint", "your-access-key", "your-secret-key", "your-bucket-name"]:
            placeholder_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required VAST environment variables: {missing_vars}")
    
    if placeholder_vars:
        raise ValueError(f"VAST environment variables contain placeholder values: {placeholder_vars}")


def get_vast_connection_info():
    """Get VAST connection information - returns None if not configured"""
    try:
        validate_vast_config()
        return {
            "endpoint": settings.VAST_ENDPOINT,
            "bucket": settings.VAST_BUCKET_NAME,
            "region": settings.VAST_REGION,
            "verify_ssl": settings.VAST_VERIFY_SSL,
            "configured": True
        }
    except ValueError as e:
        logger.warning(f"VAST configuration invalid: {e}")
        return {
            "endpoint": settings.VAST_ENDPOINT,
            "bucket": settings.VAST_BUCKET_NAME,
            "region": settings.VAST_REGION,
            "verify_ssl": settings.VAST_VERIFY_SSL,
            "configured": False,
            "error": str(e)
        }