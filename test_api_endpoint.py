#!/usr/bin/env python3

import requests
import json

def test_api_endpoint():
    """Test the actual API endpoint"""
    try:
        # API endpoint
        url = "http://localhost:8000/api/v1/vocabs_base_on_category"
        
        # Test parameters
        params = {
            "collection_id": "68e0d33953f7b332a059d506",
            "sort": "frequent"
        }
        
        # Test with a simple GET request (no auth for now - should return 401)
        print("🧪 Testing API endpoint...")
        print(f"URL: {url}")
        print(f"Params: {params}")
        
        response = requests.get(url, params=params, timeout=10)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"\nResponse JSON:")
            print(json.dumps(response_json, indent=2))
        except:
            print(f"\nResponse Text: {response.text}")
        
        # Check if it's asking for authentication (expected)
        if response.status_code == 401:
            print("\n✅ API endpoint is working (returned 401 as expected - requires auth)")
            return True
        elif response.status_code == 422:
            print("\n✅ API endpoint is working (returned 422 - validation error)")
            return True
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
    success = test_api_endpoint()
    if success:
        print("\n✅ API endpoint test completed!")
    else:
        print("\n❌ API endpoint test failed!")
        print("\n💡 Make sure the FastAPI server is running:")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")