"""
Authentication middleware for JWT token handling
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from config import settings

security = HTTPBearer()


class AuthHandler:
    """JWT authentication handler"""
    
    def __init__(self):
        self.secret = settings.JWT_SECRET
        self.algorithm = "HS256"
    
    def encode_token(self, payload: Dict[str, Any]) -> str:
        """Encode JWT token"""
        # Calculate expiration time
        expires_delta = self._parse_expires_in(settings.JWT_EXPIRES_IN)
        payload['exp'] = datetime.utcnow() + expires_delta
        payload['iat'] = datetime.utcnow()
        
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def _parse_expires_in(self, expires_in: str) -> timedelta:
        """Parse expiration time string (e.g., '8h', '30m', '1d')"""
        if expires_in.endswith('h'):
            hours = int(expires_in[:-1])
            return timedelta(hours=hours)
        elif expires_in.endswith('m'):
            minutes = int(expires_in[:-1])
            return timedelta(minutes=minutes)
        elif expires_in.endswith('d'):
            days = int(expires_in[:-1])
            return timedelta(days=days)
        else:
            # Default to hours if no suffix
            return timedelta(hours=int(expires_in))


auth_handler = AuthHandler()


async def authenticate_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Dependency to authenticate JWT token"""
    try:
        payload = auth_handler.decode_token(credentials.credentials)
        return {
            "username": payload.get("username"),
            "vastHost": payload.get("vastHost"),
            "vastPort": payload.get("vastPort"),
            "tenant": payload.get("tenant"),
            "accessToken": payload.get("accessToken"),
            "refreshToken": payload.get("refreshToken")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


async def get_current_user(user: Dict[str, Any] = Depends(authenticate_token)) -> Dict[str, Any]:
    """Get current authenticated user"""
    return user


# Optional authentication (doesn't raise error if no token)
class OptionalHTTPBearer(HTTPBearer):
    """Optional HTTP Bearer authentication"""
    
    async def __call__(self, request) -> Optional[HTTPAuthorizationCredentials]:
        try:
            return await super().__call__(request)
        except HTTPException:
            return None


optional_security = OptionalHTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security)
) -> Optional[Dict[str, Any]]:
    """Get current user if authenticated, otherwise return None"""
    if credentials:
        try:
            payload = auth_handler.decode_token(credentials.credentials)
            return {
                "username": payload.get("username"),
                "vastHost": payload.get("vastHost"),
                "vastPort": payload.get("vastPort"),
                "tenant": payload.get("tenant"),
                "accessToken": payload.get("accessToken"),
                "refreshToken": payload.get("refreshToken")
            }
        except HTTPException:
            return None
    return None
