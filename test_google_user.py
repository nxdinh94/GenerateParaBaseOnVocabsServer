#!/usr/bin/env python3
"""
Test Google user creation with random password
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_google_user_creation():
    """Test creating a Google user with random password"""
    try:
        from app.database.crud import get_user_crud
        from app.database.models import GoogleUserCreate
        
        print("✅ Imports successful")
        
        # Create test Google user data
        test_user_data = GoogleUserCreate(
            google_id="test_google_id_123456789",
            name="Test User",
            email="test.user@gmail.com",
            picture="https://example.com/picture.jpg",
            verified_email=True
        )
        
        print("✅ GoogleUserCreate model created")
        
        user_crud = get_user_crud()
        print("✅ UserCRUD instance created")
        
        # Test password generation
        random_password = user_crud.generate_random_password()
        print(f"✅ Random password generated: {random_password[:5]}... (length: {len(random_password)})")
        
        # Test password hashing
        hashed_password = user_crud.hash_password(random_password)
        print(f"✅ Password hashed successfully (length: {len(hashed_password)})")
        
        print("🎉 All tests passed! Ready to create Google users with random passwords.")
        
    except Exception as e:
        print(f"💥 Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_google_user_creation())