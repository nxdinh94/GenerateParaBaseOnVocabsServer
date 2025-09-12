"""
Test the refactored save-paragraph API
Test case: Existing vocabularies should reuse input_history_id
"""
import requests
import json

def test_save_with_new_vocabs():
    """Test saving with completely new vocabularies"""
    print("🔵 Test 1: Save with NEW vocabularies")
    
    data = {
        "vocabs": ["refactor", "test", "new"],
        "paragraph": "This is a test with completely new vocabularies that should create a new input history."
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
            return result.get('input_history_id')
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return None

def test_save_with_existing_vocabs():
    """Test saving with existing vocabularies (should reuse input_history_id)"""
    print("\n🔵 Test 2: Save with EXISTING vocabularies")
    
    # Use same vocabs as test 1 but different order
    data = {
        "vocabs": ["test", "refactor", "new"],  # Same words, different order
        "paragraph": "This paragraph uses the same vocabularies as before, so it should reuse the existing input history ID."
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
            return result.get('input_history_id')
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return None

def test_save_with_partial_existing():
    """Test saving with partially existing vocabularies"""
    print("\n🔵 Test 3: Save with PARTIALLY existing vocabularies")
    
    data = {
        "vocabs": ["refactor", "test", "partial"],  # 2 existing + 1 new
        "paragraph": "This paragraph has some existing vocabularies and some new ones, so it should create a new input history."
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
            return result.get('input_history_id')
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return None

def verify_data_consistency():
    """Verify the saved data"""
    print("\n🔍 Verifying saved data...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/saved-paragraphs")
        
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', [])
            
            print(f"✅ Total paragraphs: {result.get('total')}")
            
            # Show last 3 paragraphs
            if data:
                print(f"\n📄 Last 3 saved paragraphs:")
                for i, item in enumerate(data[-3:], 1):
                    print(f"{i}. ID: {item.get('id')[:12]}...")
                    print(f"   Vocabs: {item.get('vocabs')}")
                    print(f"   Text: {item.get('paragraph')[:60]}...")
                    print()
            
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Run refactor tests"""
    print("🚀 Testing Refactored save-paragraph API")
    print("=" * 60)
    
    # Test with new vocabularies
    new_input_id = test_save_with_new_vocabs()
    
    # Test with same vocabularies (should reuse input_history_id)
    existing_input_id = test_save_with_existing_vocabs()
    
    # Test with partially existing vocabularies
    partial_input_id = test_save_with_partial_existing()
    
    # Verify results
    print("\n" + "=" * 60)
    print("🔍 RESULTS ANALYSIS:")
    
    if new_input_id and existing_input_id:
        if new_input_id == existing_input_id:
            print("✅ SUCCESS: Same vocabularies reused input_history_id")
            print(f"   Both tests used ID: {new_input_id}")
        else:
            print("❌ ISSUE: Same vocabularies created different input_history_id")
            print(f"   New vocab ID: {new_input_id}")
            print(f"   Existing vocab ID: {existing_input_id}")
    
    if partial_input_id:
        if partial_input_id != new_input_id:
            print("✅ SUCCESS: Partial match created new input_history_id")
            print(f"   Partial vocab ID: {partial_input_id}")
        else:
            print("❌ ISSUE: Partial match reused input_history_id (should be new)")
    
    # Show final data
    verify_data_consistency()
    
    print("\n🎉 Refactor testing completed!")

if __name__ == "__main__":
    main()
