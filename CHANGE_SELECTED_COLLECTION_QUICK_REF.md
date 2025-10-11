# Change Selected Collection - Quick Reference

## Endpoint
```
POST /api/v1/change-selected-collection
```

## Request
```bash
curl -X POST "http://localhost:8000/api/v1/change-selected-collection" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"selected_collection_id": "673abc123def456789012345"}'
```

## Request Body
```json
{
  "selected_collection_id": "673abc123def456789012345"
}
```

## Response (Success)
```json
{
  "status": true,
  "message": "Selected collection updated successfully",
  "selected_collection_id": "673abc123def456789012345"
}
```

## JavaScript/TypeScript
```typescript
const response = await fetch('/api/v1/change-selected-collection', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ selected_collection_id: collectionId })
});
const data = await response.json();
```

## Python
```python
import requests

response = requests.post(
    'http://localhost:8000/api/v1/change-selected-collection',
    headers={'Authorization': f'Bearer {token}'},
    json={'selected_collection_id': collection_id}
)
data = response.json()
```

## Error Codes
- **400**: Missing/empty collection_id
- **401**: Invalid/missing authentication
- **403**: Collection not owned by user
- **404**: Collection not found
- **500**: Server error

## Files
- **Documentation**: `CHANGE_SELECTED_COLLECTION_API.md`
- **Summary**: `CHANGE_SELECTED_COLLECTION_SUMMARY.md`
- **Tests**: `test_change_selected_collection.py`

## Testing
```bash
# Run test script
python test_change_selected_collection.py
```

## Related Endpoints
- `GET /api/v1/vocab-collections` - List collections
- `POST /api/v1/vocab-collections` - Create collection
- `GET /api/v1/vocabs_base_on_category` - Get vocabs by collection
