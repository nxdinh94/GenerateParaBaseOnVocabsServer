#!/usr/bin/env python3
"""
Schema Migration Validation Script
Validates the user_id → collections migration
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import sys
import os
from bson import ObjectId

# Add the parent directory to sys.path to import from app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def get_database():
    """Get database connection"""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    return client.english_server_db

async def validate_migration():
    """Validate the migration results"""
    print("🔍 Validating Schema Migration Results")
    print("=" * 50)
    
    try:
        db = get_database()
        
        # Test connection
        await db.command('ping')
        print("✅ Database connected successfully")
        
        # Check vocab_collections
        vocab_collections = db.vocab_collections
        collections_count = await vocab_collections.count_documents({})
        print(f"\n📁 vocab_collections: {collections_count} documents")
        
        # Check collections without user_id
        no_user_id = await vocab_collections.count_documents({
            "$or": [
                {"user_id": {"$exists": False}},
                {"user_id": None}
            ]
        })
        
        if no_user_id > 0:
            print(f"⚠️ {no_user_id} collections missing user_id")
            # Show samples
            async for doc in vocab_collections.find({
                "$or": [
                    {"user_id": {"$exists": False}},
                    {"user_id": None}
                ]
            }).limit(3):
                print(f"   📄 {doc['_id']}: {doc.get('name', 'unnamed')}")
        else:
            print("✅ All collections have user_id")
        
        # Check learned_vocabs
        learned_vocabs = db.learned_vocabs
        vocabs_count = await learned_vocabs.count_documents({})
        print(f"\n📚 learned_vocabs: {vocabs_count} documents")
        
        # Check vocabs with user_id (should be 0)
        with_user_id = await learned_vocabs.count_documents({
            "user_id": {"$exists": True}
        })
        
        if with_user_id > 0:
            print(f"⚠️ {with_user_id} learned_vocabs still have user_id")
        else:
            print("✅ No learned_vocabs have user_id field")
        
        # Check vocabs without collection_id
        no_collection_id = await learned_vocabs.count_documents({
            "$or": [
                {"collection_id": {"$exists": False}},
                {"collection_id": None}
            ]
        })
        
        if no_collection_id > 0:
            print(f"⚠️ {no_collection_id} learned_vocabs missing collection_id")
            
            # Show samples
            print("   Sample documents without collection_id:")
            async for doc in learned_vocabs.find({
                "$or": [
                    {"collection_id": {"$exists": False}},
                    {"collection_id": None}
                ]
            }).limit(3):
                print(f"   📄 {doc['_id']}: {len(doc.get('vocabs', []))} vocabs")
        else:
            print("✅ All learned_vocabs have collection_id")
        
        # Check users collection
        users = db.users
        users_count = await users.count_documents({})
        print(f"\n👤 users: {users_count} documents")
        
        # Validate relationships
        print("\n🔗 Validating Relationships:")
        
        # Get all unique user_ids from collections
        collection_user_ids = set()
        async for doc in vocab_collections.find({}, {"user_id": 1}):
            if doc.get("user_id"):
                collection_user_ids.add(doc["user_id"])
        
        # Get all unique collection_ids from learned_vocabs
        vocab_collection_ids = set()
        async for doc in learned_vocabs.find({}, {"collection_id": 1}):
            if doc.get("collection_id"):
                vocab_collection_ids.add(doc["collection_id"])
        
        # Check if all collection_ids exist in vocab_collections
        existing_collection_ids = set()
        async for doc in vocab_collections.find({}, {"_id": 1}):
            existing_collection_ids.add(doc["_id"])
        
        orphaned_vocabs = vocab_collection_ids - existing_collection_ids
        if orphaned_vocabs:
            print(f"⚠️ {len(orphaned_vocabs)} learned_vocabs reference non-existent collections")
            for collection_id in list(orphaned_vocabs)[:3]:
                count = await learned_vocabs.count_documents({"collection_id": collection_id})
                print(f"   📄 {collection_id}: {count} vocabs")
        else:
            print("✅ All collection references are valid")
        
        # Check if users exist for all collection user_ids
        existing_user_ids = set()
        async for doc in users.find({}, {"_id": 1}):
            existing_user_ids.add(doc["_id"])
        
        orphaned_collections = collection_user_ids - existing_user_ids
        if orphaned_collections:
            print(f"⚠️ {len(orphaned_collections)} collections reference non-existent users")
        else:
            print("✅ All user references are valid")
        
        print(f"\n🎉 Validation completed!")
        
        if no_user_id == 0 and with_user_id == 0 and no_collection_id == 0 and len(orphaned_vocabs) == 0:
            print("✅ Migration is fully successful!")
            return True
        else:
            print("⚠️ Migration has some issues that need fixing")
            return False
            
    except ConnectionFailure:
        print("❌ Failed to connect to MongoDB")
        return False
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

async def main():
    """Main function"""
    success = await validate_migration()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())