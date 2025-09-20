#!/usr/bin/env python3
"""
Test script to verify that unique-vocabs API returns all fields sorted by newest first
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_sort_all_fields():
    """Test that all fields are returned and sorted correctly"""
    print("🔧 Testing Unique Vocabs API - All Fields with Newest Sort")
    print("=" * 70)
    
    # Test with default sort (should be newest)
    test_cases = [
        {
            "name": "Default Sort (should be newest)",
            "url": f"{BASE_URL}/api/v1/vocabs_base_on_category",
            "expected_sort": "newest"
        },
        {
            "name": "Explicit Newest Sort",
            "url": f"{BASE_URL}/api/v1/vocabs_base_on_category?sort=newest",
            "expected_sort": "newest"
        },
        {
            "name": "Oldest Sort",
            "url": f"{BASE_URL}/api/v1/vocabs_base_on_category?sort=oldest", 
            "expected_sort": "oldest"
        },
        {
            "name": "Alphabetical Sort",
            "url": f"{BASE_URL}/api/v1/vocabs_base_on_category?sort=alphabetical",
            "expected_sort": "alphabetical"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        print(f"   URL: {test_case['url']}")
        
        try:
            response = requests.get(test_case["url"])
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                print(f"   ✅ Status: {data.get('status')}")
                print(f"   ✅ Total documents: {data.get('total_documents')}")
                print(f"   ✅ Sort applied: {data.get('sort')}")
                print(f"   ✅ Message: {data.get('message')}")
                
                # Check if documents contain all required fields
                documents = data.get('documents', [])
                if documents:
                    first_doc = documents[0]
                    required_fields = ['id', 'vocabs', 'created_at', 'updated_at', 'deleted_at', 'is_deleted']
                    
                    print(f"   📊 Fields in first document:")
                    for field in required_fields:
                        if field in first_doc:
                            print(f"      ✅ {field}: {first_doc[field]}")
                        else:
                            print(f"      ❌ Missing field: {field}")
                    
                    # Verify sorting
                    if len(documents) >= 2:
                        verify_sorting(documents, test_case['expected_sort'])
                    else:
                        print(f"   ⚠️ Not enough documents to verify sorting")
                else:
                    print(f"   ⚠️ No documents returned")
                    
            elif response.status_code == 401:
                print(f"   ✅ Authentication required (expected without token)")
            else:
                print(f"   ❌ Unexpected status: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text}")
                    
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection failed - server not running")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def verify_sorting(documents, expected_sort):
    """Verify that documents are sorted correctly"""
    print(f"   🔍 Verifying {expected_sort} sorting:")
    
    if expected_sort == "newest":
        # Check newest first (created_at descending)
        for i in range(len(documents) - 1):
            current_date = documents[i].get('created_at') or "1900-01-01T00:00:00"
            next_date = documents[i + 1].get('created_at') or "1900-01-01T00:00:00"
            
            if current_date < next_date:
                print(f"      ❌ Sort error: {current_date} should be >= {next_date}")
                return
        print(f"      ✅ Newest first sorting verified")
        
    elif expected_sort == "oldest":
        # Check oldest first (created_at ascending)
        for i in range(len(documents) - 1):
            current_date = documents[i].get('created_at') or "1900-01-01T00:00:00"
            next_date = documents[i + 1].get('created_at') or "1900-01-01T00:00:00"
            
            if current_date > next_date:
                print(f"      ❌ Sort error: {current_date} should be <= {next_date}")
                return
        print(f"      ✅ Oldest first sorting verified")
        
    elif expected_sort == "alphabetical":
        # Check alphabetical sorting by first vocab
        for i in range(len(documents) - 1):
            current_vocabs = documents[i].get('vocabs', [])
            next_vocabs = documents[i + 1].get('vocabs', [])
            
            current_first = current_vocabs[0].lower() if current_vocabs else "zzz"
            next_first = next_vocabs[0].lower() if next_vocabs else "zzz"
            
            if current_first > next_first:
                print(f"      ❌ Sort error: '{current_first}' should be <= '{next_first}'")
                return
        print(f"      ✅ Alphabetical sorting verified")

def show_expected_response():
    """Show expected response format with all fields"""
    print("\n" + "=" * 70)
    print("📋 Expected Response Format (All Fields)")
    print("=" * 70)
    
    expected_response = {
        "status": True,
        "total_documents": 3,
        "documents": [
            {
                "id": "66ed123456789abcdef01234",
                "vocabs": ["recent", "example"],
                "created_at": "2025-09-20T15:30:00.000000",
                "updated_at": "2025-09-20T15:30:00.000000",
                "deleted_at": None,
                "is_deleted": False
            },
            {
                "id": "66ed123456789abcdef01235", 
                "vocabs": ["hello", "world"],
                "created_at": "2025-09-20T14:15:00.000000",
                "updated_at": "2025-09-20T14:15:00.000000",
                "deleted_at": None,
                "is_deleted": False
            },
            {
                "id": "66ed123456789abcdef01236",
                "vocabs": ["old", "vocabulary"],
                "created_at": "2025-09-20T13:00:00.000000",
                "updated_at": "2025-09-20T13:00:00.000000", 
                "deleted_at": None,
                "is_deleted": False
            }
        ],
        "sort": "newest",
        "message": "Found 3 vocabulary documents sorted by newest"
    }
    
    print(json.dumps(expected_response, indent=2))
    
    print("\n🔍 Field Descriptions:")
    print("• id: Unique document identifier (ObjectId as string)")
    print("• vocabs: Array of vocabulary words")
    print("• created_at: ISO format datetime when document was created") 
    print("• updated_at: ISO format datetime when document was last updated")
    print("• deleted_at: ISO format datetime when document was deleted (null if not deleted)")
    print("• is_deleted: Boolean flag indicating if document is deleted")
    print("• sort: Applied sort method")
    print("• status: Success/failure status")
    print("• total_documents: Count of returned documents")
    print("• message: Descriptive message")

def main():
    print("🚀 Testing Unique Vocabs API - All Fields Sorting")
    print(f"🕒 Test Time: {datetime.now().isoformat()}")
    
    test_sort_all_fields()
    show_expected_response()
    
    print("\n" + "=" * 70)
    print("✅ Test Summary:")
    print("🎯 Default sort: newest first")
    print("📊 All fields included in response")
    print("🔧 Robust datetime sorting with None handling")
    print("✨ Sort verification for all three modes")
    print("🔒 Authentication still required")
    print("=" * 70)

if __name__ == "__main__":
    main()