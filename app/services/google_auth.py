import httpx
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import os
from app.utils.logging_conf import get_logger

logger = get_logger("google_auth")

class GoogleAuthService:
    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000")
        self.jwt_secret = os.getenv("JWT_SECRET", "your-secret-key")
        
        if not self.client_id or not self.client_secret:
            logger.warning("Google OAuth credentials not found in environment variables")

    async def exchange_code_for_tokens(self, authorization_code: str, redirect_uri: str = None) -> Dict[str, Any]:
        """
        Exchange authorization code for access token and user info
        """
        try:
            # Use provided redirect_uri or default
            used_redirect_uri = redirect_uri or self.redirect_uri
            
            # Debug log environment variables
            logger.info(f"Using client_id: {self.client_id[:20]}..." if self.client_id else "No client_id")
            logger.info(f"Using redirect_uri: {used_redirect_uri}")
            
            # Prepare token exchange request
            token_url = "https://oauth2.googleapis.com/token"
            
            # Include redirect_uri - Google might still need it even for popup mode
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": authorization_code,
                "grant_type": "authorization_code",
                "redirect_uri": used_redirect_uri
            }
            
            # Debug log request data (without sensitive info)
            debug_data = {k: v for k, v in data.items() if k != "client_secret"}
            debug_data["client_secret"] = "***" if data.get("client_secret") else "MISSING"
            logger.info(f"Token exchange request data: {debug_data}")
            
            # Exchange code for tokens
            async with httpx.AsyncClient() as client:
                response = await client.post(token_url, data=data)
                logger.info(f"Google response status: {response.status_code}")
                response.raise_for_status()
                token_data = response.json()
            
            # Get user info using access token
            user_info = await self.get_user_info(token_data["access_token"])
            
            return {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "id_token": token_data.get("id_token"),
                "user_info": user_info,
                "expires_in": token_data.get("expires_in", 3600)
            }
            
        except httpx.HTTPStatusError as e:
            error_response = e.response.text
            logger.error(f"HTTP error during token exchange: {error_response}")
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response headers: {dict(e.response.headers)}")
            
            # Try to parse error details
            try:
                error_json = e.response.json()
                logger.error(f"Error details: {error_json}")
            except:
                pass
                
            raise Exception(f"Failed to exchange authorization code: {error_response}")
        except Exception as e:
            logger.error(f"Error exchanging authorization code: {str(e)}")
            raise Exception(f"Authentication failed: {str(e)}")

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information from Google using access token
        """
        try:
            user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(user_info_url, headers=headers)
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            raise Exception("Failed to get user information")

    def verify_id_token(self, id_token_str: str) -> Dict[str, Any]:
        """
        Verify Google ID token and extract user information
        """
        try:
            # Verify the token
            id_info = id_token.verify_oauth2_token(
                id_token_str, 
                Request(), 
                self.client_id
            )
            
            # Check issuer
            if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
                
            return id_info
            
        except ValueError as e:
            logger.error(f"Invalid ID token: {str(e)}")
            raise Exception("Invalid ID token")

    def create_jwt_token(self, user_data: Dict[str, Any]) -> str:
        """
        Create JWT token for user session
        """
        payload = {
            "user_id": user_data.get("id"),
            "email": user_data.get("email"),
            "name": user_data.get("name"),
            "picture": user_data.get("picture"),
            "exp": datetime.utcnow() + timedelta(days=7)  # Token expires in 7 days
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and return user data
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            logger.error("JWT token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.error("Invalid JWT token")
            return None

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        """
        try:
            token_url = "https://oauth2.googleapis.com/token"
            
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(token_url, data=data)
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            raise Exception("Failed to refresh access token")

# Global instance
google_auth_service = GoogleAuthService()