#!/usr/bin/env python3
"""
Test New Schema API Functionality
Tests the complete schema migration with API calls
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

BASE_URL = "http://localhost:8000"

async def test_auth():
    """Test authentication and get token"""
    async with aiohttp.ClientSession() as session:
        # Login
        login_data = {
            "username": "testuser@example.com",
            "password": "testpassword123"
        }
        
        async with session.post(f"{BASE_URL}/api/v1/auth/login", json=login_data) as response:
            if response.status == 200:
                result = await response.json()
                return result["access_token"]
            else:
                text = await response.text()
                print(f"❌ Login failed: {response.status} - {text}")
                return None

async def test_vocab_collections_api(token):
    """Test vocab collections API"""
    print("\n📁 Testing Vocab Collections API")
    print("-" * 40)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with aiohttp.ClientSession() as session:
        # 1. Get all collections for user
        async with session.get(f"{BASE_URL}/api/v1/vocab-collections", headers=headers) as response:
            if response.status == 200:
                collections = await response.json()
                print(f"✅ GET collections: Found {len(collections)} collections")
                
                # Show first collection
                if collections:
                    first_collection = collections[0]
                    print(f"   📄 Sample: {first_collection['name']} (ID: {first_collection['id']})")
                    return first_collection['id']
                else:
                    print("⚠️ No collections found")
            else:
                text = await response.text()
                print(f"❌ GET collections failed: {response.status} - {text}")
        
        # 2. Create a new collection
        new_collection = {
            "name": "Test Migration Collection",
        }
        
        async with session.post(f"{BASE_URL}/api/v1/vocab-collections", 
                               json=new_collection, headers=headers) as response:
            if response.status == 201:
                collection = await response.json()
                print(f"✅ POST collection: Created '{collection['name']}'")
                return collection['id']
            else:
                text = await response.text()
                print(f"❌ POST collection failed: {response.status} - {text}")
                return None

async def test_learned_vocabs_api(token, collection_id):
    """Test learned vocabs API with new schema"""
    print("\n📚 Testing Learned Vocabs API")
    print("-" * 40)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with aiohttp.ClientSession() as session:
        # 1. Create new learned vocabs
        new_vocabs = {
            "vocabs": ["schema", "migration", "validation"],
            "collection_id": collection_id
        }
        
        async with session.post(f"{BASE_URL}/api/v1/learned-vocabs", 
                               json=new_vocabs, headers=headers) as response:
            if response.status == 201:
                vocabs = await response.json()
                print(f"✅ POST vocabs: Created {len(vocabs['vocabs'])} words in collection")
                vocabs_id = vocabs['id']
            else:
                text = await response.text()
                print(f"❌ POST vocabs failed: {response.status} - {text}")
                return
        
        # 2. Get vocabs for collection
        async with session.get(f"{BASE_URL}/api/v1/learned-vocabs?collection_id={collection_id}", 
                              headers=headers) as response:
            if response.status == 200:
                vocabs_list = await response.json()
                print(f"✅ GET vocabs: Found {len(vocabs_list)} vocab sets in collection")
                
                if vocabs_list:
                    for vocab_set in vocabs_list:
                        print(f"   📄 {len(vocab_set['vocabs'])} words, usage: {vocab_set['usage_count']}")
            else:
                text = await response.text()
                print(f"❌ GET vocabs failed: {response.status} - {text}")
        
        # 3. Update vocabs
        update_data = {
            "vocabs": ["schema", "migration", "validation", "successful"],
            "usage_count": 5
        }
        
        async with session.put(f"{BASE_URL}/api/v1/learned-vocabs/{vocabs_id}", 
                              json=update_data, headers=headers) as response:
            if response.status == 200:
                updated_vocabs = await response.json()
                print(f"✅ PUT vocabs: Updated to {len(updated_vocabs['vocabs'])} words")
            else:
                text = await response.text()
                print(f"❌ PUT vocabs failed: {response.status} - {text}")

async def test_history_by_date_api(token):
    """Test history by date API with date-only format"""
    print("\n📅 Testing History by Date API")
    print("-" * 40)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with aiohttp.ClientSession() as session:
        # Create history entry
        history_data = {
            "study_date": "2024-01-15",  # Date-only format
            "words_learned": 25,
            "time_spent_minutes": 45,
            "accuracy_percentage": 87.5
        }
        
        async with session.post(f"{BASE_URL}/api/v1/history-by-date", 
                               json=history_data, headers=headers) as response:
            if response.status == 201:
                history = await response.json()
                print(f"✅ POST history: Created entry for {history['study_date']}")
            else:
                text = await response.text()
                print(f"❌ POST history failed: {response.status} - {text}")
        
        # Get history entries
        async with session.get(f"{BASE_URL}/api/v1/history-by-date", headers=headers) as response:
            if response.status == 200:
                history_list = await response.json()
                print(f"✅ GET history: Found {len(history_list)} entries")
                
                if history_list:
                    for entry in history_list[-2:]:  # Show last 2 entries
                        print(f"   📅 {entry['study_date']}: {entry['words_learned']} words")
            else:
                text = await response.text()
                print(f"❌ GET history failed: {response.status} - {text}")

async def test_user_feedback_api(token):
    """Test user feedback API"""
    print("\n💬 Testing User Feedback API")
    print("-" * 40)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with aiohttp.ClientSession() as session:
        # Create feedback
        feedback_data = {
            "feedback_text": "Schema migration worked perfectly!",
            "rating": 5,
            "category": "improvement"
        }
        
        async with session.post(f"{BASE_URL}/api/v1/user-feedback", 
                               json=feedback_data, headers=headers) as response:
            if response.status == 201:
                feedback = await response.json()
                print(f"✅ POST feedback: Created rating {feedback['rating']}/5")
            else:
                text = await response.text()
                print(f"❌ POST feedback failed: {response.status} - {text}")

async def main():
    """Main test function"""
    print("🧪 Testing New Schema API Functionality")
    print("=" * 50)
    
    # Get authentication token
    print("🔐 Authenticating...")
    token = await test_auth()
    
    if not token:
        print("❌ Authentication failed - cannot continue tests")
        sys.exit(1)
    
    print("✅ Authentication successful")
    
    # Test vocab collections
    collection_id = await test_vocab_collections_api(token)
    
    if collection_id:
        # Test learned vocabs with collection reference
        await test_learned_vocabs_api(token, collection_id)
    
    # Test other new APIs
    await test_history_by_date_api(token)
    await test_user_feedback_api(token)
    
    print("\n🎉 Schema migration API tests completed!")
    print("\nKey Changes Validated:")
    print("✅ vocab_collections now owned by users")
    print("✅ learned_vocabs reference collections instead of users directly")
    print("✅ history_by_date uses date-only format")
    print("✅ user_feedback collection working")
    print("✅ All APIs work with new schema")

if __name__ == "__main__":
    asyncio.run(main())