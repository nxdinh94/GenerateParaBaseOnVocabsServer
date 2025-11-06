"""
Test script to verify cascade deletion of vocabulary collections
This tests that deleting a collection also deletes all associated learned_vocabs
"""

import asyncio
from app.database.crud import get_vocab_collection_crud, get_learned_vocabs_crud, get_user_crud
from app.database.models import VocabCollectionCreate, LearnedVocabsCreateInternal
from bson import ObjectId

async def test_cascade_delete():
    print("🧪 Testing Cascade Delete Collection Functionality\n")
    
    # Initialize CRUD
    vocab_collection_crud = get_vocab_collection_crud()
    learned_vocabs_crud = get_learned_vocabs_crud()
    user_crud = get_user_crud()
    
    # Use a test user (replace with actual user ID from your database)
    test_user_id = "672ef6d0e50a0fe6b6e17d17"  # Replace with real user ID
    
    try:
        # Step 1: Create a test collection
        print("📚 Step 1: Creating test collection...")
        test_collection_data = VocabCollectionCreate(
            name="Test Collection for Cascade Delete",
            user_id=test_user_id
        )
        test_collection = await vocab_collection_crud.create_vocab_collection(test_collection_data)
        print(f"✅ Created collection: {test_collection.name} (ID: {test_collection.id})")
        
        # Step 2: Add some vocabularies to this collection
        print("\n📝 Step 2: Adding vocabularies to collection...")
        test_vocabs = ["cascade", "delete", "test", "vocabulary", "collection"]
        created_vocabs = []
        
        for vocab_word in test_vocabs:
            vocab_data = LearnedVocabsCreateInternal(
                vocab=vocab_word,
                collection_id=str(test_collection.id)
            )
            vocab = await learned_vocabs_crud.create_learned_vocabs(vocab_data)
            created_vocabs.append(vocab)
            print(f"   ✅ Added vocab: {vocab.vocab} (ID: {vocab.id})")
        
        # Step 3: Verify vocabularies exist
        print("\n🔍 Step 3: Verifying vocabularies exist in collection...")
        vocabs_before = await learned_vocabs_crud.get_vocabs_by_collection(str(test_collection.id), limit=100)
        print(f"   📊 Found {len(vocabs_before)} vocabularies in collection")
        
        # Step 4: Delete the collection (should cascade delete vocabularies)
        print(f"\n🗑️ Step 4: Deleting collection '{test_collection.name}'...")
        print(f"   Expected: Collection + {len(vocabs_before)} vocabularies deleted")
        
        success = await vocab_collection_crud.delete_vocab_collection(str(test_collection.id))
        
        if success:
            print(f"   ✅ Collection deleted successfully")
        else:
            print(f"   ❌ Failed to delete collection")
            return
        
        # Step 5: Verify collection is deleted
        print("\n✔️ Step 5: Verifying collection is deleted...")
        deleted_collection = await vocab_collection_crud.get_vocab_collection_by_id(str(test_collection.id))
        if deleted_collection is None:
            print("   ✅ Collection no longer exists in database")
        else:
            print("   ❌ Collection still exists in database!")
        
        # Step 6: Verify vocabularies are also deleted (cascade)
        print("\n✔️ Step 6: Verifying vocabularies were cascade deleted...")
        vocabs_after = await learned_vocabs_crud.get_vocabs_by_collection(str(test_collection.id), limit=100)
        print(f"   📊 Found {len(vocabs_after)} vocabularies in collection")
        
        if len(vocabs_after) == 0:
            print("   ✅ All vocabularies were cascade deleted successfully!")
        else:
            print(f"   ❌ {len(vocabs_after)} orphaned vocabularies still exist!")
            for vocab in vocabs_after:
                print(f"      - Orphaned: {vocab.vocab} (ID: {vocab.id})")
        
        # Step 7: Verify individual vocabulary documents
        print("\n✔️ Step 7: Checking individual vocabulary documents...")
        for created_vocab in created_vocabs:
            vocab_check = await learned_vocabs_crud.get_learned_vocabs_by_id(str(created_vocab.id))
            if vocab_check is None:
                print(f"   ✅ Vocab '{created_vocab.vocab}' was deleted")
            else:
                print(f"   ❌ Vocab '{created_vocab.vocab}' still exists!")
        
        print("\n" + "="*60)
        print("🎉 CASCADE DELETE TEST COMPLETED SUCCESSFULLY!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Cascade Delete Vocabulary Collection")
    print("=" * 60 + "\n")
    
    asyncio.run(test_cascade_delete())
