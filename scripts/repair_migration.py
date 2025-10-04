#!/usr/bin/env python3
"""
Schema Migration Repair Script
Fixes issues found after the user_id → collections migration
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import sys
import os
from bson import ObjectId
from datetime import datetime

# Add the parent directory to sys.path to import from app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def get_database():
    """Get database connection"""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    return client.english_server_db

async def repair_migration():
    """Repair the migration issues"""
    print("🔧 Repairing Schema Migration Issues")
    print("=" * 50)
    
    try:
        db = get_database()
        
        # Test connection
        await db.command('ping')
        print("✅ Database connected successfully")
        
        # Step 1: Fix vocab_collections without user_id
        print("\n🔧 Step 1: Fixing collections without user_id...")
        vocab_collections = db.vocab_collections
        
        # Get the first user to assign orphaned collections
        users = db.users
        first_user = await users.find_one({})
        
        if not first_user:
            print("❌ No users found in database")
            return False
        
        print(f"👤 Using user {first_user['_id']} for orphaned collections")
        
        # Update collections without user_id
        result = await vocab_collections.update_many(
            {
                "$or": [
                    {"user_id": {"$exists": False}},
                    {"user_id": None}
                ]
            },
            {
                "$set": {
                    "user_id": first_user["_id"],
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        print(f"✅ Fixed {result.modified_count} collections without user_id")
        
        # Step 2: Fix learned_vocabs without collection_id
        print("\n🔧 Step 2: Fixing learned_vocabs without collection_id...")
        learned_vocabs = db.learned_vocabs
        
        # Get or create a default collection for orphaned vocabs
        default_collection = await vocab_collections.find_one({
            "user_id": first_user["_id"],
            "name": "General"
        })
        
        if not default_collection:
            # Create default collection
            default_collection_data = {
                "name": "General",
                "user_id": first_user["_id"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await vocab_collections.insert_one(default_collection_data)
            default_collection_id = result.inserted_id
            print(f"📁 Created default collection: {default_collection_id}")
        else:
            default_collection_id = default_collection["_id"]
            print(f"📁 Using existing collection: {default_collection_id}")
        
        # Update learned_vocabs without collection_id
        result = await learned_vocabs.update_many(
            {
                "$or": [
                    {"collection_id": {"$exists": False}},
                    {"collection_id": None}
                ]
            },
            {
                "$set": {
                    "collection_id": default_collection_id,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        print(f"✅ Fixed {result.modified_count} learned_vocabs without collection_id")
        
        # Step 3: Validate the repair
        print("\n🔍 Step 3: Validating repair...")
        
        # Check collections
        no_user_id = await vocab_collections.count_documents({
            "$or": [
                {"user_id": {"$exists": False}},
                {"user_id": None}
            ]
        })
        
        # Check learned_vocabs
        no_collection_id = await learned_vocabs.count_documents({
            "$or": [
                {"collection_id": {"$exists": False}},
                {"collection_id": None}
            ]
        })
        
        if no_user_id == 0 and no_collection_id == 0:
            print("✅ All issues have been resolved!")
            
            # Show final statistics
            collections_count = await vocab_collections.count_documents({})
            vocabs_count = await learned_vocabs.count_documents({})
            users_count = await users.count_documents({})
            
            print(f"\n📊 Final Statistics:")
            print(f"   👤 Users: {users_count}")
            print(f"   📁 Collections: {collections_count}")
            print(f"   📚 Learned Vocabs: {vocabs_count}")
            
            return True
        else:
            print(f"⚠️ Still have issues: {no_user_id} collections, {no_collection_id} vocabs")
            return False
            
    except ConnectionFailure:
        print("❌ Failed to connect to MongoDB")
        return False
    except Exception as e:
        print(f"❌ Repair failed: {e}")
        return False

async def main():
    """Main function"""
    print("🚀 Starting Schema Migration Repair")
    success = await repair_migration()
    
    if success:
        print("\n🎉 Schema migration repair completed successfully!")
    else:
        print("\n❌ Schema migration repair failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())