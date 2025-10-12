# Increment Streak API - Quick Reference

## Endpoint
```
POST /api/v1/increment-streak
```

## Authentication
✅ **Required** - Bearer Token

## Request
```bash
curl -X POST "http://localhost:8000/api/v1/increment-streak" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{}'  # Empty = today, or {"learned_date": "YYYY-MM-DD"}
```

## Request Body (Optional)
```json
{
  "learned_date": "2025-10-12"  // Optional, defaults to today
}
```

## Response
```json
{
  "id": "673abc123...",
  "user_id": "673xyz789...",
  "learned_date": "2025-10-12",
  "count": 3,
  "is_qualify": false,
  "created_at": "2025-10-12T10:30:00",
  "incremented": true,
  "status": true
}
```

## Response Fields
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Streak entry ID |
| `user_id` | string | User's ID |
| `learned_date` | string | Date (YYYY-MM-DD) |
| `count` | int | Current count after increment |
| `is_qualify` | bool | True if count >= 5 |
| `created_at` | string | ISO timestamp |
| `incremented` | bool | True = existing entry, False = new entry |
| `status` | bool | Always true |

## Status Codes
- **200 OK** - Success
- **400 Bad Request** - Invalid date format
- **401 Unauthorized** - Missing or invalid token
- **500 Internal Server Error** - Server error

## Quick JavaScript Example
```javascript
// Increment today
const response = await fetch('http://localhost:8000/api/v1/increment-streak', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({})  // Empty = today
});

const data = await response.json();
console.log(`Count: ${data.count}/5, Qualified: ${data.is_qualify}`);
```

## Quick React Hook
```typescript
async function incrementStreak(date = null) {
  const body = date ? { learned_date: date } : {};
  
  const response = await fetch('/api/v1/increment-streak', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  });
  
  return await response.json();
}

// Usage
const result = await incrementStreak();  // Today
const result = await incrementStreak('2025-10-10');  // Specific date
```

## When to Use

✅ **Use this endpoint when:**
- User completes an activity (generates paragraph, studies vocab, etc.)
- User manually marks day as complete
- You want to track daily progress
- Building gamification features

❌ **Don't use for:**
- Just checking current status (use `GET /today-streak-status`)
- Reading historical data (use `GET /streak-chain`)

## How It Works

1. **First call on a date** → Creates entry with `count = 1`
2. **Second call** → Increments to `count = 2`
3. **Fifth call** → `count = 5`, `is_qualify = true` 🎉
4. **Subsequent calls** → Count keeps increasing

## Common Pattern
```typescript
async function onUserActivity() {
  // 1. User does something (generate paragraph, study vocab, etc.)
  await performActivity();
  
  // 2. Increment streak
  const streak = await incrementStreak();
  
  // 3. Show feedback
  if (streak.is_qualify && streak.count === 5) {
    alert('🎉 Qualified today!');
  } else {
    alert(`✅ ${streak.count}/5 activities`);
  }
}
```

## Integration Example
```typescript
// After generating paragraph
async function handleGenerateParagraph() {
  // Generate paragraph
  const paragraph = await generateParagraph(params);
  
  // Increment streak
  const streak = await incrementStreak();
  
  // Update UI
  updateStreakDisplay(streak);
}
```

## Error Handling
```typescript
try {
  const result = await incrementStreak();
  console.log(`✅ Count: ${result.count}`);
} catch (error) {
  if (error.response?.status === 401) {
    // Token expired - redirect to login
    window.location.href = '/login';
  } else {
    console.error('Failed to increment streak');
  }
}
```

## Key Features
- ✅ Automatically detects new vs existing entries
- ✅ Auto-qualifies when count >= 5
- ✅ Defaults to today if no date specified
- ✅ Accepts both date-only and ISO datetime formats
- ✅ Returns `incremented` flag to show if it was new or updated

## Related Endpoints
- `GET /today-streak-status` - Check status (read-only)
- `POST /streak` - Manual streak management
- `GET /streak-chain` - Historical data
- `POST /generate-paragraph` - Generate text (no longer auto-increments)

## Tips
- 💡 Call after successful user activity
- 💡 Use `incremented` field to customize messages
- 💡 Show celebration when `is_qualify` becomes true
- 💡 Handle errors gracefully - don't block user workflow
- 💡 Check `today-streak-status` first to show current progress

---
📘 **Full Documentation**: `INCREMENT_STREAK_API.md`  
🔗 **Related**: `TODAY_STREAK_STATUS_API.md`, `STREAK_STEP_FIELD_REMOVAL.md`
