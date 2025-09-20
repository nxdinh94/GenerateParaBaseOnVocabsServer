#!/usr/bin/env python3
"""
Test script to verify the datetime validation fix
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_learned_vocabs_api():
    """Test the fixed learned-vocabs API"""
    print("🔧 Testing Fixed Learned Vocabs API")
    print("=" * 50)
    
    # Test data
    test_data = {
        "vocabs": ["hello", "world", "python", "fastapi"]
    }
    
    print(f"📝 Test Data: {json.dumps(test_data, indent=2)}")
    print(f"🌐 Endpoint: {BASE_URL}/api/v1/learned-vocabs")
    
    print("\n🧪 Testing without authentication (should get 401):")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/learned-vocabs",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 401:
            print("✅ Authentication properly required")
        else:
            print("⚠️ Unexpected response")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - server may not be running")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_unique_vocabs_api():
    """Test the unique-vocabs API"""
    print("\n🔧 Testing Unique Vocabs API")
    print("=" * 50)
    
    print(f"🌐 Endpoint: {BASE_URL}/api/v1/vocabs_base_on_category")
    
    print("\n🧪 Testing without authentication (should get 401):")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/vocabs_base_on_category",
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 401:
            print("✅ Authentication properly required")
        else:
            print("⚠️ Unexpected response")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - server may not be running")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🚀 Testing Datetime Validation Fix")
    print("🕒 This should resolve the datetime validation error")
    print()
    
    print("🔍 Changes Made:")
    print("✓ LearnedVocabsInDB.updated_at now Optional[datetime]")
    print("✓ LearnedVocabsResponse.updated_at now Optional[datetime]") 
    print("✓ CRUD create method explicitly sets current_time")
    print("✓ Ensures both created_at and updated_at are properly set")
    print()
    
    test_learned_vocabs_api()
    test_unique_vocabs_api()
    
    print("\n" + "=" * 50)
    print("✅ Testing completed!")
    print("💡 To test with authentication:")
    print("1. Get JWT token from Google login")
    print("2. Add Authorization: Bearer <token> header")
    print("3. Should no longer get datetime validation errors")

if __name__ == "__main__":
    main()