#!/usr/bin/env python3
"""
Database Migration Script for New Collections and Schema Changes

This script:
1. Creates new collections: vocab_collections, history_by_date, user_feedback
2. Adds collection_id field to existing learned_vocabs documents
3. Creates indexes for better performance

Run this script after updating the models and CRUD operations.
"""

import asyncio
import sys
import os
from datetime import datetime, timezone
from pymongo import IndexModel, ASCENDING, DESCENDING

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import connect_to_mongo, get_database, close_mongo_connection

async def create_index_safe(collection, index_model, index_name):
    """Safely create index, skipping if it already exists"""
    try:
        await collection.create_index(index_model.document["key"], **index_model.document.get("options", {}))
        return True
    except Exception as e:
        if "already exists" in str(e).lower() or "indexoptionsconflict" in str(e).lower():
            print(f"   ℹ️ Index {index_name} already exists, skipping...")
            return True
        else:
            print(f"   ❌ Failed to create index {index_name}: {e}")
            return False

async def create_indexes():
    """Create indexes for better query performance"""
    print("🔄 Creating database indexes...")
    
    db = get_database()
    
    # Indexes for vocab_collections
    print("  📁 vocab_collections:")
    vocab_collections = db.vocab_collections
    indexes_to_create = [
        (IndexModel([("name", ASCENDING)]), "name_asc"),
        (IndexModel([("created_at", DESCENDING)]), "created_at_desc")
    ]
    
    for index_model, name in indexes_to_create:
        success = await create_index_safe(vocab_collections, index_model, name)
        if success:
            print(f"   ✅ {name}")
    
    # Indexes for learned_vocabs (including new collection_id field)
    print("  📁 learned_vocabs:")
    learned_vocabs = db.learned_vocabs
    indexes_to_create = [
        (IndexModel([("user_id", ASCENDING), ("is_deleted", ASCENDING)]), "user_id_is_deleted"),
        (IndexModel([("collection_id", ASCENDING)]), "collection_id_asc"),
        (IndexModel([("user_id", ASCENDING), ("vocabs", ASCENDING)]), "user_id_vocabs"),
        (IndexModel([("created_at", DESCENDING)]), "created_at_desc"),
        (IndexModel([("usage_count", DESCENDING)]), "usage_count_desc")
    ]
    
    for index_model, name in indexes_to_create:
        success = await create_index_safe(learned_vocabs, index_model, name)
        if success:
            print(f"   ✅ {name}")
    
    # Indexes for history_by_date
    print("  📁 history_by_date:")
    history_by_date = db.history_by_date
    indexes_to_create = [
        (IndexModel([("vocab_id", ASCENDING), ("study_date", DESCENDING)]), "vocab_id_study_date"),
        (IndexModel([("study_date", DESCENDING)]), "study_date_desc"),
        (IndexModel([("vocab_id", ASCENDING)]), "vocab_id_asc")
    ]
    
    for index_model, name in indexes_to_create:
        success = await create_index_safe(history_by_date, index_model, name)
        if success:
            print(f"   ✅ {name}")
    
    # Indexes for user_feedback
    print("  📁 user_feedback:")
    user_feedback = db.user_feedback
    indexes_to_create = [
        (IndexModel([("email", ASCENDING)]), "email_asc"),
        (IndexModel([("created_at", DESCENDING)]), "created_at_desc")
    ]
    
    for index_model, name in indexes_to_create:
        success = await create_index_safe(user_feedback, index_model, name)
        if success:
            print(f"   ✅ {name}")
    
    print("✅ Database indexes processing completed")

async def add_collection_id_to_learned_vocabs():
    """Add collection_id field to existing learned_vocabs documents"""
    print("🔄 Adding collection_id field to learned_vocabs...")
    
    db = get_database()
    learned_vocabs = db.learned_vocabs
    
    # Count documents that don't have collection_id field
    count_without_field = await learned_vocabs.count_documents({
        "collection_id": {"$exists": False}
    })
    
    if count_without_field == 0:
        print("✅ All learned_vocabs documents already have collection_id field")
        return
    
    print(f"📊 Found {count_without_field} documents without collection_id field")
    
    # Add collection_id field (set to null for existing documents)
    result = await learned_vocabs.update_many(
        {"collection_id": {"$exists": False}},
        {"$set": {"collection_id": None}}
    )
    
    print(f"✅ Updated {result.modified_count} learned_vocabs documents with collection_id field")

async def create_default_vocab_collection():
    """Create a default 'General' vocabulary collection"""
    print("🔄 Creating default vocabulary collection...")
    
    db = get_database()
    vocab_collections = db.vocab_collections
    
    # Check if 'General' collection already exists
    existing = await vocab_collections.find_one({"name": "General"})
    if existing:
        print("✅ Default 'General' collection already exists")
        return existing["_id"]
    
    # Create default collection
    default_collection = {
        "name": "General",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    result = await vocab_collections.insert_one(default_collection)
    print(f"✅ Created default 'General' collection with ID: {result.inserted_id}")
    return result.inserted_id

async def validate_collections():
    """Validate that all collections exist and have expected structure"""
    print("🔄 Validating database collections...")
    
    db = get_database()
    
    # Check collections exist
    collections = await db.list_collection_names()
    expected_collections = [
        "users", "refresh_tokens", "input_history", "saved_paragraphs",
        "learned_vocabs", "vocab_collections", "history_by_date", "user_feedback"
    ]
    
    missing_collections = []
    for collection_name in expected_collections:
        if collection_name not in collections:
            missing_collections.append(collection_name)
        else:
            print(f"✅ Collection '{collection_name}' exists")
    
    if missing_collections:
        print(f"❌ Missing collections: {missing_collections}")
        return False
    
    # Validate learned_vocabs has collection_id field
    learned_vocabs = db.learned_vocabs
    sample_with_field = await learned_vocabs.find_one({"collection_id": {"$exists": True}})
    if sample_with_field:
        print("✅ learned_vocabs collection has collection_id field")
    else:
        print("❌ learned_vocabs collection missing collection_id field")
        return False
    
    print("✅ All database collections validated successfully")
    return True

async def show_migration_summary():
    """Show summary of migration results"""
    print("\n" + "="*60)
    print("📋 MIGRATION SUMMARY")
    print("="*60)
    
    db = get_database()
    
    # Count documents in each collection
    collections_info = [
        ("users", "users"),
        ("refresh_tokens", "refresh_tokens"),
        ("input_history", "input_history"),
        ("saved_paragraphs", "saved_paragraphs"),
        ("learned_vocabs", "learned_vocabs"),
        ("vocab_collections", "vocab_collections"),
        ("history_by_date", "history_by_date"),
        ("user_feedback", "user_feedback")
    ]
    
    for display_name, collection_name in collections_info:
        try:
            count = await db[collection_name].count_documents({})
            print(f"📊 {display_name}: {count} documents")
        except Exception as e:
            print(f"❌ {display_name}: Error counting documents - {e}")
    
    print("\n🎉 Database migration completed successfully!")
    print("\nNext steps:")
    print("1. Update your API routes to use the new collections")
    print("2. Test the new functionality")
    print("3. Consider creating sample vocab collections for users")

async def main():
    """Run the complete database migration"""
    print("🚀 Starting Database Schema Migration")
    print("="*60)
    
    try:
        # Initialize database connection
        print("🔄 Connecting to database...")
        await connect_to_mongo()
        print("✅ Database connected successfully")
        
        # Step 1: Add collection_id field to learned_vocabs
        await add_collection_id_to_learned_vocabs()
        
        # Step 2: Create default vocabulary collection
        await create_default_vocab_collection()
        
        # Step 3: Create database indexes
        await create_indexes()
        
        # Step 4: Validate collections
        validation_success = await validate_collections()
        
        # Step 5: Show summary
        await show_migration_summary()
        
        if validation_success:
            print("\n✅ Migration completed successfully!")
            return 0
        else:
            print("\n❌ Migration completed with errors. Please check the validation results.")
            return 1
            
    except Exception as e:
        print(f"\n❌ Migration failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Close database connection
        print("🔄 Closing database connection...")
        await close_mongo_connection()
        print("✅ Database connection closed")

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)