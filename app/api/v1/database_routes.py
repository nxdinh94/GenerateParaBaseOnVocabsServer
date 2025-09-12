"""
API routes for database operations
"""
from typing import List
from fastapi import APIRouter, HTTPException, status
from bson import ObjectId

from app.database.crud import get_user_crud, get_input_history_crud, get_saved_paragraph_crud
from app.database.models import (
    UserCreate, UserResponse, UserUpdate,
    InputHistoryCreate, InputHistoryResponse,
    SavedParagraphCreate, SavedParagraphResponse
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

# Input History routes
@router.post("/input-history/", response_model=InputHistoryResponse, status_code=status.HTTP_201_CREATED)
async def create_input_history(history_data: InputHistoryCreate):
    """Create new input history"""
    user_crud = get_user_crud()
    input_history_crud = get_input_history_crud()
    
    # Verify user exists
    user = await user_crud.get_user_by_id(str(history_data.user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    
    history = await input_history_crud.create_input_history(history_data)
    return InputHistoryResponse(**history.dict())

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
