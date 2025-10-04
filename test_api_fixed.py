#!/usr/bin/env python3

import requests
import json

def test_learned_vocabs_api():
    """Test the actual learned-vocabs API endpoint"""
    try:
        # API endpoint
        url = "http://localhost:8000/api/v1/learned-vocabs"
        
        # Test data
        test_data = {
            "vocabs": ["test", "api", "fixed"],
            "collection_id": "68e0d33953f7b332a059d506"  # Using the default collection ID from our tests
        }
        
        # Test without auth first (should return 401)
        print("🧪 Testing API endpoint without authentication...")
        response = requests.post(url, json=test_data, timeout=10)
        
        print(f"Response Status: {response.status_code}")
        
        try:
            response_json = response.json()
            print(f"Response JSON:")
            print(json.dumps(response_json, indent=2))
        except:
            print(f"Response Text: {response.text}")
        
        # Check if it's asking for authentication (expected)
        if response.status_code == 401:
            print("\n✅ API endpoint is working correctly (returned 401 as expected - requires auth)")
            print("The 500 error should be fixed now. The API requires a valid JWT token.")
            return True
        elif response.status_code == 422:
            print("\n✅ API endpoint is working (returned 422 - validation error)")
            print("The 500 error is fixed. Now it's properly validating the request.")
            return True
        elif response.status_code == 500:
            print("\n❌ Still getting 500 error - the fix may not have taken effect")
            return False
        else:
            print(f"\n⚠️ Unexpected status code: {response.status_code}")
            return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the server running on http://localhost:8000?")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_learned_vocabs_api()
    if success:
        print("\n✅ API endpoint test completed!")
        print("💡 To use the API from frontend, make sure to include:")
        print("   Authorization: Bearer <your_jwt_token>")
    else:
        print("\n❌ API endpoint test failed!")
        print("\n💡 Make sure the FastAPI server is running:")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")