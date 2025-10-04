#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

async def test_vocabs_by_collection():
    """Test the get_vocabs_by_collection method directly"""
    try:
        from app.database.crud import get_learned_vocabs_crud, get_vocab_collection_crud
        from app.database.connection import connect_to_mongo
        
        print("🧪 Testing get_vocabs_by_collection method...")
        
        # Initialize database connection
        await connect_to_mongo()
        
        # Initialize CRUD
        learned_vocabs_crud = get_learned_vocabs_crud()
        vocab_collection_crud = get_vocab_collection_crud()
        
        # Test collection ID from the error message
        test_collection_id = "68e0d33953f7b332a059d506"
        
        print(f"📝 Testing with collection_id: {test_collection_id}")
        
        # First check if the collection exists
        print("\n1. Checking if collection exists...")
        collection = await vocab_collection_crud.get_vocab_collection_by_id(test_collection_id)
        if collection:
            print(f"✅ Collection found: {collection.name} (User: {collection.user_id})")
        else:
            print(f"❌ Collection not found with ID: {test_collection_id}")
            return False
        
        # Test the new method
        print("\n2. Testing get_vocabs_by_collection...")
        try:
            vocabs_entries = await learned_vocabs_crud.get_vocabs_by_collection(test_collection_id, limit=1000)
            print(f"✅ Found {len(vocabs_entries)} vocabulary entries in collection")
            
            # Display first few entries
            for i, entry in enumerate(vocabs_entries[:3]):
                print(f"   Entry {i+1}: {entry.vocabs} (Usage: {getattr(entry, 'usage_count', 1)})")
            
            if len(vocabs_entries) > 3:
                print(f"   ... and {len(vocabs_entries) - 3} more entries")
                
            return True
            
        except Exception as e:
            print(f"❌ Error in get_vocabs_by_collection: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_vocabs_by_collection())
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")