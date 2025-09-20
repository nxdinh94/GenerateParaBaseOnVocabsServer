# Updated API Response Format - Sort Field Contains Data Array

## Overview
The `/unique-vocabs` API endpoint has been updated with a new response format where the `sort` field now contains the actual sorted data array instead of just the sort method name.

## New Response Structure

### Success Response (HTTP 200)
```json
{
  "status": true,
  "total_documents": 3,
  "documents": [
    {
      "id": "66ed123456789abcdef01234",
      "vocabs": ["recent", "vocabulary"],
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
    },
    {
      "id": "66ed123456789abcdef01236",
      "vocabs": ["old", "example"],
      "created_at": "2025-09-20T13:00:00.000000",
      "updated_at": "2025-09-20T13:00:00.000000",
      "deleted_at": null,
      "is_deleted": false
    }
  ],
  "sort": [
    {
      "id": "66ed123456789abcdef01234",
      "vocabs": ["recent", "vocabulary"],
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
    },
    {
      "id": "66ed123456789abcdef01236",
      "vocabs": ["old", "example"],
      "created_at": "2025-09-20T13:00:00.000000",
      "updated_at": "2025-09-20T13:00:00.000000",
      "deleted_at": null,
      "is_deleted": false
    }
  ],
  "sort_method": "newest",
  "message": "Found 3 vocabulary documents sorted by newest"
}
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | boolean | Success/failure status |
| `total_documents` | number | Count of returned documents |
| `documents` | array | Array of vocabulary documents |
| `sort` | array | **NEW**: Contains the same data as documents but sorted by newest first |
| `sort_method` | string | **NEW**: The sorting method used ("newest", "oldest", "alphabetical") |
| `message` | string | Descriptive message |

## Key Changes

### Before (Old Format)
```json
{
  "sort": "newest"  // String indicating sort method
}
```

### After (New Format)
```json
{
  "sort": [           // Array containing actual sorted data
    { /* document 1 */ },
    { /* document 2 */ },
    { /* document 3 */ }
  ],
  "sort_method": "newest"  // Sort method moved to separate field
}
```

## Sorting Behavior

The `sort` field contains the same data as the `documents` field, but explicitly sorted according to the requested method:

### Default: Newest First
- Documents are sorted by `created_at` in descending order
- Most recently created vocabularies appear first in the `sort` array
- This is the default behavior when no `sort` parameter is provided

### Available Sort Options
1. **`newest`** (default): Sort by created_at DESC
2. **`oldest`**: Sort by created_at ASC  
3. **`alphabetical`**: Sort by first vocabulary word A-Z

## Usage Examples

### JavaScript Example
```javascript
const response = await fetch('/api/v1/unique-vocabs', {
  headers: {
    'Authorization': `Bearer ${jwtToken}`
  }
});

const data = await response.json();

if (data.status) {
  console.log(`Found ${data.total_documents} documents`);
  console.log(`Sorted by: ${data.sort_method}`);
  
  // Use the sort field for sorted data (newest first by default)
  data.sort.forEach((doc, index) => {
    console.log(`${index + 1}. ${doc.vocabs.join(', ')} (${doc.created_at})`);
  });
  
  // Or use documents field (identical data)
  console.log('First vocabulary:', data.documents[0].vocabs);
}
```

### Python Example
```python
import requests

response = requests.get(
    'http://localhost:8000/api/v1/unique-vocabs',
    headers={'Authorization': f'Bearer {jwt_token}'}
)

data = response.json()

if data['status']:
    print(f"Found {data['total_documents']} documents")
    print(f"Sorted by: {data['sort_method']}")
    
    # Use sort field for newest-first data
    for i, doc in enumerate(data['sort']):
        print(f"{i+1}. {', '.join(doc['vocabs'])} ({doc['created_at']})")
```

## Migration Notes

### Breaking Changes
- `sort` field changed from string to array
- Sort method moved to new `sort_method` field

### Backward Compatibility
If your client code previously used:
```javascript
// Old way
const sortMethod = data.sort;  // This was a string
```

Update to:
```javascript
// New way
const sortMethod = data.sort_method;  // Now use sort_method
const sortedData = data.sort;         // This is now the data array
```

## Error Response Format

### Error Response (HTTP 400/401/500)
```json
{
  "status": false,
  "total_documents": 0,
  "documents": [],
  "sort": [],           // Empty array for consistency
  "sort_method": "newest",
  "message": "Error message here"
}
```

## Testing

The new format can be tested using:
```bash
# Test with authentication
curl -H "Authorization: Bearer <token>" "http://localhost:8000/api/v1/unique-vocabs"

# Test with specific sort
curl -H "Authorization: Bearer <token>" "http://localhost:8000/api/v1/unique-vocabs?sort=oldest"
```

## Summary

✅ **`sort` field now contains the actual sorted data array**  
✅ **Data is sorted by newest first by default**  
✅ **`sort_method` field indicates the sorting method**  
✅ **Both `documents` and `sort` fields contain identical data**  
✅ **Robust datetime handling maintained**  
✅ **Authentication requirements unchanged**