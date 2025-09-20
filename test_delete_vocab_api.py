#!/usr/bin/env python3
"""
Test script for DELETE /learned-vocabs API endpoint
Tests the delete vocabulary functionality with bearer token authentication
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api/v1"

def test_delete_vocab_api():
    """Test the delete vocabulary API"""
    
    # You need to replace this with a valid JWT token
    # You can get this by running the Google OAuth flow or creating a test user
    BEARER_TOKEN = "your_jwt_token_here"
    
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("🧪 Testing DELETE /learned-vocabs API")
    print("=" * 50)
    
    # First, let's create some test vocabulary entries
    print("\n1. Creating test vocabulary entries...")
    
    test_vocabs = [
        {"vocabs": ["apple", "banana", "cherry"]},
        {"vocabs": ["dog", "cat", "bird"]},
        {"vocabs": ["apple", "orange", "grape"]},  # Contains "apple" again
        {"vocabs": ["computer", "mouse", "keyboard"]}
    ]
    
    for i, vocab_data in enumerate(test_vocabs, 1):
        try:
            response = requests.post(
                f"{BASE_URL}/learned-vocabs",
                headers=headers,
                json=vocab_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Created vocab set {i}: {vocab_data['vocabs']}")
                print(f"      Response: {result.get('message', 'Unknown')}")
            else:
                print(f"   ❌ Failed to create vocab set {i}: {response.status_code}")
                print(f"      Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception creating vocab set {i}: {e}")
    
    # Now test deleting a vocabulary word
    print("\n2. Testing delete vocabulary API...")
    
    test_cases = [
        {"vocab": "apple", "description": "Delete word 'apple' (should delete 2 entries)"},
        {"vocab": "dog", "description": "Delete word 'dog' (should delete 1 entry)"},
        {"vocab": "nonexistent", "description": "Delete non-existent word (should delete 0 entries)"},
        {"vocab": "", "description": "Delete empty word (should return error)"},
    ]
    
    for test_case in test_cases:
        print(f"\n   🔍 {test_case['description']}")
        
        try:
            # Test the delete API
            response = requests.delete(
                f"{BASE_URL}/learned-vocabs",
                headers=headers,
                json={"vocab": test_case["vocab"]}
            )
            
            print(f"      Status Code: {response.status_code}")
            
            if response.status_code in [200, 400]:
                result = response.json()
                print(f"      Status: {result.get('status', 'Unknown')}")
                print(f"      Message: {result.get('message', 'No message')}")
                print(f"      Deleted Count: {result.get('deleted_count', 'N/A')}")
            else:
                print(f"      Error: {response.text}")
                
        except Exception as e:
            print(f"      ❌ Exception: {e}")
    
    print("\n3. Testing error cases...")
    
    # Test missing vocab field
    print("\n   🔍 Testing missing 'vocab' field")
    try:
        response = requests.delete(
            f"{BASE_URL}/learned-vocabs",
            headers=headers,
            json={}
        )
        
        print(f"      Status Code: {response.status_code}")
        if response.status_code == 400:
            result = response.json()
            print(f"      Error: {result.get('detail', {}).get('message', 'Unknown error')}")
        else:
            print(f"      Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"      ❌ Exception: {e}")
    
    # Test invalid vocab type
    print("\n   🔍 Testing invalid 'vocab' type (number instead of string)")
    try:
        response = requests.delete(
            f"{BASE_URL}/learned-vocabs",
            headers=headers,
            json={"vocab": 123}
        )
        
        print(f"      Status Code: {response.status_code}")
        if response.status_code == 400:
            result = response.json()
            print(f"      Error: {result.get('detail', {}).get('message', 'Unknown error')}")
        else:
            print(f"      Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"      ❌ Exception: {e}")
    
    # Test without authorization
    print("\n   🔍 Testing without authorization token")
    try:
        response = requests.delete(
            f"{BASE_URL}/learned-vocabs",
            headers={"Content-Type": "application/json"},  # No Authorization header
            json={"vocab": "test"}
        )
        
        print(f"      Status Code: {response.status_code}")
        if response.status_code == 401:
            print(f"      ✅ Correctly rejected unauthorized request")
        else:
            print(f"      ❌ Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"      ❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")
    print("\nTo run this test:")
    print("1. Make sure your server is running on http://localhost:8000")
    print("2. Replace 'your_jwt_token_here' with a valid JWT token")
    print("3. Run: python test_delete_vocab_api.py")

if __name__ == "__main__":
    print("⚠️  IMPORTANT: Make sure to update the BEARER_TOKEN variable with a valid JWT token!")
    print("You can get a token by:")
    print("1. Running the Google OAuth flow")
    print("2. Using one of the existing test scripts that creates a user session")
    print()
    
    # Uncomment the line below when you have a valid token
    # test_delete_vocab_api()
    
    print("Please update the BEARER_TOKEN and uncomment the test_delete_vocab_api() call to run the test.")