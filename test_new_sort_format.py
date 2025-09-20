#!/usr/bin/env python3
"""
Test script to verify the new response format with sort field containing the data array
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_new_sort_format():
    """Test the new response format with sort field containing data array"""
    print("🔧 Testing New Sort Format - Sort Field Contains Data Array")
    print("=" * 70)
    
    test_cases = [
        {
            "name": "Default Sort (newest first)",
            "url": f"{BASE_URL}/api/v1/unique-vocabs",
            "expected_sort_method": "newest"
        },
        {
            "name": "Explicit Newest Sort",
            "url": f"{BASE_URL}/api/v1/unique-vocabs?sort=newest",
            "expected_sort_method": "newest"
        },
        {
            "name": "Oldest Sort",
            "url": f"{BASE_URL}/api/v1/unique-vocabs?sort=oldest", 
            "expected_sort_method": "oldest"
        },
        {
            "name": "Alphabetical Sort",
            "url": f"{BASE_URL}/api/v1/unique-vocabs?sort=alphabetical",
            "expected_sort_method": "alphabetical"
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
                
                # Check new response structure
                print(f"   ✅ Status: {data.get('status')}")
                print(f"   ✅ Total documents: {data.get('total_documents')}")
                print(f"   ✅ Sort method: {data.get('sort_method')}")
                
                # Check if sort field contains the data array
                sort_data = data.get('sort', [])
                documents = data.get('documents', [])
                
                if isinstance(sort_data, list):
                    print(f"   ✅ Sort field is array with {len(sort_data)} items")
                    
                    # Verify sort and documents are identical
                    if sort_data == documents:
                        print(f"   ✅ Sort field contains same data as documents field")
                    else:
                        print(f"   ❌ Sort field differs from documents field")
                        
                    # Show first item structure if exists
                    if sort_data:
                        first_item = sort_data[0]
                        print(f"   📊 First item in sort array:")
                        print(f"      ID: {first_item.get('id', 'N/A')}")
                        print(f"      Vocabs: {first_item.get('vocabs', [])}")
                        print(f"      Created: {first_item.get('created_at', 'N/A')}")
                        
                    # Verify sorting
                    if len(sort_data) >= 2:
                        verify_sorting_in_sort_field(sort_data, test_case['expected_sort_method'])
                        
                else:
                    print(f"   ❌ Sort field is not an array: {type(sort_data)}")
                    
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

def verify_sorting_in_sort_field(sort_data, expected_sort_method):
    """Verify that data in sort field is properly sorted"""
    print(f"   🔍 Verifying sorting in sort field ({expected_sort_method}):")
    
    if expected_sort_method == "newest":
        # Check newest first (created_at descending)
        for i in range(len(sort_data) - 1):
            current_date = sort_data[i].get('created_at') or "1900-01-01T00:00:00"
            next_date = sort_data[i + 1].get('created_at') or "1900-01-01T00:00:00"
            
            if current_date < next_date:
                print(f"      ❌ Sort error: {current_date} should be >= {next_date}")
                return
        print(f"      ✅ Newest first sorting verified in sort field")
        
    elif expected_sort_method == "oldest":
        # Check oldest first (created_at ascending)
        for i in range(len(sort_data) - 1):
            current_date = sort_data[i].get('created_at') or "1900-01-01T00:00:00"
            next_date = sort_data[i + 1].get('created_at') or "1900-01-01T00:00:00"
            
            if current_date > next_date:
                print(f"      ❌ Sort error: {current_date} should be <= {next_date}")
                return
        print(f"      ✅ Oldest first sorting verified in sort field")
        
    elif expected_sort_method == "alphabetical":
        # Check alphabetical sorting by first vocab
        for i in range(len(sort_data) - 1):
            current_vocabs = sort_data[i].get('vocabs', [])
            next_vocabs = sort_data[i + 1].get('vocabs', [])
            
            current_first = current_vocabs[0].lower() if current_vocabs else "zzz"
            next_first = next_vocabs[0].lower() if next_vocabs else "zzz"
            
            if current_first > next_first:
                print(f"      ❌ Sort error: '{current_first}' should be <= '{next_first}'")
                return
        print(f"      ✅ Alphabetical sorting verified in sort field")

def show_new_response_format():
    """Show the new expected response format"""
    print("\n" + "=" * 70)
    print("📋 New Response Format - Sort Field Contains Data Array")
    print("=" * 70)
    
    new_response_format = {
        "status": True,
        "total_documents": 3,
        "documents": [
            {
                "id": "66ed123456789abcdef01234",
                "vocabs": ["recent", "vocabulary"],
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
                "vocabs": ["old", "example"],
                "created_at": "2025-09-20T13:00:00.000000",
                "updated_at": "2025-09-20T13:00:00.000000",
                "deleted_at": None,
                "is_deleted": False
            }
        ],
        "sort": [
            {
                "id": "66ed123456789abcdef01234",
                "vocabs": ["recent", "vocabulary"],
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
                "vocabs": ["old", "example"],
                "created_at": "2025-09-20T13:00:00.000000",
                "updated_at": "2025-09-20T13:00:00.000000",
                "deleted_at": None,
                "is_deleted": False
            }
        ],
        "sort_method": "newest",
        "message": "Found 3 vocabulary documents sorted by newest"
    }
    
    print(json.dumps(new_response_format, indent=2))
    
    print("\n🔍 Field Descriptions:")
    print("• documents: Array of vocabulary documents (same as before)")
    print("• sort: Array containing the same data as documents but sorted")
    print("• sort_method: String indicating the sorting method used")
    print("• sort field is sorted by newest first by default")
    print("• Both documents and sort fields contain identical data")

def main():
    print("🚀 Testing New Sort Format - Sort Field as Data Array")
    print(f"🕒 Test Time: {datetime.now().isoformat()}")
    
    test_new_sort_format()
    show_new_response_format()
    
    print("\n" + "=" * 70)
    print("✅ New Format Summary:")
    print("📊 sort field now contains the actual sorted data array")
    print("🎯 Data in sort field is sorted by newest first by default")
    print("🔧 sort_method field indicates the sorting method")
    print("📋 documents and sort fields contain identical data")
    print("🔒 Authentication still required")
    print("=" * 70)

if __name__ == "__main__":
    main()