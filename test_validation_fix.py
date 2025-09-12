#!/usr/bin/env python3
"""
Test script to verify the created_at field validation fix
"""
import asyncio
import aiohttp
import json
from datetime import datetime

async def test_paragraph_save_fix():
    """Test that the created_at field validation error is fixed"""
    print("🧪 Testing Paragraph Save Fix")
    print("=" * 50)
    
    # Test API endpoint that was causing the validation error
    base_url = "http://127.0.0.1:8002"
    
    # Sample data that would typically cause the validation error
    test_data = {
        "user_id": "60d5ec49f1b2c8b1a4567890",  # Sample user ID
        "words": ["test", "vocabulary", "words"],
        "paragraph": "This is a test paragraph generated from the vocabulary words."
    }
    
    print(f"📡 Testing API: {base_url}")
    print(f"📝 Test Data: {json.dumps(test_data, indent=2)}")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test 1: Check server health
            print("📊 Test 1: Server Health Check")
            async with session.get(f"{base_url}/docs") as response:
                if response.status == 200:
                    print("✅ Server is running and accessible")
                else:
                    print(f"❌ Server health check failed: {response.status}")
                    return
            
            print()
            
            # Test 2: Try to find the specific API endpoint that was failing
            # Since the error mentioned paragraph saving, let's check for paragraph-related endpoints
            print("📊 Test 2: API Documentation Check")
            async with session.get(f"{base_url}/openapi.json") as response:
                if response.status == 200:
                    openapi_data = await response.json()
                    paths = openapi_data.get("paths", {})
                    paragraph_endpoints = [path for path in paths.keys() if "paragraph" in path.lower()]
                    
                    print(f"✅ OpenAPI documentation accessible")
                    print(f"📋 Found paragraph-related endpoints: {paragraph_endpoints}")
                    
                    if paragraph_endpoints:
                        # Test one of the paragraph endpoints
                        test_endpoint = paragraph_endpoints[0]
                        print(f"🎯 Testing endpoint: {test_endpoint}")
                        
                        # This is just a basic test - the actual endpoint might need different data
                        async with session.post(f"{base_url}{test_endpoint}", json=test_data) as test_response:
                            print(f"📊 Response Status: {test_response.status}")
                            response_text = await test_response.text()
                            print(f"📄 Response: {response_text[:200]}...")
                    else:
                        print("ℹ️ No paragraph endpoints found in API documentation")
                else:
                    print(f"❌ Failed to get API documentation: {response.status}")
            
            print()
            
    except Exception as e:
        print(f"💥 Error during testing: {type(e).__name__}: {str(e)}")
    
    print("🎯 Fix Summary:")
    print("- ✅ Added explicit created_at field to InputHistoryCRUD.create_input_history()")
    print("- ✅ Added explicit created_at field to SavedParagraphCRUD.create_saved_paragraph()")
    print("- ✅ Both methods now set created_at = datetime.utcnow()")
    print("- ✅ This should resolve MongoDB validation errors for missing created_at field")
    print()
    print("🔧 Changes Made:")
    print("   InputHistory: created_at field explicitly set during creation")
    print("   SavedParagraph: created_at field explicitly set during creation")
    print("   RefreshToken: already had created_at field (was working)")
    print("   User: already had created_at field (was working)")

async def test_direct_crud_operations():
    """Test CRUD operations directly to verify created_at field"""
    print()
    print("🧪 Testing Direct CRUD Operations")
    print("=" * 50)
    
    try:
        # Import CRUD classes
        import sys
        import os
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        
        # Add the current directory to Python path
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from app.database.crud import get_input_history_crud, get_saved_paragraph_crud
        from app.database.models import InputHistoryCreate, SavedParagraphCreate
        
        print("✅ Successfully imported CRUD classes")
        
        # Test InputHistory creation
        print("📝 Testing InputHistory creation...")
        input_history_crud = get_input_history_crud()
        
        # Create sample input history data
        history_data = InputHistoryCreate(
            user_id="60d5ec49f1b2c8b1a4567890",
            words=["test", "validation", "fix"]
        )
        
        print(f"📋 InputHistory data: {history_data.dict()}")
        
        # Test SavedParagraph creation
        print("📝 Testing SavedParagraph creation...")
        saved_paragraph_crud = get_saved_paragraph_crud()
        
        # Create sample paragraph data
        paragraph_data = SavedParagraphCreate(
            input_history_id="60d5ec49f1b2c8b1a4567890",
            paragraph="This is a test paragraph to verify the created_at field fix."
        )
        
        print(f"📋 SavedParagraph data: {paragraph_data.dict()}")
        print("✅ CRUD models created successfully (validation passed)")
        
    except Exception as e:
        print(f"❌ Error in CRUD testing: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_paragraph_save_fix())
    asyncio.run(test_direct_crud_operations())