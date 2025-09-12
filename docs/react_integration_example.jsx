// React Login Component Example
// File: src/components/GoogleLogin.jsx

import React, { useState } from 'react';
import { useGoogleLogin } from '@google-oauth/google-login';

const GoogleLoginComponent = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const login = useGoogleLogin({
    onSuccess: async (codeResponse) => {
      setLoading(true);
      setError('');
      
      try {
        console.log('Authorization Code received:', codeResponse.code);
        
        // Send authorization code to your FastAPI backend
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
          // Login successful
          console.log('Login successful:', result.user_info);
          console.log('JWT Token:', result.jwt_token);
          
          // Store tokens and user info
          localStorage.setItem('jwt_token', result.jwt_token);
          localStorage.setItem('google_access_token', result.access_token);
          localStorage.setItem('user_info', JSON.stringify(result.user_info));
          
          // Update UI
          setUser(result.user_info);
          
          // Optional: Redirect to dashboard
          // window.location.href = '/dashboard';
          
        } else {
          console.error('Login failed:', result.message);
          setError(result.message);
        }
      } catch (error) {
        console.error('Login error:', error);
        setError('Network error occurred during login');
      } finally {
        setLoading(false);
      }
    },
    onError: (error) => {
      console.error('Google login error:', error);
      setError('Google authentication failed');
      setLoading(false);
    },
    flow: 'auth-code',
  });

  const logout = () => {
    // Clear stored data
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('google_access_token');
    localStorage.removeItem('user_info');
    setUser(null);
    setError('');
  };

  const testApiCall = async () => {
    try {
      const jwt_token = localStorage.getItem('jwt_token');
      
      if (!jwt_token) {
        setError('No JWT token found. Please login first.');
        return;
      }
      
      // Test protected endpoint
      const response = await fetch('http://localhost:8000/api/v1/auth/profile', {
        headers: {
          'Authorization': `Bearer ${jwt_token}`,
          'Content-Type': 'application/json',
        }
      });
      
      const result = await response.json();
      
      if (result.status) {
        console.log('Profile data:', result.user_data);
        alert('API call successful! Check console for details.');
      } else {
        console.error('API call failed:', result.message);
        setError(result.message);
      }
    } catch (error) {
      console.error('API call error:', error);
      setError('Failed to call API');
    }
  };

  const checkTokenValidity = async () => {
    try {
      const jwt_token = localStorage.getItem('jwt_token');
      
      if (!jwt_token) {
        setError('No JWT token found');
        return;
      }
      
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
      
      if (result.status) {
        alert('Token is valid!');
        console.log('Token data:', result.user_data);
      } else {
        alert('Token is invalid or expired');
        setError(result.message);
      }
    } catch (error) {
      console.error('Token verification error:', error);
      setError('Failed to verify token');
    }
  };

  // Check if user is already logged in when component mounts
  React.useEffect(() => {
    const storedUser = localStorage.getItem('user_info');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (error) {
        console.error('Error parsing stored user info:', error);
        localStorage.removeItem('user_info');
      }
    }
  }, []);

  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
      <h2>Google Authentication Demo</h2>
      
      {error && (
        <div style={{ 
          background: '#ffe6e6', 
          color: '#d8000c', 
          padding: '10px', 
          marginBottom: '20px',
          borderRadius: '4px'
        }}>
          Error: {error}
        </div>
      )}
      
      {!user ? (
        <div>
          <p>Please login with your Google account:</p>
          <button 
            onClick={() => login()}
            disabled={loading}
            style={{
              padding: '12px 24px',
              backgroundColor: '#4285f4',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '16px'
            }}
          >
            {loading ? 'Logging in...' : 'Sign in with Google 🚀'}
          </button>
        </div>
      ) : (
        <div>
          <h3>Welcome, {user.name}!</h3>
          <div style={{ marginBottom: '20px' }}>
            <img 
              src={user.picture} 
              alt="Profile" 
              style={{ 
                width: '80px', 
                height: '80px', 
                borderRadius: '50%',
                marginRight: '20px' 
              }} 
            />
            <div>
              <p><strong>Email:</strong> {user.email}</p>
              <p><strong>Verified:</strong> {user.verified_email ? '✅' : '❌'}</p>
            </div>
          </div>
          
          <div style={{ marginBottom: '20px' }}>
            <button 
              onClick={testApiCall}
              style={{
                padding: '10px 20px',
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                marginRight: '10px'
              }}
            >
              Test API Call
            </button>
            
            <button 
              onClick={checkTokenValidity}
              style={{
                padding: '10px 20px',
                backgroundColor: '#17a2b8',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                marginRight: '10px'
              }}
            >
              Check Token
            </button>
            
            <button 
              onClick={logout}
              style={{
                padding: '10px 20px',
                backgroundColor: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Logout
            </button>
          </div>
        </div>
      )}
      
      <div style={{ 
        marginTop: '40px', 
        padding: '20px', 
        backgroundColor: '#f8f9fa',
        borderRadius: '4px' 
      }}>
        <h4>How it works:</h4>
        <ol>
          <li>Click "Sign in with Google" button</li>
          <li>Complete Google OAuth flow</li>
          <li>Authorization code is sent to FastAPI backend</li>
          <li>Backend exchanges code for tokens and user info</li>
          <li>JWT token is generated and returned</li>
          <li>JWT token is stored in localStorage</li>
          <li>Use JWT token for protected API calls</li>
        </ol>
      </div>
    </div>
  );
};

export default GoogleLoginComponent;

/*
INSTALLATION STEPS:

1. Install required packages:
   npm install @google-oauth/google-login

2. Add to your App.js:
   import GoogleLoginComponent from './components/GoogleLogin';
   
   function App() {
     return (
       <div className="App">
         <GoogleLoginComponent />
       </div>
     );
   }

3. Configure Google OAuth in Google Cloud Console:
   - Go to: https://console.cloud.google.com/
   - Create new project or select existing
   - Enable Google+ API
   - Create OAuth 2.0 credentials
   - Add authorized origins: http://localhost:3000
   - Add authorized redirect URIs: http://localhost:3000

4. Update your .env file in FastAPI backend:
   GOOGLE_CLIENT_ID=your_client_id_from_google_console
   GOOGLE_CLIENT_SECRET=your_client_secret_from_google_console
   GOOGLE_REDIRECT_URI=http://localhost:3000
   JWT_SECRET=your_random_secret_key

5. Start both servers:
   - Frontend: npm start (usually port 3000)
   - Backend: uvicorn app.main:app --reload (port 8000)

NOTES:
- The authorization code from Google is single-use and expires quickly
- JWT tokens expire after 7 days (configurable in backend)
- Store refresh tokens securely if needed for long-term access
- Always use HTTPS in production
*/
