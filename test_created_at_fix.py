"""
Test save-paragraph API với created_at fix
"""
import httpx
import asyncio
import json

async def test_save_paragraph_with_created_at():
    """Test save-paragraph API sau khi fix created_at"""
    
    base_url = "http://localhost:8001/api/v1"
    
    print("🧪 Testing Save Paragraph API with created_at fix...")
    
    # Test data
    test_data = {
        "vocabs": ["hello", "world", "test"],
        "paragraph": "This is a test paragraph with hello world test words."
    }
    
    print(f"📝 Test data: {json.dumps(test_data, indent=2)}")
    
    # Test without authentication (should fail with proper auth error, not database error)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{base_url}/save-paragraph", json=test_data)
            print(f"❌ No auth response: {response.status_code}")
            print(f"   Message: {response.json()}")
            
            # Kiểm tra xem có còn lỗi created_at không
            if "created_at" in str(response.json()):
                print("⚠️  Vẫn còn lỗi created_at!")
            elif response.status_code == 401:
                print("✅ Không còn lỗi created_at, chỉ còn lỗi authentication (đúng rồi!)")
            
    except Exception as e:
        print(f"❌ Error testing: {e}")

if __name__ == "__main__":
    asyncio.run(test_save_paragraph_with_created_at())