# Streak Feature Documentation

## Overview
The Streak feature allows users to track their daily learning progress. Users can record their learning activity for each day, and the system will generate a streak chain showing which days have been completed.

## Database Schema

### Collection: `streak`

| Field | Type | Description | Required | Default |
|-------|------|-------------|----------|---------|
| `_id` | ObjectId | Unique identifier | Auto-generated | - |
| `user_id` | ObjectId | Reference to users collection | Yes | - |
| `learned_date` | Date | Date when learning occurred (date-only, no time) | Yes | - |
| `step` | Integer | Progress step/count for the day | No | 1 |
| `created_at` | DateTime | When the record was created | Auto-set | Current UTC time |

**Indexes:**
- `user_id` + `learned_date` (compound unique index to prevent duplicates)
- `user_id` (for querying user's streaks)
- `learned_date` (for date range queries)

### Collection: `users` (Updated)

Added field:
- `selected_collection_id` (String, Optional): The ID of the user's currently selected vocabulary collection. Defaults to "default" collection for new users.

## API Endpoints

### 1. Create/Update Streak

**POST** `/api/v1/streak`

Creates a new streak entry or updates an existing one for the same user and date.

**Authentication:** Required (Bearer token)

**Request Body:**
```json
{
  "learned_date": "2025-10-11",  // Optional, defaults to today (YYYY-MM-DD format)
  "step": 5                       // Optional, defaults to 1
}
```

**Response (200 OK):**
```json
{
  "id": "67098abc123def456789",
  "user_id": "67098abc123def456789",
  "learned_date": "2025-10-11",
  "step": 5,
  "created_at": "2025-10-11T10:30:00.000Z",
  "status": true
}
```

**Error Responses:**
- `400 Bad Request`: Invalid date format
- `401 Unauthorized`: Missing or invalid token
- `500 Internal Server Error`: Database error

**Example Usage:**
```javascript
// JavaScript/React
const createStreak = async () => {
  const response = await fetch('http://localhost:8000/api/v1/streak', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      step: 5
    })
  });
  const data = await response.json();
  console.log(data);
};
```

```python
# Python
import requests

url = "http://localhost:8000/api/v1/streak"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
data = {
    "step": 5
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
```

---

### 2. Get Streak Chain

**GET** `/api/v1/streak-chain`

Retrieves a streak chain for a specified date range, showing which days have been completed.

**Authentication:** Required (Bearer token)

**Query Parameters:**
- `startday` (required): Start date in YYYY-MM-DD format
- `endday` (required): End date in YYYY-MM-DD format

**Response (200 OK):**
```json
{
  "id": 12345678,
  "start_date": "2025-09-20",
  "end_date": "2025-10-11",
  "dates": [
    { "date": "2025-09-20", "completed": false },
    { "date": "2025-09-21", "completed": true },
    { "date": "2025-09-22", "completed": false },
    { "date": "2025-09-23", "completed": true },
    // ... more dates
  ],
  "total_days": 22,
  "completed_days": 15,
  "status": true
}
```

**Response Fields:**
- `id`: A pseudo-unique identifier for this query (hash of user_id + dates)
- `start_date`: The requested start date
- `end_date`: The requested end date
- `dates`: Array of all dates in the range with completion status
  - `date`: Date in YYYY-MM-DD format
  - `completed`: Boolean indicating if user has a streak entry for this date
- `total_days`: Total number of days in the range
- `completed_days`: Number of days with completed streaks
- `status`: Success indicator

**Error Responses:**
- `400 Bad Request`: Invalid date format or invalid date range (start > end)
- `401 Unauthorized`: Missing or invalid token
- `500 Internal Server Error`: Database error

**Example Usage:**
```javascript
// JavaScript/React - Get last 30 days
const getStreakChain = async () => {
  const endDate = new Date();
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - 30);
  
  const formatDate = (date) => date.toISOString().split('T')[0];
  
  const params = new URLSearchParams({
    startday: formatDate(startDate),
    endday: formatDate(endDate)
  });
  
  const response = await fetch(
    `http://localhost:8000/api/v1/streak-chain?${params}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  const data = await response.json();
  console.log(`Completion rate: ${(data.completed_days / data.total_days * 100).toFixed(1)}%`);
  return data;
};
```

```python
# Python - Get current month
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date.replace(day=1)  # First day of current month

url = "http://localhost:8000/api/v1/streak-chain"
headers = {"Authorization": f"Bearer {token}"}
params = {
    "startday": start_date.strftime('%Y-%m-%d'),
    "endday": end_date.strftime('%Y-%m-%d')
}

response = requests.get(url, headers=headers, params=params)
data = response.json()

print(f"Completed: {data['completed_days']}/{data['total_days']} days")
print(f"Rate: {data['completed_days'] / data['total_days'] * 100:.1f}%")
```

---

## Use Cases

### 1. Daily Learning Tracker
Record a streak entry each time a user completes a learning session:
```javascript
// After user completes a lesson or practices vocabulary
const recordLearningSession = async (stepCount) => {
  await fetch('http://localhost:8000/api/v1/streak', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ step: stepCount })
  });
};
```

### 2. Monthly Progress Calendar
Display a calendar showing which days the user studied:
```javascript
const generateCalendar = async () => {
  const today = new Date();
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
  const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0);
  
  const response = await fetch(
    `http://localhost:8000/api/v1/streak-chain?startday=${formatDate(firstDay)}&endday=${formatDate(lastDay)}`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  
  const data = await response.json();
  
  // Render calendar with data.dates
  data.dates.forEach(day => {
    const dayElement = document.querySelector(`[data-date="${day.date}"]`);
    if (day.completed) {
      dayElement.classList.add('completed');
    }
  });
};
```

### 3. Streak Statistics
Calculate and display streak statistics:
```javascript
const getStreakStats = async () => {
  const response = await fetch(/* ... */);
  const data = await response.json();
  
  let currentStreak = 0;
  let longestStreak = 0;
  let tempStreak = 0;
  
  // Calculate from most recent date backwards
  for (let i = data.dates.length - 1; i >= 0; i--) {
    if (data.dates[i].completed) {
      tempStreak++;
      if (i === data.dates.length - 1 || currentStreak > 0) {
        currentStreak = tempStreak;
      }
      longestStreak = Math.max(longestStreak, tempStreak);
    } else {
      if (i === data.dates.length - 1) {
        currentStreak = 0;
      }
      tempStreak = 0;
    }
  }
  
  return {
    currentStreak,
    longestStreak,
    totalDays: data.completed_days,
    completionRate: (data.completed_days / data.total_days * 100).toFixed(1)
  };
};
```

---

## Implementation Notes

### Date Handling
- All dates are stored in the database as date-only (time set to 00:00:00 UTC)
- API accepts dates in `YYYY-MM-DD` format or ISO datetime format
- API responses always return dates in `YYYY-MM-DD` format
- Duplicate entries for the same user and date are prevented (updates existing entry instead)

### User Collection Selection
- New users automatically get a "Default" vocabulary collection created
- The `selected_collection_id` field in the users collection is set to this default collection
- This allows the frontend to know which collection is currently active for the user

### Performance Considerations
- Indexes are crucial for performance:
  - Compound index on `(user_id, learned_date)` for fast lookups and duplicate prevention
  - Index on `user_id` for fetching all user streaks
  - Index on `learned_date` for date range queries

### Migration Guide
If you have existing users without the `selected_collection_id` field:

```python
# Migration script
from app.database.connection import get_collection
from bson import ObjectId

async def migrate_users():
    users_collection = get_collection("users")
    vocab_collections = get_collection("vocab_collections")
    
    users = await users_collection.find({"selected_collection_id": {"$exists": False}}).to_list(length=None)
    
    for user in users:
        # Find user's first collection
        collection = await vocab_collections.find_one({"user_id": user["_id"]})
        if collection:
            await users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"selected_collection_id": str(collection["_id"])}}
            )
```

---

## Testing

Use the provided test script `test_streak_api.py` to verify the implementation:

```bash
# 1. Update the JWT_TOKEN in test_streak_api.py
# 2. Run the test script
python test_streak_api.py
```

The test script covers:
- Creating streaks for today (default)
- Creating streaks for specific dates
- Getting streak chains for various date ranges
- Updating existing streak entries
- Verifying completion status

---

## Frontend Integration Example (React)

```jsx
import React, { useState, useEffect } from 'react';

const StreakCalendar = ({ token }) => {
  const [streakData, setStreakData] = useState(null);
  
  useEffect(() => {
    fetchStreakData();
  }, []);
  
  const fetchStreakData = async () => {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 30);
    
    const formatDate = (date) => date.toISOString().split('T')[0];
    
    const response = await fetch(
      `http://localhost:8000/api/v1/streak-chain?startday=${formatDate(startDate)}&endday=${formatDate(endDate)}`,
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    );
    
    const data = await response.json();
    setStreakData(data);
  };
  
  const recordToday = async () => {
    await fetch('http://localhost:8000/api/v1/streak', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ step: 1 })
    });
    
    fetchStreakData(); // Refresh
  };
  
  if (!streakData) return <div>Loading...</div>;
  
  return (
    <div className="streak-calendar">
      <h2>Your Learning Streak</h2>
      <p>Completed: {streakData.completed_days} / {streakData.total_days} days</p>
      <button onClick={recordToday}>Record Today's Session</button>
      
      <div className="calendar-grid">
        {streakData.dates.map(day => (
          <div 
            key={day.date}
            className={`calendar-day ${day.completed ? 'completed' : 'incomplete'}`}
          >
            {day.date.split('-')[2]}
          </div>
        ))}
      </div>
    </div>
  );
};

export default StreakCalendar;
```

---

## Summary

The Streak feature provides:

1. **Streak Collection**: New MongoDB collection to store daily learning records
2. **User Updates**: Added `selected_collection_id` field to track user's active vocabulary collection
3. **POST /api/v1/streak**: Create or update daily streak entries
4. **GET /api/v1/streak-chain**: Retrieve completion status for a date range
5. **Automatic Default Collection**: New users get a "Default" collection automatically

This implementation allows for flexible tracking of user learning habits and provides the foundation for gamification features like streak counters, achievement badges, and progress visualization.
