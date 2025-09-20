from pydantic import BaseModel
from typing import List, Optional

# === Generic generation ===
class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 256

class GenerateResponse(BaseModel):
    result: str
    status: bool


# === English lesson ===
class LessonRequest(BaseModel):
    topic: str
    max_tokens: Optional[int] = 300

class LessonResponse(BaseModel):
    topic: str
    lesson: str
    status: bool

    

# === Paragraph with vocabularies ===
class ParagraphRequest(BaseModel):
    language: str
    vocabularies: List[str]
    length: int
    level: str
    prompt: Optional[str] = None
    tone: Optional[str] = None
    topic : Optional[str] = None

class ParagraphResponse(BaseModel):
    result: str
    status: bool

# === Save paragraph and vocabularies ===
class SaveParagraphRequest(BaseModel):
    vocabs: List[str]
    paragraph: str

class SaveParagraphResponse(BaseModel):
    input_history_id: str
    saved_paragraph_id: str
    message: str
    status: bool

# === Get saved paragraphs ===
class ParagraphInfo(BaseModel):
    id: str
    paragraph: str
    created_at: str

class SavedParagraphItem(BaseModel):
    id: str
    vocabs: List[str]
    paragraph: str
    created_at: str
    # Optional fields for grouped response
    is_group: Optional[bool] = False
    paragraphs: Optional[List[ParagraphInfo]] = []
    total_paragraphs: Optional[int] = 0

class GetAllParagraphsResponse(BaseModel):
    data: List[SavedParagraphItem]
    total: int
    status: bool

# === Unique vocabularies ===
class VocabFrequency(BaseModel):
    vocab: str
    frequency: int

class UniqueVocabsResponse(BaseModel):
    status: bool
    total_unique: int
    unique_vocabs: List[str]
    frequency_data: List[VocabFrequency]
    message: str

# === Google Authentication ===
class GoogleLoginRequest(BaseModel):
    authorization_code: str

class UserInfo(BaseModel):
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    verified_email: Optional[bool] = None

class GoogleLoginResponse(BaseModel):
    jwt_token: str
    jwt_refresh_token: str

class TokenVerifyRequest(BaseModel):
    token: str

class TokenVerifyResponse(BaseModel):
    status: bool
    message: str
    user_data: Optional[dict] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    status: bool
    message: str
    access_token: Optional[str] = None
    expires_in: Optional[int] = None

# === JWT Token Renewal ===
class RenewJWTRequest(BaseModel):
    jwt_refresh_token: str

class RenewJWTResponse(BaseModel):
    status: bool
    message: str
    jwt_token: str
    user_data: Optional[dict] = None

# === Logout ===
class LogoutResponse(BaseModel):
    status: bool
    message: str

# === Delete Vocabulary ===
class DeleteVocabRequest(BaseModel):
    vocab: str

class DeleteVocabResponse(BaseModel):
    status: bool
    message: str
    deleted_count: int
