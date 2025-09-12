#!/usr/bin/env python3
"""
Debug script for Google authentication
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_auth_code():
    """Test the Google authentication with a sample code"""
    try:
        # Import the services
        from app.services.google_auth import google_auth_service
        from app.database.crud import get_user_crud, get_refresh_token_crud
        from app.database.models import GoogleUserCreate, RefreshTokenCreate
        
        print("✅ All imports successful")
        
        # Test with a sample code (this will fail, but we can see where it fails)
        test_code = "4/0AVMBsJhzjN3VSgl861FV_0Z56ZFDn4qNdv5IYp4vazo_lHqJb6TRbXk3MXH2S_i8yk_kCw"
        
        print(f"🔄 Testing with authorization code: {test_code[:20]}...")
        
        # Try different redirect URIs that might have been used
        redirect_uris_to_try = [
            "http://localhost:5173",  # Vite default
            "http://localhost:3000",  # React default  
            "postmessage",            # For popup mode
            "urn:ietf:wg:oauth:2.0:oob"  # For desktop/mobile
        ]
        
        auth_result = None
        last_error = None
        
        for redirect_uri in redirect_uris_to_try:
            try:
                print(f"🔄 Trying redirect_uri: {redirect_uri}")
                auth_result = await google_auth_service.exchange_code_for_tokens(
                    test_code, 
                    redirect_uri
                )
                print(f"✅ Success with redirect_uri: {redirect_uri}")
                break
            except Exception as e:
                print(f"❌ Failed with redirect_uri {redirect_uri}: {str(e)}")
                last_error = e
                continue
        
        if not auth_result:
            print(f"❌ All redirect URIs failed. Last error: {last_error}")
            # This is expected for an expired code
            return
        
        # If we got here, the code worked (unlikely for an old code)
        user_info = auth_result["user_info"]
        print(f"✅ Got user info: {user_info.get('email')}")
        
        # Test database operations
        user_crud = get_user_crud()
        refresh_token_crud = get_refresh_token_crud()
        
        # Check if user already exists
        existing_user = await user_crud.get_user_by_google_id(user_info.get("id"))
        print(f"🔍 Existing user check: {existing_user is not None}")
        
        if not existing_user:
            # Test creating a new user
            google_user_data = GoogleUserCreate(
                google_id=user_info.get("id"),
                name=user_info.get("name"),
                email=user_info.get("email"),
                picture=user_info.get("picture"),
                verified_email=user_info.get("verified_email")
            )
            print(f"✅ GoogleUserCreate model created successfully")
            
            # user_db = await user_crud.create_google_user(google_user_data)
            # print(f"✅ User created in database")
        
        print("✅ All tests passed")
        
    except Exception as e:
        print(f"💥 Error occurred: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_auth_code())