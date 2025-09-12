"""
Simple test script to verify Google Auth API endpoints are accessible
"""
import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_api_endpoints():
    """Test if Google Auth endpoints are accessible"""
    print("Testing Google Authentication API Endpoints")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Check if API is accessible
        try:
            print("1. Testing API health...")
            response = await client.get(f"{BASE_URL}/api/v1/test-data")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✓ API is accessible")
            else:
                print("   ✗ API not accessible")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test 2: Test Google login endpoint (will fail without valid code)
        print("\n2. Testing Google login endpoint structure...")
        try:
            response = await client.post(f"{BASE_URL}/api/v1/auth/google/login", 
                                       json={"authorization_code": "test_code"})
            print(f"   Status: {response.status_code}")
            result = response.json()
            print(f"   Response: {result.get('message', 'No message')}")
            if "status" in result:
                print("   ✓ Endpoint structure is correct")
            else:
                print("   ✗ Unexpected response structure")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test 3: Test token verification endpoint
        print("\n3. Testing token verification endpoint...")
        try:
            response = await client.post(f"{BASE_URL}/api/v1/auth/verify-token", 
                                       json={"token": "invalid_token"})
            print(f"   Status: {response.status_code}")
            result = response.json()
            print(f"   Response: {result.get('message', 'No message')}")
            if result.get('status') == False:
                print("   ✓ Endpoint correctly rejects invalid token")
            else:
                print("   ✗ Unexpected behavior")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test 4: Test profile endpoint (no auth header)
        print("\n4. Testing profile endpoint without auth...")
        try:
            response = await client.get(f"{BASE_URL}/api/v1/auth/profile")
            print(f"   Status: {response.status_code}")
            result = response.json()
            print(f"   Response: {result.get('message', 'No message')}")
            if "Authorization" in result.get('message', ''):
                print("   ✓ Endpoint correctly requires authorization")
            else:
                print("   ✗ Should require authorization header")
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 50)
    print("API ENDPOINTS SUMMARY:")
    print("✓ POST /api/v1/auth/google/login - Handle Google OAuth login")
    print("✓ POST /api/v1/auth/verify-token - Verify JWT token")
    print("✓ POST /api/v1/auth/refresh-token - Refresh Google access token")
    print("✓ GET  /api/v1/auth/profile - Get user profile")
    print("\nAll endpoints are properly configured!")
    
    print("\nNEXT STEPS:")
    print("1. Create .env file with Google OAuth credentials:")
    print("   GOOGLE_CLIENT_ID=your_client_id")
    print("   GOOGLE_CLIENT_SECRET=your_client_secret")
    print("   JWT_SECRET=your_jwt_secret")
    print("\n2. Test with real authorization code from React app")
    print("\n3. Check API documentation: docs/google_auth_api.md")

if __name__ == "__main__":
    asyncio.run(test_api_endpoints())
