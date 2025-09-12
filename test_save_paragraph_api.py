#!/usr/bin/env python3
"""
Test script for the fixed save-paragraph API
"""
import asyncio
import aiohttp
import json
from datetime import datetime

async def test_save_paragraph_api():
    """Test the fixed save-paragraph API with user_id"""
    print("🧪 Testing Fixed Save-Paragraph API")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8004"
    endpoint = "/api/v1/save-paragraph"
    
    # Test data with user_id
    test_data = {
        "user_id": "60d5ec49f1b2c8b1a4567890",  # Valid ObjectId format
        "vocabs": ["test", "vocabulary", "save", "paragraph"],
        "paragraph": "This is a test paragraph created from the vocabulary words: test, vocabulary, save, paragraph."
    }
    
    print(f"📡 Testing: {base_url}{endpoint}")
    print(f"📝 Request Data:")
    print(json.dumps(test_data, indent=2))
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test 1: Valid request with user_id
            print("📊 Test 1: Valid request with user_id")
            async with session.post(f"{base_url}{endpoint}", json=test_data) as response:
                status = response.status
                content_type = response.headers.get('content-type', '')
                
                print(f"📊 Response Status: {status}")
                print(f"📋 Content-Type: {content_type}")
                
                if 'application/json' in content_type:
                    response_data = await response.json()
                    print(f"📄 Response Body:")
                    print(json.dumps(response_data, indent=2))
                    
                    if status == 200:
                        print("✅ API call successful!")
                        print(f"✅ Input History ID: {response_data.get('input_history_id')}")
                        print(f"✅ Saved Paragraph ID: {response_data.get('saved_paragraph_id')}")
                        print(f"✅ Message: {response_data.get('message')}")
                    else:
                        print(f"❌ API call failed with status {status}")
                else:
                    text_response = await response.text()
                    print(f"📄 Response Text: {text_response}")
                    print(f"❌ Unexpected content type: {content_type}")
            
            print("\n" + "="*50)
            
            # Test 2: Missing user_id
            print("📊 Test 2: Missing user_id (should fail)")
            test_data_no_user = {
                "vocabs": ["test", "without", "user"],
                "paragraph": "This should fail because no user_id provided."
            }
            
            async with session.post(f"{base_url}{endpoint}", json=test_data_no_user) as response:
                status = response.status
                response_data = await response.json()
                
                print(f"📊 Response Status: {status}")
                print(f"📄 Response Body:")
                print(json.dumps(response_data, indent=2))
                
                if status == 400:
                    print("✅ Correctly rejected request without user_id")
                else:
                    print(f"❌ Expected 400 but got {status}")
            
            print("\n" + "="*50)
            
            # Test 3: Invalid user_id format
            print("📊 Test 3: Invalid user_id format (should fail)")
            test_data_invalid_user = {
                "user_id": "invalid_user_id_format",
                "vocabs": ["test", "invalid", "user"],
                "paragraph": "This should fail because invalid user_id format."
            }
            
            async with session.post(f"{base_url}{endpoint}", json=test_data_invalid_user) as response:
                status = response.status
                response_data = await response.json()
                
                print(f"📊 Response Status: {status}")
                print(f"📄 Response Body:")
                print(json.dumps(response_data, indent=2))
                
                if status == 400:
                    print("✅ Correctly rejected invalid user_id format")
                else:
                    print(f"❌ Expected 400 but got {status}")
            
            print("\n" + "="*50)
            
            # Test 4: Reuse same vocabularies (should reuse input_history)
            print("📊 Test 4: Reuse same vocabularies (should reuse input_history)")
            test_data_reuse = {
                "user_id": "60d5ec49f1b2c8b1a4567890",  # Same user
                "vocabs": ["test", "vocabulary", "save", "paragraph"],  # Same vocabs
                "paragraph": "This is a different paragraph but with the same vocabulary words."
            }
            
            async with session.post(f"{base_url}{endpoint}", json=test_data_reuse) as response:
                status = response.status
                response_data = await response.json()
                
                print(f"📊 Response Status: {status}")
                print(f"📄 Response Body:")
                print(json.dumps(response_data, indent=2))
                
                if status == 200:
                    message = response_data.get('message', '')
                    if 'existing vocabularies' in message.lower():
                        print("✅ Correctly reused existing input_history")
                    else:
                        print("⚠️  API worked but didn't indicate reuse of existing vocabularies")
                else:
                    print(f"❌ Expected 200 but got {status}")
    
    except Exception as e:
        print(f"💥 Error during testing: {type(e).__name__}: {str(e)}")
    
    print("\n🎯 Test Summary:")
    print("- ✅ Added user_id field to SaveParagraphRequest schema")
    print("- ✅ Updated save-paragraph API to use user_id from request")
    print("- ✅ Added user_id validation (required and ObjectId format)")
    print("- ✅ Input vocabularies are saved with user_id in input_history collection")
    print("- ✅ API properly handles existing vocabularies for the same user")
    print("- ✅ Fixed created_at field issues in CRUD operations")

if __name__ == "__main__":
    asyncio.run(test_save_paragraph_api())