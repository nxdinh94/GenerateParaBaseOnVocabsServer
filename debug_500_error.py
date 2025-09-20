#!/usr/bin/env python3
"""
Test script to reproduce the 500 error with authentication
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_with_mock_token():
    """Test with a mock/invalid token to see what kind of 500 error we get"""
    print("🔍 Testing save-paragraph with Mock Token")
    print("=" * 60)
    
    # Test data
    test_data = {
        "vocabs": ["test", "error", "debug"],
        "paragraph": "Test paragraph to debug 500 error."
    }
    
    # Test with different mock tokens to understand the error
    mock_tokens = [
        {
            "name": "Invalid JWT Format",
            "token": "invalid.jwt.token"
        },
        {
            "name": "Valid JWT Structure but Invalid Signature", 
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        },
        {
            "name": "Empty Bearer Token",
            "token": ""
        }
    ]
    
    for mock_token in mock_tokens:
        print(f"\n🧪 Testing: {mock_token['name']}")
        
        headers = {
            "Authorization": f"Bearer {mock_token['token']}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/save-paragraph",
                json=test_data,
                headers=headers,
                timeout=10
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 500:
                print(f"   ❌ 500 Internal Server Error detected!")
                try:
                    error_data = response.json()
                    print(f"   Error Details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Raw Response: {response.text}")
            elif response.status_code == 401:
                error_data = response.json()
                print(f"   ✅ 401 Unauthorized (expected):")
                print(f"      Error: {error_data.get('detail', {}).get('error')}")
                print(f"      Message: {error_data.get('detail', {}).get('message')}")
            else:
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection failed - server not running")
        except requests.exceptions.Timeout:
            print(f"   ❌ Request timeout")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")

def test_auth_profile_endpoint():
    """Test the /auth/profile endpoint to see if it has similar issues"""
    print(f"\n🔍 Testing /auth/profile Endpoint")
    print("=" * 60)
    
    mock_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    
    headers = {
        "Authorization": f"Bearer {mock_token}"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/auth/profile",
            headers=headers,
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 500:
            print(f"   ❌ 500 Internal Server Error in auth/profile too!")
            try:
                error_data = response.json()
                print(f"   Error Details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Raw Response: {response.text}")
        else:
            try:
                response_data = response.json()
                print(f"   Response: {json.dumps(response_data, indent=2)}")
            except:
                print(f"   Raw Response: {response.text}")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_simple_endpoints():
    """Test simple non-auth endpoints to see if server is working"""
    print(f"\n🔍 Testing Simple Endpoints (No Auth)")
    print("=" * 60)
    
    endpoints = [
        {
            "name": "Test Data",
            "method": "GET",
            "url": f"{BASE_URL}/api/v1/test-data"
        },
        {
            "name": "Generate Text",
            "method": "POST", 
            "url": f"{BASE_URL}/api/v1/generate",
            "data": {"prompt": "Hello", "max_tokens": 10}
        }
    ]
    
    for endpoint in endpoints:
        print(f"\n🧪 Testing: {endpoint['name']}")
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], timeout=10)
            else:
                response = requests.post(endpoint['url'], json=endpoint.get('data'), timeout=10)
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 500:
                print(f"   ❌ 500 Error in simple endpoint!")
                print(f"   Raw Response: {response.text}")
            elif response.status_code == 200:
                print(f"   ✅ Success")
            else:
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def show_debugging_steps():
    """Show debugging steps for 500 errors"""
    print(f"\n🔧 Debugging Steps for 500 Errors")
    print("=" * 60)
    
    steps = [
        "1. Check server logs in the uvicorn terminal",
        "2. Verify database connection is working",
        "3. Check if all required environment variables are set",
        "4. Test JWT token verification service",
        "5. Check MongoDB connection and collections",
        "6. Verify all imports are working properly"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print(f"\n💡 Common 500 Error Causes:")
    print(f"   - Database connection issues")
    print(f"   - Missing environment variables") 
    print(f"   - JWT verification service errors")
    print(f"   - Import/module loading errors")
    print(f"   - MongoDB collection/CRUD errors")

def main():
    print("🚀 Debugging 500 Internal Server Error")
    print(f"🕒 Debug Time: {datetime.now().isoformat()}")
    
    test_simple_endpoints()
    test_auth_profile_endpoint() 
    test_with_mock_token()
    show_debugging_steps()
    
    print("\n" + "=" * 60)
    print("🔍 Next Steps:")
    print("1. Check the uvicorn server terminal for error logs")
    print("2. Test with a real Google OAuth JWT token")
    print("3. Verify database and environment setup")
    print("=" * 60)

if __name__ == "__main__":
    main()