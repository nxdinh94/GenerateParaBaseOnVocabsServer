# POST /learned-vocabs API Examples

## API Endpoint
```
POST /api/v1/learned-vocabs
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

## Request Schema
```json
{
  "vocabs": ["word1", "word2", "word3"]
}
```

## Example Requests

### 1. Basic Request
```bash
curl -X POST http://localhost:8001/api/v1/learned-vocabs \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"vocabs": ["hello", "world", "python"]}'
```

### 2. Multiple Vocabularies
```bash
curl -X POST http://localhost:8001/api/v1/learned-vocabs \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"vocabs": ["learn", "code", "javascript", "react", "nodejs"]}'
```

### 3. Single Vocabulary
```bash
curl -X POST http://localhost:8001/api/v1/learned-vocabs \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"vocabs": ["algorithm"]}'
```

## Response Examples

### Success (New Entry)
```json
{
  "status": true,
  "message": "Learned vocabularies created successfully",
  "data": {
    "id": "67636f8e12345678901234ab",
    "vocabs": ["hello", "world", "python"],
    "created_at": "2025-09-20T13:45:00.123456",
    "updated_at": "2025-09-20T13:45:00.123456",
    "deleted_at": null,
    "is_deleted": false
  },
  "is_new": true
}
```

### Success (Existing Entry)
```json
{
  "status": true,
  "message": "Vocabularies already exist",
  "data": {
    "id": "67636f8e12345678901234ab",
    "vocabs": ["hello", "world", "python"],
    "created_at": "2025-09-20T10:00:00.123456",
    "updated_at": "2025-09-20T10:00:00.123456",
    "deleted_at": null,
    "is_deleted": false
  },
  "is_new": false
}
```

### Error Examples

#### Missing Authorization
```json
{
  "detail": {
    "error": "missing_authorization_header",
    "message": "Authorization header is required"
  }
}
```

#### Invalid Token
```json
{
  "detail": {
    "error": "invalid_token",
    "message": "Token is invalid or expired"
  }
}
```

#### Missing vocabs Field
```json
{
  "detail": {
    "error": "missing_vocabs",
    "message": "Field 'vocabs' is required"
  }
}
```

#### Empty Array
```json
{
  "detail": {
    "error": "empty_vocabs",
    "message": "At least one vocabulary is required"
  }
}
```

## Integration with Other APIs

### Complete Flow Example
```bash
# 1. Create vocabularies
curl -X POST http://localhost:8001/api/v1/learned-vocabs \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"vocabs": ["react", "hooks", "context"]}'

# 2. Get all vocabulary documents
curl -X GET http://localhost:8001/api/v1/vocabs_base_on_category \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 3. Also works with existing input-history endpoint
curl -X POST http://localhost:8001/api/v1/db/input-history/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"words": ["nodejs", "express", "mongodb"]}'
```

## Features

- ✅ **Duplicate Detection**: Prevents saving identical vocabulary sets
- ✅ **Data Cleaning**: Automatically trims whitespace and removes empty entries
- ✅ **Normalization**: Case-insensitive comparison for duplicates
- ✅ **Authentication**: Requires valid JWT Bearer token
- ✅ **Validation**: Comprehensive input validation with clear error messages
- ✅ **Integration**: Works seamlessly with existing `/vocabs_base_on_category` endpoint