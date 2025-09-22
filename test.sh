#!/usr/bin/env python3
"""
Debug script to test VAST cluster connectivity
"""

import asyncio
import httpx
import time
import sys
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings for testing
disable_warnings(InsecureRequestWarning)

async def test_vast_connection(host="10.143.11.204", port=443, timeout=10):
    """Test connection to VAST cluster"""
    
    print(f"🔍 Testing VAST cluster connectivity...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Timeout: {timeout}s")
    print()
    
    base_url = f"https://{host}:{port}"
    
    # Test basic connectivity first
    print("1️⃣ Testing basic HTTPS connectivity...")
    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            verify=False,  # Skip SSL verification for testing
            follow_redirects=True
        ) as client:
            start_time = time.time()
            response = await client.get(f"{base_url}/", timeout=timeout)
            elapsed = time.time() - start_time
            
            print(f"   ✅ Connection successful!")
            print(f"   📊 Status: {response.status_code}")
            print(f"   ⏱️  Time: {elapsed:.2f}s")
            print(f"   📄 Response length: {len(response.content)} bytes")
            
            if response.headers:
                print(f"   🔧 Server: {response.headers.get('Server', 'Unknown')}")
            
    except httpx.TimeoutException:
        print(f"   ❌ Connection timeout after {timeout}s")
        return False
    except httpx.ConnectError as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False
    
    # Test API endpoint
    print("\n2️⃣ Testing VAST API endpoint...")
    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            verify=False,
            follow_redirects=True,
            headers={'Accept': 'application/json'}
        ) as client:
            start_time = time.time()
            response = await client.get(f"{base_url}/api/", timeout=timeout)
            elapsed = time.time() - start_time
            
            print(f"   ✅ API endpoint accessible!")
            print(f"   📊 Status: {response.status_code}")
            print(f"   ⏱️  Time: {elapsed:.2f}s")
            
            # Try to get API info
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   📝 API Response: {data}")
                except:
                    print(f"   📝 API Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ API endpoint failed: {e}")
    
    # Test token endpoint
    print("\n3️⃣ Testing token endpoint...")
    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            verify=False,
            follow_redirects=True,
            headers={'Content-Type': 'application/json'}
        ) as client:
            
            # Test OPTIONS request first (for CORS)
            start_time = time.time()
            response = await client.options(f"{base_url}/api/token/", timeout=timeout)
            elapsed = time.time() - start_time
            
            print(f"   ✅ Token endpoint OPTIONS: {response.status_code} ({elapsed:.2f}s)")
            
            # Test actual token request with dummy credentials
            token_data = {
                "username": "test",
                "password": "test"
            }
            
            start_time = time.time()
            response = await client.post(
                f"{base_url}/api/token/", 
                json=token_data,
                timeout=timeout
            )
            elapsed = time.time() - start_time
            
            print(f"   📊 Token POST Status: {response.status_code} ({elapsed:.2f}s)")
            
            if response.status_code == 401:
                print(f"   ✅ Expected 401 - token endpoint is working")
            elif response.status_code == 200:
                print(f"   ⚠️  Unexpected 200 - check credentials")
            else:
                print(f"   📝 Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Token endpoint failed: {e}")
    
    return True


async def test_from_docker():
    """Test if the issue is Docker networking"""
    print("\n🐳 Testing Docker networking...")
    
    # Test from host network vs bridge network
    print("   This script is running from the host network.")
    print("   The FastAPI app runs inside Docker with bridge networking.")
    print("   If this script works but the app doesn't, it's a Docker networking issue.")
    

def main():
    """Main function"""
    print("🚀 VAST Cluster Connection Debugger")
    print("=" * 50)
    
    # You can modify these values
    host = "10.143.11.204"
    port = 443
    timeout = 10
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    try:
        asyncio.run(test_vast_connection(host, port, timeout))
        asyncio.run(test_from_docker())
        
        print("\n" + "=" * 50)
        print("🔧 TROUBLESHOOTING SUGGESTIONS:")
        print()
        print("If connection fails:")
        print("1. Check if VAST cluster is running")
        print("2. Verify the IP address and port")
        print("3. Check firewall settings")
        print("4. Test from host: ping 10.143.11.204")
        print("5. Test HTTPS: curl -k https://10.143.11.204")
        print()
        print("If this script works but FastAPI doesn't:")
        print("1. Docker networking issue - try host networking")
        print("2. Add to docker-compose.yml: network_mode: host")
        print("3. Or add VAST cluster to Docker network")
        
    except KeyboardInterrupt:
        print("\n❌ Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")


if __name__ == "__main__":
    main()