"""
Test script to verify JWT token changes
"""
import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from app.services.google_auth import GoogleAuthService
from app.database.crud import get_user_crud
from app.database.models import GoogleUserCreate
import json

async def test_jwt_token_structure():
    """Test JWT token structure with new changes"""
    
    print("🧪 Testing JWT Token Structure Changes...")
    
    # Initialize services
    google_auth = GoogleAuthService()
    user_crud = get_user_crud()
    
    # Mock user data (similar to what we get from Google)
    mock_user_db = type('MockUser', (), {
        'id': '65a1b2c3d4e5f6789abcdef0',  # Mock database ObjectId
        'google_id': '123456789',
        'email': 'test@example.com',
        'name': 'Test User',
        'picture': 'https://example.com/avatar.jpg',
        'verified_email': True
    })()
    
    # Create JWT user data (like in the API)
    jwt_user_data = {
        "id": str(mock_user_db.id),  # Use database user ID (_id) as primary identifier
        "user_id": str(mock_user_db.id),  # Keep for backward compatibility
        "google_id": mock_user_db.google_id,  # Store Google ID for reference
        "email": mock_user_db.email,
        "name": mock_user_db.name,
        "picture": mock_user_db.picture,
        "verified_email": mock_user_db.verified_email
    }
    
    print(f"📝 JWT User Data to encode:")
    print(json.dumps(jwt_user_data, indent=2))
    
    # Create JWT token
    jwt_token = google_auth.create_jwt_token(jwt_user_data)
    print(f"🎫 Generated JWT Token: {jwt_token[:50]}...")
    
    # Verify JWT token
    decoded_user_data = google_auth.verify_jwt_token(jwt_token)
    print(f"🔓 Decoded JWT Token:")
    print(json.dumps(decoded_user_data, indent=2, default=str))
    
    # Test what current_user.get("user_id") would return
    user_id_from_token = decoded_user_data.get("user_id") if decoded_user_data else None
    print(f"👤 User ID from token (for APIs): {user_id_from_token}")
    
    # Verify this matches the original database user ID
    original_db_id = str(mock_user_db.id)
    print(f"🆔 Original DB User ID: {original_db_id}")
    print(f"✅ Match: {user_id_from_token == original_db_id}")
    
    return decoded_user_data

if __name__ == "__main__":
    asyncio.run(test_jwt_token_structure())