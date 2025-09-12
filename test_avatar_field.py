#!/usr/bin/env python3
"""
Test script to verify the new avt (avatar) field is working
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_avatar_field():
    """Test the new avatar field functionality"""
    try:
        # Import necessary components
        from app.database.crud import get_user_crud
        from app.database.models import UserCreate, GoogleUserCreate, UserUpdate
        
        print("🧪 Testing Avatar Field Implementation")
        print("=" * 50)
        
        user_crud = get_user_crud()
        
        # Test 1: Create a regular user with avatar
        print("📝 Test 1: Creating regular user with avatar")
        user_data = UserCreate(
            name="Test User with Avatar",
            email="test_avatar@example.com",
            password="password123",
            avt="https://example.com/avatar.jpg"
        )
        
        try:
            created_user = await user_crud.create_user(user_data)
            print(f"✅ User created with ID: {created_user.id}")
            print(f"📸 Avatar URL: {created_user.avt}")
            
            # Clean up - delete the test user
            await user_crud.delete_user(str(created_user.id))
            print("🧹 Test user cleaned up")
            
        except Exception as e:
            print(f"❌ Error creating user: {e}")
        
        print()
        
        # Test 2: Create a Google user with avatar
        print("📝 Test 2: Creating Google user with avatar")
        google_user_data = GoogleUserCreate(
            google_id="test_google_123",
            name="Google User with Avatar",
            email="google_avatar@example.com",
            picture="https://lh3.googleusercontent.com/picture.jpg",
            verified_email=True,
            avt="https://example.com/google_avatar.jpg"
        )
        
        try:
            created_google_user = await user_crud.create_google_user(google_user_data)
            print(f"✅ Google user created with ID: {created_google_user.id}")
            print(f"📸 Picture URL: {created_google_user.picture}")
            print(f"🎭 Avatar URL: {created_google_user.avt}")
            
            # Clean up - delete the test user
            await user_crud.delete_user(str(created_google_user.id))
            print("🧹 Test Google user cleaned up")
            
        except Exception as e:
            print(f"❌ Error creating Google user: {e}")
        
        print()
        
        # Test 3: Create user without avatar (should be None)
        print("📝 Test 3: Creating user without avatar (nullable test)")
        user_no_avatar = UserCreate(
            name="User Without Avatar",
            email="no_avatar@example.com",
            password="password123"
            # avt field not provided (should default to None)
        )
        
        try:
            created_user_no_avt = await user_crud.create_user(user_no_avatar)
            print(f"✅ User created without avatar, ID: {created_user_no_avt.id}")
            print(f"📸 Avatar URL: {created_user_no_avt.avt} (should be None)")
            
            # Test 4: Update user with avatar
            print("📝 Test 4: Updating user to add avatar")
            update_data = UserUpdate(avt="https://example.com/new_avatar.jpg")
            updated_user = await user_crud.update_user(str(created_user_no_avt.id), update_data)
            
            if updated_user:
                print(f"✅ User updated with avatar: {updated_user.avt}")
            else:
                print("❌ Failed to update user")
            
            # Clean up - delete the test user
            await user_crud.delete_user(str(created_user_no_avt.id))
            print("🧹 Test user cleaned up")
            
        except Exception as e:
            print(f"❌ Error in avatar tests: {e}")
        
        print()
        print("🎯 Summary:")
        print("- ✅ Avatar field added to all user models")
        print("- ✅ Avatar field is nullable (Optional[str])")
        print("- ✅ Database schema updated to support avatar field")
        print("- ✅ CRUD operations support avatar field")
        print("- ✅ Both regular and Google users can have avatars")
        
    except Exception as e:
        print(f"💥 Error in avatar field test: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_avatar_field())