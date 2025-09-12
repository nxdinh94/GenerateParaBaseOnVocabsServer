"""
Test API endpoints
"""
import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8000/api/v1"

async def test_api():
    """Test all API endpoints"""
    async with aiohttp.ClientSession() as session:
        print("🌐 Testing API endpoints...")
        
        # Test 1: Create user
        print("\n📝 Testing User Creation...")
        user_data = {
            "name": "Test User API",
            "email": "testapi@example.com",
            "password": "password123"
        }
        
        async with session.post(f"{BASE_URL}/db/users/", json=user_data) as response:
            if response.status == 201:
                user = await response.json()
                user_id = user["id"]
                print(f"✓ Created user: {user['name']} (ID: {user_id})")
            else:
                print(f"❌ Failed to create user: {response.status}")
                return
        
        # Test 2: Get user by ID
        print("\n🔍 Testing Get User by ID...")
        async with session.get(f"{BASE_URL}/db/users/{user_id}") as response:
            if response.status == 200:
                user = await response.json()
                print(f"✓ Retrieved user: {user['name']}")
            else:
                print(f"❌ Failed to get user: {response.status}")
        
        # Test 3: Create input history
        print("\n📚 Testing Input History Creation...")
        history_data = {
            "user_id": user_id,
            "words": ["hello", "world", "python", "api"]
        }
        
        async with session.post(f"{BASE_URL}/db/input-history/", json=history_data) as response:
            if response.status == 201:
                history = await response.json()
                history_id = history["id"]
                print(f"✓ Created input history with words: {history['words']}")
            else:
                print(f"❌ Failed to create input history: {response.status}")
                return
        
        # Test 4: Create saved paragraph
        print("\n📖 Testing Saved Paragraph Creation...")
        paragraph_data = {
            "input_history_id": history_id,
            "paragraph": "This is a test paragraph generated from the API containing hello, world, python, and api words."
        }
        
        async with session.post(f"{BASE_URL}/db/saved-paragraphs/", json=paragraph_data) as response:
            if response.status == 201:
                paragraph = await response.json()
                paragraph_id = paragraph["id"]
                print(f"✓ Created saved paragraph: {paragraph['paragraph'][:50]}...")
            else:
                print(f"❌ Failed to create saved paragraph: {response.status}")
                return
        
        # Test 5: Get user's input history
        print("\n📋 Testing Get User Input History...")
        async with session.get(f"{BASE_URL}/db/users/{user_id}/input-history") as response:
            if response.status == 200:
                histories = await response.json()
                print(f"✓ Retrieved {len(histories)} input histories for user")
            else:
                print(f"❌ Failed to get user input history: {response.status}")
        
        # Test 6: Get user's saved paragraphs
        print("\n📄 Testing Get User Saved Paragraphs...")
        async with session.get(f"{BASE_URL}/db/users/{user_id}/saved-paragraphs") as response:
            if response.status == 200:
                paragraphs = await response.json()
                print(f"✓ Retrieved {len(paragraphs)} saved paragraphs for user")
                if paragraphs:
                    print(f"   Sample paragraph: {paragraphs[0]['paragraph'][:50]}...")
            else:
                print(f"❌ Failed to get user saved paragraphs: {response.status}")
        
        # Test 7: Test paragraph generation (existing endpoint)
        print("\n🤖 Testing Paragraph Generation...")
        generate_data = {
            "vocabularies": ["hello", "world", "python"],
            "language": "English",
            "level": "intermediate",
            "length": "short",
            "tone": "friendly",
            "prompt": "Write about programming"
        }
        
        async with session.post(f"{BASE_URL}/generate-paragraph", json=generate_data) as response:
            if response.status == 200:
                result = await response.json()
                if result['status']:
                    print(f"✓ Generated paragraph: {result['result'][:100]}...")
                else:
                    print(f"❌ Failed to generate paragraph: {result['result']}")
            else:
                print(f"❌ Failed to call generate-paragraph: {response.status}")
        
        print("\n🗑️ Cleaning up...")
        
        # Clean up: Delete paragraph
        async with session.delete(f"{BASE_URL}/db/saved-paragraphs/{paragraph_id}") as response:
            if response.status in [200, 404]:
                print("✓ Cleaned up saved paragraph")
        
        # Clean up: Delete input history
        async with session.delete(f"{BASE_URL}/db/input-history/{history_id}") as response:
            if response.status in [200, 404]:
                print("✓ Cleaned up input history")
        
        # Clean up: Delete user
        async with session.delete(f"{BASE_URL}/db/users/{user_id}") as response:
            if response.status == 200:
                print("✓ Cleaned up user")
        
        print(f"\n✅ All API tests completed!")

if __name__ == "__main__":
    asyncio.run(test_api())
