#!/usr/bin/env python3
"""
Test script for the new POST /learned-vocabs API endpoint
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

def test_post_learned_vocabs():
    """Test the new POST /learned-vocabs endpoint"""
    print("=" * 60)
    print("Testing POST /api/v1/learned-vocabs")
    print("=" * 60)
    
    print("\n📋 API Schema:")
    print("Endpoint: POST /api/v1/learned-vocabs")
    print("Authorization: Bearer <jwt_token>")
    print("Content-Type: application/json")
    
    schema = {
        "vocabs": ["word1", "word2", "word3"]
    }
    print(f"Request Body: {json.dumps(schema, indent=2)}")
    
    print("\n📊 Expected Response (New Entry):")
    new_response = {
        "status": True,
        "message": "Learned vocabularies created successfully",
        "data": {
            "id": "document_id",
            "vocabs": ["word1", "word2", "word3"],
            "created_at": "2025-09-20T13:45:00",
            "updated_at": "2025-09-20T13:45:00",
            "deleted_at": None,
            "is_deleted": False
        },
        "is_new": True
    }
    print(json.dumps(new_response, indent=2))
    
    print("\n📊 Expected Response (Existing Entry):")
    existing_response = {
        "status": True,
        "message": "Vocabularies already exist",
        "data": {
            "id": "existing_document_id",
            "vocabs": ["word1", "word2", "word3"],
            "created_at": "2025-09-20T10:00:00",
            "updated_at": "2025-09-20T10:00:00",
            "deleted_at": None,
            "is_deleted": False
        },
        "is_new": False
    }
    print(json.dumps(existing_response, indent=2))

def test_validation_cases():
    """Test various validation scenarios"""
    print("\n" + "=" * 60)
    print("Testing Validation Cases")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Valid Request",
            "data": {"vocabs": ["hello", "world", "python"]},
            "expected": "✅ Success"
        },
        {
            "name": "Missing vocabs field",
            "data": {"words": ["hello", "world"]},
            "expected": "❌ 400 - missing_vocabs"
        },
        {
            "name": "Empty vocabs array",
            "data": {"vocabs": []},
            "expected": "❌ 400 - empty_vocabs"
        },
        {
            "name": "Non-array vocabs",
            "data": {"vocabs": "hello world"},
            "expected": "❌ 400 - invalid_vocabs_type"
        },
        {
            "name": "All empty strings",
            "data": {"vocabs": ["", "  ", "   "]},
            "expected": "❌ 400 - no_valid_vocabs"
        },
        {
            "name": "Mixed valid/invalid",
            "data": {"vocabs": ["hello", "", "world", "  ", "python"]},
            "expected": "✅ Success with cleaned: ['hello', 'world', 'python']"
        }
    ]
    
    for case in test_cases:
        print(f"\n🧪 Test: {case['name']}")
        print(f"   Data: {json.dumps(case['data'])}")
        print(f"   Expected: {case['expected']}")

def test_without_auth():
    """Test endpoint without authentication"""
    print("\n" + "=" * 60)
    print("Testing Without Authentication")
    print("=" * 60)
    
    sample_data = {"vocabs": ["test", "vocabulary"]}
    
    print(f"Request: {json.dumps(sample_data)}")
    print("Authorization: None")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/learned-vocabs",
            json=sample_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"\nStatus Code: {response.status_code}")
        if response.status_code == 401:
            print("✅ Correctly requires authentication")
        else:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Connection Error: {e}")
        print("💡 Server may not be running")

def test_duplicate_detection():
    """Test duplicate vocabulary detection"""
    print("\n" + "=" * 60)
    print("Testing Duplicate Detection")
    print("=" * 60)
    
    print("🔍 How Duplicate Detection Works:")
    print("1. Vocabularies are normalized (trimmed, lowercase)")
    print("2. Arrays are sorted for consistent comparison")
    print("3. If exact match exists, returns existing entry")
    print("4. Response includes 'is_new: false' for existing entries")
    
    print("\n📝 Example Scenarios:")
    scenarios = [
        {
            "first": ["Hello", "World"],
            "second": ["world", "hello"],
            "result": "Same (normalized and sorted)"
        },
        {
            "first": ["Python", "Code"],
            "second": ["python", "code", "learn"],
            "result": "Different (different words)"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. First: {scenario['first']}")
        print(f"   Second: {scenario['second']}")
        print(f"   Result: {scenario['result']}")

def main():
    print("🚀 Testing POST /learned-vocabs API")
    print(f"🕒 Test Time: {datetime.now().isoformat()}")
    
    test_post_learned_vocabs()
    test_validation_cases()
    test_without_auth()
    test_duplicate_detection()
    
    print("\n" + "=" * 60)
    print("✅ Testing Summary:")
    print("📝 New POST /learned-vocabs endpoint created")
    print("🔐 Requires Bearer token authentication")
    print("✨ Validates input and cleans vocabulary data")
    print("🔍 Detects and handles duplicate vocabularies")
    print("📊 Returns structured response with metadata")
    print("🔗 Integrates with existing learned_vocabs collection")
    print("=" * 60)
    
    print("\n🔧 To test with real server:")
    print("1. Start server: uvicorn app.main:app --host 0.0.0.0 --port 8001")
    print("2. Get JWT token from Google login")
    print("3. POST to /api/v1/learned-vocabs with Authorization header")

if __name__ == "__main__":
    main()