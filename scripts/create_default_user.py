"""
Create a default user for testing save-paragraph API
"""
import asyncio
from app.database.connection import connect_to_mongo, close_mongo_connection
from app.database.models import UserCreate

async def create_default_user():
    """Create a default user for testing"""
    print("🔌 Connecting to MongoDB...")
    await connect_to_mongo()
    
    try:
        from app.database.crud import get_user_crud
        user_crud = get_user_crud()
        
        # Check if default user already exists
        existing_user = await user_crud.get_user_by_email("default@example.com")
        
        if existing_user:
            print(f"✓ Default user already exists: {existing_user.id}")
            return str(existing_user.id)
        
        # Create default user
        user_data = UserCreate(
            name="Default User",
            email="default@example.com",
            password="defaultpassword123"
        )
        
        user = await user_crud.create_user(user_data)
        print(f"✓ Created default user: {user.name} (ID: {user.id})")
        return str(user.id)
        
    except Exception as e:
        print(f"❌ Error creating default user: {e}")
        raise
    
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    user_id = asyncio.run(create_default_user())
    print(f"\nDefault User ID: {user_id}")
    print("You can use this ID in the save-paragraph API.")
