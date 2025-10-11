"""
Test script to verify selected_collection_id is included in JWT tokens
"""
import jwt
import json

# Sample JWT tokens for testing
# Replace these with actual tokens from your application

def decode_token_without_verification(token: str):
    """Decode JWT token without signature verification (for testing only)"""
    try:
        # Decode without verification to inspect payload
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded
    except Exception as e:
        print(f"Error decoding token: {e}")
        return None

def test_jwt_token_structure():
    """Test that JWT token contains all required fields including selected_collection_id"""
    print("\n" + "="*60)
    print("TEST: JWT Token Structure")
    print("="*60)
    
    # Get a sample token from login
    sample_token = input("\nPaste your JWT token here (or press Enter to skip): ").strip()
    
    if not sample_token:
        print("⚠️ No token provided. Showing expected structure:")
        expected_structure = {
            "user_id": "673abc123def456789012345",
            "email": "user@example.com",
            "name": "John Doe",
            "picture": "https://...",
            "selected_collection_id": "673xyz789abc123456789012",
            "exp": 1728648000
        }
        print(json.dumps(expected_structure, indent=2))
        return
    
    decoded = decode_token_without_verification(sample_token)
    
    if decoded:
        print("\n✅ Token decoded successfully!")
        print("\nToken Payload:")
        print(json.dumps(decoded, indent=2))
        
        # Check for required fields
        required_fields = ["user_id", "email", "name", "selected_collection_id", "exp"]
        missing_fields = []
        
        for field in required_fields:
            if field in decoded:
                value = decoded[field]
                if field == "selected_collection_id":
                    if value is None:
                        print(f"\n⚠️  {field}: null (user may not have a selected collection yet)")
                    else:
                        print(f"\n✅ {field}: {value}")
                else:
                    print(f"✅ {field}: {decoded[field]}")
            else:
                missing_fields.append(field)
                print(f"❌ Missing field: {field}")
        
        if not missing_fields:
            print("\n✅ All required fields are present!")
        else:
            print(f"\n❌ Missing fields: {', '.join(missing_fields)}")
    else:
        print("❌ Failed to decode token")

def test_refresh_token_structure():
    """Test that refresh token contains selected_collection_id"""
    print("\n" + "="*60)
    print("TEST: JWT Refresh Token Structure")
    print("="*60)
    
    sample_token = input("\nPaste your JWT refresh token here (or press Enter to skip): ").strip()
    
    if not sample_token:
        print("⚠️ No token provided. Showing expected structure:")
        expected_structure = {
            "user_id": "673abc123def456789012345",
            "email": "user@example.com",
            "name": "John Doe",
            "picture": "https://...",
            "selected_collection_id": "673xyz789abc123456789012",
            "type": "refresh",
            "exp": 1731240000
        }
        print(json.dumps(expected_structure, indent=2))
        return
    
    decoded = decode_token_without_verification(sample_token)
    
    if decoded:
        print("\n✅ Refresh token decoded successfully!")
        print("\nRefresh Token Payload:")
        print(json.dumps(decoded, indent=2))
        
        # Check for required fields
        required_fields = ["user_id", "email", "name", "selected_collection_id", "type", "exp"]
        missing_fields = []
        
        for field in required_fields:
            if field in decoded:
                value = decoded[field]
                if field == "selected_collection_id":
                    if value is None:
                        print(f"\n⚠️  {field}: null (user may not have a selected collection yet)")
                    else:
                        print(f"\n✅ {field}: {value}")
                elif field == "type":
                    if value == "refresh":
                        print(f"✅ {field}: {value}")
                    else:
                        print(f"❌ {field}: {value} (should be 'refresh')")
                else:
                    print(f"✅ {field}: {decoded[field]}")
            else:
                missing_fields.append(field)
                print(f"❌ Missing field: {field}")
        
        if not missing_fields and decoded.get("type") == "refresh":
            print("\n✅ All required fields are present and valid!")
        else:
            print(f"\n❌ Issues found: {', '.join(missing_fields) if missing_fields else 'Invalid type field'}")
    else:
        print("❌ Failed to decode token")

def compare_tokens():
    """Compare JWT token and refresh token to ensure consistency"""
    print("\n" + "="*60)
    print("TEST: Token Consistency")
    print("="*60)
    
    jwt_token = input("\nPaste your JWT token: ").strip()
    refresh_token = input("Paste your JWT refresh token: ").strip()
    
    if not jwt_token or not refresh_token:
        print("⚠️ Both tokens required for comparison")
        return
    
    decoded_jwt = decode_token_without_verification(jwt_token)
    decoded_refresh = decode_token_without_verification(refresh_token)
    
    if decoded_jwt and decoded_refresh:
        print("\n✅ Both tokens decoded successfully!")
        
        # Compare selected_collection_id
        jwt_collection = decoded_jwt.get("selected_collection_id")
        refresh_collection = decoded_refresh.get("selected_collection_id")
        
        print(f"\nJWT Token selected_collection_id: {jwt_collection}")
        print(f"Refresh Token selected_collection_id: {refresh_collection}")
        
        if jwt_collection == refresh_collection:
            print("✅ Selected collection IDs match!")
        else:
            print("❌ Selected collection IDs do NOT match!")
        
        # Compare other fields
        fields_to_compare = ["user_id", "email", "name"]
        all_match = True
        
        for field in fields_to_compare:
            jwt_value = decoded_jwt.get(field)
            refresh_value = decoded_refresh.get(field)
            
            if jwt_value == refresh_value:
                print(f"✅ {field} matches: {jwt_value}")
            else:
                print(f"❌ {field} mismatch: JWT={jwt_value}, Refresh={refresh_value}")
                all_match = False
        
        if all_match and jwt_collection == refresh_collection:
            print("\n✅ All fields match perfectly!")
        else:
            print("\n⚠️  Some fields do not match")
    else:
        print("❌ Failed to decode one or both tokens")

def show_usage_example():
    """Show how to use the selected_collection_id in frontend"""
    print("\n" + "="*60)
    print("USAGE EXAMPLE: Frontend Integration")
    print("="*60)
    
    print("""
JavaScript/TypeScript Example:
------------------------------

import jwt_decode from 'jwt-decode';

interface JWTPayload {
  user_id: string;
  email: string;
  name: string;
  picture: string;
  selected_collection_id: string;
  exp: number;
}

// After login
const token = localStorage.getItem('jwt_token');
const decoded = jwt_decode<JWTPayload>(token);

console.log('User ID:', decoded.user_id);
console.log('Email:', decoded.email);
console.log('Selected Collection:', decoded.selected_collection_id);

// Use the collection ID immediately
if (decoded.selected_collection_id) {
  loadVocabularies(decoded.selected_collection_id);
} else {
  // Prompt user to select a collection
  showCollectionSelector();
}

// After changing collection, renew token
async function changeCollection(newCollectionId) {
  // Update collection
  await fetch('/api/v1/change-selected-collection', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ 
      selected_collection_id: newCollectionId 
    })
  });
  
  // Renew JWT token to get updated collection ID
  const refreshToken = localStorage.getItem('jwt_refresh_token');
  const renewResponse = await fetch('/api/v1/auth/renew-jwt', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ jwt_refresh_token: refreshToken })
  });
  
  const { jwt_token } = await renewResponse.json();
  localStorage.setItem('jwt_token', jwt_token);
  
  // Decode new token
  const newDecoded = jwt_decode<JWTPayload>(jwt_token);
  console.log('Updated collection:', newDecoded.selected_collection_id);
}
    """)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("JWT TOKEN - SELECTED_COLLECTION_ID TEST SUITE")
    print("="*60)
    print("\n⚠️  Note: This script decodes tokens WITHOUT signature verification")
    print("This is for testing purposes only - never do this in production!")
    
    while True:
        print("\n" + "="*60)
        print("Select a test:")
        print("="*60)
        print("1. Test JWT Token Structure")
        print("2. Test JWT Refresh Token Structure")
        print("3. Compare JWT Token and Refresh Token")
        print("4. Show Usage Example")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            test_jwt_token_structure()
        elif choice == "2":
            test_refresh_token_structure()
        elif choice == "3":
            compare_tokens()
        elif choice == "4":
            show_usage_example()
        elif choice == "5":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETED")
    print("="*60)
