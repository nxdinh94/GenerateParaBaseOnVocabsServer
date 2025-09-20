"""
API routes for database operations
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Header, Response
from bson import ObjectId

from app.database.crud import get_user_crud, get_input_history_crud, get_saved_paragraph_crud, get_learned_vocabs_crud
from app.database.models import (
    UserCreate, UserResponse, UserUpdate,
    InputHistoryCreate, InputHistoryCreateInternal, InputHistoryResponse,
    SavedParagraphCreate, SavedParagraphResponse,
    LearnedVocabsCreate, LearnedVocabsCreateInternal, LearnedVocabsResponse
)

router = APIRouter(prefix="/db", tags=["Database"])

# User routes
@router.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """Create new user"""
    user_crud = get_user_crud()
    
    # Check if email already exists
    existing_user = await user_crud.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = await user_crud.create_user(user_data)
    return UserResponse(**user.dict())

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by ID"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    user_crud = get_user_crud()
    user = await user_crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**user.dict())

@router.get("/users/email/{email}", response_model=UserResponse)
async def get_user_by_email(email: str):
    """Get user by email"""
    user_crud = get_user_crud()
    user = await user_crud.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**user.dict())

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, update_data: UserUpdate):
    """Update user"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    user_crud = get_user_crud()
    user = await user_crud.update_user(user_id, update_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**user.dict())

@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """Delete user"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    user_crud = get_user_crud()
    deleted = await user_crud.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deleted successfully"}

# Input History routes (now using learned_vocabs collection)
@router.post("/input-history/", response_model=InputHistoryResponse)
async def create_input_history(history_data: InputHistoryCreate, response: Response, authorization: Optional[str] = Header(None)):
    """Create new input history or return existing one if vocabulary already exists
    Now saves data to learned_vocabs collection instead of input_history"""
    from app.api.v1.routes import get_current_user
    
    # Get current user from JWT token
    current_user = await get_current_user(authorization)
    user_id = current_user.get("user_id") or current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail={
            "error": "invalid_user_data",
            "message": "User ID not found in token (missing both 'user_id' and 'id' fields)"
        })
    
    learned_vocabs_crud = get_learned_vocabs_crud()
    
    # Debug: Log the incoming request
    print(f"🔍 DEBUG: Checking for duplicate vocabs {history_data.words} for user {user_id}")
    
    # Check if learned vocabs with same words already exists for this user
    existing_vocabs = await learned_vocabs_crud.find_by_exact_vocabs(user_id, history_data.words)
    
    if existing_vocabs:
        # Return existing vocabs as InputHistoryResponse format for backward compatibility
        print(f"✅ DEBUG: Found existing learned vocabs with ID {existing_vocabs.id}")
        response.status_code = status.HTTP_200_OK
        return InputHistoryResponse(
            id=existing_vocabs.id,
            user_id=existing_vocabs.user_id,
            words=existing_vocabs.vocabs,
            created_at=existing_vocabs.created_at
        )
    
    # Debug: Log that we're creating new entry
    print(f"🆕 DEBUG: No duplicate found, creating new learned vocabs entry")
    
    # Create learned vocabs data with user_id from token
    vocabs_create_data = LearnedVocabsCreateInternal(
        user_id=user_id,
        vocabs=history_data.words
    )
    
    # Create new learned vocabs entry
    learned_vocabs = await learned_vocabs_crud.create_learned_vocabs(vocabs_create_data)
    response.status_code = status.HTTP_201_CREATED
    
    # Return as InputHistoryResponse format for backward compatibility
    return InputHistoryResponse(
        id=learned_vocabs.id,
        user_id=learned_vocabs.user_id,
        words=learned_vocabs.vocabs,
        created_at=learned_vocabs.created_at
    )

@router.get("/input-history/{history_id}", response_model=InputHistoryResponse)
async def get_input_history(history_id: str):
    """Get input history by ID"""
    if not ObjectId.is_valid(history_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid history ID"
        )
    
    input_history_crud = get_input_history_crud()
    history = await input_history_crud.get_input_history_by_id(history_id)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Input history not found"
        )
    
    return InputHistoryResponse(**history.dict())

@router.get("/users/{user_id}/input-history", response_model=List[InputHistoryResponse])
async def get_user_input_history(user_id: str, limit: int = 50):
    """Get input history for a user"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    input_history_crud = get_input_history_crud()
    histories = await input_history_crud.get_user_input_history(user_id, limit)
    return [InputHistoryResponse(**history.dict()) for history in histories]

# Saved Paragraph routes
@router.post("/saved-paragraphs/", response_model=SavedParagraphResponse, status_code=status.HTTP_201_CREATED)
async def create_saved_paragraph(paragraph_data: SavedParagraphCreate):
    """Create new saved paragraph"""
    input_history_crud = get_input_history_crud()
    saved_paragraph_crud = get_saved_paragraph_crud()
    
    # Verify input history exists
    history = await input_history_crud.get_input_history_by_id(str(paragraph_data.input_history_id))
    if not history:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input history not found"
        )
    
    paragraph = await saved_paragraph_crud.create_saved_paragraph(paragraph_data)
    return SavedParagraphResponse(**paragraph.dict())

@router.get("/saved-paragraphs/{paragraph_id}", response_model=SavedParagraphResponse)
async def get_saved_paragraph(paragraph_id: str):
    """Get saved paragraph by ID"""
    if not ObjectId.is_valid(paragraph_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid paragraph ID"
        )
    
    saved_paragraph_crud = get_saved_paragraph_crud()
    paragraph = await saved_paragraph_crud.get_saved_paragraph_by_id(paragraph_id)
    if not paragraph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved paragraph not found"
        )
    
    return SavedParagraphResponse(**paragraph.dict())

@router.get("/input-history/{history_id}/saved-paragraphs", response_model=List[SavedParagraphResponse])
async def get_paragraphs_by_input_history(history_id: str):
    """Get saved paragraphs by input history ID"""
    if not ObjectId.is_valid(history_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid history ID"
        )
    
    saved_paragraph_crud = get_saved_paragraph_crud()
    paragraphs = await saved_paragraph_crud.get_paragraphs_by_input_history(history_id)
    return [SavedParagraphResponse(**paragraph.dict()) for paragraph in paragraphs]

@router.get("/users/{user_id}/saved-paragraphs")
async def get_user_saved_paragraphs(user_id: str, limit: int = 50):
    """Get saved paragraphs for a user with input history info"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    saved_paragraph_crud = get_saved_paragraph_crud()
    paragraphs = await saved_paragraph_crud.get_user_saved_paragraphs(user_id, limit)
    return paragraphs
