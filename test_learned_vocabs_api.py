#!/usr/bin/env python3
"""
Test script to verify the learned_vocabs API changes
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_input_history_with_learned_vocabs():
    """Test the input-history endpoint now using learned_vocabs collection"""
    print("=" * 60)
    print("Testing POST /api/v1/db/input-history/ (now using learned_vocabs)")
    print("=" * 60)
    
    # First, let's try without authentication to see the error
    print("\n1. Testing without authentication (should fail):")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/db/input-history/",
            json={"words": ["hello", "world", "python"]},
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Note: For full testing with authentication, you would need a valid JWT token
    print("\n2. To test with authentication, you need:")
    print("   - A valid JWT token from Google login")
    print("   - Authorization header: 'Bearer <your_jwt_token>'")
    print("   - Expected behavior: Creates entry in learned_vocabs collection")

def test_unique_vocabs_endpoint():
    """Test the unique-vocabs endpoint now using learned_vocabs collection"""
    print("\n" + "=" * 60)
    print("Testing GET /api/v1/unique-vocabs (now using learned_vocabs)")
    print("=" * 60)
    
    print("\n1. Testing without authentication (should fail):")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/unique-vocabs",
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n2. To test with authentication, you need:")
    print("   - A valid JWT token from Google login")
    print("   - Authorization header: 'Bearer <your_jwt_token>'")
    print("   - Expected behavior: Returns vocabs from learned_vocabs collection")

def test_api_endpoints():
    """Test API endpoints availability"""
    print("\n" + "=" * 60)
    print("Testing API endpoint availability")
    print("=" * 60)
    
    endpoints = [
        "/api/v1/test-data",
        "/api/v1/db/input-history/",
        "/api/v1/unique-vocabs"
    ]
    
    for endpoint in endpoints:
        try:
            if endpoint == "/api/v1/db/input-history/":
                # POST request
                response = requests.post(f"{BASE_URL}{endpoint}", json={"words": ["test"]})
            else:
                # GET request
                response = requests.get(f"{BASE_URL}{endpoint}")
            
            print(f"✓ {endpoint:<30} Status: {response.status_code}")
            
            if endpoint == "/api/v1/test-data" and response.status_code == 200:
                print(f"  Sample data: {response.json()}")
                
        except requests.exceptions.ConnectionError:
            print(f"✗ {endpoint:<30} Server not running")
        except Exception as e:
            print(f"✗ {endpoint:<30} Error: {e}")

def main():
    print("🚀 Testing Learned Vocabs API Changes")
    print("📝 Summary of Changes:")
    print("   - Created new 'learned_vocabs' collection")
    print("   - POST /input-history/ now saves to learned_vocabs")
    print("   - GET /unique-vocabs now reads from learned_vocabs")
    print("   - Maintains backward compatibility for response format")
    
    test_api_endpoints()
    test_input_history_with_learned_vocabs()
    test_unique_vocabs_endpoint()
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("💡 To test with authentication:")
    print("   1. Start the server: uvicorn app.main:app --host 0.0.0.0 --port 8001")
    print("   2. Get a JWT token from Google login")
    print("   3. Use the token in Authorization header")
    print("=" * 60)

if __name__ == "__main__":
    main()