# Learned Vocab Schema Migration - Single Word per Document

## Summary
Changed the `learned_vocabs` collection schema from storing multiple vocabularies in a single document to storing one vocabulary word per document. The API request still accepts a list of vocabularies, but creates one document for each word.

## Changes Made

### 1. Database Models (`app/database/models.py`)
Changed the `vocabs` field from `List[str]` to `str` (single string):

**Before:**
```python
class LearnedVocabsCreateInternal(BaseModel):
    vocabs: List[str] = Field(..., min_length=1)
    collection_id: PyObjectId

class LearnedVocabsInDB(BaseModel):
    vocabs: List[str]
    collection_id: PyObjectId
    usage_count: int = Field(default=1)
    ...
```

**After:**
```python
class LearnedVocabsCreateInternal(BaseModel):
    vocab: str = Field(..., min_length=1)  # Single word
    collection_id: PyObjectId

class LearnedVocabsInDB(BaseModel):
    vocab: str  # Single word
    collection_id: PyObjectId
    usage_count: int = Field(default=1)
    ...
```

### 2. API Schemas (`app/api/v1/schemas.py`)
- **Request Schema**: Kept as `List[str]` to accept multiple vocabs
- **Response Schema**: Changed from `List[str]` to `str` for single vocab
- **Added**: `LearnedVocabsBatchResponse` for batch creation response

```python
class LearnedVocabsCreateRequest(BaseModel):
    vocabs: List[str]  # Still accepts a list
    collection_id: str

class LearnedVocabsResponse(BaseModel):
    id: str
    vocab: str  # Changed to single string
    collection_id: str
    usage_count: int
    ...

class LearnedVocabsBatchResponse(BaseModel):
    created: List[LearnedVocabsResponse]
    total_created: int
    status: bool = True
```

### 3. CRUD Operations (`app/database/crud.py`)

#### a. `create_learned_vocabs()`
- Updated to handle single `vocab` string instead of list
- Comment updated to clarify "single word"

#### b. `find_by_exact_vocabs()` → `find_by_exact_vocab()`
- **Renamed** to `find_by_exact_vocab()` (singular)
- Changed from comparing lists to finding exact single word match
- Uses case-insensitive regex search: `{"vocab": {"$regex": f"^{normalized_vocab}$", "$options": "i"}}`

#### c. `update_learned_vocabs()`
- Changed parameter from `new_vocabs: List[str]` to `new_vocab: str`
- Updates single `vocab` field

#### d. `delete_vocabs_containing_word()`
- Simplified to use regex search directly in delete query
- No longer needs to iterate through vocab lists
- More efficient: `{"vocab": {"$regex": f"^{normalized_word}$", "$options": "i"}}`

### 4. API Routes (`app/api/v1/routes.py`)

#### a. `POST /learned-vocabs`
**Response Model**: Changed to `LearnedVocabsBatchResponse`

**Logic Changes:**
- Accepts list of vocabs in request
- **Loops through each vocab** and creates individual documents
- For each vocab:
  - Checks if it already exists using `find_by_exact_vocab()`
  - If exists: increments `usage_count`
  - If not exists: creates new document
- Returns list of all created/updated vocabs

**Before:**
- Created 1 document with array of vocabs
- Matched entire array for duplicates

**After:**
- Creates N documents (one per vocab word)
- Matches individual words for duplicates
- Tracks usage per word

#### b. `GET /vocabs_base_on_category`
- Changed response field from `vocabs` (array) to `vocab` (string)
- Updated alphabetical sort to use `x["vocab"]` instead of `x["vocabs"][0]`

## Database Impact

### Storage Change
**Before:**
```json
{
  "_id": "...",
  "vocabs": ["hello", "world", "test"],
  "collection_id": "...",
  "usage_count": 1
}
```

**After (3 documents):**
```json
{
  "_id": "...",
  "vocab": "hello",
  "collection_id": "...",
  "usage_count": 1
}
{
  "_id": "...",
  "vocab": "world",
  "collection_id": "...",
  "usage_count": 1
}
{
  "_id": "...",
  "vocab": "test",
  "collection_id": "...",
  "usage_count": 1
}
```

### Benefits
1. **Better Tracking**: Each word has its own `usage_count`
2. **Easier Queries**: Direct word lookup without array operations
3. **Simpler Deletion**: Delete specific words without affecting others
4. **More Granular**: Individual creation/update timestamps per word

### Migration Notes
⚠️ **Breaking Change**: Existing data with `vocabs` array field will need migration

## API Behavior

### Request (Unchanged)
```json
POST /learned-vocabs
{
  "vocabs": ["hello", "world", "test"],
  "collection_id": "collection_123"
}
```

### Response (Changed)
**Before:**
```json
{
  "id": "vocab_1",
  "vocabs": ["hello", "world", "test"],
  "collection_id": "collection_123",
  "usage_count": 1,
  "is_new": true,
  "status": true
}
```

**After:**
```json
{
  "created": [
    {
      "id": "vocab_1",
      "vocab": "hello",
      "collection_id": "collection_123",
      "usage_count": 1,
      "is_new": true,
      "status": true
    },
    {
      "id": "vocab_2",
      "vocab": "world",
      "collection_id": "collection_123",
      "usage_count": 1,
      "is_new": true,
      "status": true
    },
    {
      "id": "vocab_3",
      "vocab": "test",
      "collection_id": "collection_123",
      "usage_count": 1,
      "is_new": true,
      "status": true
    }
  ],
  "total_created": 3,
  "status": true
}
```

## Testing Recommendations
1. Test creating single vocab
2. Test creating multiple vocabs in one request
3. Test duplicate detection (should increment usage_count)
4. Test GET /vocabs_base_on_category with all sort methods
5. Test DELETE /learned-vocabs with specific word
6. Verify alphabetical sorting works correctly

## Date: October 9, 2025
