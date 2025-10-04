# MongoDB Schema Changes Documentation

This document describes the new MongoDB collections and schema changes implemented to enhance the vocabulary learning system.

## 🗄️ New Collections

### 1. **vocab_collections**
Manages vocabulary collections for better organization.

```javascript
{
  _id: ObjectId,
  name: String,           // Collection name (e.g., "Business English", "Academic Words")
  created_at: Date,
  updated_at: Date
}
```

**Indexes:**
- `name` (ascending)
- `created_at` (descending)

### 2. **history_by_date** 
Tracks daily study sessions for vocabulary tracking and analytics.

```javascript
{
  _id: ObjectId,
  vocab_id: ObjectId,     // Reference to learned_vocabs collection
  study_date: Date,       // Date when vocabulary was studied (stored as YYYY-MM-DD, time normalized to 00:00:00)
  count: Number,          // Number of times studied on this date (default: 1)
  created_at: Date
}
```

**Important**: `study_date` is stored as date-only (YYYY-MM-DD format) with time components normalized to 00:00:00 for consistent daily aggregations.

**Indexes:**
- `vocab_id` + `study_date` (compound, descending)
- `study_date` (descending)
- `vocab_id` (ascending)

### 3. **user_feedback**
Stores user feedback and support messages.

```javascript
{
  _id: ObjectId,
  email: String,          // User's email address (required)
  name: String,           // User's name (optional)
  message: String,        // Feedback message (long text, max 5000 chars)
  created_at: Date
}
```

**Indexes:**
- `email` (ascending)
- `created_at` (descending)

## 🔧 Modified Collections

### **learned_vocabs** (Updated)
Added `collection_id` field to support vocabulary organization.

```javascript
{
  _id: ObjectId,
  user_id: ObjectId,      // Reference to users collection
  vocabs: [String],       // Array of vocabulary words
  collection_id: ObjectId, // NEW: Reference to vocab_collections (optional)
  usage_count: Number,    // Existing field
  created_at: Date,       // Existing field
  updated_at: Date,       // Existing field
  deleted_at: Date,       // Existing field
  is_deleted: Boolean     // Existing field
}
```

**New Index:**
- `collection_id` (ascending)

## 📊 API Endpoints

### Vocabulary Collections

#### Create Collection
```http
POST /api/v1/vocab-collections
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "name": "Business English"
}
```

#### Get All Collections
```http
GET /api/v1/vocab-collections
Authorization: Bearer {jwt_token}
```

#### Update Collection
```http
PUT /api/v1/vocab-collections/{collection_id}
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "name": "Advanced Business English"
}
```

#### Delete Collection
```http
DELETE /api/v1/vocab-collections/{collection_id}
Authorization: Bearer {jwt_token}
```

### Study History

#### Record Study Session
```http
POST /api/v1/study-session
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "vocab_id": "64f5a2b8c1d2e3f4a5b6c7d8",
  "study_date": "2024-01-15"  // Optional, YYYY-MM-DD format or ISO datetime, defaults to current date
}
```

**Note**: `study_date` can be provided as:
- Date-only format: `"2024-01-15"`
- ISO datetime format: `"2024-01-15T10:30:00Z"`
- If omitted, uses current date

All formats are normalized to date-only storage (YYYY-MM-DD with time 00:00:00).

#### Get Study History
```http
GET /api/v1/study-history?limit=50
Authorization: Bearer {jwt_token}
```

### User Feedback

#### Submit Feedback (No Auth Required)
```http
POST /api/v1/feedback
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",        // Optional
  "message": "Great app! Would love to see more features..."
}
```

#### Get All Feedback (Admin Only)
```http
GET /api/v1/feedback?limit=100
Authorization: Bearer {jwt_token}
```

### Updated Learned Vocabs

#### Create with Collection Assignment
```http
POST /api/v1/learned-vocabs
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "vocabs": ["business", "strategy", "revenue"],
  "collection_id": "64f5a2b8c1d2e3f4a5b6c7d8"  // Optional
}
```

## 🚀 Migration Guide

### 1. Run the Migration Script

Execute the migration script to set up new collections and update existing data:

```bash
cd scripts
python migrate_database_schema.py
```

### 2. Migration Process

The script will:
- ✅ Add `collection_id` field to existing `learned_vocabs` documents (set to `null`)
- ✅ Create new collections with proper indexes
- ✅ Create a default "General" vocabulary collection
- ✅ Validate all collections and schema changes

### 3. Expected Output

```
🚀 Starting Database Schema Migration
============================================================
🔄 Adding collection_id field to learned_vocabs...
📊 Found 150 documents without collection_id field
✅ Updated 150 learned_vocabs documents with collection_id field
🔄 Creating default vocabulary collection...
✅ Created default 'General' collection with ID: 64f5a2b8c1d2e3f4a5b6c7d8
🔄 Creating database indexes...
✅ Created indexes for vocab_collections
✅ Updated indexes for learned_vocabs
✅ Created indexes for history_by_date
✅ Created indexes for user_feedback
🔄 Validating database collections...
✅ Collection 'users' exists
✅ Collection 'refresh_tokens' exists
✅ Collection 'input_history' exists
✅ Collection 'saved_paragraphs' exists
✅ Collection 'learned_vocabs' exists
✅ Collection 'vocab_collections' exists
✅ Collection 'history_by_date' exists
✅ Collection 'user_feedback' exists
✅ learned_vocabs collection has collection_id field
✅ All database collections validated successfully

============================================================
📋 MIGRATION SUMMARY
============================================================
📊 users: 25 documents
📊 refresh_tokens: 18 documents
📊 input_history: 89 documents
📊 saved_paragraphs: 156 documents
📊 learned_vocabs: 150 documents
📊 vocab_collections: 1 documents
📊 history_by_date: 0 documents
📊 user_feedback: 0 documents

🎉 Database migration completed successfully!
```

## 🎯 Benefits

### 1. **Better Organization**
- Users can organize vocabularies into themed collections
- Easier to manage different learning categories

### 2. **Progress Tracking** 
- Daily study session tracking
- Analytics on learning frequency and patterns
- Visual progress indicators

### 3. **User Engagement**
- Feedback collection for continuous improvement
- Support channel for users
- Better user experience insights

### 4. **Scalability**
- Proper indexing for performance
- Flexible schema for future enhancements
- Maintainable code structure

## 🔍 Usage Examples

### Example 1: Create Learning Collections

```javascript
// Create themed collections
POST /vocab-collections { "name": "TOEFL Vocabulary" }
POST /vocab-collections { "name": "Business English" }
POST /vocab-collections { "name": "Academic Writing" }

// Add vocabularies to collections
POST /learned-vocabs {
  "vocabs": ["analyze", "evaluate", "synthesize"],
  "collection_id": "toefl_collection_id"
}
```

### Example 2: Track Study Progress

```javascript
// Record daily study sessions
POST /study-session {
  "vocab_id": "vocab_id_1",
  "study_date": "2024-01-15T09:00:00Z"
}

// Get study history with analytics
GET /study-history?limit=30
// Returns: study dates, frequency, vocabulary details
```

### Example 3: Collect User Feedback

```javascript
// Users can submit feedback anytime
POST /feedback {
  "email": "student@university.edu",
  "name": "Sarah Johnson",
  "message": "Love the new collections feature! Could you add spaced repetition?"
}
```

## ⚠️ Important Notes

1. **Backward Compatibility**: All existing API endpoints continue to work unchanged
2. **Optional Fields**: `collection_id` is optional in learned_vocabs for flexibility
3. **Data Migration**: Existing vocabulary data is preserved and enhanced
4. **Performance**: New indexes improve query performance
5. **Authentication**: Most endpoints require JWT authentication except feedback submission

## 🛠️ Troubleshooting

### Migration Issues

If migration fails:
1. Check MongoDB connection
2. Ensure proper permissions
3. Backup database before running migration
4. Check logs for specific error details

### API Issues

Common issues:
1. **401 Unauthorized**: Check JWT token validity
2. **404 Not Found**: Verify collection/vocab IDs exist
3. **400 Bad Request**: Validate request schema matches documentation

## 📈 Future Enhancements

Potential improvements:
1. **Analytics Dashboard**: Visual progress tracking
2. **Spaced Repetition**: Smart vocabulary review scheduling
3. **Collection Sharing**: Share vocabulary collections between users
4. **Export/Import**: Backup and restore functionality
5. **Gamification**: Achievements and streak tracking