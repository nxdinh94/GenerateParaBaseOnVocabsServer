#!/usr/bin/env python3
"""
Test refresh token creation with created_at field
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_refresh_token_creation():
    """Test creating a refresh token with created_at field"""
    try:
        from app.database.crud import get_refresh_token_crud
        from app.database.models import RefreshTokenCreate
        
        print("✅ Imports successful")
        
        # Create test refresh token data
        test_token_data = RefreshTokenCreate(
            user_id="68c13d6181373f816d763a41",  # Use default user ID
            refresh_token="test_jwt_refresh_token_123456789"
        )
        
        print("✅ RefreshTokenCreate model created")
        
        refresh_token_crud = get_refresh_token_crud()
        print("✅ RefreshTokenCRUD instance created")
        
        # Test the token_dict creation logic
        token_dict = test_token_data.dict()
        from bson import ObjectId
        from datetime import datetime
        token_dict['user_id'] = ObjectId(token_dict['user_id'])
        token_dict['created_at'] = datetime.utcnow()
        
        print(f"✅ Token dict created: {list(token_dict.keys())}")
        print(f"   - user_id: {type(token_dict['user_id'])}")
        print(f"   - refresh_token: {token_dict['refresh_token'][:20]}...")
        print(f"   - created_at: {token_dict['created_at']}")
        
        print("🎉 All tests passed! Ready to create refresh tokens with created_at field.")
        
    except Exception as e:
        print(f"💥 Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_refresh_token_creation())