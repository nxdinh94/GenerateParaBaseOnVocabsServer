# JWT Token - Selected Collection ID - Quick Reference

## What Changed
Added `selected_collection_id` field to JWT tokens.

## Token Payload (Now)
```json
{
  "user_id": "673abc...",
  "email": "user@example.com",
  "name": "John Doe",
  "picture": "https://...",
  "selected_collection_id": "673xyz...",  // ← NEW
  "exp": 1728648000
}
```

## Frontend Access
```typescript
import jwt_decode from 'jwt-decode';

const token = localStorage.getItem('jwt_token');
const decoded = jwt_decode(token);
const collectionId = decoded.selected_collection_id;

// Use it immediately
loadVocabularies(collectionId);
```

## After Changing Collection
```typescript
// 1. Change collection
await fetch('/api/v1/change-selected-collection', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ selected_collection_id: newId })
});

// 2. Renew token to get updated ID
const renewResponse = await fetch('/api/v1/auth/renew-jwt', {
  method: 'POST',
  body: JSON.stringify({ jwt_refresh_token: refreshToken })
});

const { jwt_token } = await renewResponse.json();
const newDecoded = jwt_decode(jwt_token);
// newDecoded.selected_collection_id now has the new value
```

## Files Modified
- ✅ `app/services/google_auth.py`
- ✅ `app/api/v1/routes.py`

## Testing
```bash
python test_jwt_selected_collection.py
```

## Documentation
- Full docs: `JWT_SELECTED_COLLECTION_ID.md`
- Summary: `JWT_SELECTED_COLLECTION_SUMMARY.md`
