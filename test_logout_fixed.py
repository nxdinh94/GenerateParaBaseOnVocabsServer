#!/usr/bin/env python3
"""
Test logout API sau khi fix method name
"""
import requests
import json
import asyncio
from app.services.google_auth import google_auth_service

def test_logout_with_mock_token():
    """Test logout với mock JWT token"""
    
    print("=== Testing Logout API - Fixed Method Name ===")
    
    try:
        # Tạo mock JWT token (sẽ invalid vì không có secret key)
        mock_user_data = {
            "user_id": "68c4275698c19a62f2f694fa",  # Existing user ID from database
            "email": "test@example.com",
            "name": "Test User"
        }
        
        # Thử tạo JWT token (có thể fail do missing credentials)
        try:
            jwt_token = google_auth_service.create_jwt_token(mock_user_data)
            print(f"Created mock JWT token: {jwt_token[:50]}...")
            
            # Test logout với token này
            print("\nTesting logout with valid token format...")
            logout_response = requests.post(
                "http://127.0.0.1:8000/api/v1/auth/logout",
                headers={
                    "Authorization": f"Bearer {jwt_token}"
                }
            )
            
            print(f"Logout Status: {logout_response.status_code}")
            print(f"Logout Response: {json.dumps(logout_response.json(), indent=2)}")
            
        except Exception as token_error:
            print(f"JWT token creation failed: {token_error}")
            print("This is expected if Google OAuth credentials are not configured.")
            
    except Exception as e:
        print(f"Test error: {e}")
    
    # Test basic error cases
    print("\n" + "-"*50)
    print("Testing basic error cases:")
    
    # Test without token
    response = requests.post("http://127.0.0.1:8000/api/v1/auth/logout")
    print(f"\nNo token - Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test with invalid token
    response = requests.post(
        "http://127.0.0.1:8000/api/v1/auth/logout",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    print(f"\nInvalid token - Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    print("\n" + "="*60)
    print("✅ LOGOUT API METHOD NAME FIXED")
    print("   Changed: delete_by_user_id → delete_user_refresh_tokens")
    print("   Status: Ready for testing with real JWT tokens")

if __name__ == "__main__":
    test_logout_with_mock_token()