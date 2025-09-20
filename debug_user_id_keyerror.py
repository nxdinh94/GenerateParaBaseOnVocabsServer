#!/usr/bin/env python3
"""
Debug the specific user_id KeyError in save-paragraph
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_with_mock_jwt():
    """Test save-paragraph with a mock JWT token to debug the exact error location"""
    print("🔍 Testing save-paragraph with Mock JWT to Debug user_id KeyError")
    print("=" * 70)
    
    # Create a JWT token with the same structure as the Google login creates
    test_user_data = {
        "id": "507f1f77bcf86cd799439011",
        "user_id": "507f1f77bcf86cd799439011", 
        "google_id": "test_google_id",
        "email": "test@example.com",
        "name": "Test User",
        "picture": "https://example.com/pic.jpg",
        "verified_email": True
    }
    
    print(f"📋 Test user data structure:")
    print(json.dumps(test_user_data, indent=2))
    
    # We need to create a real JWT token using the app's JWT service
    print(f"\n🔧 Creating valid JWT token using app's google_auth_service...")
    
    try:
        # Import the JWT service directly
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
        
        from app.services.google_auth import google_auth_service
        
        # Create a valid JWT token with our test data
        jwt_token = google_auth_service.create_jwt_token(test_user_data)
        print(f"   ✅ JWT token created: {jwt_token[:50]}...")
        
        # Verify the token works
        decoded_data = google_auth_service.verify_jwt_token(jwt_token)
        print(f"   ✅ JWT token verified successfully")
        print(f"   📋 Decoded data: {decoded_data}")
        
        # Test the save-paragraph endpoint with this valid token
        print(f"\n📤 Testing save-paragraph with valid JWT token:")
        
        test_data = {
            "vocabs": ["debug", "user", "error"],
            "paragraph": "This is a test paragraph to debug the user_id KeyError."
        }
        
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        
        print(f"   Request data: {json.dumps(test_data, indent=2)}")
        print(f"   Headers: Authorization: Bearer {jwt_token[:30]}...")
        
        response = requests.post(
            f"{BASE_URL}/api/v1/save-paragraph",
            json=test_data,
            headers=headers,
            timeout=10
        )
        
        print(f"\n📊 Response:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ SUCCESS! The fix worked!")
            response_data = response.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        elif response.status_code == 500:
            print(f"   ❌ 500 Error still occurring")
            try:
                error_data = response.json()
                print(f"   Error Details: {json.dumps(error_data, indent=2)}")
                
                # Check if it's the same user_id error
                if "user_id" in str(error_data.get("detail", {})):
                    print(f"   🔍 Same user_id KeyError detected!")
                    print(f"   💡 The error might be deeper in the CRUD operations")
                
            except:
                print(f"   Raw Response: {response.text}")
        else:
            try:
                error_data = response.json()
                print(f"   Response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Raw Response: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ JWT token creation failed: {e}")
        return False

def test_auth_flow_debug():
    """Test if the get_current_user function itself is working"""
    print(f"\n🔍 Testing get_current_user Function")
    print("=" * 70)
    
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
        
        from app.services.google_auth import google_auth_service
        
        # Create test token
        test_user_data = {
            "id": "507f1f77bcf86cd799439011",
            "user_id": "507f1f77bcf86cd799439011",
            "email": "test@example.com",
            "name": "Test User"
        }
        
        jwt_token = google_auth_service.create_jwt_token(test_user_data)
        
        # Test the /auth/profile endpoint which uses the same get_current_user function
        headers = {
            "Authorization": f"Bearer {jwt_token}"
        }
        
        response = requests.get(
            f"{BASE_URL}/api/v1/auth/profile",
            headers=headers,
            timeout=10
        )
        
        print(f"📤 Testing /auth/profile endpoint:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ get_current_user function works correctly")
            response_data = response.json()
            user_data = response_data.get("user_data", {})
            print(f"   User data from token: {json.dumps(user_data, indent=2)}")
            
            # Check if user_id is accessible
            user_id = user_data.get("user_id") or user_data.get("id")
            print(f"   🔑 Extracted user_id: {user_id}")
            
            return True
        else:
            print(f"   ❌ get_current_user function failed")
            try:
                error_data = response.json()
                print(f"   Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Raw Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Auth flow test failed: {e}")
        return False

def show_debugging_strategy():
    """Show step-by-step debugging strategy"""
    print(f"\n🔧 Debugging Strategy for user_id KeyError")
    print("=" * 70)
    
    steps = [
        "1. ✅ Test JWT token creation and verification",
        "2. ✅ Test get_current_user function via /auth/profile",
        "3. 🔍 Test save-paragraph with valid JWT token",
        "4. 🐛 If still failing, check CRUD operations",
        "5. 🔍 Check InputHistoryCreate model validation",
        "6. 🔍 Check database operations in find_by_exact_words",
        "7. 🔍 Check SavedParagraphCreate model validation"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print(f"\n💡 Possible locations of user_id KeyError:")
    print(f"   - InputHistoryCreate model validation")
    print(f"   - CRUD operations in find_by_exact_words")
    print(f"   - Database document mapping")
    print(f"   - Model field validation in create_input_history")

def main():
    print("🚀 Debugging user_id KeyError in save-paragraph")
    print(f"🕒 Debug Time: {datetime.now().isoformat()}")
    
    # Test auth flow first
    auth_ok = test_auth_flow_debug()
    
    if auth_ok:
        print(f"\n✅ Authentication flow works, testing save-paragraph...")
        save_ok = test_with_mock_jwt()
        
        if not save_ok:
            print(f"\n❌ save-paragraph still failing, need deeper investigation")
            show_debugging_strategy()
    else:
        print(f"\n❌ Authentication flow broken, fix this first")
    
    print("\n" + "=" * 70)
    print("📊 Debug Summary:")
    print(f"   Authentication: {'✅ PASS' if auth_ok else '❌ FAIL'}")
    if auth_ok:
        save_ok = test_with_mock_jwt()
        print(f"   Save Paragraph: {'✅ PASS' if save_ok else '❌ FAIL'}")
    print("=" * 70)

if __name__ == "__main__":
    main()