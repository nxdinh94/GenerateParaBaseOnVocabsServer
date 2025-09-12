"""
Test get saved paragraphs API
"""
import asyncio
import aiohttp

BASE_URL = "http://localhost:8000/api/v1"

async def test_get_saved_paragraphs():
    """Test get saved paragraphs API"""
    async with aiohttp.ClientSession() as session:
        print("🔍 Testing Get Saved Paragraphs API...")
        
        try:
            async with session.get(f"{BASE_URL}/saved-paragraphs") as response:
                print(f"📊 Response Status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ API Response:")
                    print(f"   Status: {result['status']}")
                    print(f"   Total Count: {result['total_count']}")
                    
                    if result['paragraphs']:
                        print(f"   Paragraphs:")
                        for i, paragraph in enumerate(result['paragraphs'], 1):
                            print(f"     {i}. ID: {paragraph['id'][:8]}...")
                            print(f"        Vocabs: {paragraph['vocabs']}")
                            print(f"        Paragraph: {paragraph['paragraph'][:50]}...")
                            print(f"        Created: {paragraph['created_at']}")
                            print()
                    else:
                        print("   No paragraphs found")
                        
                else:
                    error_text = await response.text()
                    print(f"❌ Failed with status {response.status}")
                    print(f"   Error: {error_text}")
                    
        except Exception as e:
            print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    asyncio.run(test_get_saved_paragraphs())
