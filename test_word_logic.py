"""
Simple test to verify word normalization logic
"""

def normalize_words(word_list):
    """Same normalization logic as in the CRUD"""
    normalized = []
    for word in word_list:
        if isinstance(word, str):
            cleaned = word.strip().lower()
            if cleaned:
                normalized.append(cleaned)
    return sorted(normalized)

def test_word_normalization():
    """Test different word combinations"""
    test_cases = [
        # Case 1: Exact same words
        (["apple", "banana"], ["apple", "banana"], True),
        
        # Case 2: Different order
        (["banana", "apple"], ["apple", "banana"], True),
        
        # Case 3: Different case
        (["Apple", "BANANA"], ["apple", "banana"], True),
        
        # Case 4: Extra whitespace
        ([" apple ", "banana "], ["apple", "banana"], True),
        
        # Case 5: Empty strings mixed in
        (["apple", "", "banana"], ["apple", "banana"], True),
        
        # Case 6: Different words
        (["apple", "banana"], ["apple", "cherry"], False),
        
        # Case 7: Subset
        (["apple"], ["apple", "banana"], False),
        
        # Case 8: Complex case
        ([" Apple ", "", "BANANA", "cherry "], ["apple", "banana", "cherry"], True),
    ]
    
    print("Testing word normalization logic:")
    print("=" * 50)
    
    for i, (words1, words2, expected) in enumerate(test_cases, 1):
        norm1 = normalize_words(words1)
        norm2 = normalize_words(words2)
        result = norm1 == norm2
        
        status = "✅ PASS" if result == expected else "❌ FAIL"
        
        print(f"Test {i}: {status}")
        print(f"  Input 1: {words1}")
        print(f"  Input 2: {words2}")
        print(f"  Normalized 1: {norm1}")
        print(f"  Normalized 2: {norm2}")
        print(f"  Match: {result} (expected: {expected})")
        print()

if __name__ == "__main__":
    test_word_normalization()