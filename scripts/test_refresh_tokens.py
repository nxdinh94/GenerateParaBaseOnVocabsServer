"""
Simple test for refresh_tokens collection
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.database.migrations import SchemaMigration

async def test_refresh_tokens():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DATABASE]
    
    try:
        migration = SchemaMigration(db)
        info = await migration.get_collection_info('refresh_tokens')
        
        print(f"🔍 refresh_tokens Collection Info:")
        print(f"   Exists: {info.get('exists')}")
        
        if info.get('exists'):
            print(f"   Document count: {info.get('document_count', 0)}")
            indexes = [idx['name'] for idx in info.get('indexes', [])]
            print(f"   Indexes: {indexes}")
            validation_status = "✓" if info.get('validation') else "✗"
            print(f"   Validation rules: {validation_status}")
            
            # Test the collection schema
            collection = db.refresh_tokens
            
            # Try to insert a test document to verify validation
            from bson import ObjectId
            from datetime import datetime
            
            test_doc = {
                "user_id": ObjectId(),
                "refresh_token": "test_token_123",
                "created_at": datetime.utcnow()
            }
            
            try:
                result = await collection.insert_one(test_doc)
                print(f"   ✅ Test insert successful: {result.inserted_id}")
                
                # Clean up test document
                await collection.delete_one({"_id": result.inserted_id})
                print(f"   🧹 Test document cleaned up")
                
            except Exception as e:
                print(f"   ❌ Test insert failed: {e}")
        else:
            print("   ❌ Collection does not exist")
            
    except Exception as e:
        print(f"Error testing collection: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_refresh_tokens())