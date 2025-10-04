#!/usr/bin/env python3
"""
Test script for new MongoDB schema functionality

This script tests:
1. Vocabulary collections CRUD operations
2. History by date tracking
3. User feedback functionality
4. Updated learned_vocabs with collection_id
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import connect_to_mongo, close_mongo_connection
from app.database.crud import (
    get_vocab_collection_crud, 
    get_history_by_date_crud,
    get_user_feedback_crud,
    get_learned_vocabs_crud
)
from app.database.models import (
    VocabCollectionCreate,
    HistoryByDateCreate, 
    UserFeedbackCreate,
    LearnedVocabsCreateInternal
)
from datetime import datetime, timezone

async def test_vocab_collections():
    """Test vocabulary collections functionality"""
    print("🧪 Testing Vocabulary Collections...")
    
    vocab_collection_crud = get_vocab_collection_crud()
    
    # Create test collection
    collection_data = VocabCollectionCreate(name="Test Collection")
    collection = await vocab_collection_crud.create_vocab_collection(collection_data)
    print(f"✅ Created collection: {collection.name} (ID: {collection.id})")
    
    # Get all collections
    collections = await vocab_collection_crud.get_all_vocab_collections()
    print(f"✅ Found {len(collections)} collections")
    
    # Update collection
    updated_collection = await vocab_collection_crud.update_vocab_collection(
        str(collection.id), "Updated Test Collection"
    )
    print(f"✅ Updated collection name: {updated_collection.name}")
    
    # Delete collection
    deleted = await vocab_collection_crud.delete_vocab_collection(str(collection.id))
    print(f"✅ Deleted collection: {deleted}")
    
    return True

async def test_learned_vocabs_with_collection():
    """Test learned vocabs with collection_id"""
    print("🧪 Testing Learned Vocabs with Collections...")
    
    vocab_collection_crud = get_vocab_collection_crud()
    learned_vocabs_crud = get_learned_vocabs_crud()
    
    # Create test collection
    collection_data = VocabCollectionCreate(name="Business English")
    collection = await vocab_collection_crud.create_vocab_collection(collection_data)
    print(f"✅ Created collection: {collection.name}")
    
    # Create learned vocabs with collection
    vocabs_data = LearnedVocabsCreateInternal(
        user_id="507f1f77bcf86cd799439011",  # Dummy user ID
        vocabs=["business", "strategy", "revenue"],
        collection_id=str(collection.id)
    )
    
    learned_vocabs = await learned_vocabs_crud.create_learned_vocabs(vocabs_data)
    print(f"✅ Created learned vocabs: {learned_vocabs.vocabs} in collection {learned_vocabs.collection_id}")
    
    # Clean up
    await vocab_collection_crud.delete_vocab_collection(str(collection.id))
    await learned_vocabs_crud.delete_learned_vocabs(str(learned_vocabs.id))
    
    return True

async def test_history_by_date():
    """Test history by date functionality"""
    print("🧪 Testing History by Date...")
    
    history_crud = get_history_by_date_crud()
    learned_vocabs_crud = get_learned_vocabs_crud()
    
    # Create a test vocab first
    vocabs_data = LearnedVocabsCreateInternal(
        user_id="507f1f77bcf86cd799439011",
        vocabs=["test", "vocabulary"]
    )
    learned_vocabs = await learned_vocabs_crud.create_learned_vocabs(vocabs_data)
    
    # Record study session (with date-only)
    study_date = datetime.now(timezone.utc)
    # Convert to date-only for testing
    date_only = study_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    history_data = HistoryByDateCreate(
        vocab_id=str(learned_vocabs.id),
        study_date=date_only
    )
    
    history = await history_crud.create_history_by_date(history_data)
    print(f"✅ Created history entry: {history.count} sessions on {history.study_date.strftime('%Y-%m-%d')}")
    
    # Increment study count for same date
    updated_history = await history_crud.increment_study_count(
        str(learned_vocabs.id), date_only
    )
    print(f"✅ Updated study count: {updated_history.count} sessions")
    
    # Get history for vocab
    vocab_history = await history_crud.get_history_by_vocab_id(str(learned_vocabs.id))
    print(f"✅ Found {len(vocab_history)} history entries for vocab")
    
    # Clean up
    await learned_vocabs_crud.delete_learned_vocabs(str(learned_vocabs.id))
    
    return True

async def test_user_feedback():
    """Test user feedback functionality"""
    print("🧪 Testing User Feedback...")
    
    feedback_crud = get_user_feedback_crud()
    
    # Create feedback
    feedback_data = UserFeedbackCreate(
        email="test@example.com",
        name="Test User",
        message="This is a test feedback message. The new collections feature is great!"
    )
    
    feedback = await feedback_crud.create_feedback(feedback_data)
    print(f"✅ Created feedback from: {feedback.email}")
    
    # Get all feedback
    all_feedback = await feedback_crud.get_all_feedback()
    print(f"✅ Found {len(all_feedback)} feedback entries")
    
    # Get feedback by email
    user_feedback = await feedback_crud.get_feedback_by_email("test@example.com")
    print(f"✅ Found {len(user_feedback)} feedback entries for user")
    
    # Clean up
    await feedback_crud.delete_feedback(str(feedback.id))
    print(f"✅ Deleted test feedback")
    
    return True

async def main():
    """Run all tests"""
    print("🚀 Starting MongoDB Schema Tests")
    print("="*60)
    
    try:
        # Initialize database connection
        await connect_to_mongo()
        print("✅ Database connected successfully\n")
        
        # Run tests
        tests = [
            test_vocab_collections(),
            test_learned_vocabs_with_collection(),
            test_history_by_date(),
            test_user_feedback()
        ]
        
        results = await asyncio.gather(*tests, return_exceptions=True)
        
        # Check results
        success_count = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Test {i+1} failed: {result}")
            elif result:
                success_count += 1
        
        print(f"\n📊 Test Results: {success_count}/{len(tests)} tests passed")
        
        if success_count == len(tests):
            print("🎉 All tests passed! New schema is working correctly.")
            return 0
        else:
            print("❌ Some tests failed. Please check the errors above.")
            return 1
            
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        await close_mongo_connection()
        print("✅ Database connection closed")

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)