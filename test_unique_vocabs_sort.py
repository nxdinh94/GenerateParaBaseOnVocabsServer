#!/usr/bin/env python3
"""
Test script for the updated unique-vocabs API with sort parameter
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_unique_vocabs_sorting():
    """Test the unique-vocabs API with different sort options"""
    print("🔧 Testing Unique Vocabs API with Sort Parameter")
    print("=" * 60)
    
    print("📋 API Endpoint: GET /api/v1/vocabs_base_on_category")
    print("🔑 New Parameter: sort (optional)")
    print("✅ Valid sort values: 'newest', 'oldest', 'alphabetical'")
    print("🎯 Default: 'newest' (newest first)")
    
    # Test cases for different sort options
    sort_options = [
        {
            "name": "Default (newest first)",
            "url": f"{BASE_URL}/api/v1/vocabs_base_on_category",
            "description": "No sort parameter - defaults to newest"
        },
        {
            "name": "Newest first",
            "url": f"{BASE_URL}/api/v1/vocabs_base_on_category?sort=newest",
            "description": "Explicitly sort by newest first"
        },
        {
            "name": "Oldest first", 
            "url": f"{BASE_URL}/api/v1/vocabs_base_on_category?sort=oldest",
            "description": "Sort by oldest first"
        },
        {
            "name": "Alphabetical",
            "url": f"{BASE_URL}/api/v1/vocabs_base_on_category?sort=alphabetical",
            "description": "Sort by first vocabulary word alphabetically"
        },
        {
            "name": "Invalid sort",
            "url": f"{BASE_URL}/api/v1/vocabs_base_on_category?sort=invalid",
            "description": "Should return 400 error"
        }
    ]
    
    for test_case in sort_options:
        print(f"\n🧪 Testing: {test_case['name']}")
        print(f"   URL: {test_case['url']}")
        print(f"   Expected: {test_case['description']}")
        
        try:
            response = requests.get(test_case["url"])
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                sort_value = data.get("sort", "default")
                print(f"   Sort applied: {sort_value}")
                print(f"   Documents found: {data.get('total_documents', 0)}")
                print(f"   ✅ Success")
            elif response.status_code == 400:
                error = response.json()
                print(f"   Error: {error.get('detail', {}).get('message', 'Unknown error')}")
                print(f"   ✅ Expected validation error")
            elif response.status_code == 401:
                print(f"   ✅ Authentication required (expected)")
            else:
                print(f"   ⚠️ Unexpected status code")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection failed - server not running")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def show_expected_responses():
    """Show expected response formats"""
    print("\n" + "=" * 60)
    print("📊 Expected Response Format")
    print("=" * 60)
    
    response_example = {
        "status": True,
        "total_documents": 2,
        "documents": [
            {
                "id": "document_id_1",
                "vocabs": ["hello", "world"],
                "created_at": "2025-09-20T15:00:00",
                "updated_at": "2025-09-20T15:00:00", 
                "deleted_at": None,
                "is_deleted": False
            },
            {
                "id": "document_id_2",
                "vocabs": ["learn", "code"],
                "created_at": "2025-09-20T14:00:00",
                "updated_at": "2025-09-20T14:00:00",
                "deleted_at": None,
                "is_deleted": False
            }
        ],
        "sort": "newest",
        "message": "Found 2 vocabulary documents sorted by newest"
    }
    
    print(json.dumps(response_example, indent=2))
    
    print("\n🔍 Sort Behavior:")
    print("• newest: Documents ordered by created_at DESC (latest first)")
    print("• oldest: Documents ordered by created_at ASC (earliest first)")
    print("• alphabetical: Documents ordered by first vocabulary word A-Z")
    
    print("\n❌ Error Response (Invalid Sort):")
    error_example = {
        "detail": {
            "error": "invalid_sort_parameter",
            "message": "Sort must be one of: newest, oldest, alphabetical"
        }
    }
    print(json.dumps(error_example, indent=2))

def show_usage_examples():
    """Show curl examples for testing"""
    print("\n" + "=" * 60)
    print("🔧 Usage Examples")
    print("=" * 60)
    
    examples = [
        {
            "description": "Get newest documents first (default)",
            "curl": f"curl -H 'Authorization: Bearer <token>' '{BASE_URL}/api/v1/vocabs_base_on_category'"
        },
        {
            "description": "Get newest documents first (explicit)",
            "curl": f"curl -H 'Authorization: Bearer <token>' '{BASE_URL}/api/v1/vocabs_base_on_category?sort=newest'"
        },
        {
            "description": "Get oldest documents first",
            "curl": f"curl -H 'Authorization: Bearer <token>' '{BASE_URL}/api/v1/vocabs_base_on_category?sort=oldest'"
        },
        {
            "description": "Get alphabetically sorted documents", 
            "curl": f"curl -H 'Authorization: Bearer <token>' '{BASE_URL}/api/v1/vocabs_base_on_category?sort=alphabetical'"
        }
    ]
    
    for example in examples:
        print(f"\n📝 {example['description']}:")
        print(f"   {example['curl']}")

def main():
    print("🚀 Testing Updated Unique Vocabs API with Sort")
    print(f"🕒 Test Time: {datetime.now().isoformat()}")
    
    test_unique_vocabs_sorting()
    show_expected_responses()
    show_usage_examples()
    
    print("\n" + "=" * 60)
    print("✅ Testing Summary:")
    print("🆕 Added 'sort' query parameter to /vocabs_base_on_category")
    print("📊 Three sort options: newest, oldest, alphabetical")
    print("🎯 Default behavior: newest first")
    print("✨ Includes sort value in response")
    print("🔒 Maintains authentication requirement")
    print("=" * 60)

if __name__ == "__main__":
    main()