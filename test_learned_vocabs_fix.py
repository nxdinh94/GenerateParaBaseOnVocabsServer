#!/usr/bin/env python3

import asyncio
import sys
import os
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

async def test_learned_vocabs_creation():
    """Test the create_learned_vocabs method directly"""
    try:
        from app.database.crud import get_learned_vocabs_crud, get_vocab_collection_crud
        from app.database.models import LearnedVocabsCreateInternal, VocabCollectionCreate
        from app.database.connection import connect_to_mongo
        
        print("🧪 Testing learned vocabs creation...")
        
        # Initialize database connection
        await connect_to_mongo()
        
        # Initialize CRUD
        learned_vocabs_crud = get_learned_vocabs_crud()
        vocab_collection_crud = get_vocab_collection_crud()
        
        # First, create a test collection or use existing one
        print("\n1. Getting/Creating test collection...")
        
        # Try to get existing collections
        collections = await vocab_collection_crud.get_all_vocab_collections(limit=5)
        
        if collections:
            test_collection = collections[0]  # Use first available collection
            print(f"✅ Using existing collection: {test_collection.name} (ID: {test_collection.id})")
        else:
            # Create a test collection
            print("Creating new test collection...")
            collection_data = VocabCollectionCreate(
                name="Test Collection",
                user_id="507f1f77bcf86cd799439011"  # Dummy user ID
            )
            test_collection = await vocab_collection_crud.create_vocab_collection(collection_data)
            print(f"✅ Created test collection: {test_collection.name} (ID: {test_collection.id})")
        
        # Test creating learned vocabs
        print("\n2. Testing create_learned_vocabs...")
        
        test_vocabs = ["hello", "world", "python", "fastapi"]
        
        vocabs_create_data = LearnedVocabsCreateInternal(
            vocabs=test_vocabs,
            collection_id=str(test_collection.id)
        )
        
        print(f"Creating learned vocabs: {test_vocabs}")
        print(f"Collection ID: {test_collection.id}")
        
        # This should now work without the user_id error
        learned_vocabs = await learned_vocabs_crud.create_learned_vocabs(vocabs_create_data)
        
        print(f"✅ Successfully created learned vocabs!")
        print(f"   ID: {learned_vocabs.id}")
        print(f"   Vocabs: {learned_vocabs.vocabs}")
        print(f"   Collection ID: {learned_vocabs.collection_id}")
        print(f"   Usage Count: {learned_vocabs.usage_count}")
        print(f"   Created At: {learned_vocabs.created_at}")
        
        # Test the find_by_exact_vocabs method (which is called by the API)
        print("\n3. Testing find_by_exact_vocabs...")
        existing_vocabs = await learned_vocabs_crud.find_by_exact_vocabs(str(test_collection.id), test_vocabs)
        
        if existing_vocabs:
            print(f"✅ Successfully found existing vocabs: {existing_vocabs.id}")
        else:
            print("❌ Could not find the vocabs we just created")
        
        # Clean up - delete the test entry
        print("\n4. Cleaning up...")
        deleted = await learned_vocabs_crud.delete_learned_vocabs(str(learned_vocabs.id))
        if deleted:
            print("✅ Test entry cleaned up successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_learned_vocabs_creation())
    if success:
        print("\n✅ Learned vocabs creation test completed successfully!")
        print("The API should now work without the 500 error.")
    else:
        print("\n❌ Test failed!")