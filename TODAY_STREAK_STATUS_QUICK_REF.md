# Today Streak Status API - Quick Reference

## Endpoint
```
GET /api/v1/today-streak-status
```

## Authentication
✅ **Required** - Bearer Token

## Request
```bash
curl -X GET "http://localhost:8000/api/v1/today-streak-status" \
  -H "Authorization: Bearer <token>"
```

## Response
```json
{
  "count": 3,
  "is_qualify": false,
  "date": "2025-10-12",
  "status": true
}
```

## Response Fields
| Field | Type | Description |
|-------|------|-------------|
| `count` | int | Number of paragraphs generated today (0 if no data) |
| `is_qualify` | bool | True if count >= 5 |
| `date` | string | Current date (YYYY-MM-DD, UTC) |
| `status` | bool | Always true |

## Status Codes
- **200 OK** - Success
- **401 Unauthorized** - Missing or invalid token
- **500 Internal Server Error** - Server error

## Key Features
- ✅ Automatically returns current day's data
- ✅ No date parameter needed
- ✅ Returns defaults if no data exists (count=0, is_qualify=false)
- ✅ Uses UTC timezone
- ✅ Fast single query

## Quick JavaScript Example
```javascript
const response = await fetch('http://localhost:8000/api/v1/today-streak-status', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const data = await response.json();

console.log(`Progress: ${data.count}/5`);
if (data.is_qualify) {
  console.log('✅ Qualified today!');
}
```

## Quick React Hook
```typescript
function useStreakStatus() {
  const [streak, setStreak] = useState(null);
  
  useEffect(() => {
    fetch('/api/v1/today-streak-status', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(r => r.json())
    .then(setStreak);
  }, []);
  
  return streak;
}
```

## Display Example
```typescript
<div>
  <h3>Today: {streak.date}</h3>
  <p>{streak.count} / 5 paragraphs</p>
  <ProgressBar value={streak.count} max={5} />
  {streak.is_qualify && <Badge>✅ Qualified</Badge>}
</div>
```

## Business Logic
- Count increments when user generates a paragraph
- Qualification when `count >= 5`
- Resets daily at midnight UTC
- Each day is independent

## Related Endpoints
- `POST /api/v1/generate-paragraph` - Increments streak count
- `POST /api/v1/streak` - Manually manage streak
- `GET /api/v1/streak-chain` - Get date range data

## Testing
```bash
python test_today_streak_status.py
```

## Common Use Cases
1. **Dashboard Widget** - Show today's progress
2. **Motivational Prompt** - Encourage users
3. **Gamification** - Unlock achievements
4. **Progress Notifications** - Alert when close to goal

## Default Behavior
When no data exists for today:
```json
{
  "count": 0,
  "is_qualify": false,
  "date": "2025-10-12",
  "status": true
}
```

---
📘 **Full Documentation**: `TODAY_STREAK_STATUS_API.md`  
🧪 **Test Script**: `test_today_streak_status.py`
