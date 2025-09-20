"""
Complete API Demo - Test all endpoints
"""
import requests
import json
import time

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🔸 {title}")
    print(f"{'='*60}")

def test_save_paragraph():
    """Test saving a new paragraph"""
    print_section("SAVE PARAGRAPH API")
    
    data = {
        "vocabs": ["demo", "api", "testing", "complete"],
        "paragraph": "This is a complete demo of our API system. We are testing all endpoints to ensure they work properly and efficiently."
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/v1/save-paragraph",
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {result.get('status')}")
            print(f"✅ Message: {result.get('message')}")
            print(f"✅ Input History ID: {result.get('input_history_id')}")
            print(f"✅ Saved Paragraph ID: {result.get('saved_paragraph_id')}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return False

def test_get_all_paragraphs():
    """Test getting all paragraphs"""
    print_section("GET ALL PARAGRAPHS API")
    
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/saved-paragraphs")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {result.get('status')}")
            print(f"✅ Total Paragraphs: {result.get('total')}")
            
            data = result.get('data', [])
            if data:
                print(f"\n📄 Latest 3 Paragraphs:")
                for i, item in enumerate(data[-3:], 1):
                    print(f"{i}. Vocabs: {item.get('vocabs')}")
                    print(f"   Text: {item.get('paragraph')[:80]}...")
                    
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return False

def test_unique_vocabs():
    """Test getting unique vocabularies"""
    print_section("UNIQUE VOCABULARIES API")
    
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/vocabs_base_on_category")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {result.get('status')}")
            print(f"✅ Total Unique: {result.get('total_unique')}")
            print(f"✅ Message: {result.get('message')}")
            
            # Show all unique vocabs
            unique_vocabs = result.get('unique_vocabs', [])
            print(f"\n📚 All Unique Vocabularies:")
            print(f"   {', '.join(unique_vocabs)}")
            
            # Show top 5 frequent vocabs
            frequency_data = result.get('frequency_data', [])
            if frequency_data:
                print(f"\n📊 Top 5 Most Frequent:")
                for i, item in enumerate(frequency_data[:5], 1):
                    vocab = item.get('vocab')
                    freq = item.get('frequency')
                    print(f"   {i}. {vocab} ({freq}x)")
                    
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return False

def test_api_endpoints():
    """Test multiple endpoints for consistency"""
    print_section("API ENDPOINTS COMPARISON")
    
    endpoints = [
        ("all-paragraphs", "http://127.0.0.1:8000/api/v1/all-paragraphs"),
        ("saved-paragraphs", "http://127.0.0.1:8000/api/v1/saved-paragraphs"),
        ("test-data", "http://127.0.0.1:8000/api/v1/test-data")
    ]
    
    print(f"📍 Testing endpoint availability:")
    for name, url in endpoints:
        try:
            response = requests.get(url)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {status} /{name} - Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ /{name} - Error: {str(e)[:50]}...")

def main():
    """Run complete API demo"""
    print("🚀 COMPLETE API DEMO STARTING...")
    print("🔗 Base URL: http://127.0.0.1:8000/api/v1/")
    
    # Test basic endpoints
    test_api_endpoints()
    
    # Test main functionality
    success_count = 0
    
    if test_save_paragraph():
        success_count += 1
        time.sleep(1)  # Brief pause for server processing
    
    if test_get_all_paragraphs():
        success_count += 1
    
    if test_unique_vocabs():
        success_count += 1
    
    # Final summary
    print_section("DEMO SUMMARY")
    print(f"✅ Successful tests: {success_count}/3")
    print(f"🎯 API Status: {'FULLY OPERATIONAL' if success_count == 3 else 'NEEDS ATTENTION'}")
    
    if success_count == 3:
        print(f"\n🎉 All APIs are working perfectly!")
        print(f"📱 Available endpoints:")
        print(f"   • POST /save-paragraph - Save vocabs + paragraph")
        print(f"   • GET  /saved-paragraphs - Get all saved data")
        print(f"   • GET  /all-paragraphs - Same as saved-paragraphs")
        print(f"   • GET  /vocabs_base_on_category - Get unique vocabularies")
        print(f"   • GET  /test-data - Simple test endpoint")
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    main()
