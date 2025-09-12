"""
Test the new all-paragraphs API endpoint
"""
import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8000/api/v1"

async def test_all_paragraphs_api():
    """Test all-paragraphs API endpoint"""
    async with aiohttp.ClientSession() as session:
        print("🔍 Testing All Paragraphs API...")
        
        try:
            async with session.get(f"{BASE_URL}/all-paragraphs") as response:
                print(f"📊 Response Status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ API Response:")
                    print(f"   Status: {result['status']}")
                    print(f"   Total: {result['total']}")
                    
                    if result['data']:
                        print(f"   Paragraphs:")
                        for i, item in enumerate(result['data'], 1):
                            print(f"     {i}. ID: {item['id'][:8]}...")
                            print(f"        Vocabs: {item['vocabs']}")
                            print(f"        Paragraph: {item['paragraph'][:80]}...")
                            print(f"        Created: {item['created_at']}")
                            print()
                            
                        # Show summary
                        print(f"\n📈 Summary:")
                        all_vocabs = []
                        for item in result['data']:
                            all_vocabs.extend(item['vocabs'])
                        unique_vocabs = list(set(all_vocabs))
                        print(f"   Total paragraphs: {len(result['data'])}")
                        print(f"   Total unique vocabularies: {len(unique_vocabs)}")
                        print(f"   Unique vocabs: {unique_vocabs}")
                        
                    else:
                        print("   No paragraphs found")
                        
                else:
                    error_text = await response.text()
                    print(f"❌ Failed with status {response.status}")
                    print(f"   Error: {error_text}")
                    
        except Exception as e:
            print(f"❌ Error testing API: {e}")

async def test_save_and_get():
    """Test saving a new paragraph and then getting all"""
    async with aiohttp.ClientSession() as session:
        print("\n🔄 Testing Save + Get All workflow...")
        
        # Save a new paragraph
        test_data = {
            "vocabs": ["workflow", "test", "api"],
            "paragraph": "This is a workflow test to verify that our API works correctly when saving and retrieving data."
        }
        
        print(f"📝 Saving new paragraph with vocabs: {test_data['vocabs']}")
        async with session.post(f"{BASE_URL}/save-paragraph", json=test_data) as response:
            if response.status == 200:
                save_result = await response.json()
                if save_result['status']:
                    print(f"✓ Saved successfully")
                else:
                    print(f"❌ Save failed: {save_result['message']}")
                    return
            else:
                print(f"❌ Save HTTP Error: {response.status}")
                return
        
        # Get all paragraphs
        print(f"\n🔍 Getting all paragraphs...")
        async with session.get(f"{BASE_URL}/all-paragraphs") as response:
            if response.status == 200:
                result = await response.json()
                if result['status']:
                    print(f"✓ Retrieved {result['total']} total paragraphs")
                    
                    # Find our new paragraph
                    found = False
                    for item in result['data']:
                        if set(item['vocabs']) == set(test_data['vocabs']):
                            print(f"✓ Found our new paragraph: {item['paragraph'][:50]}...")
                            found = True
                            break
                    
                    if not found:
                        print("❌ Could not find our new paragraph in the results")
                else:
                    print(f"❌ Get failed")
            else:
                print(f"❌ Get HTTP Error: {response.status}")

async def main():
    """Run all tests"""
    print("🚀 Starting All Paragraphs API Tests...\n")
    
    # Test getting all paragraphs
    await test_all_paragraphs_api()
    
    # Test the full workflow
    await test_save_and_get()
    
    print(f"\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
