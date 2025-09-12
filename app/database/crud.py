"""
Database operations for MongoDB collections
"""
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
import bcrypt

from app.database.connection import get_collection
from app.database.models import (
    UserCreate, UserInDB, UserUpdate, UserResponse,
    InputHistoryCreate, InputHistoryInDB, InputHistoryResponse,
    SavedParagraphCreate, SavedParagraphInDB, SavedParagraphResponse
)

class UserCRUD:
    """CRUD operations for Users collection"""
    
    @property
    def collection(self) -> AsyncIOMotorCollection:
        return get_collection("users")
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    async def create_user(self, user_data: UserCreate) -> UserInDB:
        """Create new user"""
        # Hash password
        hashed_password = self.hash_password(user_data.password)
        
        # Create user document
        user_dict = user_data.dict()
        user_dict['password'] = hashed_password
        
        # Insert to database
        result = await self.collection.insert_one(user_dict)
        
        # Return created user
        created_user = await self.collection.find_one({"_id": result.inserted_id})
        return UserInDB(**created_user)
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID"""
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        return UserInDB(**user) if user else None
    
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email"""
        user = await self.collection.find_one({"email": email})
        return UserInDB(**user) if user else None
    
    async def update_user(self, user_id: str, update_data: UserUpdate) -> Optional[UserInDB]:
        """Update user"""
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        
        if update_dict:
            await self.collection.update_one(
                {"_id": ObjectId(user_id)}, 
                {"$set": update_dict}
            )
        
        return await self.get_user_by_id(user_id)
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

class InputHistoryCRUD:
    """CRUD operations for Input History collection"""
    
    @property
    def collection(self) -> AsyncIOMotorCollection:
        return get_collection("input_history")
    
    async def create_input_history(self, history_data: InputHistoryCreate) -> InputHistoryInDB:
        """Create new input history"""
        history_dict = history_data.dict()
        # Convert user_id string to ObjectId for storage
        history_dict['user_id'] = ObjectId(history_dict['user_id'])
        
        # Insert to database
        result = await self.collection.insert_one(history_dict)
        
        # Return created history
        created_history = await self.collection.find_one({"_id": result.inserted_id})
        return InputHistoryInDB(**created_history)
    
    async def get_input_history_by_id(self, history_id: str) -> Optional[InputHistoryInDB]:
        """Get input history by ID"""
        history = await self.collection.find_one({"_id": ObjectId(history_id)})
        return InputHistoryInDB(**history) if history else None
    
    async def get_user_input_history(self, user_id: str, limit: int = 50) -> List[InputHistoryInDB]:
        """Get input history for a user"""
        cursor = self.collection.find({"user_id": ObjectId(user_id)}).sort("created_at", -1).limit(limit)
        histories = []
        async for history in cursor:
            histories.append(InputHistoryInDB(**history))
        return histories
    
    async def find_by_exact_words(self, user_id: str, words: List[str]) -> Optional[InputHistoryInDB]:
        """Find input history by exact word match for a user"""
        # Sort words for consistent comparison
        sorted_words = sorted([word.lower().strip() for word in words if word.strip()])
        
        # Find all input histories for the user
        cursor = self.collection.find({"user_id": ObjectId(user_id)})
        
        async for history in cursor:
            # Normalize existing words for comparison
            existing_words = sorted([word.lower().strip() for word in history.get('words', []) if word.strip()])
            
            # Check if words match exactly
            if existing_words == sorted_words:
                return InputHistoryInDB(**history)
        
        return None
    
    async def delete_input_history(self, history_id: str) -> bool:
        """Delete input history"""
        result = await self.collection.delete_one({"_id": ObjectId(history_id)})
        return result.deleted_count > 0

class SavedParagraphCRUD:
    """CRUD operations for Saved Paragraph collection"""
    
    @property
    def collection(self) -> AsyncIOMotorCollection:
        return get_collection("saved_paragraph")
    
    async def create_saved_paragraph(self, paragraph_data: SavedParagraphCreate) -> SavedParagraphInDB:
        """Create new saved paragraph"""
        paragraph_dict = paragraph_data.dict()
        # Convert input_history_id string to ObjectId for storage
        paragraph_dict['input_history_id'] = ObjectId(paragraph_dict['input_history_id'])
        
        # Insert to database
        result = await self.collection.insert_one(paragraph_dict)
        
        # Return created paragraph
        created_paragraph = await self.collection.find_one({"_id": result.inserted_id})
        return SavedParagraphInDB(**created_paragraph)
    
    async def get_saved_paragraph_by_id(self, paragraph_id: str) -> Optional[SavedParagraphInDB]:
        """Get saved paragraph by ID"""
        paragraph = await self.collection.find_one({"_id": ObjectId(paragraph_id)})
        return SavedParagraphInDB(**paragraph) if paragraph else None
    
    async def get_paragraphs_by_input_history(self, input_history_id: str) -> List[SavedParagraphInDB]:
        """Get paragraphs by input history ID"""
        cursor = self.collection.find({"input_history_id": ObjectId(input_history_id)}).sort("created_at", -1)
        paragraphs = []
        async for paragraph in cursor:
            paragraphs.append(SavedParagraphInDB(**paragraph))
        return paragraphs
    
    async def get_user_saved_paragraphs(self, user_id: str, limit: int = 50) -> List[dict]:
        """Get saved paragraphs for a user with input history info"""
        pipeline = [
            {
                "$lookup": {
                    "from": "input_history",
                    "localField": "input_history_id",
                    "foreignField": "_id",
                    "as": "input_history"
                }
            },
            {
                "$unwind": "$input_history"
            },
            {
                "$match": {
                    "input_history.user_id": ObjectId(user_id)
                }
            },
            {
                "$sort": {"created_at": -1}
            },
            {
                "$limit": limit
            }
        ]
        
        paragraphs = []
        async for paragraph in self.collection.aggregate(pipeline):
            paragraphs.append(paragraph)
        return paragraphs
    
    async def delete_saved_paragraph(self, paragraph_id: str) -> bool:
        """Delete saved paragraph"""
        result = await self.collection.delete_one({"_id": ObjectId(paragraph_id)})
        return result.deleted_count > 0

# Create CRUD instances (lazy initialization)
def get_user_crud():
    return UserCRUD()

def get_input_history_crud():
    return InputHistoryCRUD()

def get_saved_paragraph_crud():
    return SavedParagraphCRUD()
