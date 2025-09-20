"""
Additional edge case tests for refactored save-paragraph API
"""
import requests
import json

def test_case_sensitivity():
    """Test if case sensitivity is handled properly"""
    print("🔵 Test: Case Sensitivity")
    
    # Test 1: Save with lowercase
    data1 = {
        "vocabs": ["hello", "world", "case"],
        "paragraph": "Testing case sensitivity with lowercase words."
    }
    
    response1 = requests.post("http://127.0.0.1:8000/api/v1/save-paragraph", json=data1)
    result1 = response1.json()
    
    # Test 2: Save with mixed case (should reuse same input_history_id)
    data2 = {
        "vocabs": ["Hello", "WORLD", "Case"],  # Same words, different case
        "paragraph": "Testing case sensitivity with mixed case words."
    }
    
    response2 = requests.post("http://127.0.0.1:8000/api/v1/save-paragraph", json=data2)
    result2 = response2.json()
    
    print(f"Lowercase ID: {result1.get('input_history_id')}")
    print(f"Mixed case ID: {result2.get('input_history_id')}")
    
    if result1.get('input_history_id') == result2.get('input_history_id'):
        print("✅ SUCCESS: Case insensitive matching works")
    else:
        print("❌ ISSUE: Case sensitivity not handled properly")

def test_order_independence():
    """Test if word order independence works"""
    print("\n🔵 Test: Word Order Independence")
    
    # Test 1: Save with one order
    data1 = {
        "vocabs": ["apple", "banana", "cherry"],
        "paragraph": "First paragraph with fruits in alphabetical order."
    }
    
    response1 = requests.post("http://127.0.0.1:8000/api/v1/save-paragraph", json=data1)
    result1 = response1.json()
    
    # Test 2: Save with different order (should reuse same input_history_id)
    data2 = {
        "vocabs": ["cherry", "apple", "banana"],  # Same words, different order
        "paragraph": "Second paragraph with fruits in different order."
    }
    
    response2 = requests.post("http://127.0.0.1:8000/api/v1/save-paragraph", json=data2)
    result2 = response2.json()
    
    print(f"Original order ID: {result1.get('input_history_id')}")
    print(f"Different order ID: {result2.get('input_history_id')}")
    
    if result1.get('input_history_id') == result2.get('input_history_id'):
        print("✅ SUCCESS: Order independence works")
    else:
        print("❌ ISSUE: Word order affects matching")

def test_whitespace_handling():
    """Test if whitespace is handled properly"""
    print("\n🔵 Test: Whitespace Handling")
    
    # Test 1: Save with normal words
    data1 = {
        "vocabs": ["space", "test", "clean"],
        "paragraph": "Testing whitespace handling with clean words."
    }
    
    response1 = requests.post("http://127.0.0.1:8000/api/v1/save-paragraph", json=data1)
    result1 = response1.json()
    
    # Test 2: Save with extra whitespace (should reuse same input_history_id)
    data2 = {
        "vocabs": ["  space  ", " test", "clean "],  # Same words with whitespace
        "paragraph": "Testing whitespace handling with padded words."
    }
    
    response2 = requests.post("http://127.0.0.1:8000/api/v1/save-paragraph", json=data2)
    result2 = response2.json()
    
    print(f"Clean words ID: {result1.get('input_history_id')}")
    print(f"Padded words ID: {result2.get('input_history_id')}")
    
    if result1.get('input_history_id') == result2.get('input_history_id'):
        print("✅ SUCCESS: Whitespace normalization works")
    else:
        print("❌ ISSUE: Whitespace affects matching")

def test_empty_words():
    """Test handling of empty words"""
    print("\n🔵 Test: Empty Words Handling")
    
    data = {
        "vocabs": ["valid", "", "  ", "another"],  # Include empty and whitespace-only
        "paragraph": "Testing with some empty vocabularies in the list."
    }
    
    try:
        response = requests.post("http://127.0.0.1:8000/api/v1/save-paragraph", json=data)
        result = response.json()
        
        if result.get('status'):
            print("✅ SUCCESS: Empty words handled properly")
            print(f"✅ Message: {result.get('message')}")
        else:
            print(f"❌ ISSUE: {result.get('message')}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def show_final_summary():
    """Show final database state"""
    print("\n🔍 Final Database Summary:")
    
    try:
        # Get unique vocabs
        response1 = requests.get("http://127.0.0.1:8000/api/v1/vocabs_base_on_category")
        result1 = response1.json()
        
        # Get all paragraphs
        response2 = requests.get("http://127.0.0.1:8000/api/v1/saved-paragraphs")
        result2 = response2.json()
        
        print(f"📊 Total unique vocabularies: {result1.get('total_unique', 0)}")
        print(f"📄 Total saved paragraphs: {result2.get('total', 0)}")
        
        # Calculate efficiency
        if result2.get('total', 0) > 0:
            efficiency = result1.get('total_unique', 0) / result2.get('total', 1)
            print(f"📈 Vocabulary reuse efficiency: {efficiency:.2f} unique vocabs per paragraph")
        
    except Exception as e:
        print(f"❌ Error getting summary: {e}")

def main():
    """Run edge case tests"""
    print("🚀 Testing Edge Cases for Refactored API")
    print("=" * 60)
    
    test_case_sensitivity()
    test_order_independence()
    test_whitespace_handling()
    test_empty_words()
    
    show_final_summary()
    
    print("\n" + "=" * 60)
    print("🎉 Edge case testing completed!")

if __name__ == "__main__":
    main()
