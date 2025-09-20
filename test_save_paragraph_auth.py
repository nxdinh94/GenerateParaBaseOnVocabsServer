#!/usr/bin/env python3
"""
Test script for save-paragraph API endpoint with proper authentication
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_save_paragraph_with_auth():
    """Test save-paragraph endpoint with proper authentication"""
    print("🔧 Testing POST /save-paragraph with Authentication")
    print("=" * 60)
    
    # Test data
    test_paragraph_data = {
        "vocabs": ["test", "save", "paragraph"],
        "paragraph": "This is a test paragraph to save with vocabularies."
    }
    
    print(f"📤 Testing POST with data:")
    print(json.dumps(test_paragraph_data, indent=2))
    print(f"   URL: {BASE_URL}/api/v1/save-paragraph")
    
    # Test without authentication (will fail)
    print(f"\n🚫 Testing WITHOUT Authorization header:")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/save-paragraph", 
            json=test_paragraph_data
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            error_data = response.json()
            print(f"   ✅ Expected authentication error:")
            print(f"      Error: {error_data.get('detail', {}).get('error')}")
            print(f"      Message: {error_data.get('detail', {}).get('message')}")
        else:
            print(f"   ❌ Unexpected status code")
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection failed - server not running")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test with authentication (replace with real token)
    print(f"\n🔑 Testing WITH Authorization header:")
    print(f"   Note: Replace 'YOUR_JWT_TOKEN_HERE' with actual token from Google login")
    
    # Example with placeholder token
    headers = {
        "Authorization": "Bearer YOUR_JWT_TOKEN_HERE",
        "Content-Type": "application/json"
    }
    
    print(f"   Headers: {headers}")
    print(f"   To get a real token:")
    print(f"   1. Call POST /auth/google/login with Google authorization code")
    print(f"   2. Use the jwt_token from the response")
    print(f"   3. Replace 'YOUR_JWT_TOKEN_HERE' with the actual token")

def test_auth_flow():
    """Show the complete authentication flow"""
    print(f"\n🔐 Complete Authentication Flow")
    print("=" * 60)
    
    print("1. 📱 Google OAuth Flow:")
    print("   - User logs in with Google on frontend")
    print("   - Frontend receives authorization code")
    print("   - Send authorization code to backend")
    
    print("\n2. 🔄 Backend Token Exchange:")
    google_login_example = {
        "authorization_code": "google_auth_code_from_frontend"
    }
    print(f"   POST {BASE_URL}/api/v1/auth/google/login")
    print(f"   Body: {json.dumps(google_login_example, indent=2)}")
    
    print("\n3. ✅ Response with JWT Token:")
    login_response_example = {
        "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "jwt_refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    print(f"   Response: {json.dumps(login_response_example, indent=2)}")
    
    print("\n4. 🔑 Use JWT Token for API Calls:")
    authenticated_request_example = {
        "method": "POST",
        "url": f"{BASE_URL}/api/v1/save-paragraph",
        "headers": {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "Content-Type": "application/json"
        },
        "body": {
            "vocabs": ["test", "vocabularies"],
            "paragraph": "This is a test paragraph."
        }
    }
    print(f"   Example: {json.dumps(authenticated_request_example, indent=2)}")

def show_curl_examples():
    """Show curl examples for testing"""
    print(f"\n🔧 Curl Examples")
    print("=" * 60)
    
    examples = [
        {
            "description": "1. Google Login (get JWT token)",
            "curl": f'''curl -X POST "{BASE_URL}/api/v1/auth/google/login" \\
  -H "Content-Type: application/json" \\
  -d '{{"authorization_code": "your_google_auth_code"}}\''''
        },
        {
            "description": "2. Save Paragraph (with JWT token)",
            "curl": f'''curl -X POST "{BASE_URL}/api/v1/save-paragraph" \\
  -H "Authorization: Bearer <your_jwt_token>" \\
  -H "Content-Type: application/json" \\
  -d '{{"vocabs": ["test", "save"], "paragraph": "Test paragraph to save."}}\''''
        },
        {
            "description": "3. Get User Profile (test token validity)",
            "curl": f'''curl -H "Authorization: Bearer <your_jwt_token>" \\
  "{BASE_URL}/api/v1/auth/profile"'''
        }
    ]
    
    for example in examples:
        print(f"\n📝 {example['description']}:")
        print(f"   {example['curl']}")

def show_endpoint_requirements():
    """Show which endpoints require authentication"""
    print(f"\n📋 API Endpoint Authentication Requirements")
    print("=" * 60)
    
    endpoints = [
        {
            "endpoint": "POST /auth/google/login",
            "auth_required": False,
            "description": "Get JWT token from Google authorization code"
        },
        {
            "endpoint": "POST /auth/verify-token",
            "auth_required": False,
            "description": "Verify if JWT token is valid"
        },
        {
            "endpoint": "POST /save-paragraph",
            "auth_required": True,
            "description": "Save paragraph with vocabularies"
        },
        {
            "endpoint": "GET /vocabs_base_on_category",
            "auth_required": True,
            "description": "Get learned vocabularies with sorting"
        },
        {
            "endpoint": "POST /learned-vocabs",
            "auth_required": True,
            "description": "Create/update learned vocabularies"
        },
        {
            "endpoint": "GET /all-paragraphs",
            "auth_required": True,
            "description": "Get all saved paragraphs"
        },
        {
            "endpoint": "GET /auth/profile",
            "auth_required": True,
            "description": "Get user profile from JWT token"
        },
        {
            "endpoint": "POST /auth/logout",
            "auth_required": True,
            "description": "Logout and delete refresh tokens"
        }
    ]
    
    print("🔓 No Authentication Required:")
    for endpoint in endpoints:
        if not endpoint["auth_required"]:
            print(f"   ✅ {endpoint['endpoint']} - {endpoint['description']}")
    
    print("\n🔒 Authentication Required (Bearer Token):")
    for endpoint in endpoints:
        if endpoint["auth_required"]:
            print(f"   🔑 {endpoint['endpoint']} - {endpoint['description']}")

def show_error_solutions():
    """Show solutions for common authentication errors"""
    print(f"\n🔧 Common Authentication Errors & Solutions")
    print("=" * 60)
    
    errors = [
        {
            "error": "missing_authorization_header",
            "solution": "Add 'Authorization: Bearer <token>' header to request"
        },
        {
            "error": "invalid_authorization_format",
            "solution": "Ensure header format is exactly 'Bearer <space><token>'"
        },
        {
            "error": "invalid_token",
            "solution": "Token expired or invalid - get new token via Google login"
        },
        {
            "error": "invalid_user_data",
            "solution": "Token missing user_id - re-authenticate with Google"
        }
    ]
    
    for error in errors:
        print(f"\n❌ Error: {error['error']}")
        print(f"   ✅ Solution: {error['solution']}")

def main():
    print("🚀 Testing Save Paragraph API with Authentication")
    print(f"🕒 Test Time: {datetime.now().isoformat()}")
    
    test_save_paragraph_with_auth()
    test_auth_flow()
    show_curl_examples()
    show_endpoint_requirements()
    show_error_solutions()
    
    print("\n" + "=" * 60)
    print("✅ Summary:")
    print("🔑 save-paragraph endpoint requires JWT authentication")
    print("📱 Get JWT token via Google OAuth login first")
    print("🔒 Include 'Authorization: Bearer <token>' in all requests")
    print("⚡ Test token validity with /auth/profile endpoint")
    print("=" * 60)

if __name__ == "__main__":
    main()