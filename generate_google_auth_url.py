#!/usr/bin/env python3
"""
Generate a Google OAuth authorization URL for testing
"""
import os
from dotenv import load_dotenv
from urllib.parse import urlencode

# Load environment variables
load_dotenv()

def generate_auth_url():
    """Generate a Google OAuth authorization URL"""
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:5173/app")
    
    # Google OAuth2 authorization endpoint
    auth_base_url = "https://accounts.google.com/o/oauth2/auth"
    
    # Parameters for the authorization request
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": "openid email profile",
        "response_type": "code",
        "access_type": "offline",  # Request refresh token
        "prompt": "consent",       # Force consent screen to get refresh token
        "state": "test_state_12345"  # CSRF protection
    }
    
    # Build the full URL
    auth_url = f"{auth_base_url}?{urlencode(params)}"
    
    print("🔗 Google OAuth Authorization URL:")
    print(f"{auth_url}\n")
    
    print("📋 Instructions:")
    print("1. Copy the URL above and paste it in your browser")
    print("2. Sign in with your Google account")
    print("3. Grant permissions")
    print("4. Copy the authorization code from the redirect URL")
    print("5. Use the code to test the /api/v1/google/login endpoint")
    print("\n🌐 Expected redirect format:")
    print(f"{redirect_uri}?code=YOUR_AUTH_CODE&state=test_state_12345")
    
    return auth_url

if __name__ == "__main__":
    generate_auth_url()