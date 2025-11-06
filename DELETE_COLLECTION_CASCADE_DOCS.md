# Improved DELETE Collection API Documentation

## 🚀 Enhanced Cascade Delete Collection API

### Overview
The DELETE vocabulary collection API has been improved to implement **cascade deletion** with the following enhancements:

### ✨ New Features

#### 1. **Cascade Deletion**
When a vocabulary collection is deleted, **all associated learned vocabularies are automatically deleted**.

#### 2. **Ownership Verification**
Users can only delete their own collections (403 Forbidden if attempting to delete another user's collection).

#### 3. **Smart Selected Collection Update**
If the deleted collection was the user's `selected_collection_id`:
- Automatically updates to the first remaining collection
- Sets to `null` if no collections remain

#### 4. **Detailed Response**
Returns count of deleted vocabularies for transparency.

---

## 📡 API Endpoint

### DELETE `/api/v1/vocab-collections/{collection_id}`

**Method:** DELETE  
**Authentication:** Required (Bearer Token)  
**Content-Type:** application/json

---

## 🔧 Usage Examples

### Example 1: Delete Collection with cURL
```bash
curl -X DELETE "http://localhost:8000/api/v1/vocab-collections/673abc123def456" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

### Example 2: Delete Collection with JavaScript/Fetch
```javascript
const collectionId = "673abc123def456";
const token = "YOUR_JWT_TOKEN_HERE";

fetch(`http://localhost:8000/api/v1/vocab-collections/${collectionId}`, {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => {
  console.log(data);
  // { 
  //   status: true, 
  //   message: "Vocabulary collection deleted successfully (including 25 vocabularies)",
  //   deleted_vocab_count: 25
  // }
})
.catch(error => console.error('Error:', error));
```

### Example 3: Delete Collection with Python Requests
```python
import requests

collection_id = "673abc123def456"
token = "YOUR_JWT_TOKEN_HERE"

response = requests.delete(
    f"http://localhost:8000/api/v1/vocab-collections/{collection_id}",
    headers={"Authorization": f"Bearer {token}"}
)

result = response.json()
print(f"Deleted collection with {result['deleted_vocab_count']} vocabularies")
```

---

## 📥 Request Format

### Headers
```
Authorization: Bearer <JWT_TOKEN>
```

### URL Parameters
- `collection_id` (required): The ID of the collection to delete

### Request Body
No body required

---

## 📤 Response Format

### Success Response (200 OK)
```json
{
  "status": true,
  "message": "Vocabulary collection deleted successfully (including 25 vocabularies)",
  "deleted_vocab_count": 25
}
```

### Error Responses

#### 401 Unauthorized - Missing/Invalid Token
```json
{
  "error": "missing_authorization_header",
  "message": "Authorization header is required"
}
```

#### 403 Forbidden - Not Collection Owner
```json
{
  "error": "access_denied",
  "message": "You can only delete your own vocabulary collections"
}
```

#### 404 Not Found - Collection Doesn't Exist
```json
{
  "error": "collection_not_found",
  "message": "Vocabulary collection not found"
}
```

#### 500 Internal Server Error
```json
{
  "error": "deletion_failed",
  "message": "Failed to delete vocabulary collection",
  "details": "Error details..."
}
```

---

## 🗄️ Database Impact

### What Gets Deleted (Cascade):

#### 1. **vocab_collections** Collection
```javascript
// Deleted document:
{
  "_id": ObjectId("673abc123def456"),
  "name": "My Collection",
  "user_id": ObjectId("672def456abc789"),
  "created_at": ISODate("2025-11-01T10:00:00Z"),
  "updated_at": ISODate("2025-11-05T15:30:00Z")
}
```

#### 2. **learned_vocabs** Collection (CASCADE)
```javascript
// All documents with matching collection_id are deleted:
db.learned_vocabs.deleteMany({
  "collection_id": ObjectId("673abc123def456")
})

// Example deleted vocabularies:
[
  { "_id": ObjectId("674xxx111"), "vocab": "apple", "collection_id": ObjectId("673abc123def456") },
  { "_id": ObjectId("674xxx222"), "vocab": "banana", "collection_id": ObjectId("673abc123def456") },
  { "_id": ObjectId("674xxx333"), "vocab": "cherry", "collection_id": ObjectId("673abc123def456") }
  // ... all vocabularies in this collection
]
```

#### 3. **google_users** Collection (UPDATE if needed)
```javascript
// If user's selected_collection_id points to deleted collection:

// BEFORE:
{
  "_id": ObjectId("672def456abc789"),
  "email": "user@example.com",
  "selected_collection_id": "673abc123def456"  // Points to deleted collection
}

// AFTER (automatically updated to first remaining collection):
{
  "_id": ObjectId("672def456abc789"),
  "email": "user@example.com",
  "selected_collection_id": "673def789abc456"  // Updated to next collection
}

// OR if no collections remain:
{
  "_id": ObjectId("672def456abc789"),
  "email": "user@example.com",
  "selected_collection_id": null  // Set to null
}
```

---

## ⚡ Processing Flow

```
1. Authenticate user from Bearer token
   ↓
2. Verify collection exists
   ↓
3. Verify user owns the collection (403 if not)
   ↓
4. Count vocabularies in collection
   ↓
5. DELETE all learned_vocabs with matching collection_id (CASCADE)
   ↓
6. DELETE the collection document
   ↓
7. Check if user's selected_collection_id was deleted
   ↓
8. If yes: Update to first remaining collection or null
   ↓
9. Return success with deleted vocabulary count
```

---

## 🔒 Security Features

✅ **Authentication Required** - Must provide valid Bearer token  
✅ **Ownership Verification** - Can only delete own collections  
✅ **No Orphaned Data** - All associated vocabularies are cascade deleted  
✅ **Auto-Update References** - User's selected_collection_id is auto-updated if needed  

---

## 📊 Comparison: Before vs After Improvement

| Feature | Before | After (Improved) |
|---------|--------|------------------|
| Delete Collection | ✅ Yes | ✅ Yes |
| Delete Associated Vocabs | ❌ No (orphaned) | ✅ Yes (cascade) |
| Ownership Check | ❌ No | ✅ Yes |
| Update selected_collection_id | ❌ No | ✅ Yes (auto) |
| Return Deletion Count | ❌ No | ✅ Yes |
| Prevent Orphaned Data | ❌ No | ✅ Yes |

---

## 🧪 Testing

Run the test script to verify cascade deletion:

```bash
python test_cascade_delete_collection.py
```

Expected output:
```
✅ Created collection: Test Collection for Cascade Delete
✅ Added 5 vocabularies
🗑️ Deleting collection...
✅ Collection deleted successfully
✅ All vocabularies were cascade deleted successfully!
```

---

## 📝 Notes

1. **Permanent Deletion**: This operation is **irreversible**. All data is permanently deleted.
2. **Performance**: For collections with many vocabularies, deletion may take a few seconds.
3. **Logging**: All deletions are logged with vocabulary counts for audit purposes.
4. **Auto-Update**: Users don't need to manually update their selected collection after deletion.

---

## 🚨 Important Warnings

⚠️ **This is a destructive operation**  
⚠️ **All vocabularies in the collection will be permanently deleted**  
⚠️ **Cannot be undone**  
⚠️ **Consider implementing soft delete or backup if needed**
