# Today Streak Status API Documentation

## Date: 2025-10-12

## Overview
API endpoint to get the current day's streak status, including the count of paragraphs generated, qualification status, and the current date. This endpoint automatically returns data for today's date.

## Endpoint Details

### GET `/api/v1/today-streak-status`

Returns the streak status for the current day (UTC timezone).

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
```

### Query Parameters
None - The endpoint automatically uses the current date (UTC)

## Response Schema

### Success Response (200 OK)
```json
{
  "count": 3,
  "is_qualify": false,
  "date": "2025-10-12",
  "status": true
}
```

**Fields:**
- `count` (integer): Number of paragraphs generated today (0 if no data exists)
- `is_qualify` (boolean): Whether user has qualified today (true if count >= 5)
- `date` (string): Current date in YYYY-MM-DD format (UTC)
- `status` (boolean): Always true for successful responses

### Scenarios

#### Scenario 1: User has generated paragraphs today
```json
{
  "count": 3,
  "is_qualify": false,
  "date": "2025-10-12",
  "status": true
}
```

#### Scenario 2: User has qualified (count >= 5)
```json
{
  "count": 5,
  "is_qualify": true,
  "date": "2025-10-12",
  "status": true
}
```

#### Scenario 3: No data for today (fresh start)
```json
{
  "count": 0,
  "is_qualify": false,
  "date": "2025-10-12",
  "status": true
}
```

### Error Responses

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
    "error": "retrieval_failed",
    "message": "Failed to get today's streak status",
    "details": "Error details..."
  }
}
```

## Usage Examples

### Example 1: Basic Request (cURL)

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/today-streak-status" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response (200 OK):**
```json
{
  "count": 2,
  "is_qualify": false,
  "date": "2025-10-12",
  "status": true
}
```

### Example 2: JavaScript/TypeScript

```typescript
async function getTodayStreakStatus() {
  const token = localStorage.getItem('jwt_token');
  
  try {
    const response = await fetch('http://localhost:8000/api/v1/today-streak-status', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('Today\'s Streak Status:', data);
      
      // Display to user
      console.log(`Date: ${data.date}`);
      console.log(`Count: ${data.count}`);
      console.log(`Qualified: ${data.is_qualify ? 'Yes' : 'No'}`);
      
      // Calculate progress
      const progress = Math.min((data.count / 5) * 100, 100);
      console.log(`Progress: ${progress}%`);
      
      return data;
    } else {
      console.error('Failed to fetch streak status:', response.status);
      throw new Error('Failed to fetch streak status');
    }
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

// Usage
getTodayStreakStatus()
  .then(status => {
    if (status.is_qualify) {
      alert('Congratulations! You qualified today! 🎉');
    } else {
      const remaining = 5 - status.count;
      console.log(`${remaining} more paragraphs to qualify`);
    }
  })
  .catch(error => {
    console.error('Error fetching streak:', error);
  });
```

### Example 3: React Component

```typescript
import { useState, useEffect } from 'react';

interface StreakStatus {
  count: number;
  is_qualify: boolean;
  date: string;
  status: boolean;
}

function TodayStreakCard() {
  const [streak, setStreak] = useState<StreakStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    fetchStreakStatus();
  }, []);
  
  const fetchStreakStatus = async () => {
    const token = localStorage.getItem('jwt_token');
    
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/today-streak-status', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setStreak(data);
        setError(null);
      } else {
        setError('Failed to fetch streak status');
      }
    } catch (err) {
      setError('Network error');
      console.error('Error fetching streak:', err);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!streak) return null;
  
  const progress = (streak.count / 5) * 100;
  const remaining = Math.max(0, 5 - streak.count);
  
  return (
    <div className="streak-card">
      <h3>Today's Progress</h3>
      <div className="date">{streak.date}</div>
      
      <div className="count-display">
        <div className="count-number">{streak.count}</div>
        <div className="count-label">paragraphs today</div>
      </div>
      
      <div className="progress-bar-container">
        <div 
          className="progress-bar" 
          style={{ width: `${progress}%` }}
        />
      </div>
      
      {streak.is_qualify ? (
        <div className="qualified-badge">
          ✅ Qualified Today!
        </div>
      ) : (
        <div className="remaining-text">
          {remaining} more to qualify
        </div>
      )}
      
      <button onClick={fetchStreakStatus}>Refresh</button>
    </div>
  );
}

export default TodayStreakCard;
```

### Example 4: Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
jwt_token = "your_jwt_token_here"

def get_today_streak_status():
    """Get today's streak status"""
    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/today-streak-status",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Today's Streak Status:")
        print(f"   Date: {data['date']}")
        print(f"   Count: {data['count']}")
        print(f"   Qualified: {data['is_qualify']}")
        
        if data['is_qualify']:
            print("🎉 You qualified today!")
        else:
            remaining = 5 - data['count']
            print(f"📈 {remaining} more paragraphs to qualify")
        
        return data
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.json())
        return None

# Usage
status = get_today_streak_status()
if status and status['count'] > 0:
    progress = (status['count'] / 5) * 100
    print(f"\nProgress: {progress:.1f}%")
```

## Integration Flow

### Typical User Flow

1. **User logs in** → Dashboard loads
2. **Call today-streak-status** → Display current progress
3. **User generates paragraphs** → Count increments automatically
4. **Refresh streak status** → Show updated count
5. **Count reaches 5** → is_qualify becomes true
6. **Show celebration** → User qualified for the day!

### Complete Example Flow

```typescript
// 1. On dashboard load
useEffect(() => {
  loadStreakStatus();
}, []);

async function loadStreakStatus() {
  const status = await fetch('/api/v1/today-streak-status', {
    headers: { 'Authorization': `Bearer ${token}` }
  }).then(r => r.json());
  
  setStreakStatus(status);
}

// 2. After generating paragraph
async function handleGenerateParagraph() {
  // Generate paragraph
  const result = await fetch('/api/v1/generate-paragraph', {...});
  
  if (result.ok) {
    // Refresh streak status
    const newStatus = await fetch('/api/v1/today-streak-status', {
      headers: { 'Authorization': `Bearer ${token}` }
    }).then(r => r.json());
    
    setStreakStatus(newStatus);
    
    // Show celebration if qualified
    if (newStatus.is_qualify && !streakStatus.is_qualify) {
      showCelebration('You qualified today! 🎉');
    }
  }
}

// 3. Display UI
<div className="streak-widget">
  <h3>Today: {streakStatus.date}</h3>
  <div className="count">{streakStatus.count} / 5</div>
  <ProgressBar value={streakStatus.count} max={5} />
  {streakStatus.is_qualify && <Badge>✅ Qualified</Badge>}
</div>
```

## Business Logic

### Count Increment
- Count increments when user generates a paragraph
- Handled automatically by `POST /generate-paragraph` endpoint
- Updates the streak entry for the current date

### Qualification Rule
- User qualifies when `count >= 5`
- `is_qualify` is automatically set to `true` when count reaches 5
- Qualification status persists for the day

### Date Handling
- Uses UTC timezone
- Date format: YYYY-MM-DD
- Resets daily at midnight UTC
- Each day is independent

## Use Cases

### 1. Dashboard Widget
Display today's progress prominently on the dashboard:
```typescript
function DashboardWidget() {
  const [streak, setStreak] = useState(null);
  
  useEffect(() => {
    // Fetch on load
    fetchStreak();
    
    // Refresh every 60 seconds
    const interval = setInterval(fetchStreak, 60000);
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="widget">
      <h3>Today's Goal</h3>
      <CircularProgress value={streak.count} max={5} />
      {streak.is_qualify && <Confetti />}
    </div>
  );
}
```

### 2. Motivational Prompt
Show encouragement based on progress:
```typescript
function getMotivationalMessage(count: number, is_qualify: boolean) {
  if (is_qualify) {
    return "Amazing! You've qualified today! 🎉";
  } else if (count === 0) {
    return "Start your learning journey today!";
  } else if (count < 3) {
    return `Great start! ${5 - count} more to go!`;
  } else if (count < 5) {
    return `You're almost there! Just ${5 - count} more!`;
  }
}
```

### 3. Gamification Features
```typescript
function StreakGamification({ streak }) {
  const milestones = [
    { count: 1, message: "🌟 First paragraph of the day!" },
    { count: 3, message: "🔥 You're on fire!" },
    { count: 5, message: "🏆 Qualified! You're a champion!" }
  ];
  
  return (
    <div>
      {milestones.map(m => 
        streak.count >= m.count && (
          <Achievement key={m.count} message={m.message} />
        )
      )}
    </div>
  );
}
```

### 4. Progress Notification
```typescript
// Show notification when user gets closer to goal
if (previousCount < streak.count) {
  if (streak.count === 4) {
    showNotification('One more paragraph to qualify! 🎯');
  } else if (streak.is_qualify) {
    showNotification('Congratulations! You qualified today! 🎉');
  }
}
```

## Related Endpoints

- `POST /api/v1/generate-paragraph` - Generates paragraph and auto-updates streak
- `POST /api/v1/streak` - Manually create/update streak entry
- `GET /api/v1/streak-chain` - Get streak data for a date range
- `GET /api/v1/auth/profile` - Get user profile

## Performance Considerations

- **Single Database Query**: Fetches only today's data
- **Indexed Fields**: user_id and learned_date are indexed
- **Fast Response**: Typically < 50ms
- **No Pagination Needed**: Returns single day data

## Caching Strategy (Optional)

For high-traffic applications:
```typescript
// Cache for 60 seconds
const CACHE_TTL = 60000;
let cachedStreak = null;
let cacheTimestamp = 0;

async function getCachedStreakStatus() {
  const now = Date.now();
  
  if (cachedStreak && (now - cacheTimestamp) < CACHE_TTL) {
    return cachedStreak;
  }
  
  const streak = await fetchStreakStatus();
  cachedStreak = streak;
  cacheTimestamp = now;
  
  return streak;
}
```

## Testing

Run the test script:
```bash
python test_today_streak_status.py
```

Test scenarios:
1. ✅ Get status with data
2. ✅ Get status without data (returns defaults)
3. ✅ Verify current date
4. ✅ Check qualification logic
5. ✅ Test authentication
6. ✅ Test after paragraph generation

## Troubleshooting

### Common Issues

**Issue: Returns count=0 when expecting data**
- Check if data exists for today's date in UTC
- Verify user_id matches the authenticated user
- Check database for streak entries: `db.streak.find({user_id: ObjectId("..."), learned_date: ISODate("2025-10-12")})`

**Issue: is_qualify is false when count >= 5**
- This should auto-update when count reaches 5
- Check the generate-paragraph endpoint logic
- Manually verify database: `db.streak.find({count: {$gte: 5}, is_qualify: false})`

**Issue: Wrong date returned**
- Server uses UTC timezone
- Check server time: `date -u`
- Adjust timezone in frontend if needed

## Security Considerations

1. **Authentication Required**: All requests must include valid JWT token
2. **User Isolation**: Returns data only for authenticated user
3. **Read-Only**: Endpoint only reads data, doesn't modify
4. **Rate Limiting**: Consider adding rate limits for high-traffic scenarios

---

**Version**: 1.0  
**Last Updated**: 2025-10-12  
**API Endpoint**: `GET /api/v1/today-streak-status`  
**Authentication**: Required (Bearer Token)
