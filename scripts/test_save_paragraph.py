"""
Test the save-paragraph API endpoint
"""
import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8000/api/v1"

async def test_save_paragraph_api():
    """Test save-paragraph API endpoint"""
    async with aiohttp.ClientSession() as session:
        print("🌐 Testing Save Paragraph API...")
        
        # Test data
        test_data = {
            "vocabs": ["hello", "world", "python", "programming"],
            "paragraph": "Hello world! This is a test paragraph about python programming. Python is a powerful programming language that makes it easy to build applications. The world of programming becomes more accessible with languages like Python."
        }
        
        print(f"\n📝 Testing with data:")
        print(f"   Vocabularies: {test_data['vocabs']}")
        print(f"   Paragraph: {test_data['paragraph'][:100]}...")
        
        try:
            async with session.post(f"{BASE_URL}/save-paragraph", json=test_data) as response:
                print(f"\n📊 Response Status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Success!")
                    print(f"   Status: {result['status']}")
                    print(f"   Message: {result['message']}")
                    print(f"   Input History ID: {result['input_history_id']}")
                    print(f"   Saved Paragraph ID: {result['saved_paragraph_id']}")
                    
                    # Test retrieving the saved data
                    history_id = result['input_history_id']
                    
                    print(f"\n🔍 Testing retrieval of saved data...")
                    async with session.get(f"{BASE_URL}/db/input-history/{history_id}") as get_response:
                        if get_response.status == 200:
                            history_data = await get_response.json()
                            print(f"✓ Retrieved input history: {history_data['words']}")
                        else:
                            print(f"❌ Failed to retrieve input history: {get_response.status}")
                    
                    paragraph_id = result['saved_paragraph_id']
                    async with session.get(f"{BASE_URL}/db/saved-paragraphs/{paragraph_id}") as get_response:
                        if get_response.status == 200:
                            paragraph_data = await get_response.json()
                            print(f"✓ Retrieved paragraph: {paragraph_data['paragraph'][:50]}...")
                        else:
                            print(f"❌ Failed to retrieve paragraph: {get_response.status}")
                    
                    return result
                    
                else:
                    error_text = await response.text()
                    print(f"❌ Failed with status {response.status}")
                    print(f"   Error: {error_text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Error testing API: {e}")
            return None

async def test_multiple_saves():
    """Test saving multiple different paragraphs"""
    test_cases = [
        {
            "vocabs": ["apple", "tree", "garden"],
            "paragraph": "In my garden, there is a beautiful apple tree that provides shade and delicious fruit during the summer months."
        },
        {
            "vocabs": ["computer", "code", "software"],
            "paragraph": "Modern computer software requires well-written code to function properly and efficiently serve users."
        },
        {
            "vocabs": ["ocean", "wave", "beach"],
            "paragraph": "The ocean waves crashed gently against the sandy beach, creating a peaceful and relaxing atmosphere."
        }
    ]
    
    print(f"\n🔄 Testing multiple saves...")
    
    async with aiohttp.ClientSession() as session:
        for i, test_data in enumerate(test_cases, 1):
            print(f"\n📝 Test case {i}:")
            print(f"   Vocabs: {test_data['vocabs']}")
            
            async with session.post(f"{BASE_URL}/save-paragraph", json=test_data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result['status']:
                        print(f"   ✓ Saved successfully (ID: {result['saved_paragraph_id'][:8]}...)")
                    else:
                        print(f"   ❌ Save failed: {result['message']}")
                else:
                    print(f"   ❌ HTTP Error: {response.status}")

async def main():
    """Run all tests"""
    print("🚀 Starting Save Paragraph API Tests...\n")
    
    # Test single save
    result = await test_save_paragraph_api()
    
    if result and result['status']:
        # Test multiple saves
        await test_multiple_saves()
        
        print(f"\n✅ All tests completed successfully!")
    else:
        print(f"\n❌ Initial test failed, skipping additional tests.")

if __name__ == "__main__":
    asyncio.run(main())
