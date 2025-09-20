#!/usr/bin/env python3
"""
Direct database test for learned_vocabs CRUD operations
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_learned_vocabs_crud():
    """Test the LearnedVocabsCRUD operations directly"""
    try:
        from app.database.crud import get_learned_vocabs_crud
        from app.database.models import LearnedVocabsCreateInternal
        from bson import ObjectId
        
        print("🧪 Testing LearnedVocabsCRUD operations...")
        
        # Initialize CRUD
        crud = get_learned_vocabs_crud()
        
        # Test data
        test_user_id = str(ObjectId())  # Generate a test user ID
        test_vocabs = ["hello", "world", "python", "fastapi"]
        
        print(f"📝 Test user ID: {test_user_id}")
        print(f"📝 Test vocabs: {test_vocabs}")
        
        # Test 1: Create learned vocabs
        print("\n1. Testing create_learned_vocabs...")
        create_data = LearnedVocabsCreateInternal(
            user_id=test_user_id,
            vocabs=test_vocabs
        )
        
        created_entry = await crud.create_learned_vocabs(create_data)
        print(f"✅ Created entry with ID: {created_entry.id}")
        print(f"   Vocabs: {created_entry.vocabs}")
        print(f"   Created at: {created_entry.created_at}")
        print(f"   Is deleted: {created_entry.is_deleted}")
        
        # Test 2: Get by ID
        print("\n2. Testing get_learned_vocabs_by_id...")
        retrieved_entry = await crud.get_learned_vocabs_by_id(str(created_entry.id))
        if retrieved_entry:
            print(f"✅ Retrieved entry: {retrieved_entry.vocabs}")
        else:
            print("❌ Failed to retrieve entry")
        
        # Test 3: Find by exact vocabs
        print("\n3. Testing find_by_exact_vocabs...")
        found_entry = await crud.find_by_exact_vocabs(test_user_id, test_vocabs)
        if found_entry:
            print(f"✅ Found matching entry: {found_entry.id}")
        else:
            print("❌ No matching entry found")
        
        # Test 4: Get user learned vocabs
        print("\n4. Testing get_user_learned_vocabs...")
        user_entries = await crud.get_user_learned_vocabs(test_user_id)
        print(f"✅ Found {len(user_entries)} entries for user")
        
        # Test 5: Get all user vocabs
        print("\n5. Testing get_all_user_vocabs...")
        all_vocabs = await crud.get_all_user_vocabs(test_user_id)
        print(f"✅ All unique vocabs: {all_vocabs}")
        
        # Test 6: Update vocabs
        print("\n6. Testing update_learned_vocabs...")
        new_vocabs = ["updated", "vocabulary", "list"]
        updated_entry = await crud.update_learned_vocabs(str(created_entry.id), new_vocabs)
        if updated_entry:
            print(f"✅ Updated vocabs: {updated_entry.vocabs}")
        else:
            print("❌ Failed to update")
        
        # Test 7: Soft delete
        print("\n7. Testing soft_delete_learned_vocabs...")
        deleted = await crud.soft_delete_learned_vocabs(str(created_entry.id))
        if deleted:
            print("✅ Soft delete successful")
            
            # Verify it's not found in normal queries
            not_found = await crud.get_learned_vocabs_by_id(str(created_entry.id))
            if not_found is None:
                print("✅ Entry properly soft deleted (not found in queries)")
            else:
                print("⚠️ Entry still found after soft delete")
        else:
            print("❌ Soft delete failed")
        
        print("\n🎉 All CRUD tests completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

async def test_models():
    """Test the LearnedVocabs models"""
    print("\n🧪 Testing LearnedVocabs models...")
    
    try:
        from app.database.models import (
            LearnedVocabsCreate, 
            LearnedVocabsCreateInternal, 
            LearnedVocabsInDB, 
            LearnedVocabsResponse
        )
        from bson import ObjectId
        from datetime import datetime
        
        # Test LearnedVocabsCreate
        print("1. Testing LearnedVocabsCreate...")
        create_model = LearnedVocabsCreate(vocabs=["test", "vocab"])
        print(f"✅ Created: {create_model.dict()}")
        
        # Test LearnedVocabsCreateInternal
        print("\n2. Testing LearnedVocabsCreateInternal...")
        internal_model = LearnedVocabsCreateInternal(
            user_id=str(ObjectId()),
            vocabs=["internal", "test"]
        )
        print(f"✅ Created internal: {internal_model.dict()}")
        
        # Test LearnedVocabsInDB
        print("\n3. Testing LearnedVocabsInDB...")
        db_data = {
            "_id": ObjectId(),
            "user_id": ObjectId(),
            "vocabs": ["db", "test"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_deleted": False,
            "deleted_at": None
        }
        db_model = LearnedVocabsInDB(**db_data)
        print(f"✅ Created DB model: {db_model.dict()}")
        
        print("\n🎉 All model tests passed!")
        
    except Exception as e:
        print(f"❌ Error testing models: {e}")
        import traceback
        traceback.print_exc()

async def main():
    print("🚀 Testing Learned Vocabs Implementation")
    print("=" * 60)
    
    await test_models()
    await test_learned_vocabs_crud()
    
    print("\n" + "=" * 60)
    print("✅ Testing completed!")
    print("💡 If you see connection errors, make sure MongoDB is running")

if __name__ == "__main__":
    asyncio.run(main())