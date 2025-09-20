"""
Test the unique-vocabs API endpoint
"""
import requests
import json

def test_unique_vocabs():
    """Test the unique-vocabs endpoint"""
    try:
        print("🔍 Testing /vocabs_base_on_category endpoint...")
        
        response = requests.get("http://127.0.0.1:8000/api/v1/vocabs_base_on_category")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status Code: {response.status_code}")
            print(f"✅ API Status: {result.get('status', False)}")
            print(f"✅ Total Unique Vocabularies: {result.get('total_unique', 0)}")
            print(f"✅ Message: {result.get('message', 'N/A')}")
            
            # Display unique vocabularies
            unique_vocabs = result.get('unique_vocabs', [])
            if unique_vocabs:
                print(f"\n📚 All Unique Vocabularies ({len(unique_vocabs)}):")
                for i, vocab in enumerate(unique_vocabs, 1):
                    print(f"  {i:2d}. {vocab}")
                
                # Display frequency data
                frequency_data = result.get('frequency_data', [])
                if frequency_data:
                    print(f"\n📊 Vocabulary Frequency (Top 10):")
                    for i, item in enumerate(frequency_data[:10], 1):
                        vocab = item.get('vocab', '')
                        freq = item.get('frequency', 0)
                        bar = "█" * min(freq, 20)  # Visual bar
                        print(f"  {i:2d}. {vocab:<15} {freq:3d}x {bar}")
                    
                    if len(frequency_data) > 10:
                        print(f"       ... and {len(frequency_data) - 10} more vocabularies")
                
                # Statistics
                total_words = sum(item.get('frequency', 0) for item in frequency_data)
                most_frequent = frequency_data[0] if frequency_data else None
                
                print(f"\n📈 Statistics:")
                print(f"  • Total word occurrences: {total_words}")
                print(f"  • Unique vocabularies: {len(unique_vocabs)}")
                print(f"  • Average frequency: {total_words / len(unique_vocabs):.1f}")
                if most_frequent:
                    print(f"  • Most frequent word: '{most_frequent['vocab']}' ({most_frequent['frequency']}x)")
                
                return True
            else:
                print("   No vocabularies found")
                
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    return False

def test_api_comparison():
    """Compare with saved-paragraphs to verify data consistency"""
    try:
        print("\n🔄 Comparing with saved-paragraphs data...")
        
        # Get saved paragraphs
        response1 = requests.get("http://127.0.0.1:8000/api/v1/saved-paragraphs")
        # Get unique vocabs
        response2 = requests.get("http://127.0.0.1:8000/api/v1/vocabs_base_on_category")
        
        if response1.status_code == 200 and response2.status_code == 200:
            paragraphs_data = response1.json()
            vocabs_data = response2.json()
            
            # Extract all vocabs from paragraphs
            all_vocabs_from_paragraphs = set()
            for item in paragraphs_data.get('data', []):
                for vocab in item.get('vocabs', []):
                    all_vocabs_from_paragraphs.add(vocab.lower().strip())
            
            # Get unique vocabs from API
            unique_from_api = set(vocabs_data.get('unique_vocabs', []))
            
            # Compare
            if all_vocabs_from_paragraphs == unique_from_api:
                print(f"✅ Data consistency verified!")
                print(f"   Both sources show {len(unique_from_api)} unique vocabularies")
            else:
                diff1 = all_vocabs_from_paragraphs - unique_from_api
                diff2 = unique_from_api - all_vocabs_from_paragraphs
                print(f"⚠️  Data differences found:")
                if diff1:
                    print(f"   In paragraphs but not in unique-vocabs: {diff1}")
                if diff2:
                    print(f"   In unique-vocabs but not in paragraphs: {diff2}")
        
    except Exception as e:
        print(f"❌ Error in comparison: {e}")

if __name__ == "__main__":
    print("🚀 Testing the /vocabs_base_on_category endpoint...\n")
    
    if test_unique_vocabs():
        test_api_comparison()
    
    print(f"\n🎉 Testing completed!")
