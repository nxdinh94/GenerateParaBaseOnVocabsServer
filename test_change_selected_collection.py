"""
Test script for the change-selected-collection API endpoint
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
# Replace with your actual JWT token
JWT_TOKEN = "your_jwt_token_here"

def test_change_selected_collection():
    """Test changing selected collection"""
    print("\n" + "="*60)
    print("TEST: Change Selected Collection")
    print("="*60)
    
    # First, get all collections to find a valid collection_id
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}"
    }
    
    print("\n1. Getting user's vocabulary collections...")
    collections_response = requests.get(
        f"{BASE_URL}/vocab-collections",
        headers=headers
    )
    
    if collections_response.status_code == 200:
        collections_data = collections_response.json()
        print(f"✅ Found {collections_data['total']} collections")
        
        if collections_data['total'] > 0:
            # Get first collection ID
            first_collection = collections_data['collections'][0]
            collection_id = first_collection['id']
            collection_name = first_collection['name']
            
            print(f"\n2. Changing selected collection to: {collection_name} (ID: {collection_id})")
            
            # Test change selected collection
            change_response = requests.post(
                f"{BASE_URL}/change-selected-collection",
                headers=headers,
                json={
                    "selected_collection_id": collection_id
                }
            )
            
            print(f"Status Code: {change_response.status_code}")
            response_data = change_response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            
            if change_response.status_code == 200:
                print("✅ Successfully changed selected collection")
            else:
                print("❌ Failed to change selected collection")
        else:
            print("⚠️ No collections found. Create a collection first.")
    else:
        print(f"❌ Failed to get collections: {collections_response.status_code}")
        print(f"Response: {collections_response.text}")

def test_invalid_collection_id():
    """Test with invalid collection ID"""
    print("\n" + "="*60)
    print("TEST: Invalid Collection ID")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}"
    }
    
    # Test with invalid collection ID
    response = requests.post(
        f"{BASE_URL}/change-selected-collection",
        headers=headers,
        json={
            "selected_collection_id": "000000000000000000000000"  # Non-existent ID
        }
    )
    
    print(f"Status Code: {response.status_code}")
    response_data = response.json()
    print(f"Response: {json.dumps(response_data, indent=2)}")
    
    if response.status_code == 404:
        print("✅ Correctly returned 404 for non-existent collection")
    else:
        print("❌ Expected 404 error")

def test_missing_token():
    """Test without authentication token"""
    print("\n" + "="*60)
    print("TEST: Missing Authentication Token")
    print("="*60)
    
    response = requests.post(
        f"{BASE_URL}/change-selected-collection",
        json={
            "selected_collection_id": "some_collection_id"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    response_data = response.json()
    print(f"Response: {json.dumps(response_data, indent=2)}")
    
    if response.status_code == 401:
        print("✅ Correctly returned 401 for missing token")
    else:
        print("❌ Expected 401 error")

def test_empty_collection_id():
    """Test with empty collection ID"""
    print("\n" + "="*60)
    print("TEST: Empty Collection ID")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}"
    }
    
    response = requests.post(
        f"{BASE_URL}/change-selected-collection",
        headers=headers,
        json={
            "selected_collection_id": ""
        }
    )
    
    print(f"Status Code: {response.status_code}")
    response_data = response.json()
    print(f"Response: {json.dumps(response_data, indent=2)}")
    
    if response.status_code == 400:
        print("✅ Correctly returned 400 for empty collection ID")
    else:
        print("❌ Expected 400 error")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("CHANGE SELECTED COLLECTION API TEST SUITE")
    print("="*60)
    print("\n⚠️  Make sure to:")
    print("1. Update JWT_TOKEN with your actual token")
    print("2. Server is running on http://localhost:8000")
    print("3. You have at least one vocabulary collection")
    
    # Run tests
    test_change_selected_collection()
    test_invalid_collection_id()
    test_missing_token()
    test_empty_collection_id()
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETED")
    print("="*60)
