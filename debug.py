#!/usr/bin/env python3
"""
Debug script to identify FastAPI route conflicts
Run this inside your backend directory to diagnose the 405 error
"""

import sys
import os
sys.path.append('.')

def debug_routes():
    """Debug FastAPI routes to identify conflicts"""
    
    print("🔍 FastAPI Route Debugging")
    print("=" * 50)
    
    try:
        # Import your FastAPI app
        from main import app
        
        print(f"✅ Successfully imported FastAPI app")
        print(f"📊 Total routes: {len(app.routes)}")
        print()
        
        # Filter routes related to schemas
        schema_routes = []
        for route in app.routes:
            if hasattr(route, 'path') and '/api/database/schemas' in route.path:
                route_info = {
                    'path': route.path,
                    'methods': list(getattr(route, 'methods', [])),
                    'name': getattr(route, 'name', 'Unknown'),
                    'endpoint': str(getattr(route, 'endpoint', 'Unknown'))
                }
                schema_routes.append(route_info)
        
        print("🎯 Schema-related routes:")
        print("-" * 30)
        
        if not schema_routes:
            print("❌ No schema routes found!")
            print("   This means the router isn't being included properly")
            return False
        
        # Sort by path length (shortest first) to see route resolution order
        schema_routes.sort(key=lambda x: len(x['path']))
        
        for i, route in enumerate(schema_routes, 1):
            print(f"{i}. Path: {route['path']}")
            print(f"   Methods: {route['methods']}")
            print(f"   Name: {route['name']}")
            print(f"   Endpoint: {route['endpoint']}")
            print()
        
        # Check for the problematic route
        root_schema_routes = [r for r in schema_routes if r['path'] == '/api/database/schemas']
        
        if not root_schema_routes:
            print("❌ PROBLEM FOUND: No route for '/api/database/schemas'")
            print("   This explains the 405 error!")
            return False
        
        # Check if GET method is supported
        root_route = root_schema_routes[0]
        if 'GET' not in root_route['methods']:
            print("❌ PROBLEM FOUND: GET method not allowed on '/api/database/schemas'")
            print(f"   Allowed methods: {root_route['methods']}")
            print("   This explains the 405 error!")
            return False
        
        print("✅ Route configuration looks correct")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import main app: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during route analysis: {e}")
        return False


def check_router_inclusion():
    """Check if schema router is properly included"""
    
    print("\n🔧 Router Inclusion Check")
    print("-" * 30)
    
    try:
        # Check if schema_controller can be imported
        from controllers.schema_controller import router as schema_router
        print("✅ Schema router imported successfully")
        
        # Check routes in the router
        router_routes = []
        for route in schema_router.routes:
            if hasattr(route, 'path'):
                router_routes.append({
                    'path': route.path,
                    'methods': list(getattr(route, 'methods', [])),
                    'name': getattr(route, 'name', 'Unknown')
                })
        
        print(f"📊 Router has {len(router_routes)} routes:")
        
        for route in router_routes:
            print(f"   • {route['path']} [{', '.join(route['methods'])}]")
        
        # Check if root route exists
        root_routes = [r for r in router_routes if r['path'] == '/']
        if not root_routes:
            print("❌ PROBLEM: No root route ('/') in schema router")
            return False
        
        if 'GET' not in root_routes[0]['methods']:
            print("❌ PROBLEM: Root route doesn't allow GET method")
            return False
        
        print("✅ Schema router configuration is correct")
        return True
        
    except ImportError as e:
        print(f"❌ Cannot import schema router: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking router: {e}")
        return False


def test_manual_request():
    """Test making a manual request to identify the issue"""
    
    print("\n🧪 Manual Request Test")
    print("-" * 30)
    
    try:
        import httpx
        
        # Test the problematic endpoint
        print("Testing GET /api/database/schemas...")
        
        with httpx.Client() as client:
            try:
                response = client.get("http://localhost:3001/api/database/schemas")
                print(f"Response: {response.status_code} {response.reason_phrase}")
                
                if response.status_code == 405:
                    # Check allowed methods
                    allow_header = response.headers.get('allow', 'Not provided')
                    print(f"Allowed methods: {allow_header}")
                    
                    # Try to get more details
                    try:
                        error_detail = response.json()
                        print(f"Error details: {error_detail}")
                    except:
                        print(f"Response text: {response.text}")
                
            except httpx.ConnectError:
                print("❌ Cannot connect to http://localhost:3001")
                print("   Make sure the server is running")
            except Exception as e:
                print(f"❌ Request failed: {e}")
        
    except ImportError:
        print("❌ httpx not available, skipping request test")


def suggest_fixes():
    """Suggest potential fixes based on common issues"""
    
    print("\n💡 Potential Solutions")
    print("-" * 30)
    
    print("1. Check route order in schema_controller.py:")
    print("   - Static routes (/connection) must come BEFORE parameterized routes (/{name})")
    print("   - Root route (/) must be defined with @router.get('/')")
    print()
    
    print("2. Verify router inclusion in main.py:")
    print("   - app.include_router(schema_router, prefix='/api/database/schemas')")
    print("   - Check for any errors during router inclusion")
    print()
    
    print("3. Check for duplicate route definitions:")
    print("   - Remove any conflicting @router.get('') or @router.post('') at the bottom")
    print("   - Each route path+method combination should be unique")
    print()
    
    print("4. Restart the application after changes:")
    print("   - docker compose down && docker compose up --build")
    print()
    
    print("5. Test with curl to isolate the issue:")
    print("   - curl -X GET http://localhost:3001/api/database/schemas")
    print("   - curl -X GET http://localhost:3001/api/database/schemas/connection")


def main():
    """Main debugging function"""
    
    # Change to backend directory if not already there
    if os.path.exists('backend'):
        os.chdir('backend')
        print("Changed to backend directory")
    
    # Run all debug checks
    route_ok = debug_routes()
    router_ok = check_router_inclusion()
    
    if not route_ok or not router_ok:
        print("\n❌ Issues found in route configuration")
        suggest_fixes()
    else:
        print("\n✅ Route configuration appears correct")
        print("   The 405 error might be due to other factors:")
        print("   - Server restart needed")
        print("   - Caching issues")
        print("   - Middleware interference")
    
    # Always test the actual request
    test_manual_request()


if __name__ == "__main__":
    main()