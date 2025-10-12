# Increment Streak API Documentation

## Date: 2025-10-12

## Overview
Dedicated API endpoint to increment the streak count for a specific date (defaults to today). This endpoint creates a new streak entry if it doesn't exist, or increments the count if it already exists.

## Endpoint Details

### POST `/api/v1/increment-streak`

Increments the streak count for the authenticated user on a specific date.

## Authentication
**Required**: Yes (Bearer Token)

Include JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Request

### Headers
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Request Body Schema
```json
{
  "learned_date": "YYYY-MM-DD"  // Optional, defaults to today
}
```

**Fields:**
- `learned_date` (string, optional): Date to increment streak. If not provided, uses current date (UTC)
  - Formats accepted: `YYYY-MM-DD` or ISO datetime
  - Examples: `"2025-10-12"` or `"2025-10-12T10:30:00Z"`

## Response Schema

### Success Response (200 OK)
```json
{
  "id": "673abc123def456789012345",
  "user_id": "673xyz789abc123456789012",
  "learned_date": "2025-10-12",
  "count": 3,
  "is_qualify": false,
  "created_at": "2025-10-12T10:30:00",
  "incremented": true,
  "status": true
}
```

**Fields:**
- `id` (string): Unique streak entry ID
- `user_id` (string): User's ID
- `learned_date` (string): Date of the streak (YYYY-MM-DD)
- `count` (integer): Current count after increment
- `is_qualify` (boolean): True when count >= 5
- `created_at` (string): ISO timestamp when first created
- `incremented` (boolean): 
  - `true` = Existing entry was incremented
  - `false` = New entry was created
- `status` (boolean): Always true for successful responses

### Error Responses

#### 400 Bad Request - Invalid Date Format
```json
{
  "detail": {
    "error": "invalid_date_format",
    "message": "learned_date must be in YYYY-MM-DD or ISO datetime format"
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

#### 500 Internal Server Error
```json
{
  "detail": {
    "error": "increment_failed",
    "message": "Failed to increment streak",
    "details": "Error details..."
  }
}
```

## Usage Examples

### Example 1: Increment Today's Streak (Default)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/increment-streak" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response (First time today):**
```json
{
  "id": "673abc123def456789012345",
  "user_id": "673xyz789abc123456789012",
  "learned_date": "2025-10-12",
  "count": 1,
  "is_qualify": false,
  "created_at": "2025-10-12T10:30:00",
  "incremented": false,
  "status": true
}
```

**Response (Second time today):**
```json
{
  "id": "673abc123def456789012345",
  "user_id": "673xyz789abc123456789012",
  "learned_date": "2025-10-12",
  "count": 2,
  "is_qualify": false,
  "created_at": "2025-10-12T10:30:00",
  "incremented": true,
  "status": true
}
```

### Example 2: Increment Specific Date

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/increment-streak" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"learned_date": "2025-10-10"}'
```

**Response:**
```json
{
  "id": "673def456abc789012345678",
  "user_id": "673xyz789abc123456789012",
  "learned_date": "2025-10-10",
  "count": 1,
  "is_qualify": false,
  "created_at": "2025-10-12T10:35:00",
  "incremented": false,
  "status": true
}
```

### Example 3: JavaScript/TypeScript

```typescript
async function incrementStreak(date = null) {
  const token = localStorage.getItem('jwt_token');
  
  const body = date ? { learned_date: date } : {};
  
  try {
    const response = await fetch('http://localhost:8000/api/v1/increment-streak', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('Streak incremented:', data);
      console.log(`Count: ${data.count}/5`);
      console.log(`Action: ${data.incremented ? 'Incremented' : 'Created'}`);
      
      if (data.is_qualify) {
        console.log('🎉 Qualified!');
      }
      
      return data;
    } else {
      console.error('Failed to increment streak:', response.status);
      throw new Error('Failed to increment streak');
    }
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

// Usage
await incrementStreak();  // Increment today
await incrementStreak('2025-10-10');  // Increment specific date
```

### Example 4: After User Action (React)

```tsx
import { useState } from 'react';
import axios from 'axios';

function ParagraphGenerator() {
  const [streakData, setStreakData] = useState(null);
  
  const handleGenerateParagraph = async () => {
    try {
      // 1. Generate paragraph
      const paragraphResponse = await axios.post('/api/v1/generate-paragraph', {
        language: 'English',
        vocabularies: ['hello', 'world'],
        length: 100,
        level: 'beginner'
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      // 2. Increment streak after successful generation
      const streakResponse = await axios.post('/api/v1/increment-streak', 
        {},  // Empty body = today
        {
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      setStreakData(streakResponse.data);
      
      // 3. Show notification
      if (streakResponse.data.is_qualify && !streakData?.is_qualify) {
        alert('🎉 Congratulations! You qualified today!');
      } else {
        alert(`✅ Streak updated! Count: ${streakResponse.data.count}/5`);
      }
      
    } catch (error) {
      console.error('Error:', error);
    }
  };
  
  return (
    <div>
      <button onClick={handleGenerateParagraph}>
        Generate Paragraph
      </button>
      
      {streakData && (
        <div className="streak-widget">
          <p>Today's Progress: {streakData.count}/5</p>
          {streakData.is_qualify && <span>🏆 Qualified!</span>}
        </div>
      )}
    </div>
  );
}
```

### Example 5: Python

```python
import requests

def increment_streak(token, learned_date=None):
    """
    Increment streak count for a specific date
    
    Args:
        token: JWT authentication token
        learned_date: Date string (YYYY-MM-DD) or None for today
    """
    url = "http://localhost:8000/api/v1/increment-streak"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    body = {"learned_date": learned_date} if learned_date else {}
    
    response = requests.post(url, headers=headers, json=body)
    return response.json()

# Usage
token = "YOUR_JWT_TOKEN"

# Increment today
result = increment_streak(token)
print(f"Count: {result['count']}, Qualified: {result['is_qualify']}")
print(f"Action: {'Incremented' if result['incremented'] else 'Created'}")

# Increment specific date
result = increment_streak(token, "2025-10-10")
print(f"Streak incremented for {result['learned_date']}")
```

### Example 6: Axios with Error Handling

```typescript
import axios from 'axios';

async function incrementStreakSafely(date = null) {
  try {
    const body = date ? { learned_date: date } : {};
    
    const response = await axios.post(
      'http://localhost:8000/api/v1/increment-streak',
      body,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    const data = response.data;
    
    // Handle success
    if (data.incremented) {
      console.log(`✅ Streak incremented to ${data.count}`);
    } else {
      console.log(`🆕 New streak started with count ${data.count}`);
    }
    
    // Check qualification
    if (data.is_qualify) {
      console.log('🏆 Qualified!');
    } else {
      const remaining = 5 - data.count;
      console.log(`📈 ${remaining} more to qualify`);
    }
    
    return data;
    
  } catch (error) {
    if (error.response) {
      const errorData = error.response.data.detail;
      
      switch (errorData.error) {
        case 'invalid_date_format':
          console.error('❌ Invalid date format. Use YYYY-MM-DD');
          break;
        case 'invalid_token':
          console.error('❌ Token expired. Please login again.');
          // Redirect to login
          window.location.href = '/login';
          break;
        default:
          console.error('❌ Failed to increment streak:', errorData.message);
      }
    } else {
      console.error('❌ Network error:', error.message);
    }
    
    throw error;
  }
}
```

## Integration Flow

### Typical Usage Pattern

```typescript
// 1. User completes an activity (generates paragraph, studies vocab, etc.)
async function onUserActivity() {
  try {
    // Perform the activity
    await performActivity();
    
    // Increment streak
    const streak = await incrementStreak();
    
    // Update UI
    updateStreakDisplay(streak);
    
    // Show celebration if qualified
    if (streak.is_qualify && streak.count === 5) {
      showCelebration();
    }
    
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### Complete React Example

```tsx
import { useState, useEffect } from 'react';
import axios from 'axios';

function StreakTracker() {
  const [streak, setStreak] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Load today's status on mount
  useEffect(() => {
    loadTodayStatus();
  }, []);
  
  const loadTodayStatus = async () => {
    const response = await axios.get('/api/v1/today-streak-status', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    setStreak(response.data);
  };
  
  const handleIncrementStreak = async () => {
    setLoading(true);
    try {
      const response = await axios.post(
        '/api/v1/increment-streak',
        {},
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      setStreak(response.data);
      
      // Show appropriate message
      if (response.data.is_qualify) {
        if (response.data.count === 5) {
          alert('🎉 You just qualified! Congratulations!');
        } else {
          alert(`🏆 You're qualified! Count: ${response.data.count}`);
        }
      } else {
        alert(`✅ Progress updated! ${response.data.count}/5`);
      }
      
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to update streak');
    } finally {
      setLoading(false);
    }
  };
  
  if (!streak) return <div>Loading...</div>;
  
  const progress = Math.min((streak.count / 5) * 100, 100);
  
  return (
    <div className="streak-tracker">
      <h3>Today's Streak: {streak.date}</h3>
      
      <div className="count-display">
        <div className="count">{streak.count} / 5</div>
      </div>
      
      <div className="progress-bar">
        <div className="fill" style={{ width: `${progress}%` }} />
      </div>
      
      {streak.is_qualify ? (
        <div className="qualified-badge">
          🏆 Qualified Today!
        </div>
      ) : (
        <div>
          <p>{5 - streak.count} more activities to qualify</p>
          <button 
            onClick={handleIncrementStreak}
            disabled={loading}
          >
            {loading ? 'Updating...' : 'Record Activity'}
          </button>
        </div>
      )}
    </div>
  );
}
```

## How It Works

### Count Increment Logic

1. **First Call on a Date** → Creates entry with `count = 1`, `incremented = false`
2. **Second Call** → Updates entry to `count = 2`, `incremented = true`
3. **Third Call** → Updates entry to `count = 3`, `incremented = true`
4. **...continues...**
5. **Fifth Call** → Updates to `count = 5`, `is_qualify = true`
6. **Sixth Call and beyond** → `count = 6, 7, 8...`, `is_qualify` stays `true`

### Example Flow

```javascript
// Day 1 - First activity
POST /increment-streak → { count: 1, incremented: false, is_qualify: false }

// Day 1 - Second activity
POST /increment-streak → { count: 2, incremented: true, is_qualify: false }

// Day 1 - Fifth activity
POST /increment-streak → { count: 5, incremented: true, is_qualify: true } 🎉

// Day 1 - Sixth activity
POST /increment-streak → { count: 6, incremented: true, is_qualify: true }

// Day 2 - First activity (new date)
POST /increment-streak → { count: 1, incremented: false, is_qualify: false }
```

## Common Use Cases

### 1. After Generating Paragraph
```typescript
// After user generates a paragraph successfully
const paragraph = await generateParagraph(params);
await incrementStreak();  // Track this activity
```

### 2. After Studying Vocabulary
```typescript
// After user studies a vocabulary word
await studyVocabulary(vocabId);
await incrementStreak();  // Track this study session
```

### 3. Manual Activity Recording
```typescript
// User clicks "Mark Today as Complete"
<button onClick={() => incrementStreak()}>
  ✅ Mark Activity Complete
</button>
```

### 4. Backfill Historical Data
```typescript
// Retroactively record activities for past dates
const dates = ['2025-10-01', '2025-10-02', '2025-10-03'];
for (const date of dates) {
  await incrementStreak(date);
}
```

### 5. Gamification Features
```typescript
async function recordActivityWithRewards() {
  const result = await incrementStreak();
  
  // Unlock achievements
  if (result.count === 1) {
    unlockAchievement('first_activity_today');
  }
  if (result.count === 5) {
    unlockAchievement('daily_goal_reached');
    showConfetti();
  }
  if (result.count === 10) {
    unlockAchievement('over_achiever');
  }
}
```

## Related Endpoints

- `GET /api/v1/today-streak-status` - Check current status without incrementing
- `POST /api/v1/generate-paragraph` - Generate paragraph (no longer auto-increments streak)
- `POST /api/v1/streak` - Manual streak management (create/update)
- `GET /api/v1/streak-chain` - Get historical streak data

## Key Differences from Other Endpoints

| Endpoint | Purpose | Auto-Increment |
|----------|---------|----------------|
| `POST /increment-streak` | **Increment count** | ✅ Yes |
| `POST /streak` | Manual create/update | ❌ No |
| `GET /today-streak-status` | Read-only status | ❌ No |
| `POST /generate-paragraph` | Generate text | ❌ No (removed) |

## Best Practices

1. ✅ **Call after successful activity** - Only increment when user completes meaningful action
2. ✅ **Handle errors gracefully** - Don't block user workflow if streak increment fails
3. ✅ **Show feedback to user** - Display count and qualification status
4. ✅ **Use for gamification** - Unlock achievements, show progress
5. ✅ **Date format must be `YYYY-MM-DD`**
6. ✅ **Token is required** - Ensure user is authenticated
7. ✅ **Check `incremented` field** - Know if it was new or existing entry

## Performance Considerations

- **Single Database Query**: Fast lookup and update
- **Indexed Fields**: `user_id` and `learned_date` are indexed
- **Response Time**: Typically < 50ms
- **Idempotent**: Can be called multiple times safely

## Troubleshooting

### Issue: Count not incrementing
- Check if you're using the correct date format
- Verify the date matches the entry you're trying to update
- Check database for existing entries: `db.streak.find({user_id: ObjectId("..."), learned_date: ISODate("2025-10-12")})`

### Issue: `is_qualify` not updating
- Qualification happens automatically when `count >= 5`
- Check the response to see actual count value
- Verify database entry was updated

### Issue: Wrong date
- Server uses UTC timezone
- Make sure your date string matches UTC date
- Check server time: `date -u`

## Security Considerations

1. **Authentication Required**: All requests must include valid JWT token
2. **User Isolation**: Can only increment own streak
3. **Rate Limiting**: Consider adding rate limits for abuse prevention
4. **Data Validation**: Date format is validated server-side

---

**Version**: 1.0  
**Last Updated**: 2025-10-12  
**API Endpoint**: `POST /api/v1/increment-streak`  
**Authentication**: Required (Bearer Token)
