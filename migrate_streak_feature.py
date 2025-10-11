"""
Database migration script for Streak feature
Creates indexes and migrates existing users
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "english_learning")

async def create_streak_indexes():
    """Create indexes for the streak collection"""
    print("Creating indexes for streak collection...")
    
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    streak_collection = db["streak"]
    
    # Create compound unique index on user_id and learned_date
    await streak_collection.create_index(
        [("user_id", 1), ("learned_date", 1)],
        unique=True,
        name="user_date_unique_idx"
    )
    print("✅ Created compound unique index on (user_id, learned_date)")
    
    # Create index on user_id for querying user's streaks
    await streak_collection.create_index(
        [("user_id", 1)],
        name="user_id_idx"
    )
    print("✅ Created index on user_id")
    
    # Create index on learned_date for date range queries
    await streak_collection.create_index(
        [("learned_date", 1)],
        name="learned_date_idx"
    )
    print("✅ Created index on learned_date")
    
    client.close()

async def migrate_users_selected_collection():
    """
    Migrate existing users to have selected_collection_id
    Sets it to their first vocabulary collection (or creates a default one)
    """
    print("\nMigrating users to add selected_collection_id...")
    
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    users_collection = db["users"]
    vocab_collections = db["vocab_collections"]
    
    # Find users without selected_collection_id
    users_cursor = users_collection.find({
        "$or": [
            {"selected_collection_id": {"$exists": False}},
            {"selected_collection_id": None}
        ]
    })
    
    users = await users_cursor.to_list(length=None)
    print(f"Found {len(users)} users to migrate")
    
    migrated_count = 0
    created_collections = 0
    
    for user in users:
        user_id = user["_id"]
        
        # Find user's first vocabulary collection
        collection = await vocab_collections.find_one({"user_id": user_id})
        
        if collection:
            # User has a collection, use it
            await users_collection.update_one(
                {"_id": user_id},
                {"$set": {"selected_collection_id": str(collection["_id"])}}
            )
            print(f"✅ Set selected_collection_id for user {user.get('email', user_id)}")
            migrated_count += 1
        else:
            # User has no collections, create a default one
            from datetime import datetime
            default_collection = {
                "name": "Default",
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            result = await vocab_collections.insert_one(default_collection)
            
            # Set selected_collection_id to the new collection
            await users_collection.update_one(
                {"_id": user_id},
                {"$set": {"selected_collection_id": str(result.inserted_id)}}
            )
            print(f"✅ Created default collection and set selected_collection_id for user {user.get('email', user_id)}")
            created_collections += 1
            migrated_count += 1
    
    print(f"\n📊 Migration Summary:")
    print(f"   Total users migrated: {migrated_count}")
    print(f"   New collections created: {created_collections}")
    
    client.close()

async def verify_migration():
    """Verify that migration was successful"""
    print("\nVerifying migration...")
    
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    users_collection = db["users"]
    streak_collection = db["streak"]
    
    # Check users with selected_collection_id
    total_users = await users_collection.count_documents({})
    users_with_collection = await users_collection.count_documents({
        "selected_collection_id": {"$exists": True, "$ne": None}
    })
    
    print(f"✅ Users with selected_collection_id: {users_with_collection}/{total_users}")
    
    # Check streak indexes
    indexes = await streak_collection.index_information()
    print(f"\n✅ Streak collection indexes:")
    for index_name, index_info in indexes.items():
        print(f"   - {index_name}: {index_info.get('key', [])}")
    
    # Check if compound unique index exists
    has_unique_index = any(
        'unique' in info and info['unique'] 
        for info in indexes.values()
    )
    
    if has_unique_index:
        print(f"✅ Unique index on (user_id, learned_date) verified")
    else:
        print(f"⚠️  Warning: Unique index not found")
    
    client.close()

async def main():
    """Run all migrations"""
    print("=" * 60)
    print("STREAK FEATURE MIGRATION SCRIPT")
    print("=" * 60)
    print(f"\nDatabase: {DATABASE_NAME}")
    print(f"MongoDB URL: {MONGODB_URL}\n")
    
    try:
        # Create indexes
        await create_streak_indexes()
        
        # Migrate users
        await migrate_users_selected_collection()
        
        # Verify migration
        await verify_migration()
        
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR during migration: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
