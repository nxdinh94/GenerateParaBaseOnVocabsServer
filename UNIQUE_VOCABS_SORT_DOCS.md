# Unique Vocabs API - Sort Functionality Documentation

## Overview
The `/vocabs_base_on_category` API endpoint has been enhanced with comprehensive sorting functionality that returns all fields sorted by newest first by default.

## API Endpoint
```
GET /api/v1/vocabs_base_on_category?sort={sort_option}
```

## Authentication
- **Required**: Bearer token in Authorization header
- **Format**: `Authorization: Bearer <jwt_token>`
- **Source**: JWT token from Google OAuth login

## Query Parameters

### sort (optional)
Controls the sorting order of returned documents.

**Valid Values:**
- `newest` (default) - Sort by created_at descending (newest first)
- `oldest` - Sort by created_at ascending (oldest first)  
- `alphabetical` - Sort by first vocabulary word alphabetically (A-Z)

**Default Behavior:**
- If no `sort` parameter is provided, defaults to `newest`
- Invalid sort values return HTTP 400 with error details

## Response Format

### Success Response (HTTP 200)
```json
{
  "status": true,
  "total_documents": 3,
  "documents": [
    {
      "id": "66ed123456789abcdef01234",
      "vocabs": ["recent", "example"],
      "created_at": "2025-09-20T15:30:00.000000",
      "updated_at": "2025-09-20T15:30:00.000000",
      "deleted_at": null,
      "is_deleted": false
    },
    {
      "id": "66ed123456789abcdef01235", 
      "vocabs": ["hello", "world"],
      "created_at": "2025-09-20T14:15:00.000000",
      "updated_at": "2025-09-20T14:15:00.000000",
      "deleted_at": null,
      "is_deleted": false
    }
  ],
  "sort": "newest",
  "message": "Found 3 vocabulary documents sorted by newest"
}
```

### Error Response - Authentication (HTTP 401)
```json
{
  "detail": {
    "error": "missing_authorization_header",
    "message": "Authorization header is required"
  }
}
```

### Error Response - Invalid Sort (HTTP 400)
```json
{
  "detail": {
    "error": "invalid_sort_parameter",
    "message": "Sort must be one of: newest, oldest, alphabetical"
  }
}
```

## Document Fields

All documents include the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique document identifier (ObjectId as string) |
| `vocabs` | array | Array of vocabulary words |
| `created_at` | string | ISO format datetime when document was created |
| `updated_at` | string | ISO format datetime when document was last updated |
| `deleted_at` | string/null | ISO format datetime when deleted (null if not deleted) |
| `is_deleted` | boolean | Flag indicating if document is deleted |

**Note:** The `user_id` field is excluded from the response for privacy.

## Sorting Logic

### Newest First (default)
- Sorts by `created_at` field in descending order
- Documents with null `created_at` are treated as oldest (1900-01-01)
- Most recently created documents appear first

### Oldest First
- Sorts by `created_at` field in ascending order
- Documents with null `created_at` are treated as oldest (1900-01-01)
- Earliest created documents appear first

### Alphabetical
- Sorts by the first vocabulary word in the `vocabs` array
- Case-insensitive alphabetical sorting (A-Z)
- Documents with empty `vocabs` array are sorted last

## Usage Examples

### Default Sort (Newest First)
```bash
curl -H "Authorization: Bearer <token>" "http://localhost:8000/api/v1/vocabs_base_on_category"
```

### Explicit Newest Sort
```bash
curl -H "Authorization: Bearer <token>" "http://localhost:8000/api/v1/vocabs_base_on_category?sort=newest"
```

### Oldest First Sort
```bash
curl -H "Authorization: Bearer <token>" "http://localhost:8000/api/v1/vocabs_base_on_category?sort=oldest"
```

### Alphabetical Sort
```bash
curl -H "Authorization: Bearer <token>" "http://localhost:8000/api/v1/vocabs_base_on_category?sort=alphabetical"
```

## JavaScript Example

```javascript
// Get newest vocabularies (default)
const response = await fetch('/api/v1/vocabs_base_on_category', {
  headers: {
    'Authorization': `Bearer ${jwtToken}`
  }
});

// Get with specific sort
const oldestResponse = await fetch('/api/v1/vocabs_base_on_category?sort=oldest', {
  headers: {
    'Authorization': `Bearer ${jwtToken}`
  }
});

const data = await response.json();
if (data.status) {
  console.log(`Found ${data.total_documents} documents`);
  console.log(`Sorted by: ${data.sort}`);
  data.documents.forEach(doc => {
    console.log(`${doc.id}: ${doc.vocabs.join(', ')}`);
  });
}
```

## Implementation Details

### Database Collection
- **Source**: `learned_vocabs` collection
- **Filter**: Only documents where `is_deleted = false`
- **User Scope**: Only documents belonging to authenticated user

### Performance Considerations
- Default limit of 1000 documents to prevent large responses
- Sorting is done in application layer after fetching from database
- Consider adding database-level sorting for large datasets

### Error Handling
- Robust handling of null/undefined datetime values
- Graceful fallback for empty vocabulary arrays
- Comprehensive validation of sort parameters

## Testing

### Test Files
- `test_sort_all_fields.py` - Comprehensive sorting tests
- `test_auth_sort.py` - Authentication and usage examples
- `test_unique_vocabs_sort.py` - Original sort functionality tests

### Running Tests
```bash
# Test without authentication (will show 401 responses)
python test_sort_all_fields.py

# Test with authentication examples
python test_auth_sort.py
```

## Migration Notes

### Changes Made
1. Enhanced sorting algorithm with robust null handling
2. Improved datetime comparison using ISO strings
3. Added comprehensive error messages
4. Maintained backward compatibility with existing clients

### Backward Compatibility
- Default behavior unchanged (newest first)
- All existing API consumers will continue to work
- Response format identical except for improved `sort` field

## Security
- All requests require valid JWT authentication
- User data isolation maintained
- No sensitive fields exposed in response
- Input validation prevents injection attacks