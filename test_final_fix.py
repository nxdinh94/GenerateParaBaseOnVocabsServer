#!/usr/bin/env python3
"""
Quick test to verify the user_id KeyError fix
"""
import requests
import json
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

BASE_URL = "http://127.0.0.1:8000"

def test_fixed_save_paragraph():
    """Test save-paragraph with the KeyError fix"""
    print("🔧 Testing Fixed save-paragraph Endpoint")
    print("=" * 50)
    
    try:
        from app.services.google_auth import google_auth_service
        
        # Create valid JWT token
        test_user_data = {
            "id": "507f1f77bcf86cd799439011",
            "user_id": "507f1f77bcf86cd799439011",
            "email": "test@example.com",
            "name": "Test User"
        }
        
        jwt_token = google_auth_service.create_jwt_token(test_user_data)
        print(f"✅ JWT token created")
        
        # Test data
        test_data = {
            "vocabs": ["fix", "test", "success"],
            "paragraph": "This paragraph tests the user_id KeyError fix."
        }
        
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        
        # Make the request
        response = requests.post(
            f"{BASE_URL}/api/v1/save-paragraph",
            json=test_data,
            headers=headers,
            timeout=10
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"🎉 SUCCESS! The user_id KeyError has been fixed!")
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    import time
    
    print("⏱️ Waiting for server to start...")
    time.sleep(3)
    
    success = test_fixed_save_paragraph()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ FIXED! save-paragraph endpoint is now working properly")
        print("🔧 The user_id KeyError has been resolved")
    else:
        print("❌ Issue still exists - need further investigation")
    print("=" * 50)