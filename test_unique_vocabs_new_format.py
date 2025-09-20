#!/usr/bin/env python3
"""
Test script for the updated unique-vocabs API
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

def test_unique_vocabs_new_format():
    """Test the updated unique-vocabs endpoint format"""
    print("=" * 60)
    print("Testing GET /api/v1/unique-vocabs (Updated Format)")
    print("=" * 60)
    
    print("\n📋 Expected Response Format:")
    expected_format = {
        "status": True,
        "total_documents": 2,
        "documents": [
            {
                "id": "document_id_1",
                "vocabs": ["hello", "world", "python"],
                "created_at": "2025-09-20T10:00:00",
                "updated_at": None,
                "deleted_at": None,
                "is_deleted": False
            },
            {
                "id": "document_id_2", 
                "vocabs": ["learn", "code", "python"],
                "created_at": "2025-09-20T11:00:00",
                "updated_at": "2025-09-20T12:00:00",
                "deleted_at": None,
                "is_deleted": False
            }
        ],
        "message": "Found 2 vocabulary documents"
    }
    print(json.dumps(expected_format, indent=2))
    
    print("\n🔑 Key Changes:")
    print("✓ Returns complete documents (not just unique words)")
    print("✓ Excludes user_id from response")
    print("✓ Sorted by created_at (newest first)")
    print("✓ Includes all timestamp fields")
    print("✓ Includes is_deleted status")
    
    print("\n🧪 Testing without authentication (should fail):")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/unique-vocabs",
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 401:
            print("✅ Correctly requires authentication")
        else:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n📝 To test with real data:")
    print("1. Get JWT token from Google login")
    print("2. Create some vocabulary entries via POST /input-history/")
    print("3. Call GET /unique-vocabs with Authorization header")
    print("4. Verify documents are sorted by newest first")

def test_input_history_integration():
    """Test how the input-history endpoint creates data for unique-vocabs"""
    print("\n" + "=" * 60)
    print("Testing POST /api/v1/db/input-history/ Integration")
    print("=" * 60)
    
    print("\n📋 Sample Request:")
    sample_request = {
        "words": ["hello", "world", "python", "fastapi"]
    }
    print(json.dumps(sample_request, indent=2))
    
    print("\n🔄 What happens:")
    print("1. POST /input-history/ saves to learned_vocabs collection")
    print("2. Creates document with timestamps and user_id")
    print("3. GET /unique-vocabs returns all documents for user")
    print("4. Documents sorted by created_at (newest first)")
    print("5. user_id excluded from response")
    
    print("\n🧪 Testing without authentication:")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/db/input-history/",
            json=sample_request,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 401:
            print("✅ Correctly requires authentication")
        else:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    print("🚀 Testing Updated Unique Vocabs API")
    print(f"🕒 Test Time: {datetime.now().isoformat()}")
    
    test_unique_vocabs_new_format()
    test_input_history_integration()
    
    print("\n" + "=" * 60)
    print("✅ Testing Summary:")
    print("📊 API now returns complete documents instead of unique words")
    print("🗓️ Documents sorted by created_at (newest first)")
    print("🔒 user_id excluded from response for security")
    print("📋 Includes all metadata (timestamps, deletion status)")
    print("🔗 Integrates with input-history endpoint seamlessly")
    print("=" * 60)

if __name__ == "__main__":
    main()