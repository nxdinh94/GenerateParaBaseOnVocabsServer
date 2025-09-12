# Google Authentication API Documentation

## Overview
API endpoints để xử lý đăng nhập với Google OAuth 2.0, sử dụng authorization code flow từ React app.

## Prerequisites
1. Google OAuth 2.0 credentials (Client ID và Client Secret)
2. Cấu hình environment variables trong `.env` file
3. Frontend React app sử dụng `@google-oauth/google-login` package

## Environment Variables
```bash
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:3000
JWT_SECRET=your_secret_key_here_change_this_in_production
```

## API Endpoints

### 1. Login with Google
**POST** `/api/v1/auth/google/login`

Xử lý đăng nhập với Google sử dụng authorization code từ React app.

#### Request Body
```json
{
  "authorization_code": "4/0AVMBsJgemoPHnKMzzqpfbxAJ05bEx2zN18hGvhZjPXud7Q3FTJjDzW-O4a5xg-w27mwFCA"
}
```

#### Response
```json
{
  "status": true,
  "message": "Login successful",
  "user_info": {
    "id": "123456789",
    "email": "user@example.com",
    "name": "John Doe",
    "picture": "https://lh3.googleusercontent.com/...",
    "verified_email": true
  },
  "access_token": "ya29.a0ARrdaM...",
  "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600
}
```

### 2. Verify JWT Token
**POST** `/api/v1/auth/verify-token`

Kiểm tra tính hợp lệ của JWT token.

#### Request Body
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Response
```json
{
  "status": true,
  "message": "Token is valid",
  "user_data": {
    "user_id": "123456789",
    "email": "user@example.com",
    "name": "John Doe",
    "picture": "https://lh3.googleusercontent.com/...",
    "exp": 1693737600
  }
}
```

### 3. Get User Profile
**GET** `/api/v1/auth/profile`

Lấy thông tin profile từ JWT token trong Authorization header.

#### Headers
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Response
```json
{
  "status": true,
  "message": "Profile retrieved successfully",
  "user_data": {
    "user_id": "123456789",
    "email": "user@example.com",
    "name": "John Doe",
    "picture": "https://lh3.googleusercontent.com/...",
    "exp": 1693737600
  }
}
```

### 4. Refresh Access Token
**POST** `/api/v1/auth/refresh-token`

Làm mới Google access token sử dụng refresh token.

#### Request Body
```json
{
  "refresh_token": "1//04123456789..."
}
```

#### Response
```json
{
  "status": true,
  "message": "Token refreshed successfully",
  "access_token": "ya29.a0ARrdaM...",
  "expires_in": 3600
}
```

## React Integration Example

### 1. Install Package
```bash
npm install @google-oauth/google-login
```

### 2. Setup Google Login Component
```jsx
import { useGoogleLogin } from '@google-oauth/google-login';

function LoginComponent() {
  const login = useGoogleLogin({
    onSuccess: async (codeResponse) => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/auth/google/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            authorization_code: codeResponse.code
          })
        });
        
        const result = await response.json();
        
        if (result.status) {
          // Store tokens
          localStorage.setItem('jwt_token', result.jwt_token);
          localStorage.setItem('user_info', JSON.stringify(result.user_info));
          
          console.log('Login successful:', result.user_info);
          // Redirect or update UI
        } else {
          console.error('Login failed:', result.message);
        }
      } catch (error) {
        console.error('Login error:', error);
      }
    },
    onError: (error) => {
      console.error('Google login error:', error);
    },
    flow: 'auth-code',
  });

  return (
    <button onClick={() => login()}>
      Sign in with Google
    </button>
  );
}
```

### 3. Using JWT Token for API Calls
```jsx
async function makeAuthenticatedRequest(endpoint, options = {}) {
  const jwt_token = localStorage.getItem('jwt_token');
  
  const response = await fetch(`http://localhost:8000${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${jwt_token}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  
  return response.json();
}

// Example usage
const userProfile = await makeAuthenticatedRequest('/api/v1/auth/profile');
```

### 4. Token Verification
```jsx
async function verifyToken() {
  const jwt_token = localStorage.getItem('jwt_token');
  
  if (!jwt_token) {
    console.log('No token found');
    return false;
  }
  
  try {
    const response = await fetch('http://localhost:8000/api/v1/auth/verify-token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        token: jwt_token
      })
    });
    
    const result = await response.json();
    return result.status;
  } catch (error) {
    console.error('Token verification error:', error);
    return false;
  }
}
```

## Error Handling

### Common Error Responses
```json
{
  "status": false,
  "message": "Login failed: Invalid authorization code"
}
```

```json
{
  "status": false,
  "message": "Token is invalid or expired"
}
```

```json
{
  "status": false,
  "message": "Authorization header missing or invalid"
}
```

## Testing

1. Cài đặt dependencies:
```bash
pip install google-auth google-auth-oauthlib PyJWT
```

2. Chạy test script:
```bash
python scripts/test_google_auth.py
```

3. Test với Postman hoặc curl:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/google/login" \
  -H "Content-Type: application/json" \
  -d '{"authorization_code": "your_auth_code_here"}'
```

## Security Notes

1. **JWT Secret**: Sử dụng secret key mạnh và khác nhau cho mỗi environment
2. **HTTPS**: Luôn sử dụng HTTPS trong production
3. **Token Expiry**: JWT tokens có thời hạn 7 ngày, có thể điều chỉnh
4. **Refresh Tokens**: Store refresh tokens securely, không expose trong frontend
5. **CORS**: Cấu hình CORS properly cho frontend domain

## Troubleshooting

### 1. "Import jwt could not be resolved"
```bash
pip install PyJWT
```

### 2. "Google OAuth credentials not found"
Kiểm tra file `.env` và đảm bảo có đủ:
- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET

### 3. "Invalid authorization code"
- Đảm bảo authorization code chưa được sử dụng
- Kiểm tra redirect_uri khớp với Google Console
- Authorization code có thời hạn ngắn (vài phút)

### 4. "Token verification failed"
- Kiểm tra JWT_SECRET trong .env
- Đảm bảo token chưa hết hạn
- Format Authorization header: "Bearer <token>"
