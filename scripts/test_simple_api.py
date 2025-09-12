"""
Simple HTTP test for the all-paragraphs API
"""
import requests
import json

def test_all_paragraphs_api():
    """Test the all-paragraphs API endpoint"""
    try:
        print("🔍 Testing All Paragraphs API...")
        
        url = "http://localhost:8000/api/v1/all-paragraphs"
        response = requests.get(url)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Response:")
            print(f"   Status: {result['status']}")
            print(f"   Total: {result['total']}")
            
            if result['data']:
                print(f"\n📄 All Paragraphs:")
                for i, item in enumerate(result['data'], 1):
                    print(f"\n{i}. ID: {item['id'][:8]}...")
                    print(f"   Vocabs: {item['vocabs']}")
                    print(f"   Paragraph: {item['paragraph'][:100]}...")
                
                # Summary
                all_vocabs = []
                for item in result['data']:
                    all_vocabs.extend(item['vocabs'])
                unique_vocabs = list(set(all_vocabs))
                
                print(f"\n📊 Summary:")
                print(f"   Total paragraphs: {len(result['data'])}")
                print(f"   Total unique vocabularies: {len(unique_vocabs)}")
                print(f"   All unique vocabs: {unique_vocabs}")
                
                return result
            else:
                print("   No paragraphs found")
                
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return None

if __name__ == "__main__":
    test_all_paragraphs_api()
