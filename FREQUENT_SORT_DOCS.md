# Frequent Sort Feature Documentation

## Overview
The `/vocabs_base_on_category` API has been enhanced with a new "frequent" sort option that sorts vocabulary documents by usage frequency. This allows users to see their most frequently used vocabulary sets first.

## New Features

### 1. Usage Count Tracking
- Added `usage_count` field to learned_vocabs collection
- Tracks how many times each vocabulary set has been used
- Automatically increments when existing vocabularies are reused

### 2. Frequent Sort Option
- New sort parameter: `sort=frequent`
- Sorts by `usage_count` in descending order (most used first)
- Tiebreaker: newest `created_at` for vocabularies with same usage count

## API Changes

### GET /vocabs_base_on_category

#### New Sort Option
```
GET /api/v1/vocabs_base_on_category?sort=frequent
```

#### Updated Sort Options
- `newest` (default) - Sort by created_at DESC
- `oldest` - Sort by created_at ASC
- `alphabetical` - Sort by first vocabulary word A-Z
- `frequent` - **NEW**: Sort by usage_count DESC (most used first)

#### Updated Response Format
```json
{
  "status": true,
  "total_documents": 3,
  "documents": [
    {
      "id": "66ed123456789abcdef01234",
      "vocabs": ["frequently", "used"],
      "usage_count": 15,  // NEW FIELD
      "created_at": "2025-09-20T10:00:00.000000",
      "updated_at": "2025-09-20T14:30:00.000000",
      "deleted_at": null,
      "is_deleted": false
    }
  ],
  "sort": [
    // Same data as documents but sorted by usage_count DESC
  ],
  "sort_method": "frequent",
  "message": "Found 3 vocabulary documents sorted by frequent"
}
```

### POST /learned-vocabs

#### Enhanced Behavior
- When creating vocabularies that already exist:
  - Increments `usage_count` by 1
  - Updates `updated_at` timestamp
  - Returns enhanced response with usage information

#### Updated Response Format
```json
{
  "status": true,
  "message": "Vocabularies already exist, usage count incremented",
  "data": {
    "id": "66ed123456789abcdef01234",
    "vocabs": ["hello", "world"],
    "usage_count": 5,  // Incremented value
    "created_at": "2025-09-20T10:00:00.000000",
    "updated_at": "2025-09-20T14:30:00.000000",  // Updated timestamp
    "deleted_at": null,
    "is_deleted": false
  },
  "is_new": false,
  "usage_incremented": true  // NEW FIELD
}
```

## Database Schema Changes

### LearnedVocabs Collection
Added new field:
```typescript
{
  _id: ObjectId,
  user_id: ObjectId,
  vocabs: string[],
  usage_count: number,      // NEW: Tracks usage frequency
  created_at: Date,
  updated_at: Date,
  deleted_at: Date | null,
  is_deleted: boolean
}
```

### Default Values
- New documents: `usage_count = 1`
- Existing documents without field: Default to `1` in API response

## Usage Examples

### 1. Get Most Frequently Used Vocabularies
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/vocabs_base_on_category?sort=frequent"
```

### 2. Create/Use Vocabularies (Auto-increment usage)
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"vocabs": ["hello", "world"]}' \
  "http://localhost:8000/api/v1/learned-vocabs"
```

### 3. JavaScript Usage
```javascript
// Get most frequently used vocabularies
const response = await fetch('/api/v1/vocabs_base_on_category?sort=frequent', {
  headers: {
    'Authorization': `Bearer ${jwtToken}`
  }
});

const data = await response.json();

if (data.status) {
  console.log('Most frequently used vocabularies:');
  data.sort.forEach((item, index) => {
    console.log(`${index + 1}. ${item.vocabs.join(', ')} (used ${item.usage_count} times)`);
  });
}

// Use existing vocabularies (increments usage count)
const createResponse = await fetch('/api/v1/learned-vocabs', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    vocabs: ['hello', 'world']
  })
});

const createData = await createResponse.json();
if (createData.usage_incremented) {
  console.log(`Usage count incremented to: ${createData.data.usage_count}`);
}
```

## Sorting Behavior

### Frequent Sort Logic
1. Primary sort: `usage_count` DESC (highest usage first)
2. Tiebreaker: `created_at` DESC (newest first for same usage count)

### Example Sort Order
```
1. ["study", "learn"] - usage_count: 25, created: 2025-09-19
2. ["hello", "world"] - usage_count: 15, created: 2025-09-20
3. ["practice", "test"] - usage_count: 15, created: 2025-09-18  // Same usage, but older
4. ["new", "vocab"] - usage_count: 1, created: 2025-09-20
```

## Migration Notes

### Backward Compatibility
- Existing API clients continue to work
- Default sort remains "newest"
- Existing documents without `usage_count` field are handled gracefully

### Database Migration
For existing documents without `usage_count`:
```javascript
// MongoDB update to add usage_count field to existing documents
db.learned_vocabs.updateMany(
  { usage_count: { $exists: false } },
  { $set: { usage_count: 1 } }
);
```

## Use Cases

### 1. Vocabulary Review Priority
Users can focus on their most frequently used vocabulary sets for review.

### 2. Learning Analytics
Track which vocabulary sets are used most often to identify learning patterns.

### 3. Smart Recommendations
Suggest frequently used vocabularies for new study sessions.

### 4. Progress Tracking
Monitor usage patterns over time to assess learning engagement.

## Error Handling

### Invalid Sort Parameter
```json
{
  "detail": {
    "error": "invalid_sort_parameter",
    "message": "Sort must be one of: newest, oldest, alphabetical, frequent"
  }
}
```

### Usage Count Edge Cases
- Missing `usage_count` field: Defaults to 1
- Invalid `usage_count` value: Treated as 1
- Usage increment failure: Returns original entry

## Performance Considerations

### Indexing Recommendations
```javascript
// Recommended MongoDB indexes for optimal performance
db.learned_vocabs.createIndex({ "user_id": 1, "usage_count": -1, "created_at": -1 });
db.learned_vocabs.createIndex({ "user_id": 1, "is_deleted": 1, "usage_count": -1 });
```

### Limitations
- Current implementation sorts in application layer
- For large datasets (>1000 documents), consider database-level sorting
- Usage count increment is atomic but requires database round-trip

## Testing

### Test Coverage
- ✅ Frequent sort validation
- ✅ Usage count increment on reuse
- ✅ Backward compatibility with existing sort options
- ✅ Error handling for invalid sort parameters
- ✅ Default value handling for missing usage_count

### Test Files
- `test_frequent_sort.py` - Comprehensive frequent sort testing
- `test_new_sort_format.py` - General sort format validation

## Summary

✅ **Added frequent sort option for most-used vocabularies**  
✅ **Usage count tracking with automatic increments**  
✅ **Enhanced API responses with usage information**  
✅ **Backward compatibility maintained**  
✅ **Proper error handling and validation**  
✅ **Comprehensive test coverage**  

The frequent sort feature enables users to prioritize their most commonly used vocabulary sets, providing valuable insights into their learning patterns and helping optimize study sessions.