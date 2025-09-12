"""
Test the new saved-paragraphs endpoint
"""
import requests
import json

def test_saved_paragraphs_endpoint():
    """Test the saved-paragraphs endpoint"""
    try:
        print("🔍 Testing /saved-paragraphs endpoint...")
        
        response = requests.get("http://127.0.0.1:8000/api/v1/saved-paragraphs")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status Code: {response.status_code}")
            print(f"✅ API Status: {result.get('status', False)}")
            print(f"✅ Total Paragraphs: {result.get('total', 0)}")
            
            if 'data' in result and result['data']:
                print(f"\n📄 Sample Paragraphs:")
                for i, item in enumerate(result['data'][:3], 1):  # Show first 3
                    print(f"{i}. ID: {item.get('id', 'N/A')[:12]}...")
                    print(f"   Vocabs: {item.get('vocabs', [])}")
                    print(f"   Text: {item.get('paragraph', '')[:80]}...")
                    print()
                
                if len(result['data']) > 3:
                    print(f"   ... and {len(result['data']) - 3} more paragraphs")
                
                return True
            else:
                print("   No paragraphs found")
                
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    return False

def test_both_endpoints():
    """Test both endpoints to verify they return the same data"""
    try:
        print("🔄 Comparing both endpoints...")
        
        # Test saved-paragraphs
        response1 = requests.get("http://127.0.0.1:8000/api/v1/saved-paragraphs")
        # Test all-paragraphs  
        response2 = requests.get("http://127.0.0.1:8000/api/v1/all-paragraphs")
        
        if response1.status_code == 200 and response2.status_code == 200:
            data1 = response1.json()
            data2 = response2.json()
            
            if data1['total'] == data2['total']:
                print(f"✅ Both endpoints return same count: {data1['total']}")
                print(f"✅ /saved-paragraphs is working correctly!")
                return True
            else:
                print(f"❌ Data mismatch: {data1['total']} vs {data2['total']}")
        
    except Exception as e:
        print(f"❌ Error comparing endpoints: {e}")
        
    return False

if __name__ == "__main__":
    print("🚀 Testing the /saved-paragraphs endpoint...\n")
    
    if test_saved_paragraphs_endpoint():
        print("\n" + "="*50)
        test_both_endpoints()
    
    print(f"\n🎉 Testing completed!")
