#!/usr/bin/env python3
"""
Simple test for database connection
"""
import asyncio
import sys
import os

# Add the app directory to the path  
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_basic_database():
    """Test basic database connection"""
    print("🔍 Testing Basic Database Connection")
    print("=" * 60)
    
    try:
        from app.database.connection import get_database
        from app.core.config import settings
        
        print(f"📋 Database settings:")
        print(f"   MONGODB_URL: {settings.MONGODB_URL}")
        print(f"   MONGODB_DATABASE: {settings.MONGODB_DATABASE}")
        
        # Test database connection
        print("🔗 Testing database connection...")
        db = get_database()
        
        # Test a simple operation
        print("📊 Testing database operation...")
        collections = await db.list_collection_names()
        print(f"   ✅ Found {len(collections)} collections: {collections}")
        
        # Test the input_history collection specifically
        if "input_history" in collections:
            input_history_collection = db.input_history
            count = await input_history_collection.count_documents({})
            print(f"   📝 input_history collection: {count} documents")
        else:
            print(f"   ⚠️ input_history collection not found")
            
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

async def test_crud_without_data():
    """Test CRUD initialization without actual data operations"""
    print(f"\n🔍 Testing CRUD Initialization")
    print("=" * 60)
    
    try:
        from app.database.crud import get_input_history_crud
        
        print("🔧 Initializing InputHistoryCRUD...")
        crud = get_input_history_crud()
        print(f"   ✅ CRUD initialized: {type(crud).__name__}")
        
        # Check if collection exists
        collection_name = crud.collection.name
        print(f"   📂 Collection name: {collection_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ CRUD initialization failed: {e}")
        return False

async def test_object_id_operations():
    """Test ObjectId operations that might be causing issues"""
    print(f"\n🔍 Testing ObjectId Operations")
    print("=" * 60)
    
    try:
        from bson import ObjectId
        
        # Test ObjectId creation and validation
        test_id = "507f1f77bcf86cd799439011"
        print(f"📝 Test ID: {test_id}")
        
        # Test ObjectId validation
        is_valid = ObjectId.is_valid(test_id)
        print(f"   ✅ ObjectId.is_valid(): {is_valid}")
        
        if is_valid:
            obj_id = ObjectId(test_id)
            print(f"   ✅ ObjectId created: {obj_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ ObjectId operation failed: {e}")
        return False

async def main():
    print("🚀 Simple Database Connection Test")
    
    # Test ObjectId operations
    obj_id_ok = await test_object_id_operations()
    
    # Test database connection
    db_ok = await test_basic_database()
    
    # Test CRUD initialization
    crud_ok = await test_crud_without_data()
    
    print("\n" + "=" * 60)
    print("📊 Simple Test Results:")
    print(f"   ObjectId Operations: {'✅ PASS' if obj_id_ok else '❌ FAIL'}")
    print(f"   Database Connection: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"   CRUD Initialization: {'✅ PASS' if crud_ok else '❌ FAIL'}")
    
    if not db_ok:
        print("\n💡 Database connection issue might be causing 500 errors")
        print("🔧 Check MongoDB is running and connection settings are correct")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())