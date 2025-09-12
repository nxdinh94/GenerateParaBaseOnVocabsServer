# Avatar Field Implementation

## Overview
Added a new `avt` (avatar) field to the user collection that is nullable (Optional[str]).

## Changes Made

### 1. Database Models (`app/database/models.py`)
- Added `avt: Optional[str] = None` to all user-related models:
  - `UserCreate`
  - `GoogleUserCreate` 
  - `UserUpdate`
  - `UserInDB`
  - `UserResponse`

### 2. Database Schema (`app/database/migrations.py`)
- Updated MongoDB validation schema for users collection
- Added `avt` field as optional with type `["string", "null"]`
- Field is not required (not in the `required` array)

### 3. CRUD Operations (`app/database/crud.py`)
- Updated `update_google_user` method to handle `avt` field updates
- All create operations now support the `avt` field

## Usage

### Creating a User with Avatar
```python
user_data = UserCreate(
    name="John Doe",
    email="john@example.com", 
    password="password123",
    avt="https://example.com/avatar.jpg"  # Optional
)
```

### Creating a Google User with Avatar
```python
google_user_data = GoogleUserCreate(
    google_id="123456789",
    name="John Doe",
    email="john@example.com",
    picture="https://lh3.googleusercontent.com/...",  # Google profile picture
    verified_email=True,
    avt="https://example.com/custom_avatar.jpg"  # Custom avatar (optional)
)
```

### Updating User Avatar
```python
update_data = UserUpdate(avt="https://example.com/new_avatar.jpg")
updated_user = await user_crud.update_user(user_id, update_data)
```

## API Response Examples

### User Response with Avatar
```json
{
  "id": "60d5ec49f1b2c8b1a4567890",
  "name": "John Doe",
  "email": "john@example.com",
  "google_id": null,
  "picture": null,
  "verified_email": null,
  "avt": "https://example.com/avatar.jpg",
  "auth_type": "local",
  "created_at": "2025-09-12T14:00:00Z"
}
```

### Google User Response with Both Picture and Avatar
```json
{
  "id": "60d5ec49f1b2c8b1a4567890",
  "name": "John Doe", 
  "email": "john@example.com",
  "google_id": "123456789",
  "picture": "https://lh3.googleusercontent.com/profile.jpg",
  "verified_email": true,
  "avt": "https://example.com/custom_avatar.jpg",
  "auth_type": "google",
  "created_at": "2025-09-12T14:00:00Z"
}
```

## Field Difference: `picture` vs `avt`
- `picture`: Google profile picture URL (for Google OAuth users)
- `avt`: Custom avatar URL (for all users, including local and Google users)

## Database Schema
- Field Name: `avt`
- Type: `Optional[str]` (nullable string)
- Validation: Must be a valid string or null
- Required: No (optional field)
- Default: `None`

## Server Status
✅ Server running on http://127.0.0.1:8001
✅ Database schema synchronized with avatar field
✅ All CRUD operations support avatar field
✅ API documentation updated at http://127.0.0.1:8001/docs