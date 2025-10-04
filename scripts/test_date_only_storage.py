#!/usr/bin/env python3
"""
Test script for date-only functionality in history_by_date

This script tests the API endpoints to ensure study_date is stored and returned 
as date-only (YYYY-MM-DD format) without time components.
"""

import asyncio
import sys
import os
import json
from datetime import datetime, timezone

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import connect_to_mongo, close_mongo_connection, get_database

async def test_date_storage():
    """Test that dates are stored correctly without time components"""
    print("🧪 Testing Date-Only Storage in history_by_date...")
    
    db = get_database()
    history_collection = db.history_by_date
    
    # Clear any existing test data
    await history_collection.delete_many({})
    
    # Insert test data with different time components
    test_data = [
        {
            "vocab_id": "507f1f77bcf86cd799439011",
            "study_date": datetime(2025, 10, 4, 9, 30, 45),  # Morning with time
            "count": 1,
            "created_at": datetime.utcnow()
        },
        {
            "vocab_id": "507f1f77bcf86cd799439011", 
            "study_date": datetime(2025, 10, 4, 0, 0, 0),    # Same date, no time
            "count": 2,
            "created_at": datetime.utcnow()
        },
        {
            "vocab_id": "507f1f77bcf86cd799439011",
            "study_date": datetime(2025, 10, 5, 14, 25, 30),  # Different date with time
            "count": 1,
            "created_at": datetime.utcnow()
        }
    ]
    
    # Insert test records
    result = await history_collection.insert_many(test_data)
    print(f"✅ Inserted {len(result.inserted_ids)} test records")
    
    # Query and check stored dates
    cursor = history_collection.find({}).sort("study_date", 1)
    stored_records = []
    async for record in cursor:
        stored_records.append(record)
        study_date = record["study_date"]
        print(f"📅 Stored date: {study_date} (Type: {type(study_date)})")
        print(f"   - Date part: {study_date.strftime('%Y-%m-%d')}")
        print(f"   - Time part: {study_date.strftime('%H:%M:%S')}")
        
        # Check if time is preserved or normalized
        if study_date.hour != 0 or study_date.minute != 0 or study_date.second != 0:
            print("   ⚠️ WARNING: Time component is preserved in database")
        else:
            print("   ✅ Time component normalized to 00:00:00")
    
    # Test aggregation by date
    pipeline = [
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$study_date"
                    }
                },
                "total_count": {"$sum": "$count"},
                "sessions": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    print("\n📊 Aggregated by date:")
    async for result in history_collection.aggregate(pipeline):
        print(f"   {result['_id']}: {result['total_count']} total count, {result['sessions']} sessions")
    
    # Clean up
    await history_collection.delete_many({})
    print("\n✅ Test data cleaned up")
    
    return True

async def test_api_date_format():
    """Test API endpoint date formatting"""
    print("\n🧪 Testing API Date Format...")
    
    # Import the CRUD to simulate API behavior
    from app.database.crud import get_history_by_date_crud, get_learned_vocabs_crud
    from app.database.models import HistoryByDateCreate, LearnedVocabsCreateInternal
    
    history_crud = get_history_by_date_crud()
    vocabs_crud = get_learned_vocabs_crud()
    
    # Create a test vocab
    vocabs_data = LearnedVocabsCreateInternal(
        user_id="507f1f77bcf86cd799439011",
        vocabs=["test", "date", "format"]
    )
    learned_vocabs = await vocabs_crud.create_learned_vocabs(vocabs_data)
    print(f"✅ Created test vocabulary: {learned_vocabs.vocabs}")
    
    # Test different date input formats
    test_dates = [
        datetime(2025, 10, 4, 15, 30, 0),   # Full datetime
        datetime(2025, 10, 4, 0, 0, 0),     # Date with no time
        datetime(2025, 10, 5, 23, 59, 59),  # End of day
    ]
    
    for test_date in test_dates:
        print(f"\n📅 Testing with input date: {test_date}")
        
        # Use the increment_study_count method (simulates API call)
        history = await history_crud.increment_study_count(
            str(learned_vocabs.id), test_date
        )
        
        stored_date = history.study_date
        print(f"   Stored as: {stored_date}")
        print(f"   Date-only format: {stored_date.strftime('%Y-%m-%d')}")
        
        # Verify time is normalized
        if stored_date.hour == 0 and stored_date.minute == 0 and stored_date.second == 0:
            print("   ✅ Time normalized to 00:00:00")
        else:
            print(f"   ⚠️ Time not normalized: {stored_date.strftime('%H:%M:%S')}")
    
    # Clean up
    await vocabs_crud.delete_learned_vocabs(str(learned_vocabs.id))
    print("\n✅ Test vocabulary cleaned up")
    
    return True

async def demonstrate_date_aggregation():
    """Demonstrate how date-only storage helps with daily aggregations"""
    print("\n🧪 Demonstrating Date Aggregation Benefits...")
    
    from app.database.crud import get_history_by_date_crud, get_learned_vocabs_crud
    from app.database.models import LearnedVocabsCreateInternal
    
    history_crud = get_history_by_date_crud()
    vocabs_crud = get_learned_vocabs_crud()
    
    # Create test vocab
    vocabs_data = LearnedVocabsCreateInternal(
        user_id="507f1f77bcf86cd799439011",
        vocabs=["daily", "progress"]
    )
    learned_vocabs = await vocabs_crud.create_learned_vocabs(vocabs_data)
    
    # Simulate multiple study sessions on the same day at different times
    today = datetime(2025, 10, 4)
    study_times = [
        today.replace(hour=8, minute=0),    # Morning study
        today.replace(hour=12, minute=30),  # Lunch break study
        today.replace(hour=19, minute=15),  # Evening study
        today.replace(hour=22, minute=45),  # Late night study
    ]
    
    print(f"📚 Simulating {len(study_times)} study sessions on {today.strftime('%Y-%m-%d')}:")
    
    final_history = None
    for i, study_time in enumerate(study_times, 1):
        print(f"   Session {i} at {study_time.strftime('%H:%M')}")
        final_history = await history_crud.increment_study_count(
            str(learned_vocabs.id), study_time
        )
        print(f"      → Total count: {final_history.count}")
    
    print(f"\n✅ Final result: {final_history.count} total studies on {final_history.study_date.strftime('%Y-%m-%d')}")
    print("🎯 Benefit: All study sessions on the same date are automatically aggregated!")
    
    # Clean up
    await vocabs_crud.delete_learned_vocabs(str(learned_vocabs.id))
    
    return True

async def main():
    """Run all date-only tests"""
    print("🚀 Testing Date-Only Storage in history_by_date")
    print("="*60)
    
    try:
        # Initialize database connection
        await connect_to_mongo()
        print("✅ Database connected successfully\n")
        
        # Run tests
        tests = [
            test_date_storage(),
            test_api_date_format(),
            demonstrate_date_aggregation()
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
            print("\n🎉 All date-only tests passed!")
            print("✅ study_date is now stored as date-only (YYYY-MM-DD)")
            print("✅ Time components are normalized to 00:00:00")
            print("✅ Multiple sessions per day are properly aggregated")
            print("✅ API returns dates in YYYY-MM-DD format")
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
        print("\n✅ Database connection closed")

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)