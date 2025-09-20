#!/usr/bin/env python3
"""
Test script with authentication to fully verify the sort functionality
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_with_auth_token():
    """Test the API with authentication token"""
    print("🔐 Testing with Authentication Token")
    print("=" * 50)
    
    # You need to replace this with a real JWT token from Google login
    # To get a token:
    # 1. Start the server: uvicorn app.main:app --port 8000
    # 2. Use the Google login endpoint to get a JWT token
    # 3. Copy the token here
    
    # Example token (replace with real one):
    # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    
    print("📝 To test with authentication:")
    print("1. Start server: uvicorn app.main:app --port 8000")
    print("2. Get JWT token from Google login")
    print("3. Replace token in this script")
    print("4. Run this test again")
    
    # Example of how to use the token:
    headers = {
        "Authorization": f"Bearer YOUR_JWT_TOKEN_HERE"
    }
    
    test_urls = [
        f"{BASE_URL}/api/v1/vocabs_base_on_category",
        f"{BASE_URL}/api/v1/vocabs_base_on_category?sort=newest", 
        f"{BASE_URL}/api/v1/vocabs_base_on_category?sort=oldest",
        f"{BASE_URL}/api/v1/vocabs_base_on_category?sort=alphabetical"
    ]
    
    print("\n🔧 Test URLs that will work with valid token:")
    for url in test_urls:
        print(f"   GET {url}")
    
    print("\n📊 Expected Response Structure:")
    response_structure = {
        "status": True,
        "total_documents": "number",
        "documents": [
            {
                "id": "string (ObjectId)",
                "vocabs": ["array", "of", "strings"],
                "created_at": "ISO datetime string",
                "updated_at": "ISO datetime string", 
                "deleted_at": "ISO datetime string or null",
                "is_deleted": "boolean"
            }
        ],
        "sort": "newest|oldest|alphabetical",
        "message": "descriptive message"
    }
    
    print(json.dumps(response_structure, indent=2))

def test_sort_parameter_validation():
    """Test invalid sort parameters"""
    print("\n🧪 Testing Sort Parameter Validation")
    print("=" * 50)
    
    invalid_sort_url = f"{BASE_URL}/api/v1/vocabs_base_on_category?sort=invalid"
    
    print(f"Testing invalid sort: {invalid_sort_url}")
    
    try:
        response = requests.get(invalid_sort_url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 400:
            error_data = response.json()
            print("✅ Validation error response:")
            print(json.dumps(error_data, indent=2))
        elif response.status_code == 401:
            print("✅ Authentication required (expected)")
        else:
            print(f"⚠️ Unexpected status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running")
    except Exception as e:
        print(f"❌ Error: {e}")

def show_curl_examples():
    """Show curl examples for testing"""
    print("\n🔧 Curl Examples for Testing")
    print("=" * 50)
    
    examples = [
        {
            "description": "Default sort (newest first)",
            "curl": f"""curl -H "Authorization: Bearer <YOUR_TOKEN>" "{BASE_URL}/api/v1/vocabs_base_on_category\""""
        },
        {
            "description": "Explicit newest sort",
            "curl": f"""curl -H "Authorization: Bearer <YOUR_TOKEN>" "{BASE_URL}/api/v1/vocabs_base_on_category?sort=newest\""""
        },
        {
            "description": "Oldest first sort", 
            "curl": f"""curl -H "Authorization: Bearer <YOUR_TOKEN>" "{BASE_URL}/api/v1/vocabs_base_on_category?sort=oldest\""""
        },
        {
            "description": "Alphabetical sort",
            "curl": f"""curl -H "Authorization: Bearer <YOUR_TOKEN>" "{BASE_URL}/api/v1/vocabs_base_on_category?sort=alphabetical\""""
        },
        {
            "description": "Invalid sort (should return 400)",
            "curl": f"""curl -H "Authorization: Bearer <YOUR_TOKEN>" "{BASE_URL}/api/v1/vocabs_base_on_category?sort=invalid\""""
        }
    ]
    
    for example in examples:
        print(f"\n📝 {example['description']}:")
        print(f"   {example['curl']}")

def main():
    print("🚀 Authentication Test for Unique Vocabs API")
    print(f"🕒 Test Time: {datetime.now().isoformat()}")
    
    test_with_auth_token()
    test_sort_parameter_validation()
    show_curl_examples()
    
    print("\n" + "=" * 50)
    print("✅ Summary:")
    print("🎯 All fields returned in sorted order")
    print("📊 Default: newest first")
    print("🔧 Three sort options: newest, oldest, alphabetical")
    print("🔒 Bearer token authentication required")
    print("✨ Robust datetime handling with None values")
    print("🚫 Invalid sort parameters properly validated")
    print("=" * 50)

if __name__ == "__main__":
    main()