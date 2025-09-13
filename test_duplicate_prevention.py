"""
Test script to verify input history duplicate prevention
"""
import requests
import json

# Server configuration
BASE_URL = "http://localhost:8000"

def test_duplicate_prevention():
    print("Testing input history duplicate prevention...")
    
    # Test data
    test_words = ["apple", "banana", "cherry"]
    
    # You'll need to replace this with a valid JWT token for testing
    # You can get this by logging in through your authentication endpoint
    auth_token = "Bearer YOUR_JWT_TOKEN_HERE"
    
    headers = {
        "Authorization": auth_token,
        "Content-Type": "application/json"
    }
    
    data = {
        "words": test_words
    }
    
    print(f"Sending first request with words: {test_words}")
    
    # First request - should create new record (201)
    response1 = requests.post(f"{BASE_URL}/api/v1/db/input-history/", 
                             headers=headers, 
                             json=data)
    
    print(f"First response status: {response1.status_code}")
    print(f"First response: {response1.json()}")
    
    print("\nSending second request with same words...")
    
    # Second request - should return existing record (200)
    response2 = requests.post(f"{BASE_URL}/api/v1/db/input-history/", 
                             headers=headers, 
                             json=data)
    
    print(f"Second response status: {response2.status_code}")
    print(f"Second response: {response2.json()}")
    
    # Check if the IDs are the same (indicating same record was returned)
    if response1.status_code in [200, 201] and response2.status_code in [200, 201]:
        id1 = response1.json().get("id")
        id2 = response2.json().get("id")
        
        if id1 == id2:
            print(f"\n✅ SUCCESS: Both requests returned the same record ID: {id1}")
            print("Duplicate prevention is working correctly!")
        else:
            print(f"\n❌ FAILURE: Different IDs returned - {id1} vs {id2}")
            print("Duplicate prevention is NOT working!")
    else:
        print(f"\n❌ Error in requests: {response1.status_code}, {response2.status_code}")

if __name__ == "__main__":
    test_duplicate_prevention()