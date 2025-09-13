"""
Test input history API with JWT authentication
"""
import httpx
import asyncio
import json

async def test_input_history_with_auth():
    """Test input-history API with JWT authentication"""
    
    base_url = "http://localhost:8000/api/v1"
    
    # First, you need to get a JWT token by logging in
    # Using a sample token for demo (replace with real token from login)
    jwt_token = "YOUR_JWT_TOKEN_HERE"  # Replace with actual JWT token
    
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    # Test data for input history (no user_id needed)
    test_data = {
        "words": ["hello", "world", "test", "vocabulary"]
    }
    
    async with httpx.AsyncClient() as client:
        print("🧪 Testing Input History API with Authentication...")
        
        try:
            # Test creating input history with JWT token
            response = await client.post(
                f"{base_url}/db/input-history/",
                headers=headers,
                json=test_data
            )
            
            print(f"📨 Response Status: {response.status_code}")
            print(f"📨 Response Headers: {dict(response.headers)}")
            
            result = response.json()
            print(f"📨 Response Body: {json.dumps(result, indent=2)}")
            
            if response.status_code == 201:
                print("✅ Input history created successfully!")
                print(f"📝 Created history ID: {result.get('id')}")
                print(f"👤 User ID: {result.get('user_id')}")
                print(f"📝 Words: {result.get('words')}")
                return result
            else:
                print(f"❌ Failed to create input history: {result}")
                
        except Exception as e:
            print(f"💥 Error testing input history API: {str(e)}")
    
    return None

async def test_without_auth():
    """Test input-history API without authentication (should fail)"""
    
    base_url = "http://localhost:8000/api/v1"
    
    # Test data for input history
    test_data = {
        "words": ["hello", "world", "test", "vocabulary"]
    }
    
    async with httpx.AsyncClient() as client:
        print("\n🧪 Testing Input History API without Authentication...")
        
        try:
            # Test creating input history without JWT token
            response = await client.post(
                f"{base_url}/db/input-history/",
                headers={"Content-Type": "application/json"},
                json=test_data
            )
            
            print(f"📨 Response Status: {response.status_code}")
            result = response.json()
            print(f"📨 Response Body: {json.dumps(result, indent=2)}")
            
            if response.status_code == 401:
                print("✅ Correctly rejected request without authentication!")
            else:
                print(f"❌ Unexpected response: {result}")
                
        except Exception as e:
            print(f"💥 Error testing input history API: {str(e)}")

if __name__ == "__main__":
    print("🔐 Input History Authentication Test")
    print("=" * 50)
    
    print("\n📋 INSTRUCTIONS:")
    print("1. Make sure the server is running: uvicorn app.main:app --reload")
    print("2. Get a JWT token by logging in through Google OAuth")
    print("3. Replace 'YOUR_JWT_TOKEN_HERE' with the actual token")
    print("4. Run this test")
    
    # Run tests
    asyncio.run(test_without_auth())
    asyncio.run(test_input_history_with_auth())