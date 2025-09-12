"""
CRUD operations for refresh tokens
"""
from typing import Optional, List
from datetime import datetime, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.models import RefreshTokenCreate, RefreshTokenInDB, RefreshTokenResponse
from app.database.connection import get_collection

class RefreshTokenCRUD:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.refresh_tokens
    
    async def create(self, token_data: RefreshTokenCreate) -> RefreshTokenResponse:
        """Create a new refresh token"""
        token_dict = token_data.model_dump()
        token_dict["created_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(token_dict)
        
        # Retrieve the created document
        created_token = await self.collection.find_one({"_id": result.inserted_id})
        return RefreshTokenResponse.model_validate(created_token)
    
    async def get_by_token(self, refresh_token: str) -> Optional[RefreshTokenResponse]:
        """Get refresh token by token string"""
        token_doc = await self.collection.find_one({"refresh_token": refresh_token})
        if token_doc:
            return RefreshTokenResponse.model_validate(token_doc)
        return None
    
    async def get_by_user_id(self, user_id: str) -> List[RefreshTokenResponse]:
        """Get all refresh tokens for a user"""
        cursor = self.collection.find({"user_id": ObjectId(user_id)}).sort("created_at", -1)
        tokens = []
        async for token_doc in cursor:
            tokens.append(RefreshTokenResponse.model_validate(token_doc))
        return tokens
    
    async def delete_by_token(self, refresh_token: str) -> bool:
        """Delete a refresh token"""
        result = await self.collection.delete_one({"refresh_token": refresh_token})
        return result.deleted_count > 0
    
    async def delete_by_user_id(self, user_id: str) -> int:
        """Delete all refresh tokens for a user"""
        result = await self.collection.delete_many({"user_id": ObjectId(user_id)})
        return result.deleted_count
    
    async def cleanup_expired(self, expiry_days: int = 30) -> int:
        """Clean up tokens older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=expiry_days)
        result = await self.collection.delete_many({"created_at": {"$lt": cutoff_date}})
        return result.deleted_count

# Convenience function to get CRUD instance
def get_refresh_token_crud(database: AsyncIOMotorDatabase) -> RefreshTokenCRUD:
    return RefreshTokenCRUD(database)