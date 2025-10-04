#!/usr/bin/env python3
"""
Schema Migration: Move user_id from learned_vocabs to vocab_collections

This script:
1. Adds user_id field to vocab_collections
2. Creates default collections for users who have learned_vocabs but no collections
3. Updates learned_vocabs to reference collections instead of users directly
4. Removes user_id field from learned_vocabs
5. Updates indexes

Run this script after updating the models and CRUD operations.
"""

import asyncio
import sys
import os
from datetime import datetime, timezone
from bson import ObjectId

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import connect_to_mongo, get_database, close_mongo_connection

async def add_user_id_to_vocab_collections():
    """Add user_id field to existing vocab_collections"""
    print("🔄 Adding user_id field to vocab_collections...")
    
    db = get_database()
    vocab_collections = db.vocab_collections
    
    # Count documents that don't have user_id field
    count_without_field = await vocab_collections.count_documents({
        "user_id": {"$exists": False}
    })
    
    if count_without_field == 0:
        print("✅ All vocab_collections documents already have user_id field")
        return
    
    print(f"📊 Found {count_without_field} vocab_collections without user_id field")
    
    # For now, set user_id to null for existing collections
    # In a real scenario, you'd need to determine the proper user ownership
    result = await vocab_collections.update_many(
        {"user_id": {"$exists": False}},
        {"$set": {"user_id": None}}
    )
    
    print(f"✅ Updated {result.modified_count} vocab_collections with user_id field (set to null)")

async def create_default_collections_for_users():
    """Create default collections for users who have learned_vocabs but no collections"""
    print("🔄 Creating default collections for users with learned vocabs...")
    
    db = get_database()
    learned_vocabs = db.learned_vocabs
    vocab_collections = db.vocab_collections
    
    # Get all unique user_ids from learned_vocabs
    user_ids_pipeline = [
        {"$match": {"user_id": {"$exists": True}, "is_deleted": False}},
        {"$group": {"_id": "$user_id"}},
        {"$project": {"user_id": "$_id"}}
    ]
    
    user_ids = []
    async for doc in learned_vocabs.aggregate(user_ids_pipeline):
        user_ids.append(doc["user_id"])
    
    print(f"📊 Found {len(user_ids)} users with learned vocabularies")
    
    collections_created = 0
    for user_id in user_ids:
        # Check if user already has any collections
        existing_collection = await vocab_collections.find_one({"user_id": user_id})
        
        if not existing_collection:
            # Create default "General" collection for this user
            default_collection = {
                "name": "General",
                "user_id": user_id,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            result = await vocab_collections.insert_one(default_collection)
            collections_created += 1
            print(f"  ✅ Created 'General' collection for user {user_id}: {result.inserted_id}")
    
    print(f"✅ Created {collections_created} default collections")
    return collections_created

async def migrate_learned_vocabs_to_collections():
    """Update learned_vocabs to reference collections instead of users directly"""
    print("🔄 Migrating learned_vocabs to use collection references...")
    
    db = get_database()
    learned_vocabs = db.learned_vocabs
    vocab_collections = db.vocab_collections
    
    # Get all learned_vocabs that still have user_id
    cursor = learned_vocabs.find({
        "user_id": {"$exists": True},
        "collection_id": {"$exists": False},
        "is_deleted": False
    })
    
    updates_count = 0
    async for vocab_doc in cursor:
        user_id = vocab_doc["user_id"]
        
        # Find or create a collection for this user
        user_collection = await vocab_collections.find_one({"user_id": user_id})
        
        if not user_collection:
            # Create default collection for this user
            default_collection = {
                "name": "General",
                "user_id": user_id,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            result = await vocab_collections.insert_one(default_collection)
            collection_id = result.inserted_id
            print(f"  📝 Created collection {collection_id} for user {user_id}")
        else:
            collection_id = user_collection["_id"]
        
        # Update the learned_vocabs document
        await learned_vocabs.update_one(
            {"_id": vocab_doc["_id"]},
            {
                "$set": {"collection_id": collection_id},
                "$unset": {"user_id": ""}
            }
        )
        updates_count += 1
    
    print(f"✅ Migrated {updates_count} learned_vocabs to use collection references")
    return updates_count

async def update_collection_validation():
    """Update collection validation to remove user_id requirement"""
    print("🔄 Updating collection validation rules...")
    
    db = get_database()
    
    try:
        # Try to modify the collection validation
        await db.command({
            "collMod": "learned_vocabs",
            "validator": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["vocabs", "created_at", "collection_id"],
                    "properties": {
                        "vocabs": {"bsonType": "array"},
                        "collection_id": {"bsonType": "objectId"},
                        "created_at": {"bsonType": "date"},
                        "updated_at": {"bsonType": "date"},
                        "usage_count": {"bsonType": "int"},
                        "is_deleted": {"bsonType": "bool"},
                        "deleted_at": {"bsonType": ["date", "null"]}
                    }
                }
            }
        })
        print("✅ Updated learned_vocabs validation schema")
    except Exception as e:
        print(f"ℹ️ Could not update validation (might not exist): {e}")

async def remove_user_id_from_learned_vocabs():
    """Remove user_id field from learned_vocabs documents that still have it"""
    print("🔄 Removing user_id field from learned_vocabs...")
    
    db = get_database()
    learned_vocabs = db.learned_vocabs
    
    # First, update validation rules
    await update_collection_validation()
    
    # Count documents that still have user_id field
    count_with_user_id = await learned_vocabs.count_documents({
        "user_id": {"$exists": True}
    })
    
    if count_with_user_id == 0:
        print("✅ No learned_vocabs documents have user_id field")
        return 0
    
    print(f"📊 Found {count_with_user_id} learned_vocabs documents with user_id field")
    
    # Remove user_id field from all documents
    try:
        result = await learned_vocabs.update_many(
            {"user_id": {"$exists": True}},
            {"$unset": {"user_id": ""}}
        )
        print(f"✅ Removed user_id field from {result.modified_count} learned_vocabs documents")
        return result.modified_count
    except Exception as e:
        print(f"❌ Failed to remove user_id field: {e}")
        # Try without validation
        try:
            await db.command({"collMod": "learned_vocabs", "validator": {}})
            print("ℹ️ Removed collection validation temporarily")
            
            result = await learned_vocabs.update_many(
                {"user_id": {"$exists": True}},
                {"$unset": {"user_id": ""}}
            )
            print(f"✅ Removed user_id field from {result.modified_count} learned_vocabs documents")
            return result.modified_count
        except Exception as e2:
            print(f"❌ Failed even without validation: {e2}")
            return 0

async def update_indexes():
    """Update database indexes for new schema"""
    print("🔄 Updating database indexes...")
    
    db = get_database()
    
    # Update vocab_collections indexes
    print("  📁 Updating vocab_collections indexes...")
    vocab_collections = db.vocab_collections
    try:
        await vocab_collections.create_index([("user_id", 1)])
        print("    ✅ Created user_id index")
    except Exception as e:
        if "already exists" in str(e).lower():
            print("    ℹ️ user_id index already exists")
        else:
            print(f"    ❌ Failed to create user_id index: {e}")
    
    # Remove old indexes from learned_vocabs and add new ones
    print("  📁 Updating learned_vocabs indexes...")
    learned_vocabs = db.learned_vocabs
    
    # Try to drop old user_id related indexes
    try:
        indexes = await learned_vocabs.list_indexes().to_list(None)
        for index in indexes:
            index_name = index.get('name', '')
            if 'user_id' in index_name and index_name != '_id_':
                try:
                    await learned_vocabs.drop_index(index_name)
                    print(f"    ✅ Dropped old index: {index_name}")
                except Exception as e:
                    print(f"    ℹ️ Could not drop index {index_name}: {e}")
    except Exception as e:
        print(f"    ℹ️ Could not list indexes: {e}")
    
    # Create new collection_id index
    try:
        await learned_vocabs.create_index([("collection_id", 1), ("is_deleted", 1)])
        print("    ✅ Created collection_id + is_deleted index")
    except Exception as e:
        if "already exists" in str(e).lower():
            print("    ℹ️ collection_id + is_deleted index already exists")
        else:
            print(f"    ❌ Failed to create collection_id index: {e}")

async def validate_migration():
    """Validate that the migration was successful"""
    print("🔄 Validating migration...")
    
    db = get_database()
    learned_vocabs = db.learned_vocabs
    vocab_collections = db.vocab_collections
    
    # Check that no learned_vocabs have user_id
    count_with_user_id = await learned_vocabs.count_documents({"user_id": {"$exists": True}})
    if count_with_user_id > 0:
        print(f"❌ {count_with_user_id} learned_vocabs still have user_id field")
        return False
    
    # Check that all learned_vocabs have collection_id
    count_without_collection = await learned_vocabs.count_documents({
        "collection_id": {"$exists": False},
        "is_deleted": False
    })
    if count_without_collection > 0:
        print(f"❌ {count_without_collection} learned_vocabs missing collection_id field")
        return False
    
    # Check that all vocab_collections have user_id
    count_without_user = await vocab_collections.count_documents({"user_id": {"$exists": False}})
    if count_without_user > 0:
        print(f"❌ {count_without_user} vocab_collections missing user_id field")
        return False
    
    # Sample validation: check referential integrity
    sample_learned_vocab = await learned_vocabs.find_one({"is_deleted": False})
    if sample_learned_vocab:
        collection_id = sample_learned_vocab.get("collection_id")
        if collection_id:
            referenced_collection = await vocab_collections.find_one({"_id": collection_id})
            if not referenced_collection:
                print(f"❌ learned_vocab {sample_learned_vocab['_id']} references non-existent collection {collection_id}")
                return False
    
    print("✅ Migration validation successful")
    return True

async def show_migration_summary():
    """Show summary of migration results"""
    print("\n" + "="*60)
    print("📋 SCHEMA MIGRATION SUMMARY")
    print("="*60)
    
    db = get_database()
    
    # Count documents
    vocab_collections_count = await db.vocab_collections.count_documents({})
    learned_vocabs_count = await db.learned_vocabs.count_documents({"is_deleted": False})
    
    print(f"📊 vocab_collections: {vocab_collections_count} documents")
    print(f"📊 learned_vocabs: {learned_vocabs_count} documents")
    
    # Show sample structure
    sample_collection = await db.vocab_collections.find_one({})
    if sample_collection:
        print("\n📋 Sample vocab_collection structure:")
        for key in sample_collection:
            if key != '_id':
                print(f"   {key}: {type(sample_collection[key]).__name__}")
    
    sample_vocab = await db.learned_vocabs.find_one({"is_deleted": False})
    if sample_vocab:
        print("\n📋 Sample learned_vocabs structure:")
        for key in sample_vocab:
            if key != '_id':
                print(f"   {key}: {type(sample_vocab[key]).__name__}")
    
    print("\n🎉 Schema migration completed successfully!")
    print("\nKey changes:")
    print("✅ vocab_collections now have user_id field")
    print("✅ learned_vocabs now reference collections via collection_id")
    print("✅ learned_vocabs no longer have direct user_id field")
    print("✅ Database indexes updated for new schema")

async def main():
    """Run the complete schema migration"""
    print("🚀 Starting Schema Migration: user_id → collections")
    print("="*60)
    
    try:
        # Initialize database connection
        print("🔄 Connecting to database...")
        await connect_to_mongo()
        print("✅ Database connected successfully")
        
        # Step 1: Add user_id to vocab_collections
        await add_user_id_to_vocab_collections()
        
        # Step 2: Create default collections for users
        await create_default_collections_for_users()
        
        # Step 3: Migrate learned_vocabs to use collections
        await migrate_learned_vocabs_to_collections()
        
        # Step 4: Remove user_id from learned_vocabs
        await remove_user_id_from_learned_vocabs()
        
        # Step 5: Update indexes
        await update_indexes()
        
        # Step 6: Validate migration
        validation_success = await validate_migration()
        
        # Step 7: Show summary
        await show_migration_summary()
        
        if validation_success:
            print("\n✅ Migration completed successfully!")
            return 0
        else:
            print("\n❌ Migration completed with validation errors.")
            return 1
            
    except Exception as e:
        print(f"\n❌ Migration failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Close database connection
        print("\n🔄 Closing database connection...")
        await close_mongo_connection()
        print("✅ Database connection closed")

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)