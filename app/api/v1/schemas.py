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

# === Vocab Collections ===
class VocabCollectionCreateRequest(BaseModel):
    name: str

class VocabCollectionUpdateRequest(BaseModel):
    name: str

class VocabCollectionResponse(BaseModel):
    id: str
    name: str
    user_id: str
    created_at: str
    updated_at: Optional[str] = None
    status: bool = True

class VocabCollectionsListResponse(BaseModel):
    collections: List[VocabCollectionResponse]
    total: int
    status: bool

# === History by Date ===
class StudySessionRequest(BaseModel):
    vocab_id: str
    study_date: Optional[str] = None  # ISO format date string (YYYY-MM-DD) or datetime

class StudySessionResponse(BaseModel):
    id: str
    vocab_id: str
    study_date: str  # Will be returned as YYYY-MM-DD format
    count: int
    created_at: str
    status: bool = True

class StudyHistoryResponse(BaseModel):
    history: List[dict]  # Contains vocab info and study data
    total: int
    status: bool

# === User Feedback ===
class UserFeedbackRequest(BaseModel):
    email: str
    name: Optional[str] = None
    message: str

class UserFeedbackResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    message: str
    created_at: str
    status: bool = True

class UserFeedbackListResponse(BaseModel):
    feedbacks: List[UserFeedbackResponse]
    total: int
    status: bool

# === Updated Learned Vocabs (with collection support) ===
class LearnedVocabsCreateRequest(BaseModel):
    vocabs: List[str]  # Request still accepts a list of vocabs
    collection_id: str  # Now required since user_id is in collections

class LearnedVocabsResponse(BaseModel):
    id: str
    vocab: str  # Changed to single string
    collection_id: str  # Now required
    usage_count: int
    created_at: str
    updated_at: Optional[str] = None
    is_new: bool = False
    usage_incremented: bool = False
    status: bool = True

class LearnedVocabsBatchResponse(BaseModel):
    """Response for batch creation of learned vocabs"""
    created: List[LearnedVocabsResponse]
    total_created: int
    status: bool = True
