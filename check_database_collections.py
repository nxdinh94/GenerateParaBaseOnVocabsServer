#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

async def check_collections_and_data():
    """Check what collections and vocab data exist in the database"""
    try:
        from app.database.crud import get_learned_vocabs_crud, get_vocab_collection_crud
        from app.database.connection import connect_to_mongo
        
        print("🔍 Checking database collections and vocab data...")
        
        # Initialize database connection
        await connect_to_mongo()
        
        # Initialize CRUD
        learned_vocabs_crud = get_learned_vocabs_crud()
        vocab_collection_crud = get_vocab_collection_crud()
        
        print("\n=== All Vocabulary Collections ===")
        collections = await vocab_collection_crud.get_all_vocab_collections(limit=20)
        
        if not collections:
            print("❌ No vocabulary collections found in database")
            return False
        
        for i, collection in enumerate(collections, 1):
            print(f"{i}. Collection: {collection.name}")
            print(f"   ID: {collection.id}")
            print(f"   User ID: {collection.user_id}")
            print(f"   Created: {collection.created_at}")
            
            # Check how many vocab entries are in this collection
            try:
                vocabs_entries = await learned_vocabs_crud.get_vocabs_by_collection(str(collection.id), limit=1000)
                print(f"   📚 Vocab entries: {len(vocabs_entries)}")
                
                if vocabs_entries:
                    # Show first few entries
                    for j, entry in enumerate(vocabs_entries[:3], 1):
                        usage_count = getattr(entry, 'usage_count', 1)
                        print(f"      {j}. {entry.vocabs} (Usage: {usage_count})")
                    if len(vocabs_entries) > 3:
                        print(f"      ... and {len(vocabs_entries) - 3} more entries")
                        
            except Exception as e:
                print(f"   ❌ Error getting vocab entries: {e}")
            
            print()  # Empty line for separation
        
        return True
        
    except Exception as e:
        print(f"❌ Check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(check_collections_and_data())
    if success:
        print("✅ Database check completed!")
    else:
        print("❌ Database check failed!")