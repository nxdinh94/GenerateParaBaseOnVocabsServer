# JWT Token - Selected Collection ID Field Addition

## Date: 2025-10-11

## Overview
Added `selected_collection_id` field to JWT tokens and JWT refresh tokens to allow the frontend to know which vocabulary collection is currently selected by the user without making additional API calls.

## Changes Made

### 1. Google Auth Service (`app/services/google_auth.py`)

#### `create_jwt_token()` method
**Before:**
```python
payload = {
    "user_id": user_data.get("id"),
    "email": user_data.get("email"),
    "name": user_data.get("name"),
    "picture": user_data.get("picture"),
    "exp": datetime.utcnow() + timedelta(hours=1)
}
```

**After:**
```python
payload = {
    "user_id": user_data.get("id"),
    "email": user_data.get("email"),
    "name": user_data.get("name"),
    "picture": user_data.get("picture"),
    "selected_collection_id": user_data.get("selected_collection_id"),  # NEW
    "exp": datetime.utcnow() + timedelta(hours=1)
}
```

#### `create_jwt_refresh_token()` method
**Before:**
```python
payload = {
    "user_id": user_data.get("id"),
    "email": user_data.get("email"),
    "name": user_data.get("name"),
    "picture": user_data.get("picture"),
    "type": "refresh",
    "exp": datetime.utcnow() + timedelta(days=30)
}
```

**After:**
```python
payload = {
    "user_id": user_data.get("id"),
    "email": user_data.get("email"),
    "name": user_data.get("name"),
    "picture": user_data.get("picture"),
    "selected_collection_id": user_data.get("selected_collection_id"),  # NEW
    "type": "refresh",
    "exp": datetime.utcnow() + timedelta(days=30)
}
```

### 2. API Routes (`app/api/v1/routes.py`)

#### Google Login Endpoint - Refactored Token Creation Order

**Key Changes:**
1. Moved collection setup BEFORE JWT token creation
2. Fetch updated user from database after setting selected_collection_id
3. Include selected_collection_id in jwt_user_data

**Before:**
```python
# Create JWT tokens FIRST (before setting selected_collection_id)
jwt_user_data = {...}
jwt_token = google_auth_service.create_jwt_token(jwt_user_data)

# Set selected_collection_id LATER
await user_crud.collection.update_one(...)
```

**After:**
```python
# Set selected_collection_id FIRST
await user_crud.collection.update_one(...)

# Fetch updated user to get selected_collection_id
user_db = await user_crud.get_user_by_id(str(user_db.id))

# Create JWT tokens with selected_collection_id
jwt_user_data = {
    ...
    "selected_collection_id": user_db.selected_collection_id  # NEW
}
jwt_token = google_auth_service.create_jwt_token(jwt_user_data)
```

#### Renew JWT Token Endpoint - Fetch Latest Collection

**Changes:**
1. Fetch latest user data from database before creating new token
2. Update user_data with current selected_collection_id
3. Include selected_collection_id in response

**Before:**
```python
# Use old user_data from refresh token directly
new_jwt_token = google_auth_service.create_jwt_token(user_data)
```

**After:**
```python
# Fetch latest user data from database
user_db = await user_crud.get_user_by_id(user_id)
if user_db:
    # Update with latest selected_collection_id
    user_data["selected_collection_id"] = user_db.selected_collection_id

# Create token with updated data
new_jwt_token = google_auth_service.create_jwt_token(user_data)
```

## JWT Token Structure

### JWT Token Payload (Now)
```json
{
  "user_id": "673abc123def456789012345",
  "email": "user@example.com",
  "name": "John Doe",
  "picture": "https://...",
  "selected_collection_id": "673xyz789abc123456789012",
  "exp": 1728648000
}
```

### JWT Refresh Token Payload (Now)
```json
{
  "user_id": "673abc123def456789012345",
  "email": "user@example.com",
  "name": "John Doe",
  "picture": "https://...",
  "selected_collection_id": "673xyz789abc123456789012",
  "type": "refresh",
  "exp": 1731240000
}
```

## Benefits

1. **Reduced API Calls**: Frontend doesn't need to call `/auth/profile` or another endpoint to get selected collection
2. **Immediate Access**: Selected collection ID is available as soon as user authenticates
3. **Consistent State**: Token renewal updates the selected_collection_id from database
4. **Better UX**: Faster loading of user preferences

## Usage in Frontend

### Decode JWT Token
```typescript
import jwt_decode from 'jwt-decode';

interface JWTPayload {
  user_id: string;
  email: string;
  name: string;
  picture: string;
  selected_collection_id: string;
  exp: number;
}

// After login
const token = localStorage.getItem('jwt_token');
const decoded = jwt_decode<JWTPayload>(token);

console.log('User ID:', decoded.user_id);
console.log('Selected Collection:', decoded.selected_collection_id);

// Use selected collection ID immediately
loadVocabulariesFromCollection(decoded.selected_collection_id);
```

### React Example
```typescript
import { useEffect, useState } from 'react';
import jwt_decode from 'jwt-decode';

function App() {
  const [selectedCollectionId, setSelectedCollectionId] = useState<string | null>(null);
  
  useEffect(() => {
    const token = localStorage.getItem('jwt_token');
    if (token) {
      const decoded = jwt_decode<JWTPayload>(token);
      setSelectedCollectionId(decoded.selected_collection_id);
    }
  }, []);
  
  return (
    <div>
      <h1>Current Collection: {selectedCollectionId}</h1>
      {/* Your app content */}
    </div>
  );
}
```

### Update After Collection Change
```typescript
async function changeCollection(newCollectionId: string) {
  // Call API to change selected collection
  const response = await fetch('/api/v1/change-selected-collection', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ selected_collection_id: newCollectionId })
  });
  
  if (response.ok) {
    // Renew JWT token to get updated selected_collection_id
    const renewResponse = await fetch('/api/v1/auth/renew-jwt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ jwt_refresh_token: refreshToken })
    });
    
    const { jwt_token } = await renewResponse.json();
    localStorage.setItem('jwt_token', jwt_token);
    
    // Decode new token
    const decoded = jwt_decode<JWTPayload>(jwt_token);
    console.log('Updated collection:', decoded.selected_collection_id);
  }
}
```

## Token Flow

### Login Flow
```
1. User logs in with Google
   ↓
2. Create/update user in database
   ↓
3. Create/set default collection
   ↓
4. Fetch updated user (with selected_collection_id)
   ↓
5. Create JWT token (includes selected_collection_id)
   ↓
6. Create JWT refresh token (includes selected_collection_id)
   ↓
7. Return tokens to frontend
```

### Token Renewal Flow
```
1. Frontend requests token renewal
   ↓
2. Verify refresh token
   ↓
3. Fetch latest user data from database
   ↓
4. Update user_data with current selected_collection_id
   ↓
5. Create new JWT token (with latest selected_collection_id)
   ↓
6. Return new token to frontend
```

### Change Collection Flow
```
1. User changes selected collection
   ↓
2. API updates selected_collection_id in database
   ↓
3. Frontend requests token renewal
   ↓
4. New token includes updated selected_collection_id
   ↓
5. Frontend uses new collection ID
```

## Important Notes

### Token Expiration
- **JWT Token**: Expires in 1 hour
- **JWT Refresh Token**: Expires in 30 days
- Selected collection ID is updated when token is renewed

### Synchronization
When user changes selected collection:
1. Call `/change-selected-collection` API
2. Optionally renew JWT token immediately to get updated ID
3. Or wait until next automatic token renewal

### Null Value Handling
- `selected_collection_id` may be `null` for older users
- Frontend should handle `null` case gracefully
- Can default to first collection or prompt user to select

## Migration Considerations

### Existing Tokens
- Old tokens won't have `selected_collection_id` field
- Will be `undefined` when decoded
- New token will include it when renewed
- No breaking changes - field is optional

### Backward Compatibility
```typescript
// Safe decoding with fallback
const decoded = jwt_decode<JWTPayload>(token);
const collectionId = decoded.selected_collection_id || null;

if (!collectionId) {
  // Fetch from API or use default
  const profile = await fetch('/api/v1/auth/profile', {
    headers: { 'Authorization': `Bearer ${token}` }
  }).then(r => r.json());
  
  // Or renew token to get updated version
}
```

## Testing

### Test JWT Token Contains Field
```python
import jwt
from datetime import datetime, timedelta

# Create test token
user_data = {
    "id": "test_user_id",
    "email": "test@example.com",
    "name": "Test User",
    "picture": "https://...",
    "selected_collection_id": "test_collection_id"
}

token = google_auth_service.create_jwt_token(user_data)
decoded = jwt.decode(token, jwt_secret, algorithms=["HS256"])

assert decoded["selected_collection_id"] == "test_collection_id"
print("✅ JWT token includes selected_collection_id")
```

### Test Token Renewal Updates Collection
```python
# 1. Login and get tokens
login_response = await client.post("/api/v1/auth/google/login", ...)
jwt_token = login_response.json()["jwt_token"]
refresh_token = login_response.json()["jwt_refresh_token"]

# Decode original token
decoded1 = jwt.decode(jwt_token, verify=False)
original_collection = decoded1["selected_collection_id"]

# 2. Change collection
await client.post("/api/v1/change-selected-collection", 
    json={"selected_collection_id": "new_collection_id"},
    headers={"Authorization": f"Bearer {jwt_token}"})

# 3. Renew token
renew_response = await client.post("/api/v1/auth/renew-jwt",
    json={"jwt_refresh_token": refresh_token})
new_jwt_token = renew_response.json()["jwt_token"]

# Decode new token
decoded2 = jwt.decode(new_jwt_token, verify=False)
new_collection = decoded2["selected_collection_id"]

assert new_collection == "new_collection_id"
assert new_collection != original_collection
print("✅ Token renewal updates selected_collection_id")
```

## Security Considerations

1. **Token Size**: Adding one field has minimal impact on token size
2. **Sensitive Data**: Collection ID is not sensitive (user-specific identifier)
3. **Validation**: Always validate collection belongs to user when using it
4. **Tampering**: JWT signature prevents tampering with selected_collection_id

## Related Endpoints

- `POST /api/v1/auth/google/login` - Returns tokens with selected_collection_id
- `POST /api/v1/auth/renew-jwt` - Renews token with latest selected_collection_id
- `POST /api/v1/change-selected-collection` - Updates collection (recommend token renewal after)
- `GET /api/v1/auth/profile` - Returns user profile (includes selected_collection_id)

## Files Modified

1. ✅ `app/services/google_auth.py` - Added field to token payloads
2. ✅ `app/api/v1/routes.py` - Refactored login and renewal flows

## Validation

All files validated with no compilation errors:
- ✅ google_auth.py - No errors
- ✅ routes.py - No errors

---

**Status**: ✅ Completed  
**Version**: 1.0  
**Date Implemented**: 2025-10-11  
**Breaking Changes**: None (backward compatible)  
**Ready for Production**: Yes
