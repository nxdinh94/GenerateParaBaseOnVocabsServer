#!/usr/bin/env python3
"""
Test Google OAuth credentials loading
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.services.google_auth import google_auth_service
    
    print("✅ Environment variables loaded:")
    print(f"   GOOGLE_CLIENT_ID: {os.getenv('GOOGLE_CLIENT_ID')[:20]}..." if os.getenv('GOOGLE_CLIENT_ID') else "❌ GOOGLE_CLIENT_ID: None")
    print(f"   GOOGLE_CLIENT_SECRET: {'SET' if os.getenv('GOOGLE_CLIENT_SECRET') else 'None'}")
    print(f"   JWT_SECRET: {'SET' if os.getenv('JWT_SECRET') else 'None'}")
    
    print("\n✅ Google Auth Service initialized:")
    print(f"   client_id: {google_auth_service.client_id[:20]}..." if google_auth_service.client_id else "❌ No client_id")
    print(f"   client_secret: {'SET' if google_auth_service.client_secret else 'NOT SET'}")
    print(f"   redirect_uri: {google_auth_service.redirect_uri}")
    print(f"   jwt_secret: {'SET' if google_auth_service.jwt_secret else 'NOT SET'}")
    
    if google_auth_service.client_id and google_auth_service.client_secret:
        print("\n🎉 Google OAuth credentials are properly configured!")
        print("The 500 error should be resolved after restarting the server.")
    else:
        print("\n❌ Google OAuth credentials are still missing!")
        
except Exception as e:
    print(f"💥 Error: {e}")
    import traceback
    traceback.print_exc()