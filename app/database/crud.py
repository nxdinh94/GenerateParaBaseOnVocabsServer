"""
Database operations for MongoDB collections
"""
from typing import List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
import bcrypt
import secrets
import string

from app.database.connection import get_collection
from app.database.models import (
    UserCreate, GoogleUserCreate, UserInDB, UserUpdate, UserResponse,
    RefreshTokenCreate, RefreshTokenInDB, RefreshTokenResponse,
    InputHistoryCreate, InputHistoryCreateInternal, InputHistoryInDB, InputHistoryResponse,
    SavedParagraphCreate, SavedParagraphInDB, SavedParagraphResponse,
    LearnedVocabsCreate, LearnedVocabsCreateInternal, LearnedVocabsInDB, LearnedVocabsResponse
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
    
    def generate_random_password(self, length: int = 16) -> str:
        """Generate a random password for OAuth users"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    async def create_user(self, user_data: UserCreate) -> UserInDB:
        """Create new user"""
        # Hash password
        hashed_password = self.hash_password(user_data.password)
        
        # Create user document
        user_dict = user_data.dict()
        user_dict['password'] = hashed_password
        user_dict['auth_type'] = 'local'
        user_dict['created_at'] = datetime.utcnow()  # Ensure created_at is set
        
        # Insert to database
        result = await self.collection.insert_one(user_dict)
        
        # Return created user
        created_user = await self.collection.find_one({"_id": result.inserted_id})
        return UserInDB(**created_user)
    
    async def create_google_user(self, user_data: GoogleUserCreate) -> UserInDB:
        """Create new Google user"""
        # Generate random password for OAuth users (required by schema)
        random_password = self.generate_random_password()
        hashed_password = self.hash_password(random_password)
        
        # Create user document
        user_dict = user_data.dict()
        user_dict['auth_type'] = 'google'
        user_dict['password'] = hashed_password  # Add required password field
        user_dict['created_at'] = datetime.utcnow()  # Add required created_at field
        
        # Insert to database
        result = await self.collection.insert_one(user_dict)
        
        # Return created user
        created_user = await self.collection.find_one({"_id": result.inserted_id})
        return UserInDB(**created_user)
    
    async def get_user_by_google_id(self, google_id: str) -> Optional[UserInDB]:
        """Get user by Google ID"""
        user = await self.collection.find_one({"google_id": google_id, "auth_type": "google"})
        return UserInDB(**user) if user else None
    
    async def update_google_user(self, google_id: str, user_data: dict) -> Optional[UserInDB]:
        """Update Google user data"""
        update_dict = {
            "name": user_data.get("name"),
            "email": user_data.get("email"),
            "picture": user_data.get("picture"),
            "verified_email": user_data.get("verified_email"),
            "avt": user_data.get("avt")
        }
        
        # Remove None values
        update_dict = {k: v for k, v in update_dict.items() if v is not None}
        
        if update_dict:
            await self.collection.update_one(
                {"google_id": google_id, "auth_type": "google"}, 
                {"$set": update_dict}
            )
        
        return await self.get_user_by_google_id(google_id)
    
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

class RefreshTokenCRUD:
    """CRUD operations for RefreshTokens collection"""
    
    @property
    def collection(self) -> AsyncIOMotorCollection:
        return get_collection("refresh_tokens")
    
    async def create_refresh_token(self, token_data: RefreshTokenCreate) -> RefreshTokenInDB:
        """Create new refresh token"""
        token_dict = token_data.dict()
        # Convert user_id string to ObjectId for storage
        token_dict['user_id'] = ObjectId(token_dict['user_id'])
        token_dict['created_at'] = datetime.utcnow()  # Add required created_at field
        
        # Insert to database
        result = await self.collection.insert_one(token_dict)
        
        # Return created token
        created_token = await self.collection.find_one({"_id": result.inserted_id})
        return RefreshTokenInDB(**created_token)
    
    async def get_refresh_token_by_token(self, refresh_token: str) -> Optional[RefreshTokenInDB]:
        """Get refresh token by token string"""
        token = await self.collection.find_one({"refresh_token": refresh_token})
        return RefreshTokenInDB(**token) if token else None
    
    async def get_user_refresh_tokens(self, user_id: str) -> List[RefreshTokenInDB]:
        """Get all refresh tokens for a user"""
        cursor = self.collection.find({"user_id": ObjectId(user_id)}).sort("created_at", -1)
        tokens = []
        async for token in cursor:
            tokens.append(RefreshTokenInDB(**token))
        return tokens
    
    async def delete_refresh_token(self, refresh_token: str) -> bool:
        """Delete a refresh token"""
        result = await self.collection.delete_one({"refresh_token": refresh_token})
        return result.deleted_count > 0
    
    async def delete_user_refresh_tokens(self, user_id: str) -> int:
        """Delete all refresh tokens for a user"""
        result = await self.collection.delete_many({"user_id": ObjectId(user_id)})
        return result.deleted_count
    
    async def cleanup_expired_tokens(self, expiry_days: int = 30) -> int:
        """Clean up tokens older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=expiry_days)
        result = await self.collection.delete_many({"created_at": {"$lt": cutoff_date}})
        return result.deleted_count

class InputHistoryCRUD:
    """CRUD operations for Input History collection"""
    
    @property
    def collection(self) -> AsyncIOMotorCollection:
        return get_collection("input_history")
    
    async def create_input_history(self, history_data: InputHistoryCreateInternal) -> InputHistoryInDB:
        """Create new input history"""
        history_dict = history_data.dict()
        # Convert user_id string to ObjectId for storage
        history_dict['user_id'] = ObjectId(history_dict['user_id'])
        history_dict['created_at'] = datetime.utcnow()  # Add required created_at field
        
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
        # Normalize and sort words for consistent comparison
        def normalize_words(word_list):
            # Filter out empty/whitespace-only words, convert to lowercase, strip, and sort
            normalized = []
            for word in word_list:
                if isinstance(word, str):
                    cleaned = word.strip().lower()
                    if cleaned:  # Only add non-empty words
                        normalized.append(cleaned)
            return sorted(normalized)
        
        target_words = normalize_words(words)
        print(f"🔍 DEBUG: Looking for normalized words: {target_words}")
        
        # Don't search if no valid words provided
        if not target_words:
            print("⚠️ DEBUG: No valid words provided, returning None")
            return None
        
        # Find all input histories for the user
        cursor = self.collection.find({"user_id": ObjectId(user_id)})
        
        count = 0
        async for history in cursor:
            count += 1
            # Get the words from the document
            history_words = history.get('words', [])
            existing_words = normalize_words(history_words)
            print(f"🔍 DEBUG: Comparing with existing #{count}: {existing_words}")
            
            # Check if words match exactly
            if existing_words == target_words:
                print(f"✅ DEBUG: Match found at record #{count}!")
                return InputHistoryInDB(**history)
        
        print(f"❌ DEBUG: No match found among {count} records")
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
        paragraph_dict['created_at'] = datetime.utcnow()  # Add required created_at field
        
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

class LearnedVocabsCRUD:
    """CRUD operations for Learned Vocabs collection"""
    
    @property
    def collection(self) -> AsyncIOMotorCollection:
        return get_collection("learned_vocabs")
    
    async def create_learned_vocabs(self, vocabs_data: LearnedVocabsCreateInternal) -> LearnedVocabsInDB:
        """Create new learned vocabs entry"""
        vocabs_dict = vocabs_data.dict()
        # Convert user_id string to ObjectId for storage
        vocabs_dict['user_id'] = ObjectId(vocabs_dict['user_id'])
        current_time = datetime.utcnow()
        vocabs_dict['created_at'] = current_time
        vocabs_dict['updated_at'] = current_time
        vocabs_dict['is_deleted'] = False
        vocabs_dict['deleted_at'] = None
        vocabs_dict['usage_count'] = 1  # Initialize usage count
        
        # Insert to database
        result = await self.collection.insert_one(vocabs_dict)
        
        # Return created entry
        created_vocabs = await self.collection.find_one({"_id": result.inserted_id})
        return LearnedVocabsInDB(**created_vocabs)
    
    async def get_learned_vocabs_by_id(self, vocabs_id: str) -> Optional[LearnedVocabsInDB]:
        """Get learned vocabs by ID"""
        vocabs = await self.collection.find_one({"_id": ObjectId(vocabs_id), "is_deleted": False})
        return LearnedVocabsInDB(**vocabs) if vocabs else None
    
    async def get_user_learned_vocabs(self, user_id: str, limit: int = 50) -> List[LearnedVocabsInDB]:
        """Get learned vocabs for a user, sorted by created_at descending (newest first)"""
        cursor = self.collection.find({"user_id": ObjectId(user_id), "is_deleted": False}).sort("created_at", -1).limit(limit)
        vocabs_list = []
        async for vocabs in cursor:
            vocabs_list.append(LearnedVocabsInDB(**vocabs))
        return vocabs_list
    
    async def find_by_exact_vocabs(self, user_id: str, vocabs: List[str]) -> Optional[LearnedVocabsInDB]:
        """Find learned vocabs by exact vocab match for a user"""
        # Normalize and sort vocabs for consistent comparison
        def normalize_vocabs(vocab_list):
            # Filter out empty/whitespace-only vocabs, convert to lowercase, strip, and sort
            normalized = []
            for vocab in vocab_list:
                if isinstance(vocab, str):
                    cleaned = vocab.strip().lower()
                    if cleaned:  # Only add non-empty vocabs
                        normalized.append(cleaned)
            return sorted(normalized)
        
        target_vocabs = normalize_vocabs(vocabs)
        print(f"🔍 DEBUG: Looking for normalized vocabs: {target_vocabs}")
        
        # Don't search if no valid vocabs provided
        if not target_vocabs:
            print("⚠️ DEBUG: No valid vocabs provided, returning None")
            return None
        
        # Find all learned vocabs for the user
        cursor = self.collection.find({"user_id": ObjectId(user_id), "is_deleted": False})
        
        count = 0
        async for vocabs_entry in cursor:
            count += 1
            # Get the vocabs from the document
            entry_vocabs = vocabs_entry.get('vocabs', [])
            existing_vocabs = normalize_vocabs(entry_vocabs)
            print(f"🔍 DEBUG: Comparing with existing #{count}: {existing_vocabs}")
            
            # Check if vocabs match exactly
            if existing_vocabs == target_vocabs:
                print(f"✅ DEBUG: Match found at record #{count}!")
                return LearnedVocabsInDB(**vocabs_entry)
        
        print(f"❌ DEBUG: No match found among {count} records")
        return None
    
    async def get_all_user_vocabs(self, user_id: str) -> List[str]:
        """Get all unique vocabs learned by a user"""
        cursor = self.collection.find({"user_id": ObjectId(user_id), "is_deleted": False})
        
        all_vocabs = set()
        async for vocabs_entry in cursor:
            for vocab in vocabs_entry.get('vocabs', []):
                cleaned_vocab = vocab.strip().lower()
                if cleaned_vocab:
                    all_vocabs.add(cleaned_vocab)
        
        return sorted(list(all_vocabs))
    
    async def update_learned_vocabs(self, vocabs_id: str, new_vocabs: List[str]) -> Optional[LearnedVocabsInDB]:
        """Update learned vocabs entry"""
        update_dict = {
            "vocabs": new_vocabs,
            "updated_at": datetime.utcnow()
        }
        
        await self.collection.update_one(
            {"_id": ObjectId(vocabs_id), "is_deleted": False}, 
            {"$set": update_dict}
        )
        
        return await self.get_learned_vocabs_by_id(vocabs_id)
    
    async def increment_usage_count(self, vocabs_id: str) -> Optional[LearnedVocabsInDB]:
        """Increment usage count for learned vocabs entry"""
        update_dict = {
            "$inc": {"usage_count": 1},  # Increment usage_count by 1
            "$set": {"updated_at": datetime.utcnow()}
        }
        
        await self.collection.update_one(
            {"_id": ObjectId(vocabs_id), "is_deleted": False}, 
            update_dict
        )
        
        return await self.get_learned_vocabs_by_id(vocabs_id)
    
    async def soft_delete_learned_vocabs(self, vocabs_id: str) -> bool:
        """Soft delete learned vocabs entry"""
        update_dict = {
            "is_deleted": True,
            "deleted_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await self.collection.update_one(
            {"_id": ObjectId(vocabs_id), "is_deleted": False}, 
            {"$set": update_dict}
        )
        return result.modified_count > 0
    
    async def delete_learned_vocabs(self, vocabs_id: str) -> bool:
        """Hard delete learned vocabs entry"""
        result = await self.collection.delete_one({"_id": ObjectId(vocabs_id)})
        return result.deleted_count > 0
    
    async def delete_vocabs_containing_word(self, user_id: str, word: str) -> int:
        """Delete all learned vocabs entries containing the specified word for a user"""
        # Normalize the word for comparison
        normalized_word = word.strip().lower()
        
        if not normalized_word:
            return 0
        
        # Find all user's learned vocabs entries that contain the word
        cursor = self.collection.find({"user_id": ObjectId(user_id), "is_deleted": False})
        
        entries_to_delete = []
        async for vocabs_entry in cursor:
            entry_vocabs = vocabs_entry.get('vocabs', [])
            # Check if any vocab in the entry matches the target word
            for vocab in entry_vocabs:
                if isinstance(vocab, str) and vocab.strip().lower() == normalized_word:
                    entries_to_delete.append(vocabs_entry['_id'])
                    break  # Found the word in this entry, no need to check other vocabs
        
        # Delete all matching entries
        if entries_to_delete:
            result = await self.collection.delete_many({"_id": {"$in": entries_to_delete}})
            return result.deleted_count
        
        return 0

# Create CRUD instances (lazy initialization)
def get_user_crud():
    return UserCRUD()

def get_refresh_token_crud():
    return RefreshTokenCRUD()

def get_input_history_crud():
    return InputHistoryCRUD()

def get_saved_paragraph_crud():
    return SavedParagraphCRUD()

def get_learned_vocabs_crud():
    return LearnedVocabsCRUD()
