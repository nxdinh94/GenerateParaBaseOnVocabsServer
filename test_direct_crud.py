"""
Direct test của create_input_history function để kiểm tra created_at
"""
import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from app.database.crud import get_input_history_crud
from app.database.models import InputHistoryCreate
import json

async def test_create_input_history_directly():
    """Test trực tiếp function create_input_history"""
    
    print("🧪 Testing create_input_history function directly...")
    
    try:
        # Initialize CRUD
        input_history_crud = get_input_history_crud()
        
        # Test data
        test_user_id = "65a1b2c3d4e5f6789abcdef0"  # Mock user ID
        test_words = ["hello", "world", "test"]
        
        print(f"📝 Test user_id: {test_user_id}")
        print(f"📝 Test words: {test_words}")
        
        # Create InputHistoryCreate object
        history_data = InputHistoryCreate(
            user_id=test_user_id,
            words=test_words
        )
        
        print(f"📝 InputHistoryCreate data: {history_data.dict()}")
        
        # Call create_input_history
        result = await input_history_crud.create_input_history(history_data)
        
        print(f"✅ Success! Created input_history:")
        print(f"   ID: {result.id}")
        print(f"   User ID: {result.user_id}")
        print(f"   Words: {result.words}")
        print(f"   Created at: {result.created_at}")
        print(f"   Created at type: {type(result.created_at)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error creating input_history: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_create_input_history_directly())