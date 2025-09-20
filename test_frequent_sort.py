#!/usr/bin/env python3
"""
Test script for frequent sorting functionality in unique-vocabs API
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_frequent_sorting():
    """Test the new frequent sorting functionality"""
    print("🔧 Testing Frequent Sorting - Sort by Most Used Vocabularies")
    print("=" * 70)
    
    test_cases = [
        {
            "name": "Default Sort (newest first)",
            "url": f"{BASE_URL}/api/v1/unique-vocabs",
            "expected_sort_method": "newest"
        },
        {
            "name": "Frequent Sort (most used first)",
            "url": f"{BASE_URL}/api/v1/unique-vocabs?sort=frequent",
            "expected_sort_method": "frequent"
        },
        {
            "name": "Newest Sort",
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
                
                # Check response structure
                print(f"   ✅ Status: {data.get('status')}")
                print(f"   ✅ Total documents: {data.get('total_documents')}")
                print(f"   ✅ Sort method: {data.get('sort_method')}")
                
                # Check if sort field contains the data array
                sort_data = data.get('sort', [])
                
                if isinstance(sort_data, list) and sort_data:
                    print(f"   ✅ Sort field contains {len(sort_data)} items")
                    
                    # Show usage counts if frequent sort
                    if test_case['expected_sort_method'] == 'frequent':
                        print(f"   📊 Usage counts (most frequent first):")
                        for i, item in enumerate(sort_data[:5]):  # Show first 5
                            usage_count = item.get('usage_count', 'N/A')
                            vocabs = ', '.join(item.get('vocabs', []))
                            print(f"      {i+1}. {vocabs} (used {usage_count} times)")
                        
                        # Verify frequency sorting
                        if verify_frequency_sorting(sort_data):
                            print(f"   ✅ Frequency sorting verified")
                        else:
                            print(f"   ❌ Frequency sorting failed")
                    
                    # Show first item structure
                    first_item = sort_data[0]
                    print(f"   📋 First item structure:")
                    print(f"      ID: {first_item.get('id', 'N/A')}")
                    print(f"      Vocabs: {first_item.get('vocabs', [])}")
                    print(f"      Usage count: {first_item.get('usage_count', 'N/A')}")
                    print(f"      Created: {first_item.get('created_at', 'N/A')}")
                        
                else:
                    print(f"   ❌ Sort field is empty or invalid")
                    
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

def verify_frequency_sorting(sort_data):
    """Verify that data is sorted by usage_count descending"""
    if len(sort_data) < 2:
        return True  # Cannot verify with less than 2 items
    
    for i in range(len(sort_data) - 1):
        current_usage = sort_data[i].get('usage_count', 0)
        next_usage = sort_data[i + 1].get('usage_count', 0)
        
        if current_usage < next_usage:
            print(f"      ❌ Frequency sort error: usage {current_usage} should be >= {next_usage}")
            return False
    
    return True

def test_learned_vocabs_post():
    """Test the updated POST /learned-vocabs endpoint with usage count"""
    print("\n🔧 Testing POST /learned-vocabs - Usage Count Increment")
    print("=" * 70)
    
    # Test data
    test_vocabs = {
        "vocabs": ["test", "frequency"]
    }
    
    print(f"📤 Testing POST with vocabs: {test_vocabs['vocabs']}")
    print(f"   URL: {BASE_URL}/api/v1/learned-vocabs")
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/learned-vocabs", json=test_vocabs)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data.get('status')}")
            print(f"   ✅ Message: {data.get('message')}")
            print(f"   ✅ Is new: {data.get('is_new')}")
            print(f"   ✅ Usage incremented: {data.get('usage_incremented')}")
            
            vocab_data = data.get('data', {})
            if vocab_data:
                print(f"   📊 Data:")
                print(f"      ID: {vocab_data.get('id')}")
                print(f"      Vocabs: {vocab_data.get('vocabs')}")
                print(f"      Usage count: {vocab_data.get('usage_count')}")
                print(f"      Created: {vocab_data.get('created_at')}")
                print(f"      Updated: {vocab_data.get('updated_at')}")
                
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

def show_frequent_sort_format():
    """Show expected response format with usage_count field"""
    print("\n" + "=" * 70)
    print("📋 Expected Response Format - With Usage Count and Frequent Sort")
    print("=" * 70)
    
    frequent_response_format = {
        "status": True,
        "total_documents": 3,
        "documents": [
            {
                "id": "66ed123456789abcdef01234",
                "vocabs": ["frequently", "used"],
                "usage_count": 15,
                "created_at": "2025-09-20T10:00:00.000000",
                "updated_at": "2025-09-20T14:30:00.000000",
                "deleted_at": None,
                "is_deleted": False
            },
            {
                "id": "66ed123456789abcdef01235",
                "vocabs": ["hello", "world"],
                "usage_count": 8,
                "created_at": "2025-09-20T11:00:00.000000",
                "updated_at": "2025-09-20T13:15:00.000000",
                "deleted_at": None,
                "is_deleted": False
            },
            {
                "id": "66ed123456789abcdef01236",
                "vocabs": ["rarely", "used"],
                "usage_count": 2,
                "created_at": "2025-09-20T12:00:00.000000",
                "updated_at": "2025-09-20T12:30:00.000000",
                "deleted_at": None,
                "is_deleted": False
            }
        ],
        "sort": [
            {
                "id": "66ed123456789abcdef01234",
                "vocabs": ["frequently", "used"],
                "usage_count": 15,
                "created_at": "2025-09-20T10:00:00.000000",
                "updated_at": "2025-09-20T14:30:00.000000",
                "deleted_at": None,
                "is_deleted": False
            },
            {
                "id": "66ed123456789abcdef01235",
                "vocabs": ["hello", "world"],
                "usage_count": 8,
                "created_at": "2025-09-20T11:00:00.000000",
                "updated_at": "2025-09-20T13:15:00.000000",
                "deleted_at": None,
                "is_deleted": False
            },
            {
                "id": "66ed123456789abcdef01236",
                "vocabs": ["rarely", "used"],
                "usage_count": 2,
                "created_at": "2025-09-20T12:00:00.000000",
                "updated_at": "2025-09-20T12:30:00.000000",
                "deleted_at": None,
                "is_deleted": False
            }
        ],
        "sort_method": "frequent",
        "message": "Found 3 vocabulary documents sorted by frequent"
    }
    
    print(json.dumps(frequent_response_format, indent=2))
    
    print("\n🔍 New Field Descriptions:")
    print("• usage_count: Number of times this vocabulary set has been used")
    print("• sort=frequent: Sorts by usage_count DESC (most used first)")
    print("• Each time existing vocabs are used, usage_count increments")
    print("• Tiebreaker for same usage_count: newest created_at first")

def show_usage_examples():
    """Show usage examples for the new frequent sort"""
    print("\n" + "=" * 70)
    print("🔧 Usage Examples - Frequent Sort")
    print("=" * 70)
    
    examples = [
        {
            "description": "Get most frequently used vocabularies",
            "curl": f"""curl -H "Authorization: Bearer <token>" "{BASE_URL}/api/v1/unique-vocabs?sort=frequent\""""
        },
        {
            "description": "Create vocabularies (increments usage if exists)",
            "curl": f"""curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{{"vocabs": ["word1", "word2"]}}' "{BASE_URL}/api/v1/learned-vocabs\""""
        },
        {
            "description": "Get newest vocabularies (default)",
            "curl": f"""curl -H "Authorization: Bearer <token>" "{BASE_URL}/api/v1/unique-vocabs\""""
        }
    ]
    
    for example in examples:
        print(f"\n📝 {example['description']}:")
        print(f"   {example['curl']}")

def main():
    print("🚀 Testing Frequent Sorting for Unique Vocabs API")
    print(f"🕒 Test Time: {datetime.now().isoformat()}")
    
    test_frequent_sorting()
    test_learned_vocabs_post()
    show_frequent_sort_format()
    show_usage_examples()
    
    print("\n" + "=" * 70)
    print("✅ Frequent Sort Summary:")
    print("📊 Added 'frequent' sort option")
    print("🔢 Added usage_count field to track vocabulary usage")
    print("📈 Most used vocabularies appear first in frequent sort")
    print("🔄 Usage count increments when existing vocabs are reused")
    print("🎯 Tiebreaker: newest first for same usage count")
    print("🔒 Authentication still required")
    print("=" * 70)

if __name__ == "__main__":
    main()