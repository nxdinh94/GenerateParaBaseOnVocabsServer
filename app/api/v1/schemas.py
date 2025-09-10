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
