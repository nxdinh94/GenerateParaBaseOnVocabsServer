# HTTP Status Codes - API Documentation Update

## 🔄 API Response Changes

Tất cả API endpoints đã được cập nhật để sử dụng **HTTP status codes chuẩn** thay vì luôn trả về 200 với `status: false`.

## 📊 HTTP Status Code Mapping

### ✅ Success Responses
- **200 OK** - Request thành công
- **201 Created** - Resource được tạo thành công

### ❌ Client Error Responses  
- **400 Bad Request** - Input không hợp lệ, missing required fields
- **401 Unauthorized** - Authentication thất bại, token invalid/expired
- **403 Forbidden** - Client không có quyền truy cập
- **404 Not Found** - Resource không tồn tại

### 💥 Server Error Responses
- **500 Internal Server Error** - Lỗi server, database errors, service unavailable

## 🔐 Google Authentication Endpoints

### POST `/api/v1/auth/google/login`

**Success (200):**
```json
{
  "status": true,
  "message": "Login successful",
  "user_info": {...},
  "jwt_token": "...",
  "access_token": "...",
  "expires_in": 3600
}
```

**Invalid Authorization Code (400):**
```json
{
  "detail": {
    "error": "invalid_authorization_code",
    "message": "Authorization code is invalid, expired, or already used",
    "details": "Failed to exchange authorization code: ..."
  }
}
```

**Invalid Client Credentials (401):**
```json
{
  "detail": {
    "error": "invalid_client_credentials", 
    "message": "Google OAuth client credentials are invalid",
    "details": "..."
  }
}
```

**Unauthorized Client (403):**
```json
{
  "detail": {
    "error": "unauthorized_client",
    "message": "Client is not authorized for this operation",
    "details": "..."
  }
}
```

**Server Error (500):**
```json
{
  "detail": {
    "error": "internal_server_error",
    "message": "An unexpected error occurred during authentication",
    "details": "..."
  }
}
```

### POST `/api/v1/auth/verify-token`

**Missing Token (400):**
```json
{
  "detail": {
    "error": "missing_token",
    "message": "Token is required"
  }
}
```

**Invalid Token (401):**
```json
{
  "detail": {
    "error": "invalid_token",
    "message": "Token is invalid or expired"
  }
}
```

### GET `/api/v1/auth/profile`

**Missing Authorization Header (401):**
```json
{
  "detail": {
    "error": "missing_authorization_header",
    "message": "Authorization header is required"
  }
}
```

**Invalid Authorization Format (401):**
```json
{
  "detail": {
    "error": "invalid_authorization_format",
    "message": "Authorization header must be in format: Bearer <token>"
  }
}
```

### POST `/api/v1/auth/refresh-token`

**Missing Refresh Token (400):**
```json
{
  "detail": {
    "error": "missing_refresh_token",
    "message": "Refresh token is required"
  }
}
```

**Invalid Refresh Token (401):**
```json
{
  "detail": {
    "error": "invalid_refresh_token",
    "message": "Refresh token is invalid or expired"
  }
}
```

## 📝 Content Generation Endpoints

### POST `/api/v1/generate-paragraph`

**Missing Language (400):**
```json
{
  "detail": {
    "error": "missing_language",
    "message": "Language is required"
  }
}
```

**Missing Vocabularies (400):**
```json
{
  "detail": {
    "error": "missing_vocabularies",
    "message": "At least one vocabulary is required"
  }
}
```

**Missing Level (400):**
```json
{
  "detail": {
    "error": "missing_level", 
    "message": "Level is required"
  }
}
```

**Invalid Length (400):**
```json
{
  "detail": {
    "error": "invalid_length",
    "message": "Length must be a positive number"
  }
}
```

**Generation Failed (500):**
```json
{
  "detail": {
    "error": "paragraph_generation_failed",
    "message": "Failed to generate paragraph",
    "details": "..."
  }
}
```

### POST `/api/v1/save-paragraph`

**Missing Vocabularies (400):**
```json
{
  "detail": {
    "error": "missing_vocabularies",
    "message": "At least one vocabulary is required"
  }
}
```

**Missing Paragraph (400):**
```json
{
  "detail": {
    "error": "missing_paragraph",
    "message": "Paragraph content is required"
  }
}
```

**Invalid Vocabularies (400):**
```json
{
  "detail": {
    "error": "invalid_vocabularies",
    "message": "All vocabularies are empty or invalid"
  }
}
```

**Save Failed (500):**
```json
{
  "detail": {
    "error": "paragraph_save_failed",
    "message": "Failed to save paragraph to database",
    "details": "..."
  }
}
```

## 🔧 Frontend Integration Updates

### JavaScript/React Error Handling

**Before (Old Way):**
```javascript
const response = await fetch('/api/v1/auth/google/login', {...});
const result = await response.json();

if (result.status) {
  // Success
} else {
  // Error - always got 200 status
  console.error(result.message);
}
```

**After (New Way):**
```javascript
try {
  const response = await fetch('/api/v1/auth/google/login', {...});
  
  if (response.ok) {
    // Success (200-299)
    const result = await response.json();
    console.log('Login successful:', result);
  } else {
    // Error (400, 401, 403, 500, etc.)
    const errorData = await response.json();
    console.error(`Error ${response.status}:`, errorData.detail);
    
    // Handle specific errors
    if (response.status === 400) {
      alert('Invalid input: ' + errorData.detail.message);
    } else if (response.status === 401) {
      alert('Authentication failed: ' + errorData.detail.message);
      // Redirect to login
    } else if (response.status === 500) {
      alert('Server error. Please try again later.');
    }
  }
} catch (error) {
  console.error('Network error:', error);
}
```

### Axios Error Handling

```javascript
try {
  const response = await axios.post('/api/v1/auth/google/login', data);
  // Success
  console.log('Login successful:', response.data);
} catch (error) {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    console.error(`Error ${status}:`, data.detail);
    
    switch (status) {
      case 400:
        showError('Invalid input: ' + data.detail.message);
        break;
      case 401:
        showError('Authentication failed');
        redirectToLogin();
        break;
      case 500:
        showError('Server error. Please try again.');
        break;
    }
  } else {
    // Network error
    console.error('Network error:', error.message);
  }
}
```

## 🧪 Testing HTTP Status Codes

Chạy test suite để kiểm tra tất cả status codes:

```bash
python scripts/test_http_status_codes.py
```

Expected output:
```
✅ Passed: 10/10
❌ Failed: 0/10

📋 Detailed Results:
✅ Google Login - Invalid Code: 400 (expected: 400)
✅ Verify Token - Missing Token: 400 (expected: 400)
✅ Verify Token - Invalid Token: 401 (expected: 401)
✅ Get Profile - Missing Auth Header: 401 (expected: 401)
✅ Get Profile - Invalid Auth Format: 401 (expected: 401)
✅ Refresh Token - Missing Token: 400 (expected: 400)
✅ Generate Paragraph - Missing Language: 400 (expected: 400)
✅ Generate Paragraph - Missing Vocabularies: 400 (expected: 400)
✅ Save Paragraph - Missing Vocabs: 400 (expected: 400)
✅ Save Paragraph - Missing Paragraph: 400 (expected: 400)
```

## 📈 Benefits of HTTP Status Codes

### ✅ For Frontend Developers
- **Easier error handling** - Use standard HTTP status checks
- **Better user experience** - Specific error messages based on status
- **Consistent behavior** - All APIs follow same pattern
- **Framework integration** - Works better with HTTP libraries

### ✅ For API Consumers  
- **Standard compliance** - Follows HTTP/REST conventions
- **Clear error categories** - Easy to distinguish error types
- **Better debugging** - Status codes provide immediate context
- **Monitoring friendly** - Easy to track error rates by status

### ✅ For System Administration
- **Better monitoring** - Status codes in logs and metrics
- **Alerting capabilities** - Set up alerts based on error rates
- **Load balancer integration** - Health checks work properly
- **Caching behavior** - Proper cache headers based on status

## 🎯 Migration Notes

- **Breaking Change**: Frontend code cần update error handling
- **Backward Compatibility**: Response body format vẫn giữ nguyên cho success cases
- **Error Format**: Error responses bây giờ dùng FastAPI's `detail` field
- **Status Field**: Success responses vẫn có `status: true` field

---

**🎉 All API endpoints now follow HTTP status code standards!**
