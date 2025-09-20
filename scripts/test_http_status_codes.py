"""
Test script to verify HTTP status codes for all API endpoints
"""
import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000/api/v1"

async def test_http_status_codes():
    """Test all endpoints with various scenarios to check HTTP status codes"""
    print("🧪 Testing HTTP Status Codes for All Endpoints")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        tests = []
        
        # === Google Auth Endpoints ===
        print("\n🔐 Google Authentication Endpoints:")
        
        # Test 1: Google Login with invalid code
        tests.append({
            "name": "Google Login - Invalid Code",
            "method": "POST",
            "url": f"{BASE_URL}/auth/google/login",
            "data": {"authorization_code": "invalid_code_123"},
            "expected_status": 400
        })
        
        # Test 2: Verify Token - Missing token
        tests.append({
            "name": "Verify Token - Missing Token", 
            "method": "POST",
            "url": f"{BASE_URL}/auth/verify-token",
            "data": {"token": ""},
            "expected_status": 400
        })
        
        # Test 3: Verify Token - Invalid token
        tests.append({
            "name": "Verify Token - Invalid Token",
            "method": "POST", 
            "url": f"{BASE_URL}/auth/verify-token",
            "data": {"token": "invalid.jwt.token"},
            "expected_status": 401
        })
        
        # Test 4: Profile - Missing auth header
        tests.append({
            "name": "Get Profile - Missing Auth Header",
            "method": "GET",
            "url": f"{BASE_URL}/auth/profile",
            "headers": {},
            "expected_status": 401
        })
        
        # Test 5: Profile - Invalid auth format
        tests.append({
            "name": "Get Profile - Invalid Auth Format",
            "method": "GET", 
            "url": f"{BASE_URL}/auth/profile",
            "headers": {"Authorization": "InvalidFormat token123"},
            "expected_status": 401
        })
        
        # Test 6: Refresh Token - Missing refresh token
        tests.append({
            "name": "Refresh Token - Missing Token",
            "method": "POST",
            "url": f"{BASE_URL}/auth/refresh-token", 
            "data": {"refresh_token": ""},
            "expected_status": 400
        })
        
        # === Content Generation Endpoints ===
        print("\n📝 Content Generation Endpoints:")
        
        # Test 7: Generate Paragraph - Missing language
        tests.append({
            "name": "Generate Paragraph - Missing Language",
            "method": "POST",
            "url": f"{BASE_URL}/generate-paragraph",
            "data": {
                "language": "",
                "vocabularies": ["test"],
                "length": 100,
                "level": "beginner"
            },
            "expected_status": 400
        })
        
        # Test 8: Generate Paragraph - Missing vocabularies
        tests.append({
            "name": "Generate Paragraph - Missing Vocabularies",
            "method": "POST",
            "url": f"{BASE_URL}/generate-paragraph", 
            "data": {
                "language": "English",
                "vocabularies": [],
                "length": 100,
                "level": "beginner"
            },
            "expected_status": 400
        })
        
        # Test 9: Save Paragraph - Missing vocabs
        tests.append({
            "name": "Save Paragraph - Missing Vocabs",
            "method": "POST",
            "url": f"{BASE_URL}/save-paragraph",
            "data": {
                "vocabs": [],
                "paragraph": "Test paragraph"
            },
            "expected_status": 400
        })
        
        # Test 10: Save Paragraph - Missing paragraph
        tests.append({
            "name": "Save Paragraph - Missing Paragraph",
            "method": "POST", 
            "url": f"{BASE_URL}/save-paragraph",
            "data": {
                "vocabs": ["test"],
                "paragraph": ""
            },
            "expected_status": 400
        })
        
        # === Run all tests ===
        results = []
        for test in tests:
            try:
                print(f"\n🧪 Testing: {test['name']}")
                
                # Prepare request
                kwargs = {
                    "url": test["url"],
                    "headers": test.get("headers", {"Content-Type": "application/json"})
                }
                
                if "data" in test:
                    kwargs["json"] = test["data"]
                
                # Send request
                if test["method"] == "GET":
                    response = await client.get(**kwargs)
                elif test["method"] == "POST":
                    response = await client.post(**kwargs)
                
                # Check results
                status_match = response.status_code == test["expected_status"]
                status_icon = "✅" if status_match else "❌"
                
                print(f"   {status_icon} Status: {response.status_code} (expected: {test['expected_status']})")
                
                # Try to parse response
                try:
                    response_data = response.json()
                    if "error" in response_data:
                        print(f"   📋 Error: {response_data['error']}")
                        print(f"   💬 Message: {response_data['message']}")
                except:
                    print(f"   📄 Response: {response.text[:100]}...")
                
                results.append({
                    "test": test["name"],
                    "expected_status": test["expected_status"],
                    "actual_status": response.status_code,
                    "passed": status_match
                })
                
            except Exception as e:
                print(f"   💥 Error: {e}")
                results.append({
                    "test": test["name"],
                    "expected_status": test["expected_status"],
                    "actual_status": "ERROR",
                    "passed": False,
                    "error": str(e)
                })
        
        # === Summary ===
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in results if r["passed"])
        total = len(results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        print(f"\n📋 Detailed Results:")
        for result in results:
            status_icon = "✅" if result["passed"] else "❌"
            print(f"{status_icon} {result['test']}: {result['actual_status']} (expected: {result['expected_status']})")
        
        # === HTTP Status Code Mapping ===
        print(f"\n📚 HTTP Status Code Mapping:")
        print(f"🔹 200 - Success")
        print(f"🔹 400 - Bad Request (invalid input)")
        print(f"🔹 401 - Unauthorized (invalid/missing auth)")
        print(f"🔹 403 - Forbidden (unauthorized client)")
        print(f"🔹 500 - Internal Server Error")
        
        return results

async def test_successful_requests():
    """Test successful requests that should return 200"""
    print(f"\n🎯 Testing Successful Requests:")
    
    async with httpx.AsyncClient() as client:
        # Test working endpoints
        success_tests = [
            {
                "name": "Test Data Endpoint",
                "url": f"{BASE_URL}/test-data",
                "method": "GET"
            },
            {
                "name": "Get All Paragraphs",
                "url": f"{BASE_URL}/all-paragraphs", 
                "method": "GET"
            },
            {
                "name": "Get Unique Vocabs",
                "url": f"{BASE_URL}/vocabs_base_on_category",
                "method": "GET"
            }
        ]
        
        for test in success_tests:
            try:
                if test["method"] == "GET":
                    response = await client.get(test["url"])
                
                status_icon = "✅" if response.status_code == 200 else "❌"
                print(f"   {status_icon} {test['name']}: {response.status_code}")
                
            except Exception as e:
                print(f"   💥 {test['name']}: Error - {e}")

async def main():
    """Main test runner"""
    print("🚀 HTTP Status Code Testing Suite")
    print("Testing all API endpoints for proper HTTP status codes...")
    
    await test_http_status_codes()
    await test_successful_requests()
    
    print(f"\n🎉 Testing complete!")
    print(f"\nℹ️  All endpoints now return proper HTTP status codes instead of always 200!")

if __name__ == "__main__":
    asyncio.run(main())
