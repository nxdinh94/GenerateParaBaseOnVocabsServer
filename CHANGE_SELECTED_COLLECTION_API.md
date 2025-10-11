# Change Selected Collection API Documentation

## Date: 2025-10-11

## Overview
API endpoint to change a user's selected vocabulary collection. This allows users to switch between different vocabulary collections they have created.

## Endpoint Details

### POST `/api/v1/change-selected-collection`

Changes the user's currently selected vocabulary collection.

## Authentication
**Required**: Yes (Bearer Token)

Include JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Request Schema

### Headers
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Body
```json
{
  "selected_collection_id": "string (required)"
}
```

**Fields:**
- `selected_collection_id` (string, required): The ID of the vocabulary collection to select. Must be a valid ObjectId and belong to the authenticated user.

## Response Schema

### Success Response (200 OK)
```json
{
  "status": true,
  "message": "Selected collection updated successfully",
  "selected_collection_id": "673abc123def456789012345"
}
```

### Error Responses

#### 400 Bad Request - Missing Collection ID
```json
{
  "detail": {
    "error": "missing_collection_id",
    "message": "selected_collection_id is required"
  }
}
```

#### 401 Unauthorized - Missing or Invalid Token
```json
{
  "detail": {
    "error": "missing_authorization_header",
    "message": "Authorization header is required"
  }
}
```

```json
{
  "detail": {
    "error": "invalid_token",
    "message": "Token is invalid or expired"
  }
}
```

#### 403 Forbidden - Collection Belongs to Another User
```json
{
  "detail": {
    "error": "access_denied",
    "message": "You can only select your own vocabulary collections"
  }
}
```

#### 404 Not Found - Collection Does Not Exist
```json
{
  "detail": {
    "error": "collection_not_found",
    "message": "Vocabulary collection not found"
  }
}
```

#### 500 Internal Server Error
```json
{
  "detail": {
    "error": "update_failed",
    "message": "Failed to change selected collection",
    "details": "Error details..."
  }
}
```

## Usage Examples

### Example 1: Change Selected Collection (Success)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/change-selected-collection" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "selected_collection_id": "673abc123def456789012345"
  }'
```

**Response (200 OK):**
```json
{
  "status": true,
  "message": "Selected collection updated successfully",
  "selected_collection_id": "673abc123def456789012345"
}
```

### Example 2: JavaScript/TypeScript (React/Next.js)

```typescript
async function changeSelectedCollection(collectionId: string) {
  const token = localStorage.getItem('jwt_token');
  
  try {
    const response = await fetch('http://localhost:8000/api/v1/change-selected-collection', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        selected_collection_id: collectionId
      })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      console.log('✅ Collection changed:', data.message);
      // Update local state or reload collections
      return data;
    } else {
      console.error('❌ Error:', data.detail.message);
      throw new Error(data.detail.message);
    }
  } catch (error) {
    console.error('Failed to change collection:', error);
    throw error;
  }
}

// Usage
changeSelectedCollection('673abc123def456789012345')
  .then(result => {
    console.log('Selected collection ID:', result.selected_collection_id);
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

### Example 3: Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
jwt_token = "your_jwt_token_here"

def change_selected_collection(collection_id: str):
    """Change user's selected vocabulary collection"""
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "selected_collection_id": collection_id
    }
    
    response = requests.post(
        f"{BASE_URL}/change-selected-collection",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {data['message']}")
        return data
    else:
        error = response.json()
        print(f"❌ Error: {error['detail']['message']}")
        raise Exception(error['detail']['message'])

# Usage
try:
    result = change_selected_collection("673abc123def456789012345")
    print(f"Selected collection: {result['selected_collection_id']}")
except Exception as e:
    print(f"Failed: {e}")
```

## Integration Flow

### Typical User Flow:

1. **User logs in** → Receives JWT token
2. **Get collections** → `GET /api/v1/vocab-collections`
3. **User selects a collection** → `POST /api/v1/change-selected-collection`
4. **Use selected collection** → All vocabulary operations use this collection

### Complete Example Flow:

```typescript
// Step 1: Login
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/google/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ authorization_code: googleAuthCode })
});
const { jwt_token } = await loginResponse.json();

// Step 2: Get all collections
const collectionsResponse = await fetch('http://localhost:8000/api/v1/vocab-collections', {
  headers: { 'Authorization': `Bearer ${jwt_token}` }
});
const { collections } = await collectionsResponse.json();

// Step 3: Display collections to user (UI)
collections.forEach(collection => {
  console.log(`${collection.name} - ${collection.id}`);
});

// Step 4: User selects a collection
const selectedCollectionId = collections[0].id;

// Step 5: Change selected collection
const changeResponse = await fetch('http://localhost:8000/api/v1/change-selected-collection', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${jwt_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ selected_collection_id: selectedCollectionId })
});

const result = await changeResponse.json();
console.log('Selected collection:', result.selected_collection_id);
```

## Validation Rules

1. **Authentication Required**: Must provide valid JWT token
2. **Collection ID Required**: Cannot be empty or null
3. **Collection Must Exist**: Collection ID must reference an existing collection
4. **User Authorization**: Collection must belong to the authenticated user
5. **Valid ObjectId**: Collection ID must be a valid MongoDB ObjectId format

## Database Changes

### Users Collection Update

When this API is called, it updates the `selected_collection_id` field in the `users` collection:

```javascript
// MongoDB Update Operation
db.users.updateOne(
  { _id: ObjectId(user_id) },
  { $set: { selected_collection_id: "673abc123def456789012345" } }
)
```

## Use Cases

1. **Switch Between Work and Personal Vocabularies**
   - User has "Work" and "Personal" collections
   - Can switch context by changing selected collection

2. **Topic-Based Learning**
   - User has collections for different topics (Business, Travel, Technical)
   - Switch collection based on current learning focus

3. **Difficulty Levels**
   - User has collections for different difficulty levels
   - Switch as they progress in learning

4. **Language Learning**
   - User has different collections for different languages
   - Switch between language learning sessions

## Security Considerations

1. **Token Validation**: Always validates JWT token before processing
2. **Ownership Verification**: Ensures collection belongs to authenticated user
3. **Input Validation**: Validates collection_id format and existence
4. **Error Handling**: Provides specific error messages without exposing sensitive data

## Related Endpoints

- `GET /api/v1/vocab-collections` - Get all user's collections
- `POST /api/v1/vocab-collections` - Create new collection
- `PUT /api/v1/vocab-collections/{collection_id}` - Update collection name
- `DELETE /api/v1/vocab-collections/{collection_id}` - Delete collection
- `GET /api/v1/vocabs_base_on_category` - Get vocabularies from selected collection

## Testing

Run the test script:
```bash
python test_change_selected_collection.py
```

Make sure to:
1. Update `JWT_TOKEN` in the test script
2. Have the server running
3. Have at least one vocabulary collection created

## Implementation Details

### Files Modified:

1. **app/api/v1/schemas.py**
   - Added `ChangeSelectedCollectionRequest`
   - Added `ChangeSelectedCollectionResponse`

2. **app/database/crud.py**
   - Added `update_selected_collection()` method to `UserCRUD` class

3. **app/api/v1/routes.py**
   - Added `POST /change-selected-collection` endpoint

### Code References:

**Schema Definition:**
```python
class ChangeSelectedCollectionRequest(BaseModel):
    selected_collection_id: str

class ChangeSelectedCollectionResponse(BaseModel):
    status: bool = True
    message: str
    selected_collection_id: str
```

**CRUD Method:**
```python
async def update_selected_collection(self, user_id: str, collection_id: str) -> Optional[UserInDB]:
    """Update user's selected collection"""
    await self.collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"selected_collection_id": collection_id}}
    )
    return await self.get_user_by_id(user_id)
```

## Performance Considerations

- **Single Database Query**: Updates selected_collection_id with one operation
- **Indexed Field**: User ID is indexed for fast lookups
- **Lightweight Operation**: Only updates one field, minimal overhead

## Future Enhancements

1. **Return Full User Object**: Include updated user data in response
2. **Collection Statistics**: Return vocab count for selected collection
3. **Recent Collections**: Track and suggest recently used collections
4. **Default Collection**: Allow setting a permanent default collection
5. **Collection Switching History**: Track when users switch collections

## Troubleshooting

### Common Issues:

1. **401 Unauthorized**
   - Check if JWT token is valid and not expired
   - Ensure token is in correct format: `Bearer <token>`

2. **403 Forbidden**
   - Verify collection belongs to authenticated user
   - Check collection ownership in database

3. **404 Not Found**
   - Verify collection ID exists in database
   - Check for typos in collection ID

4. **400 Bad Request**
   - Ensure selected_collection_id is not empty
   - Verify JSON payload format is correct

## Support

For issues or questions:
1. Check server logs for detailed error messages
2. Verify database connections
3. Test with provided test script
4. Review API documentation

---

**Version**: 1.0  
**Last Updated**: 2025-10-11  
**API Endpoint**: `POST /api/v1/change-selected-collection`
