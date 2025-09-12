"""
Simple test for save-paragraph API
"""
import requests
import json

def test_save_paragraph():
    """Test saving a new paragraph using requests"""
    try:
        print("🔄 Testing Save Paragraph API...")
        
        # Test data
        test_data = {
            "vocabs": ["final", "test", "success"],
            "paragraph": "This is our final test to ensure the save-paragraph API works correctly. We are testing with new vocabularies."
        }
        
        # Make the request
        response = requests.post(
            "http://localhost:8000/api/v1/save-paragraph",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status'):
                print(f"✅ Successfully saved paragraph:")
                print(f"   Input History ID: {result.get('input_history_id')}")
                print(f"   Saved Paragraph ID: {result.get('saved_paragraph_id')}")
                print(f"   Message: {result.get('message')}")
                return True
            else:
                print(f"❌ Save failed: {result.get('message')}")
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    return False

def test_get_all():
    """Test getting all paragraphs"""
    try:
        print("🔍 Testing Get All Paragraphs...")
        
        response = requests.get("http://localhost:8000/api/v1/all-paragraphs")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved {result.get('total', 0)} paragraphs")
            
            # Show last 3 paragraphs
            if 'data' in result and result['data']:
                print("\n📄 Last 3 paragraphs:")
                for i, item in enumerate(result['data'][-3:], 1):
                    print(f"{i}. Vocabs: {item.get('vocabs', [])}")
                    print(f"   Text: {item.get('paragraph', '')[:80]}...")
                    
            return True
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    return False

if __name__ == "__main__":
    print("🚀 Testing APIs with requests library...\n")
    
    # Test current state
    test_get_all()
    
    print("\n" + "="*50)
    
    # Test save
    if test_save_paragraph():
        print("\n" + "="*50)
        # Test get all again
        test_get_all()
    
    print(f"\n🎉 Testing completed!")
