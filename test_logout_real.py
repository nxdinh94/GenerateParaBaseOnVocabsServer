#!/usr/bin/env python3
"""
Test logout với JWT token thật từ database
"""
import requests
import json
import asyncio
from app.database.connection import connect_to_mongo, close_mongo_connection, get_database
from app.database.refresh_token_crud import get_refresh_token_crud
from app.services.google_auth import google_auth_service

async def test_logout_with_real_token():
    """Test logout với JWT token thật"""
    
    await connect_to_mongo()
    try:
        print("=== Testing Logout with Real JWT Token ===")
        
        # Lấy user_id từ existing refresh token trong database
        db = get_database()
        existing_tokens = await db.refresh_tokens.find({}).limit(1).to_list(1)
        
        if not existing_tokens:
            print("❌ No existing tokens found. Please login first to create test data.")
            return
            
        existing_user_id = existing_tokens[0]["user_id"]
        
        mock_user_data = {
            "user_id": str(existing_user_id),
            "email": "test@example.com", 
            "name": "Test User"
        }
        
        # Tạo JWT token thật
        jwt_token = google_auth_service.create_jwt_token(mock_user_data)
        print(f"Created JWT token: {jwt_token[:50]}...")
        
        # Tạo refresh token và lưu vào database
        jwt_refresh_token = google_auth_service.create_jwt_refresh_token(mock_user_data)
        
        from app.database.models import RefreshTokenCreate
        refresh_token_crud = get_refresh_token_crud(get_database())
        
        refresh_token_data = RefreshTokenCreate(
            user_id=existing_user_id,  # Use existing ObjectId
            refresh_token=jwt_refresh_token
        )
        
        saved_token = await refresh_token_crud.create(refresh_token_data)
        print(f"Saved refresh token to database: {saved_token.id}")
        
        # Kiểm tra tokens trước logout
        tokens_before = await refresh_token_crud.get_by_user_id(mock_user_data["user_id"])
        print(f"Tokens in database before logout: {len(tokens_before)}")
        
        # Test logout API
        print("\\nTesting logout API...")
        logout_response = requests.post(
            "http://127.0.0.1:8000/api/v1/auth/logout",
            headers={
                "Authorization": f"Bearer {jwt_token}"
            }
        )
        
        print(f"Logout Status: {logout_response.status_code}")
        print(f"Logout Response: {json.dumps(logout_response.json(), indent=2)}")
        
        # Kiểm tra tokens sau logout
        tokens_after = await refresh_token_crud.get_by_user_id(mock_user_data["user_id"])
        print(f"\\nTokens in database after logout: {len(tokens_after)}")
        
        if len(tokens_after) == 0:
            print("✅ SUCCESS: All refresh tokens deleted!")
        else:
            print("❌ FAILED: Some tokens still remain")
            
    finally:
        await close_mongo_connection()

def test_logout_api_summary():
    """Summary của logout API"""
    print("\\n" + "="*60)
    print("📋 LOGOUT API IMPLEMENTATION SUMMARY")
    print("="*60)
    
    print("🔗 Endpoint: POST /api/v1/auth/logout")
    print("🔐 Auth: Bearer token required")
    print("📥 Input: JWT token in Authorization header")
    print("📤 Output: Status + deleted count")
    print("🗄️ Action: Delete all refresh tokens for user")
    
    print("\\n🔄 Complete Flow:")
    print("1. User sends POST request with Bearer token")
    print("2. Server validates JWT token")
    print("3. Extract user_id from token payload")
    print("4. Delete all refresh tokens for that user_id")
    print("5. Return success with deleted count")
    
    print("\\n🛡️ Security Features:")
    print("- JWT token validation")
    print("- User isolation (only delete own tokens)")
    print("- Proper error handling")
    print("- Audit logging")
    
    print("\\n🚀 Frontend Integration:")
    print("```javascript")
    print("const logout = async () => {")
    print("  try {")
    print("    await axios.post('/api/v1/auth/logout', {}, {")
    print("      headers: { Authorization: `Bearer ${jwt_token}` }")
    print("    });")
    print("    localStorage.removeItem('jwt_token');")
    print("    window.location.href = '/login';")
    print("  } catch (error) {")
    print("    console.error('Logout failed:', error);")
    print("  }")
    print("};")
    print("```")

if __name__ == "__main__":
    # Run async test
    asyncio.run(test_logout_with_real_token())
    
    # Show summary
    test_logout_api_summary()