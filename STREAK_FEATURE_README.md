# 🔥 Streak Feature - Quick Start Guide

## What's New?

This update adds a **Streak Tracking** feature to help users monitor their daily learning progress!

## 🚀 Quick Setup

### 1. Run the Migration Script
```bash
python migrate_streak_feature.py
```

This will:
- Create necessary database indexes
- Update existing users with `selected_collection_id`
- Create default collections for users who don't have one

### 2. Start the Server
```bash
python -m uvicorn app.main:app --reload
```

### 3. Test the API
```bash
# Update JWT_TOKEN in test_streak_api.py first
python test_streak_api.py
```

## 📋 What Changed?

### New Database Collection
- **`streak`** - Stores daily learning records

### Updated Collections
- **`users`** - Added `selected_collection_id` field

### New API Endpoints

#### 1. POST /api/v1/streak
Record a learning session for today (or a specific date)

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/streak \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"step": 5}'
```

**Response:**
```json
{
  "id": "...",
  "user_id": "...",
  "learned_date": "2025-10-11",
  "step": 5,
  "created_at": "2025-10-11T10:30:00.000Z",
  "status": true
}
```

#### 2. GET /api/v1/streak-chain
Get streak data for a date range

**Request:**
```bash
curl "http://localhost:8000/api/v1/streak-chain?startday=2025-09-20&endday=2025-10-11" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "id": 12345678,
  "start_date": "2025-09-20",
  "end_date": "2025-10-11",
  "dates": [
    { "date": "2025-09-20", "completed": false },
    { "date": "2025-09-21", "completed": true },
    ...
  ],
  "total_days": 22,
  "completed_days": 15,
  "status": true
}
```

## 📚 Documentation

For complete documentation, see:
- **[STREAK_API_DOCUMENTATION.md](./STREAK_API_DOCUMENTATION.md)** - Full API reference
- **[STREAK_IMPLEMENTATION_SUMMARY.md](./STREAK_IMPLEMENTATION_SUMMARY.md)** - Technical details

## 🎯 Common Use Cases

### 1. Record Today's Session
```javascript
await fetch('http://localhost:8000/api/v1/streak', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ step: 1 })
});
```

### 2. Display Monthly Calendar
```javascript
const today = new Date();
const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0);

const formatDate = (d) => d.toISOString().split('T')[0];

const response = await fetch(
  `http://localhost:8000/api/v1/streak-chain?startday=${formatDate(firstDay)}&endday=${formatDate(lastDay)}`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);

const data = await response.json();
// Use data.dates to render calendar
```

### 3. Show Current Streak
```javascript
// Get last 90 days
const endDate = new Date();
const startDate = new Date();
startDate.setDate(startDate.getDate() - 90);

const response = await fetch(
  `http://localhost:8000/api/v1/streak-chain?...`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);

const data = await response.json();

// Calculate current streak (consecutive days from today backwards)
let currentStreak = 0;
for (let i = data.dates.length - 1; i >= 0; i--) {
  if (data.dates[i].completed) {
    currentStreak++;
  } else {
    break; // Stop at first incomplete day
  }
}

console.log(`Current streak: ${currentStreak} days! 🔥`);
```

## 🎨 React Component Example

```jsx
import { useState, useEffect } from 'react';

function StreakTracker({ token }) {
  const [streakData, setStreakData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStreakData();
  }, []);

  const fetchStreakData = async () => {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 30);
    
    const formatDate = (d) => d.toISOString().split('T')[0];
    
    const response = await fetch(
      `http://localhost:8000/api/v1/streak-chain?startday=${formatDate(startDate)}&endday=${formatDate(endDate)}`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    );
    
    const data = await response.json();
    setStreakData(data);
    setLoading(false);
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

  if (loading) return <div>Loading...</div>;

  return (
    <div className="streak-tracker">
      <h2>🔥 Your Learning Streak</h2>
      <p>
        Completed: <strong>{streakData.completed_days}</strong> / {streakData.total_days} days
      </p>
      <button onClick={recordToday}>✅ Record Today's Session</button>
      
      <div className="streak-calendar">
        {streakData.dates.map(day => (
          <div 
            key={day.date}
            className={`day ${day.completed ? 'completed' : ''}`}
            title={day.date}
          >
            {day.date.split('-')[2]}
          </div>
        ))}
      </div>
    </div>
  );
}

export default StreakTracker;
```

## 🐛 Troubleshooting

### Migration Issues
If migration fails:
```bash
# Check MongoDB connection
python -c "from app.database.connection import get_db; import asyncio; asyncio.run(get_db())"

# Run migration again
python migrate_streak_feature.py
```

### API Returns 401 Unauthorized
Make sure you're passing a valid JWT token:
```javascript
headers: {
  'Authorization': `Bearer ${token}` // Note the 'Bearer ' prefix
}
```

### Dates Not Showing as Completed
- Verify the date format is YYYY-MM-DD
- Check that the streak was created successfully (check response status)
- Ensure you're querying with the correct date range

## ✅ Testing Checklist

After setup, verify:
- [ ] Can create a streak for today
- [ ] Can create a streak for a specific date
- [ ] Can get streak chain for last 30 days
- [ ] Completed dates show `"completed": true`
- [ ] Duplicate streak creation updates existing entry
- [ ] Migration script completed without errors

## 📞 Support

For issues or questions, refer to:
- **STREAK_API_DOCUMENTATION.md** - Complete API documentation
- **test_streak_api.py** - Working examples
- **STREAK_IMPLEMENTATION_SUMMARY.md** - Technical details

---

**Happy Learning! Keep that streak alive! 🔥📚**
