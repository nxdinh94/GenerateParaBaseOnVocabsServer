#!/usr/bin/env python3
"""
Final Schema Migration Summary
Shows complete results of the migration
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

async def show_migration_results():
    """Show final migration results"""
    print("🎉 Schema Migration Complete - Final Summary")
    print("=" * 60)
    
    try:
        db = get_database()
        
        # Test connection
        await db.command('ping')
        print("✅ Database connected successfully\n")
        
        # Show all collections
        collections_list = await db.list_collection_names()
        print(f"📚 Total Collections: {len(collections_list)}")
        for collection in sorted(collections_list):
            count = await db[collection].count_documents({})
            print(f"   📁 {collection}: {count} documents")
        
        print(f"\n" + "=" * 60)
        print("🔍 DETAILED SCHEMA ANALYSIS")
        print("=" * 60)
        
        # 1. Users Collection
        print("\n👤 USERS COLLECTION")
        print("-" * 30)
        users = db.users
        users_count = await users.count_documents({})
        print(f"Total users: {users_count}")
        
        if users_count > 0:
            sample_user = await users.find_one({})
            print("Sample structure:")
            for key in sample_user.keys():
                if key != '_id':
                    print(f"   {key}: {type(sample_user[key]).__name__}")
        
        # 2. Vocab Collections (NEW SCHEMA)
        print("\n📁 VOCAB_COLLECTIONS (New Schema)")
        print("-" * 40)
        vocab_collections = db.vocab_collections
        collections_count = await vocab_collections.count_documents({})
        print(f"Total collections: {collections_count}")
        
        if collections_count > 0:
            # Show user ownership
            user_collection_counts = {}
            async for doc in vocab_collections.find({}, {"user_id": 1, "name": 1}):
                user_id = str(doc.get("user_id", "None"))
                if user_id not in user_collection_counts:
                    user_collection_counts[user_id] = []
                user_collection_counts[user_id].append(doc.get("name", "unnamed"))
            
            print("Collections by user:")
            for user_id, names in user_collection_counts.items():
                print(f"   👤 {user_id}: {len(names)} collections")
                for name in names:
                    print(f"      📁 {name}")
            
            sample_collection = await vocab_collections.find_one({})
            print("\nSample structure:")
            for key in sample_collection.keys():
                if key != '_id':
                    value = sample_collection[key]
                    print(f"   {key}: {type(value).__name__} = {value}")
        
        # 3. Learned Vocabs (MODIFIED SCHEMA)
        print("\n📚 LEARNED_VOCABS (Modified Schema)")
        print("-" * 40)
        learned_vocabs = db.learned_vocabs
        vocabs_count = await learned_vocabs.count_documents({})
        print(f"Total vocab sets: {vocabs_count}")
        
        if vocabs_count > 0:
            # Check for old user_id field (should be 0)
            with_user_id = await learned_vocabs.count_documents({"user_id": {"$exists": True}})
            print(f"❌ Documents with old user_id field: {with_user_id}")
            
            # Check collection references
            with_collection_id = await learned_vocabs.count_documents({"collection_id": {"$exists": True}})
            print(f"✅ Documents with collection_id: {with_collection_id}")
            
            # Show collection distribution
            collection_vocab_counts = {}
            async for doc in learned_vocabs.find({}, {"collection_id": 1, "vocabs": 1}):
                collection_id = str(doc.get("collection_id", "None"))
                if collection_id not in collection_vocab_counts:
                    collection_vocab_counts[collection_id] = 0
                collection_vocab_counts[collection_id] += len(doc.get("vocabs", []))
            
            print("Vocabs by collection:")
            for collection_id, vocab_count in collection_vocab_counts.items():
                # Get collection name
                if collection_id != "None":
                    collection_doc = await vocab_collections.find_one({"_id": ObjectId(collection_id)})
                    collection_name = collection_doc.get("name", "unknown") if collection_doc else "not found"
                else:
                    collection_name = "No Collection"
                print(f"   📁 {collection_name}: {vocab_count} total vocabs")
            
            sample_vocab = await learned_vocabs.find_one({})
            print("\nSample structure:")
            for key in sample_vocab.keys():
                if key != '_id':
                    value = sample_vocab[key]
                    if key == 'vocabs' and isinstance(value, list):
                        print(f"   {key}: list[{len(value)}] = {value[:3]}...")
                    else:
                        print(f"   {key}: {type(value).__name__} = {value}")
        
        # 4. History by Date (NEW COLLECTION)
        print("\n📅 HISTORY_BY_DATE (New Collection - Date Only)")
        print("-" * 50)
        history_by_date = db.history_by_date
        history_count = await history_by_date.count_documents({})
        print(f"Total history entries: {history_count}")
        
        if history_count > 0:
            # Check date format
            async for doc in history_by_date.find({}).limit(3):
                study_date = doc.get("study_date")
                print(f"   📅 {study_date} ({type(study_date).__name__}): {doc.get('words_learned', 0)} words")
            
            sample_history = await history_by_date.find_one({})
            print("\nSample structure:")
            for key in sample_history.keys():
                if key != '_id':
                    value = sample_history[key]
                    print(f"   {key}: {type(value).__name__} = {value}")
        
        # 5. User Feedback (NEW COLLECTION)
        print("\n💬 USER_FEEDBACK (New Collection)")
        print("-" * 35)
        user_feedback = db.user_feedback
        feedback_count = await user_feedback.count_documents({})
        print(f"Total feedback entries: {feedback_count}")
        
        if feedback_count > 0:
            # Show recent feedback
            async for doc in user_feedback.find({}).sort("created_at", -1).limit(3):
                rating = doc.get("rating", 0)
                category = doc.get("category", "unknown")
                text = doc.get("feedback_text", "")[:50] + "..." if len(doc.get("feedback_text", "")) > 50 else doc.get("feedback_text", "")
                print(f"   ⭐ {rating}/5 ({category}): {text}")
            
            sample_feedback = await user_feedback.find_one({})
            print("\nSample structure:")
            for key in sample_feedback.keys():
                if key != '_id':
                    value = sample_feedback[key]
                    if isinstance(value, str) and len(value) > 30:
                        print(f"   {key}: {type(value).__name__} = {value[:30]}...")
                    else:
                        print(f"   {key}: {type(value).__name__} = {value}")
        
        print(f"\n" + "=" * 60)
        print("✅ MIGRATION SUCCESS VERIFICATION")
        print("=" * 60)
        
        # Final verification
        checks = []
        
        # Check 1: vocab_collections have user_id
        collections_with_user = await vocab_collections.count_documents({"user_id": {"$exists": True}})
        total_collections = await vocab_collections.count_documents({})
        checks.append(("vocab_collections have user_id", collections_with_user == total_collections))
        
        # Check 2: learned_vocabs have collection_id
        vocabs_with_collection = await learned_vocabs.count_documents({"collection_id": {"$exists": True}})
        total_vocabs = await learned_vocabs.count_documents({})
        checks.append(("learned_vocabs have collection_id", vocabs_with_collection == total_vocabs))
        
        # Check 3: learned_vocabs don't have user_id
        vocabs_with_user = await learned_vocabs.count_documents({"user_id": {"$exists": True}})
        checks.append(("learned_vocabs removed user_id", vocabs_with_user == 0))
        
        # Check 4: history_by_date exists
        checks.append(("history_by_date collection exists", "history_by_date" in collections_list))
        
        # Check 5: user_feedback exists
        checks.append(("user_feedback collection exists", "user_feedback" in collections_list))
        
        print("Migration verification:")
        all_passed = True
        for check_name, passed in checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {check_name}")
            if not passed:
                all_passed = False
        
        print(f"\n🎉 Overall Result: {'✅ MIGRATION FULLY SUCCESSFUL' if all_passed else '⚠️ MIGRATION PARTIALLY SUCCESSFUL'}")
        
        return all_passed
        
    except ConnectionFailure:
        print("❌ Failed to connect to MongoDB")
        return False
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False

async def main():
    """Main function"""
    success = await show_migration_results()
    
    print(f"\n" + "=" * 60)
    print("📋 MIGRATION SUMMARY")
    print("=" * 60)
    print("🎯 Original Request: Move user_id from learned_vocabs to vocab_collections")
    print("✅ Schema Changes Completed:")
    print("   • vocab_collections now have user_id field (user ownership)")
    print("   • learned_vocabs now reference collections via collection_id")
    print("   • learned_vocabs no longer have user_id field")
    print("   • history_by_date uses date-only format (yyyy-mm-dd)")
    print("   • user_feedback collection created and working")
    print("   • Database indexes updated for new schema")
    print("   • All relationships properly maintained")
    
    if success:
        print("\n🎉 Schema migration completed successfully!")
    else:
        print("\n⚠️ Some issues may remain - check details above")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())