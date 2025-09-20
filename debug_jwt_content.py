#!/usr/bin/env python3
"""
Debug script to test JWT token content and save-paragraph endpoint
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def debug_jwt_content():
    """Debug what's actually in the JWT token"""
    print("🔍 Debug JWT Token Content")
    print("=" * 60)
    
    # Example JWT payload that should be created during Google login
    expected_jwt_data = {
        "id": "507f1f77bcf86cd799439011",  # MongoDB ObjectId as string
        "user_id": "507f1f77bcf86cd799439011",  # Same as id for backward compatibility
        "google_id": "1234567890",
        "email": "test@example.com", 
        "name": "Test User",
        "picture": "https://example.com/picture.jpg",
        "verified_email": True
    }
    
    print("📋 Expected JWT token payload structure:")
    print(json.dumps(expected_jwt_data, indent=2))
    
    # Test a simple endpoint that shows what the JWT actually contains
    print(f"\n🧪 Testing JWT content with /auth/profile endpoint")
    print("   This endpoint returns the decoded JWT data")
    
    # Instructions for manual testing
    print(f"\n📝 Manual Testing Steps:")
    print(f"1. Get Google OAuth authorization code from frontend")
    print(f"2. Exchange for JWT token:")
    print(f"   curl -X POST '{BASE_URL}/api/v1/auth/google/login' \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{\"authorization_code\": \"your_google_auth_code\"}}'")
    
    print(f"\n3. Use JWT token to check content:")
    print(f"   curl -H 'Authorization: Bearer <jwt_token>' \\")
    print(f"     '{BASE_URL}/api/v1/auth/profile'")
    
    print(f"\n4. Then test save-paragraph:")
    print(f"   curl -X POST '{BASE_URL}/api/v1/save-paragraph' \\")
    print(f"     -H 'Authorization: Bearer <jwt_token>' \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{\"vocabs\": [\"test\"], \"paragraph\": \"Test paragraph.\"}}'")

def debug_user_id_access():
    """Debug different ways to access user_id from current_user"""
    print(f"\n🔧 Debug user_id Access Patterns")
    print("=" * 60)
    
    # Show different access patterns
    user_data_examples = [
        {
            "name": "Google Login JWT (current)",
            "data": {
                "id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439011", 
                "google_id": "1234567890",
                "email": "test@example.com"
            }
        },
        {
            "name": "Possible broken JWT",
            "data": {
                "id": "507f1f77bcf86cd799439011",
                "google_id": "1234567890", 
                "email": "test@example.com"
                # Missing user_id!
            }
        }
    ]
    
    for example in user_data_examples:
        print(f"\n📊 {example['name']}:")
        data = example['data']
        print(f"   Raw data: {data}")
        
        # Test different access patterns
        user_id_methods = [
            ("current_user.get('user_id')", data.get('user_id')),
            ("current_user.get('id')", data.get('id')),
            ("current_user['user_id'] (KeyError if missing)", "KeyError" if 'user_id' not in data else data['user_id']),
            ("current_user.get('user_id') or current_user.get('id')", data.get('user_id') or data.get('id'))
        ]
        
        for method, result in user_id_methods:
            print(f"   {method}: {result}")

def show_fixed_save_paragraph():
    """Show the fixed save_paragraph function"""
    print(f"\n🔧 Recommended Fix for save_paragraph")
    print("=" * 60)
    
    fixed_code = '''
# Current problematic code:
user_id = current_user.get("user_id")

# Fixed code (handles both id and user_id):
user_id = current_user.get("user_id") or current_user.get("id")

# Or more robust version:
def get_user_id_from_current_user(current_user: dict) -> str:
    """
    Extract user_id from current_user data, handling different JWT formats
    """
    user_id = current_user.get("user_id") or current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail={
            "error": "invalid_user_data",
            "message": "User ID not found in token (missing both 'user_id' and 'id')"
        })
    return user_id
'''
    
    print(fixed_code)

def main():
    print("🚀 Debug JWT Content and save-paragraph Error")
    print(f"🕒 Debug Time: {datetime.now().isoformat()}")
    
    debug_jwt_content()
    debug_user_id_access()
    show_fixed_save_paragraph()
    
    print("\n" + "=" * 60)
    print("✅ Summary:")
    print("🔍 The error 'user_id' suggests current_user.get('user_id') returns None")
    print("🔧 JWT should contain both 'id' and 'user_id' with same value")
    print("💡 Fix: Use fallback - current_user.get('user_id') or current_user.get('id')")
    print("🧪 Test JWT content with /auth/profile to confirm structure")
    print("=" * 60)

if __name__ == "__main__":
    main()