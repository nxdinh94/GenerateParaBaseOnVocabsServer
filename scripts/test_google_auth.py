"""
Demo script to test Google Authentication API
"""
import asyncio
import httpx
import json

# Base URL of your FastAPI server
BASE_URL = "http://localhost:8000/api/v1"

async def test_google_login():
    """
    Test Google login with authorization code
    """
    print("=== Testing Google Login API ===")
    
    # This is a sample authorization code - you'll get this from your React app
    # In real usage, this comes from the Google OAuth flow in React
    sample_auth_code = "4/0AVMBsJgemoPHnKMzzqpfbxAJ05bEx2zN18hGvhZjPXud7Q3FTJjDzW-O4a5xg-w27mwFCA"
    
    login_data = {
        "authorization_code": sample_auth_code
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Test login endpoint
            print("1. Testing login endpoint...")
            response = await client.post(f"{BASE_URL}/auth/google/login", json=login_data)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") and result.get("jwt_token"):
                    jwt_token = result["jwt_token"]
                    print(f"Login successful! JWT Token: {jwt_token[:50]}...")
                    
                    # Test token verification
                    print("\n2. Testing token verification...")
                    verify_data = {"token": jwt_token}
                    verify_response = await client.post(f"{BASE_URL}/auth/verify-token", json=verify_data)
                    print(f"Verify Status: {verify_response.status_code}")
                    print(f"Verify Response: {json.dumps(verify_response.json(), indent=2)}")
                    
                    # Test profile endpoint with Bearer token
                    print("\n3. Testing profile endpoint...")
                    headers = {"Authorization": f"Bearer {jwt_token}"}
                    profile_response = await client.get(f"{BASE_URL}/auth/profile", headers=headers)
                    print(f"Profile Status: {profile_response.status_code}")
                    print(f"Profile Response: {json.dumps(profile_response.json(), indent=2)}")
                    
                else:
                    print("Login failed!")
            
        except Exception as e:
            print(f"Error during testing: {str(e)}")

async def test_token_operations():
    """
    Test token verification and refresh operations
    """
    print("\n=== Testing Token Operations ===")
    
    # Test with invalid token
    print("1. Testing with invalid token...")
    invalid_token_data = {"token": "invalid_token_here"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{BASE_URL}/auth/verify-token", json=invalid_token_data)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
        except Exception as e:
            print(f"Error during token testing: {str(e)}")

def print_integration_guide():
    """
    Print integration guide for React app
    """
    print("\n" + "="*60)
    print("INTEGRATION GUIDE FOR REACT APP")
    print("="*60)
    
    print("""
1. Install packages in your React app:
   npm install @google-oauth/google-login

2. Setup Google OAuth in your React component:

   import { useGoogleLogin } from '@google-oauth/google-login';
   
   const login = useGoogleLogin({
     onSuccess: async (codeResponse) => {
       // Send the authorization code to your FastAPI backend
       try {
         const response = await fetch('http://localhost:8000/api/v1/auth/google/login', {
           method: 'POST',
           headers: {
             'Content-Type': 'application/json',
           },
           body: JSON.stringify({
             authorization_code: codeResponse.code
           })
         });
         
         const result = await response.json();
         
         if (result.status) {
           // Login successful
           console.log('User info:', result.user_info);
           console.log('JWT Token:', result.jwt_token);
           
           // Store JWT token for future API calls
           localStorage.setItem('jwt_token', result.jwt_token);
           localStorage.setItem('user_info', JSON.stringify(result.user_info));
           
           // Redirect to dashboard or update UI
         } else {
           console.error('Login failed:', result.message);
         }
       } catch (error) {
         console.error('Login error:', error);
       }
     },
     flow: 'auth-code',
   });

3. Use the stored JWT token for API calls:

   const jwt_token = localStorage.getItem('jwt_token');
   
   // Include in API requests
   const response = await fetch('http://localhost:8000/api/v1/some-protected-endpoint', {
     headers: {
       'Authorization': `Bearer ${jwt_token}`,
       'Content-Type': 'application/json',
     }
   });

4. Environment Variables needed in .env file:
   GOOGLE_CLIENT_ID=your_google_client_id_from_google_console
   GOOGLE_CLIENT_SECRET=your_google_client_secret_from_google_console
   GOOGLE_REDIRECT_URI=http://localhost:3000
   JWT_SECRET=your_secret_key_for_jwt_signing

5. API Endpoints available:
   - POST /api/v1/auth/google/login        - Login with Google
   - POST /api/v1/auth/verify-token        - Verify JWT token
   - POST /api/v1/auth/refresh-token       - Refresh Google access token
   - GET  /api/v1/auth/profile             - Get user profile
    """)

async def main():
    """
    Main function to run all tests
    """
    print("Google Authentication API Test Suite")
    print("=" * 50)
    
    # Note: The actual login test will fail without real Google OAuth setup
    # This is just to show the API structure
    await test_token_operations()
    
    print_integration_guide()
    
    print(f"\nTo test actual Google login:")
    print(f"1. Set up Google OAuth credentials in .env file")
    print(f"2. Get a real authorization code from your React app")
    print(f"3. Replace the sample_auth_code in this script")
    print(f"4. Run: await test_google_login()")

if __name__ == "__main__":
    asyncio.run(main())
