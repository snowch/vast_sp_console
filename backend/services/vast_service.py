"""
VAST API service for cluster authentication with improved timeout handling
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
        # Disable SSL warnings for development
        disable_warnings(InsecureRequestWarning)
        
    def create_client(self, host: str, port: int, timeout: float = 10.0, skip_ssl_verify: bool = True) -> httpx.AsyncClient:
        """Create HTTP client for VAST API with proper timeout settings"""
        base_url = f"https://{host}:{port}/api"
        
        # Configure SSL verification
        verify_ssl = not skip_ssl_verify
        
        # Create timeout configuration
        timeout_config = httpx.Timeout(
            timeout=timeout,
            connect=5.0,  # Connection timeout
            read=timeout,  # Read timeout
            write=5.0,    # Write timeout
            pool=2.0      # Pool timeout
        )
        
        return httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout_config,
            verify=verify_ssl,
            follow_redirects=True,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'VAST-Services-Client/1.0'
            }
        )
    
    async def test_connectivity(self, host: str, port: int, timeout: float = 5.0) -> Dict[str, Any]:
        """Test basic connectivity to VAST cluster before attempting authentication"""
        try:
            logger.info(f"Testing connectivity to {host}:{port}")
            client = self.create_client(host, port, timeout=timeout)
            
            async with client as c:
                start_time = time.time()
                
                # Try a simple GET request to test connectivity
                response = await c.get("/", timeout=timeout)
                
                elapsed = time.time() - start_time
                
                logger.info(f"Connectivity test successful: {response.status_code} ({elapsed:.2f}s)")
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response_time": elapsed,
                    "server": response.headers.get("Server", "Unknown")
                }
                
        except httpx.TimeoutException:
            logger.error(f"Connectivity test timeout after {timeout}s")
            return {
                "success": False,
                "error": "timeout",
                "message": f"Connection timeout after {timeout}s"
            }
        except httpx.ConnectError as e:
            logger.error(f"Connectivity test connection error: {e}")
            return {
                "success": False,
                "error": "connection_error",
                "message": f"Cannot connect to {host}:{port}"
            }
        except Exception as e:
            logger.error(f"Connectivity test error: {e}")
            return {
                "success": False,
                "error": "unknown",
                "message": str(e)
            }
    
    async def authenticate(self, host: str, port: int, username: str, password: str, tenant: str = "default", timeout: float = 15.0) -> Dict[str, Any]:
        """Authenticate with VAST cluster with improved error handling"""
        try:
            # First test basic connectivity
            logger.info(f"Starting authentication to {host}:{port} for user {username}")
            
            connectivity_test = await self.test_connectivity(host, port, timeout=5.0)
            if not connectivity_test["success"]:
                return {
                    "success": False,
                    "message": f"Cannot reach VAST cluster: {connectivity_test['message']}"
                }
            
            logger.info(f"Connectivity test passed, proceeding with authentication")
            
            client = self.create_client(host, port, timeout=timeout)
            
            # Use the token endpoint from the swagger spec
            token_endpoint = "/token/" if tenant == "default" else f"/token/{tenant}"
            
            async with client as c:
                start_time = time.time()
                
                logger.debug(f"Sending POST request to {token_endpoint}")
                
                response = await c.post(token_endpoint, json={
                    "username": username,
                    "password": password
                }, timeout=timeout)
                
                elapsed = time.time() - start_time
                logger.info(f"Authentication request completed: {response.status_code} ({elapsed:.2f}s)")
                
                if response.status_code != 200:
                    error_data = {}
                    try:
                        error_data = response.json()
                    except:
                        pass
                    
                    if response.status_code == 401:
                        return {"success": False, "message": "Invalid credentials"}
                    elif response.status_code == 404:
                        return {"success": False, "message": "VAST API endpoint not found - check host and port"}
                    elif response.status_code == 403:
                        return {"success": False, "message": "Access forbidden - check user permissions"}
                    elif response.status_code >= 500:
                        return {"success": False, "message": f"VAST server error ({response.status_code})"}
                    else:
                        message = error_data.get("message", response.text)
                        return {"success": False, "message": f"Authentication failed: {message}"}
                
                try:
                    data = response.json()
                except Exception as e:
                    logger.error(f"Failed to parse authentication response: {e}")
                    return {"success": False, "message": "Invalid response format from VAST server"}
                
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
                    
                    logger.info(f"Authentication successful for {username}@{host}")
                    
                    return {
                        "success": True,
                        "accessToken": data["access"],
                        "refreshToken": data["refresh"]
                    }
                
                return {
                    "success": False,
                    "message": "Authentication response missing access token"
                }
                
        except httpx.TimeoutException:
            logger.error(f"Authentication timeout after {timeout}s")
            return {
                "success": False, 
                "message": f"Authentication timeout after {timeout}s - VAST cluster may be slow or unreachable"
            }
        except httpx.ConnectError:
            logger.error(f"Cannot connect to VAST server {host}:{port}")
            return {
                "success": False, 
                "message": f"Cannot connect to VAST server {host}:{port} - check network connectivity"
            }
        except Exception as e:
            logger.error(f"VAST authentication error: {str(e)}")
            return {"success": False, "message": f"Authentication failed: {str(e)}"}
    
    async def verify_token(self, access_token: str, host: str, port: int, timeout: float = 10.0) -> bool:
        """Verify if token is still valid with shorter timeout"""
        try:
            client = self.create_client(host, port, timeout=timeout)
            
            async with client as c:
                c.headers["Authorization"] = f"Bearer {access_token}"
                
                # Try to make a simple API call to verify token
                response = await c.get("/tenants/configured_idp/", timeout=timeout)
                return response.status_code == 200
                
        except httpx.TimeoutException:
            logger.error(f"Token verification timeout after {timeout}s")
            return False
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
    
    async def get_tenants(self, host: str, port: int, tenant: str = "default", timeout: float = 10.0) -> Dict[str, Any]:
        """Get list of tenants with timeout"""
        try:
            client_info = self.get_authenticated_client_info(host, port, tenant)
            if not client_info:
                return {"success": False, "message": "No authenticated session found"}
            
            client = self.create_client(host, port, timeout=timeout)
            
            async with client as c:
                c.headers["Authorization"] = f"Bearer {client_info['access_token']}"
                response = await c.get("/tenants/", timeout=timeout)
                
                if response.status_code == 200:
                    return {"success": True, "data": response.json()}
                else:
                    return {"success": False, "message": f"HTTP {response.status_code}"}
                    
        except httpx.TimeoutException:
            logger.error(f"Get tenants timeout after {timeout}s")
            return {"success": False, "message": "Request timeout"}
        except Exception as e:
            logger.error(f"Get tenants error: {str(e)}")
            return {"success": False, "message": str(e)}
    
    async def get_vip_pools(self, host: str, port: int, tenant: str = "default", timeout: float = 10.0) -> Dict[str, Any]:
        """Get VIP pools with timeout"""
        try:
            client_info = self.get_authenticated_client_info(host, port, tenant)
            if not client_info:
                return {"success": False, "message": "No authenticated session found"}
            
            client = self.create_client(host, port, timeout=timeout)
            
            async with client as c:
                c.headers["Authorization"] = f"Bearer {client_info['access_token']}"
                response = await c.get("/vippools/", timeout=timeout)
                
                if response.status_code == 200:
                    return {"success": True, "data": response.json()}
                else:
                    return {"success": False, "message": f"HTTP {response.status_code}"}
                    
        except httpx.TimeoutException:
            logger.error(f"Get VIP pools timeout after {timeout}s")
            return {"success": False, "message": "Request timeout"}
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