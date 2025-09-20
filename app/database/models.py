"""
Pydantic models for MongoDB collections
"""
from datetime import datetime
from typing import List, Optional, Any, Annotated
from pydantic import BaseModel, Field, EmailStr, field_serializer, field_validator, BeforeValidator
from bson import ObjectId

def validate_object_id(v: Any) -> str:
    """Validate and convert ObjectId to string"""
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, str):
        if ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId string")
    raise ValueError("ObjectId must be a valid ObjectId or string")

# Create a type annotation for ObjectId fields
PyObjectId = Annotated[str, BeforeValidator(validate_object_id)]

# User Models
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    avt: Optional[str] = None

class GoogleUserCreate(BaseModel):
    google_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    picture: Optional[str] = None
    verified_email: Optional[bool] = None
    avt: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    avt: Optional[str] = None

class UserInDB(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    email: str
    password: Optional[str] = None  # For regular users
    google_id: Optional[str] = None  # For Google users
    picture: Optional[str] = None
    verified_email: Optional[bool] = None
    avt: Optional[str] = None  # Avatar field
    auth_type: str = Field(default="local")  # "local" or "google"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('id', mode='before')
    @classmethod
    def validate_id(cls, v):
        if v is None:
            return None
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "str_strip_whitespace": True,
    }

class UserResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    name: str
    email: str
    google_id: Optional[str] = None
    picture: Optional[str] = None
    verified_email: Optional[bool] = None
    avt: Optional[str] = None  # Avatar field
    auth_type: str = "local"
    created_at: datetime
    
    @field_validator('id', mode='before')
    @classmethod
    def validate_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
    
    model_config = {
        "populate_by_name": True,
    }

# Refresh Token Models
class RefreshTokenCreate(BaseModel):
    user_id: PyObjectId
    refresh_token: str = Field(..., min_length=1)
    
    @field_validator('user_id', mode='before')
    @classmethod
    def validate_user_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid user_id ObjectId")

class RefreshTokenInDB(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId
    refresh_token: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('id', 'user_id', mode='before')
    @classmethod
    def validate_object_ids(cls, v):
        if v is None:
            return None
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

class RefreshTokenResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    user_id: PyObjectId
    refresh_token: str
    created_at: datetime
    
    @field_validator('id', 'user_id', mode='before')
    @classmethod
    def validate_object_ids(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
    
    model_config = {
        "populate_by_name": True,
    }

# Input History Models
class InputHistoryCreate(BaseModel):
    words: List[str] = Field(..., min_length=1)

class InputHistoryCreateInternal(BaseModel):
    user_id: PyObjectId
    words: List[str] = Field(..., min_length=1)
    
    @field_validator('user_id', mode='before')
    @classmethod
    def validate_user_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid user_id ObjectId")

class InputHistoryInDB(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId
    words: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('id', 'user_id', mode='before')
    @classmethod
    def validate_object_ids(cls, v):
        if v is None:
            return None
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

class InputHistoryResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    user_id: PyObjectId
    words: List[str]
    created_at: datetime
    
    @field_validator('id', 'user_id', mode='before')
    @classmethod
    def validate_object_ids(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
    
    model_config = {
        "populate_by_name": True,
    }

# Saved Paragraph Models
class SavedParagraphCreate(BaseModel):
    input_history_id: PyObjectId
    paragraph: str = Field(..., min_length=1)
    
    @field_validator('input_history_id', mode='before')
    @classmethod
    def validate_input_history_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid input_history_id ObjectId")

class SavedParagraphInDB(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    input_history_id: PyObjectId
    paragraph: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('id', 'input_history_id', mode='before')
    @classmethod
    def validate_object_ids(cls, v):
        if v is None:
            return None
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

class SavedParagraphResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    input_history_id: PyObjectId
    paragraph: str
    created_at: datetime
    
    @field_validator('id', 'input_history_id', mode='before')
    @classmethod
    def validate_object_ids(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
    
    model_config = {
        "populate_by_name": True,
    }

# Learned Vocabs Models
class LearnedVocabsCreate(BaseModel):
    vocabs: List[str] = Field(..., min_length=1)

class LearnedVocabsCreateInternal(BaseModel):
    user_id: PyObjectId
    vocabs: List[str] = Field(..., min_length=1)
    
    @field_validator('user_id', mode='before')
    @classmethod
    def validate_user_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid user_id ObjectId")

class LearnedVocabsInDB(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId
    vocabs: List[str]
    usage_count: int = Field(default=1)  # Track how many times this vocab set is used
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
    is_deleted: bool = Field(default=False)
    
    @field_validator('id', 'user_id', mode='before')
    @classmethod
    def validate_object_ids(cls, v):
        if v is None:
            return None
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

class LearnedVocabsResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    user_id: PyObjectId
    vocabs: List[str]
    usage_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    is_deleted: bool
    
    @field_validator('id', 'user_id', mode='before')
    @classmethod
    def validate_object_ids(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
    
    model_config = {
        "populate_by_name": True,
    }
