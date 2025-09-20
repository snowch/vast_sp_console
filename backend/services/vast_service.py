"""
VAST API service for cluster authentication and operations
"""

import httpx
import time
import logging
from typing import Dict, Optional, Any
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

logger = logging.getLogger(__name__)


class VastService:
    """VAST API service for authentication and basic operations"""
    
    def __init__(self):
        self.clients: Dict[str, Dict[str, Any]] = {}
        
    def create_client(self, host: str, port: int, skip_ssl_verify: bool = True) -> httpx.AsyncClient:
        """Create HTTP client for VAST API"""
        base_url = f"https://{host}:{port}/api"
        
        # Configure SSL verification
        verify_ssl = not skip_ssl_verify
        if skip_ssl_verify:
            disable_warnings(InsecureRequestWarning)
        
        return httpx.AsyncClient(
            base_url=base_url,
            timeout=30.0,
            verify=verify_ssl,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
    
    async def authenticate(self, host: str, port: int, username: str, password: str, tenant: str = "default") -> Dict[str, Any]:
        """Authenticate with VAST cluster"""
        try:
            client = self.create_client(host, port)
            
            # Use the token endpoint from the swagger spec
            token_endpoint = "/token/" if tenant == "default" else f"/token/{tenant}"
            
            async with client as c:
                response = await c.post(token_endpoint, json={
                    "username": username,
                    "password": password
                })
                
                if response.status_code != 200:
                    error_data = {}
                    try:
                        error_data = response.json()
                    except:
                        pass
                    
                    if response.status_code == 401:
                        return {"success": False, "message": "Invalid credentials"}
                    elif response.status_code == 404:
                        return {"success": False, "message": "VAST API endpoint not found"}
                    else:
                        message = error_data.get("message", response.text)
                        return {"success": False, "message": f"Authentication failed: {message}"}
                
                data = response.json()
                
                if data.get("access"):
                    client_key = f"{host}:{port}:{tenant}"
                    
                    # Store authenticated client info
                    self.clients[client_key] = {
                        "access_token": data["access"],
                        "refresh_token": data["refresh"],
                        "username": username,
                        "tenant": tenant,
                        "created_at": time.time(),
                        "host": host,
                        "port": port
                    }
                    
                    return {
                        "success": True,
                        "accessToken": data["access"],
                        "refreshToken": data["refresh"]
                    }
                
                return {
                    "success": False,
                    "message": "Invalid response format"
                }
                
        except httpx.ConnectError:
            return {"success": False, "message": "Cannot connect to VAST server"}
        except httpx.ConnectTimeout:
            return {"success": False, "message": "Connection timeout"}
        except Exception as e:
            logger.error(f"VAST authentication error: {str(e)}")
            return {"success": False, "message": f"Authentication failed: {str(e)}"}
    
    async def verify_token(self, access_token: str, host: str, port: int) -> bool:
        """Verify if token is still valid"""
        try:
            client = self.create_client(host, port)
            
            async with client as c:
                c.headers["Authorization"] = f"Bearer {access_token}"
                
                # Try to make a simple API call to verify token
                response = await c.get("/tenants/configured_idp/")
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            return False
    
    def get_authenticated_client_info(self, host: str, port: int, tenant: str = "default") -> Optional[Dict[str, Any]]:
        """Get cached client information"""
        client_key = f"{host}:{port}:{tenant}"
        cached = self.clients.get(client_key)
        
        if not cached:
            return None
        
        # Check if token is too old (8 hours)
        age_hours = (time.time() - cached["created_at"]) / 3600
        if age_hours > 8:
            del self.clients[client_key]
            return None
            
        return cached
    
    async def get_tenants(self, host: str, port: int, tenant: str = "default") -> Dict[str, Any]:
        """Get list of tenants"""
        try:
            client_info = self.get_authenticated_client_info(host, port, tenant)
            if not client_info:
                return {"success": False, "message": "No authenticated session found"}
            
            client = self.create_client(host, port)
            
            async with client as c:
                c.headers["Authorization"] = f"Bearer {client_info['access_token']}"
                response = await c.get("/tenants/")
                
                if response.status_code == 200:
                    return {"success": True, "data": response.json()}
                else:
                    return {"success": False, "message": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Get tenants error: {str(e)}")
            return {"success": False, "message": str(e)}
    
    async def get_vip_pools(self, host: str, port: int, tenant: str = "default") -> Dict[str, Any]:
        """Get VIP pools"""
        try:
            client_info = self.get_authenticated_client_info(host, port, tenant)
            if not client_info:
                return {"success": False, "message": "No authenticated session found"}
            
            client = self.create_client(host, port)
            
            async with client as c:
                c.headers["Authorization"] = f"Bearer {client_info['access_token']}"
                response = await c.get("/vippools/")
                
                if response.status_code == 200:
                    return {"success": True, "data": response.json()}
                else:
                    return {"success": False, "message": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Get VIP pools error: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def cleanup_sessions(self):
        """Clean up expired sessions"""
        now = time.time()
        expired_keys = []
        
        for key, session in self.clients.items():
            age_hours = (now - session["created_at"]) / 3600
            if age_hours > 8:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.clients[key]


# Global service instance
vast_service = VastService()
