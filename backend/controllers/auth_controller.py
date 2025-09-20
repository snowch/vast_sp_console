"""
Authentication controller for VAST cluster login/logout
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
import logging
from typing import Dict, Any

from models import LoginRequest, LoginResponse, TokenVerifyResponse
from services.vast_service import vast_service
from middleware.auth_middleware import auth_handler, security, get_current_user_optional

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate with VAST cluster and return JWT token"""
    try:
        # Authenticate with VAST API
        auth_result = await vast_service.authenticate(
            host=request.vastHost,
            port=request.vastPort,
            username=request.username,
            password=request.password,
            tenant=request.tenant
        )
        
        if not auth_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=auth_result["message"]
            )
        
        # Create JWT token with VAST credentials
        token_payload = {
            "username": request.username,
            "vastHost": request.vastHost,
            "vastPort": request.vastPort,
            "tenant": request.tenant,
            "accessToken": auth_result["accessToken"],
            "refreshToken": auth_result["refreshToken"]
        }
        
        token = auth_handler.encode_token(token_payload)
        
        return LoginResponse(
            success=True,
            token=token,
            user={
                "username": request.username,
                "vastHost": request.vastHost,
                "vastPort": request.vastPort,
                "tenant": request.tenant
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/logout")
async def logout():
    """Logout user (JWT tokens are stateless, so just return success)"""
    return {"success": True, "message": "Logged out successfully"}


@router.get("/verify", response_model=TokenVerifyResponse)
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Verify JWT token and optionally check with VAST cluster"""
    try:
        # Decode and validate token
        payload = auth_handler.decode_token(credentials.credentials)
        
        # Optionally verify token is still valid with VAST
        is_valid = await vast_service.verify_token(
            access_token=payload.get("accessToken"),
            host=payload.get("vastHost"),
            port=payload.get("vastPort")
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired or invalid"
            )
        
        return TokenVerifyResponse(
            valid=True,
            user={
                "username": payload.get("username"),
                "vastHost": payload.get("vastHost"),
                "vastPort": payload.get("vastPort"),
                "tenant": payload.get("tenant")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


@router.get("/me")
async def get_current_user_info(user: Dict[str, Any] = Depends(get_current_user_optional)):
    """Get current user information"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    return {
        "success": True,
        "user": {
            "username": user.get("username"),
            "vastHost": user.get("vastHost"),
            "vastPort": user.get("vastPort"),
            "tenant": user.get("tenant")
        }
    }
