# Save Paragraph API - Validation Fix & User ID Integration

## 🚨 **Vấn đề gốc**
1. **Lỗi validation MongoDB**: Thiếu trường `created_at` khi lưu paragraph
2. **Thiếu user_id**: API save-paragraph không lưu input vocabs với user_id trong collection input_history

## ✅ **Giải pháp đã thực hiện**

### 1. **Fixed MongoDB Validation Error**

#### **InputHistoryCRUD.create_input_history()**
```python
# TRƯỚC
async def create_input_history(self, history_data: InputHistoryCreate) -> InputHistoryInDB:
    history_dict = history_data.dict()
    history_dict['user_id'] = ObjectId(history_dict['user_id'])
    # ❌ THIẾU: created_at field

# SAU
async def create_input_history(self, history_data: InputHistoryCreate) -> InputHistoryInDB:
    history_dict = history_data.dict()
    history_dict['user_id'] = ObjectId(history_dict['user_id'])
    history_dict['created_at'] = datetime.utcnow()  # ✅ THÊM
```

#### **SavedParagraphCRUD.create_saved_paragraph()**
```python
# TRƯỚC  
async def create_saved_paragraph(self, paragraph_data: SavedParagraphCreate) -> SavedParagraphInDB:
    paragraph_dict = paragraph_data.dict()
    paragraph_dict['input_history_id'] = ObjectId(paragraph_dict['input_history_id'])
    # ❌ THIẾU: created_at field

# SAU
async def create_saved_paragraph(self, paragraph_data: SavedParagraphCreate) -> SavedParagraphInDB:
    paragraph_dict = paragraph_data.dict()
    paragraph_dict['input_history_id'] = ObjectId(paragraph_dict['input_history_id'])
    paragraph_dict['created_at'] = datetime.utcnow()  # ✅ THÊM
```

### 2. **Added User ID to Save Paragraph API**

#### **Updated Schema (schemas.py)**
```python
# TRƯỚC
class SaveParagraphRequest(BaseModel):
    vocabs: List[str]
    paragraph: str

# SAU
class SaveParagraphRequest(BaseModel):
    user_id: str  # ✅ THÊM user_id field
    vocabs: List[str]
    paragraph: str
```

#### **Updated API Endpoint (routes.py)**
```python
# TRƯỚC: Sử dụng default_user_id cố định
default_user_id = "68c13d6181373f816d763a41"  # ❌ Hard-coded

# SAU: Sử dụng user_id từ request
user_id = req.user_id.strip()  # ✅ Từ request

# Thêm validation cho user_id
try:
    ObjectId(user_id)
except Exception:
    raise HTTPException(status_code=400, detail={
        "error": "invalid_user_id",
        "message": "User ID must be a valid ObjectId"
    })
```

## 📊 **API Request Format Mới**

### **Before (Cũ)**
```json
{
  "vocabs": ["test", "vocabulary"],
  "paragraph": "Test paragraph"
}
```

### **After (Mới)**
```json
{
  "user_id": "60d5ec49f1b2c8b1a4567890",
  "vocabs": ["test", "vocabulary"],
  "paragraph": "Test paragraph"
}
```

## 🔄 **Data Flow**

1. **Request**: Client gửi `user_id`, `vocabs`, `paragraph`
2. **Validation**: Kiểm tra user_id format (ObjectId), vocabs không rỗng, paragraph không rỗng
3. **Input History**: 
   - Tìm existing input_history với cùng user_id và vocabs
   - Nếu có: reuse existing
   - Nếu không: tạo mới với `user_id`, `words`, `created_at`
4. **Saved Paragraph**: Tạo mới với `input_history_id`, `paragraph`, `created_at`

## ✅ **Validation & Error Handling**

| Trường hợp | HTTP Status | Error Message |
|------------|-------------|---------------|
| Missing user_id | 400 | "User ID is required" |
| Invalid user_id format | 400 | "User ID must be a valid ObjectId" |
| Empty vocabs | 400 | "At least one vocabulary is required" |
| Empty paragraph | 400 | "Paragraph content is required" |
| Database error | 500 | "Failed to save paragraph to database" |

## 🎯 **Benefits**

1. **✅ Đã sửa lỗi validation MongoDB**: Không còn lỗi missing `created_at`
2. **✅ User-specific data**: Input vocabs được lưu theo user_id
3. **✅ Data integrity**: Vocabulary reuse logic hoạt động theo user
4. **✅ Better error handling**: Validation rõ ràng cho tất cả input fields
5. **✅ Consistent data model**: Tất cả collections đều có proper timestamps

## 🚀 **Trạng thái**

- **Database**: Tất cả schemas đã được sync ✅
- **CRUD Operations**: Đã sửa created_at fields ✅
- **API Schema**: Đã thêm user_id field ✅  
- **Validation**: Comprehensive input validation ✅
- **Error Handling**: Proper HTTP status codes ✅

## 📝 **Test Cases**

1. **Valid request with user_id** ✅ Expected: 200 + success response
2. **Missing user_id** ✅ Expected: 400 + error message
3. **Invalid user_id format** ✅ Expected: 400 + validation error
4. **Reuse vocabularies** ✅ Expected: 200 + "existing vocabularies" message

---

**Cập nhật:** September 12, 2025  
**Status:** ✅ Đã khắc phục hoàn toàn lỗi validation và thêm user_id integration  
**Ready for production testing**