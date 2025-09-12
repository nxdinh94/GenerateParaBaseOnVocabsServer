"""
Test script for database operations
"""
import asyncio
from app.database.connection import connect_to_mongo, close_mongo_connection
from app.database.models import (
    UserCreate, InputHistoryCreate, SavedParagraphCreate
)

async def test_database():
    """Test all database operations"""
    print("🔌 Connecting to MongoDB...")
    await connect_to_mongo()
    
    # Import CRUD after connection is established
    from app.database.crud import get_user_crud, get_input_history_crud, get_saved_paragraph_crud
    
    try:
        print("\n📝 Testing User operations...")
        
        user_crud = get_user_crud()
        input_history_crud = get_input_history_crud()
        saved_paragraph_crud = get_saved_paragraph_crud()
        
        # Create user
        user_data = UserCreate(
            name="Test User",
            email="test@example.com",
            password="testpassword123"
        )
        
        user = await user_crud.create_user(user_data)
        print(f"✓ Created user: {user.name} ({user.email})")
        
        # Get user by ID
        retrieved_user = await user_crud.get_user_by_id(str(user.id))
        print(f"✓ Retrieved user by ID: {retrieved_user.name}")
        
        # Get user by email
        user_by_email = await user_crud.get_user_by_email(user.email)
        print(f"✓ Retrieved user by email: {user_by_email.name}")
        
        print(f"\n📚 Testing Input History operations...")
        
        # Create input history
        history_data = InputHistoryCreate(
            user_id=user.id,
            words=["hello", "world", "test"]
        )
        
        history = await input_history_crud.create_input_history(history_data)
        print(f"✓ Created input history with words: {history.words}")
        
        # Get user's input history
        user_histories = await input_history_crud.get_user_input_history(str(user.id))
        print(f"✓ Retrieved {len(user_histories)} input histories for user")
        
        print(f"\n📖 Testing Saved Paragraph operations...")
        
        # Create saved paragraph
        paragraph_data = SavedParagraphCreate(
            input_history_id=history.id,
            paragraph="This is a test paragraph containing hello, world, and test words."
        )
        
        paragraph = await saved_paragraph_crud.create_saved_paragraph(paragraph_data)
        print(f"✓ Created saved paragraph: {paragraph.paragraph[:50]}...")
        
        # Get paragraphs by input history
        history_paragraphs = await saved_paragraph_crud.get_paragraphs_by_input_history(str(history.id))
        print(f"✓ Retrieved {len(history_paragraphs)} paragraphs for input history")
        
        # Get user's saved paragraphs with lookup
        user_paragraphs = await saved_paragraph_crud.get_user_saved_paragraphs(str(user.id))
        print(f"✓ Retrieved {len(user_paragraphs)} paragraphs for user with lookup")
        
        print(f"\n🗑️ Testing Delete operations...")
        
        # Delete saved paragraph
        deleted_paragraph = await saved_paragraph_crud.delete_saved_paragraph(str(paragraph.id))
        print(f"✓ Deleted saved paragraph: {deleted_paragraph}")
        
        # Delete input history
        deleted_history = await input_history_crud.delete_input_history(str(history.id))
        print(f"✓ Deleted input history: {deleted_history}")
        
        # Delete user
        deleted_user = await user_crud.delete_user(str(user.id))
        print(f"✓ Deleted user: {deleted_user}")
        
        print(f"\n✅ All database tests passed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        raise
    
    finally:
        print("\n🔌 Closing MongoDB connection...")
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(test_database())
