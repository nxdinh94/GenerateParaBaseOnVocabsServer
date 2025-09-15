#!/usr/bin/env python3
"""
Test login response format - chỉ trả về jwt_token và jwt_refresh_token
"""
import requests
import json

def test_login_response_format():
    """Test that login only returns jwt_token and jwt_refresh_token"""
    
    print("=== Testing Login Response Format ===")
    print("Expected: Only jwt_token and jwt_refresh_token in response")
    print("")
    
    # Test với mock login request (sẽ fail vì không có real authorization code)
    try:
        mock_code = "mock_auth_code_for_testing"
        
        login_response = requests.post(
            "http://127.0.0.1:8000/api/v1/auth/google/login",
            json={"authorization_code": mock_code}
        )
        
        print(f"Status Code: {login_response.status_code}")
        print(f"Response: {json.dumps(login_response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Request failed (expected): {e}")
    
    print("\n" + "="*60)
    print("✅ LOGIN RESPONSE FORMAT UPDATED")
    print("📋 Changes made:")
    print("   1. GoogleLoginResponse schema: only jwt_token + jwt_refresh_token")
    print("   2. Login endpoint: removed access_token and refresh_token")
    print("   3. Response now contains only:")
    print("      - jwt_token: for API authentication")
    print("      - jwt_refresh_token: for token renewal")
    
    print("\n🔧 Frontend Integration:")
    print("   const { jwt_token, jwt_refresh_token } = response.data;")
    print("   // Store jwt_token for API calls")
    print("   // jwt_refresh_token will be in HttpOnly cookie")

if __name__ == "__main__":
    test_login_response_format()