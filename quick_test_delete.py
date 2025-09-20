#!/usr/bin/env python3
"""
Quick test for the DELETE endpoint
"""
import requests
import json
import time

def test_delete_endpoint():
    """Test the delete endpoint"""
    base_url = "http://localhost:8000/api/v1"
    
    # Test 1: Test without authentication (should get 401)
    print("1. Testing DELETE without authentication...")
    try:
        response = requests.delete(
            f"{base_url}/learned-vocabs",
            json={"vocab": "test"},
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Test with fake token (should get 401 or 403)
    print("\n2. Testing DELETE with fake token...")
    try:
        response = requests.delete(
            f"{base_url}/learned-vocabs",
            json={"vocab": "test"},
            headers={"Authorization": "Bearer fake_token"},
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Test if endpoint exists by checking error message
    print("\n3. Testing if the DELETE endpoint is recognized...")
    try:
        response = requests.delete(
            f"{base_url}/learned-vocabs",
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 405:
            print("   ERROR: Method Not Allowed - The DELETE method is not registered!")
        elif response.status_code in [401, 422]:
            print("   SUCCESS: DELETE method is recognized (just missing auth/data)")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    # Wait a moment for server to start
    print("Waiting for server to start...")
    time.sleep(3)
    test_delete_endpoint()