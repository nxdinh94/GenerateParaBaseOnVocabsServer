#!/usr/bin/env python3
"""
Test database operations directly to isolate the 500 error
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_database_operations():
    """Test database operations that might be causing 500 errors"""
    print("🔍 Testing Database Operations")
    print("=" * 60)
    
    try:
        # Test basic imports
        print("📦 Testing imports...")
        from app.database.crud import get_input_history_crud, get_saved_paragraph_crud
        from app.database.models import InputHistoryCreate, SavedParagraphCreate
        print("   ✅ CRUD imports successful")
        
        # Test CRUD initialization
        print("🔧 Testing CRUD initialization...")
        input_history_crud = get_input_history_crud()
        saved_paragraph_crud = get_saved_paragraph_crud()
        print("   ✅ CRUD initialization successful")
        
        # Test a simple database connection
        print("🗄️ Testing database connection...")
        # This will test if the database connection works
        
        # Create test data similar to save_paragraph endpoint
        test_user_id = "507f1f77bcf86cd799439011"  # Valid ObjectId format
        test_vocabs = ["test", "database", "connection"]
        test_paragraph = "This is a test paragraph for database operations."
        
        print(f"📝 Test data:")
        print(f"   user_id: {test_user_id}")
        print(f"   vocabs: {test_vocabs}")
        print(f"   paragraph: {test_paragraph}")
        
        # Test finding existing input history (should not crash)
        print("🔍 Testing find_by_exact_words...")
        try:
            existing_input_history = await input_history_crud.find_by_exact_words(test_user_id, test_vocabs)
            print(f"   ✅ find_by_exact_words completed: {existing_input_history is not None}")
        except Exception as e:
            print(f"   ❌ find_by_exact_words failed: {e}")
            return False
        
        # Test creating input history if it doesn't exist
        if not existing_input_history:
            print("📝 Testing InputHistory creation...")
            try:
                history_data = InputHistoryCreate(
                    user_id=test_user_id,
                    words=test_vocabs
                )
                print(f"   ✅ InputHistoryCreate model created")
                
                # Test actual creation (this might fail if DB is not accessible)
                input_history = await input_history_crud.create_input_history(history_data)
                print(f"   ✅ InputHistory created with ID: {input_history.id}")
                
                # Test creating saved paragraph
                print("📝 Testing SavedParagraph creation...")
                paragraph_data = SavedParagraphCreate(
                    input_history_id=str(input_history.id),
                    paragraph=test_paragraph
                )
                
                saved_paragraph = await saved_paragraph_crud.create_saved_paragraph(paragraph_data)
                print(f"   ✅ SavedParagraph created with ID: {saved_paragraph.id}")
                
                return True
                
            except Exception as e:
                print(f"   ❌ Database operation failed: {e}")
                print(f"   Error type: {type(e).__name__}")
                return False
        else:
            print("   ✅ Existing input history found, database connection works")
            return True
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

async def test_environment_variables():
    """Test if required environment variables are set"""
    print(f"\n🔍 Testing Environment Variables")
    print("=" * 60)
    
    try:
        from app.core.config import settings
        print("✅ Config imported successfully")
        
        # Check important environment variables
        env_vars = [
            ("MONGODB_URL", getattr(settings, 'MONGODB_URL', None)),
            ("DATABASE_NAME", getattr(settings, 'DATABASE_NAME', None)),
            ("JWT_SECRET_KEY", getattr(settings, 'JWT_SECRET_KEY', None)),
        ]
        
        for var_name, var_value in env_vars:
            if var_value:
                # Don't print sensitive values, just confirm they exist
                print(f"   ✅ {var_name}: SET")
            else:
                print(f"   ❌ {var_name}: NOT SET")
                
    except Exception as e:
        print(f"❌ Config error: {e}")

async def test_jwt_operations():
    """Test JWT operations that might be causing issues"""
    print(f"\n🔍 Testing JWT Operations")
    print("=" * 60)
    
    try:
        from app.services.google_auth import google_auth_service
        print("✅ google_auth_service imported successfully")
        
        # Test creating a JWT token
        test_user_data = {
            "id": "507f1f77bcf86cd799439011",
            "user_id": "507f1f77bcf86cd799439011",
            "email": "test@example.com",
            "name": "Test User"
        }
        
        jwt_token = google_auth_service.create_jwt_token(test_user_data)
        print(f"✅ JWT token created: {jwt_token[:50]}...")
        
        # Test verifying the JWT token
        verified_data = google_auth_service.verify_jwt_token(jwt_token)
        print(f"✅ JWT token verified: {verified_data is not None}")
        
        if verified_data:
            user_id = verified_data.get("user_id") or verified_data.get("id")
            print(f"✅ user_id extracted: {user_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ JWT operation failed: {e}")
        return False

async def main():
    print("🚀 Database and Service Testing")
    print(f"🕒 Test Time: {asyncio.get_event_loop().time()}")
    
    # Test environment
    await test_environment_variables()
    
    # Test JWT operations
    jwt_ok = await test_jwt_operations()
    
    # Test database operations
    db_ok = await test_database_operations()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"   JWT Operations: {'✅ PASS' if jwt_ok else '❌ FAIL'}")
    print(f"   Database Operations: {'✅ PASS' if db_ok else '❌ FAIL'}")
    
    if jwt_ok and db_ok:
        print("\n✅ All tests passed - the 500 error might be token-specific")
        print("💡 Try with a real Google OAuth JWT token")
    else:
        print("\n❌ Issues found - these might be causing the 500 error")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())