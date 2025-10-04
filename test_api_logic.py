#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

async def test_api_directly():
    """Test the API endpoint logic directly without authentication"""
    try:
        from app.database.crud import get_learned_vocabs_crud, get_vocab_collection_crud
        from app.database.connection import connect_to_mongo
        
        print("🧪 Testing API logic directly...")
        
        # Initialize database connection
        await connect_to_mongo()
        
        # Initialize CRUD
        learned_vocabs_crud = get_learned_vocabs_crud()
        vocab_collection_crud = get_vocab_collection_crud()
        
        # Test collection ID from the error message
        test_collection_id = "68e0d33953f7b332a059d506"
        
        print(f"📝 Testing with collection_id: {test_collection_id}")
        
        # Simulate the API endpoint logic
        print("\n=== Simulating API Endpoint Logic ===")
        
        # 1. Verify collection exists and belongs to the user
        collection = await vocab_collection_crud.get_vocab_collection_by_id(test_collection_id)
        if not collection:
            print("❌ Collection not found")
            return False
            
        print(f"✅ Collection verified: {collection.name} (User: {collection.user_id})")
        
        # 2. Get learned vocabs entries for the specific collection
        learned_vocabs_entries = await learned_vocabs_crud.get_vocabs_by_collection(test_collection_id, limit=1000)
        
        print(f"✅ Retrieved {len(learned_vocabs_entries)} vocabulary entries")
        
        # 3. Format documents for response (simulate API formatting)
        documents = []
        for entry in learned_vocabs_entries:
            document = {
                "id": str(entry.id),
                "vocabs": entry.vocabs,
                "collection_id": str(entry.collection_id),
                "usage_count": getattr(entry, 'usage_count', 1),
                "created_at": entry.created_at.isoformat() if entry.created_at else None,
                "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,
                "deleted_at": entry.deleted_at.isoformat() if entry.deleted_at else None,
                "is_deleted": entry.is_deleted
            }
            documents.append(document)
        
        # 4. Apply sorting (simulate "frequent" sort)
        sort_method = "frequent"
        if sort_method == "frequent":
            documents.sort(key=lambda x: (x["usage_count"], x["created_at"] or "1900-01-01T00:00:00"), reverse=True)
        
        print(f"✅ Sorted documents by {sort_method}")
        
        # 5. Create response
        response = {
            "status": True,
            "collection_id": test_collection_id,
            "collection_name": collection.name,
            "total_documents": len(documents),
            "documents": documents,
            "sort": documents,  # Put the sorted data array in the sort field
            "sort_method": sort_method,
            "message": f"Found {len(documents)} vocabulary documents in collection '{collection.name}' sorted by {sort_method}"
        }
        
        print(f"\n=== API Response ===")
        print(f"Status: {response['status']}")
        print(f"Total documents: {response['total_documents']}")
        print(f"Sort method: {response['sort_method']}")
        print(f"Message: {response['message']}")
        
        if documents:
            print(f"\nFirst few documents:")
            for i, doc in enumerate(documents[:3]):
                print(f"  {i+1}. {doc['vocabs']} (Usage: {doc['usage_count']})")
        else:
            print("\nNo documents found in this collection")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_api_directly())
    if success:
        print("\n✅ API logic test completed successfully!")
    else:
        print("\n❌ API logic test failed!")