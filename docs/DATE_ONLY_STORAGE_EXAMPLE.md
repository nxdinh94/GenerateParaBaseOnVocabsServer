# Date-Only Storage Example

## Overview

The `history_by_date` collection now stores dates in **YYYY-MM-DD format** without time components. This ensures consistent daily aggregations regardless of when during the day a study session occurs.

## How It Works

### Input Processing
```javascript
// All these inputs result in the same stored date:
"2024-01-15"                    // Date-only format
"2024-01-15T08:30:00Z"          // Morning study session  
"2024-01-15T12:45:00Z"          // Lunch break session
"2024-01-15T20:15:30Z"          // Evening session
"2024-01-15T23:59:59Z"          // Late night session

// All stored as: 2024-01-15 00:00:00
```

### Database Storage
```javascript
// Before (with time components):
{
  "vocab_id": "64f5a2b8c1d2e3f4a5b6c7d8",
  "study_date": "2024-01-15T08:30:00Z",
  "count": 1
}
{
  "vocab_id": "64f5a2b8c1d2e3f4a5b6c7d8", 
  "study_date": "2024-01-15T20:15:30Z",
  "count": 1
}

// After (date-only, aggregated):
{
  "vocab_id": "64f5a2b8c1d2e3f4a5b6c7d8",
  "study_date": "2024-01-15T00:00:00Z",
  "count": 2  // ← Automatically combined!
}
```

### API Response Format
```javascript
// POST /api/v1/study-session
{
  "vocab_id": "64f5a2b8c1d2e3f4a5b6c7d8",
  "study_date": "2024-01-15T14:30:00Z"  // Input with time
}

// Response:
{
  "id": "64f5a2b8c1d2e3f4a5b6c7d9",
  "vocab_id": "64f5a2b8c1d2e3f4a5b6c7d8", 
  "study_date": "2024-01-15",  // ← Date-only format
  "count": 3,
  "created_at": "2024-01-15T14:30:45Z",
  "status": true
}
```

## Benefits

### ✅ Automatic Daily Aggregation
Multiple study sessions on the same day are automatically combined:

```javascript
// Session 1: Morning study
POST /study-session { "vocab_id": "abc123", "study_date": "2024-01-15T08:00:00Z" }
// Result: count = 1

// Session 2: Evening study  
POST /study-session { "vocab_id": "abc123", "study_date": "2024-01-15T20:00:00Z" }
// Result: count = 2 (same record updated!)
```

### ✅ Consistent Analytics
Daily progress tracking becomes much simpler:

```javascript
// Get study history
GET /study-history

// Clean daily data:
[
  { "study_date": "2024-01-15", "count": 5 },
  { "study_date": "2024-01-14", "count": 3 },
  { "study_date": "2024-01-13", "count": 2 }
]
```

### ✅ Simplified Queries
Date-based queries work intuitively:

```javascript
// MongoDB query for specific date
db.history_by_date.find({
  "study_date": ISODate("2024-01-15T00:00:00Z")
})

// Date range queries
db.history_by_date.find({
  "study_date": {
    "$gte": ISODate("2024-01-01T00:00:00Z"),
    "$lte": ISODate("2024-01-31T00:00:00Z")
  }
})
```

## Migration Notes

### Existing Data
- All existing `history_by_date` records are preserved
- Time components in existing records remain unchanged
- New records will use date-only format
- Aggregation queries work with both old and new formats

### API Compatibility
- **Fully backward compatible**: Existing API calls continue to work
- **Enhanced flexibility**: Accept both date and datetime input formats
- **Consistent output**: Always returns date-only format in responses

## Example Usage

### Frontend Integration
```javascript
// Simple date submission (recommended)
const response = await fetch('/api/v1/study-session', {
  method: 'POST',
  headers: { 
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    vocab_id: 'abc123',
    study_date: '2024-01-15'  // Just the date!
  })
});

// Automatic current date (when omitted)
const response = await fetch('/api/v1/study-session', {
  method: 'POST', 
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    vocab_id: 'abc123'
    // study_date omitted = uses today's date
  })
});
```

### Analytics Dashboard
```javascript
// Get daily study data for charts
const historyResponse = await fetch('/api/v1/study-history');
const data = await historyResponse.json();

// data.history contains clean daily aggregations:
data.history.forEach(session => {
  console.log(`${session.study_date}: ${session.count} studies`);
  // Output: 
  // 2024-01-15: 5 studies
  // 2024-01-14: 3 studies
  // 2024-01-13: 2 studies
});
```

This date-only approach makes daily progress tracking much more intuitive and reliable! 🎯