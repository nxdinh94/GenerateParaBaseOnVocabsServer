"""
Test script for the increment-streak API endpoint

This script tests:
1. Increment today's streak (first time)
2. Increment today's streak (second time - should increment count)
3. Increment specific date
4. Check qualification when count reaches 5
5. Test without authentication
6. Test with invalid date format

Usage:
    python test_increment_streak.py
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
jwt_token = "YOUR_JWT_TOKEN_HERE"  # Replace with your actual JWT token

def print_separator():
    print("\n" + "="*80 + "\n")

def test_increment_today_first_time():
    """Test incrementing today's streak for the first time"""
    print("TEST 1: Increment Today's Streak (First Time)")
    print("-" * 80)
    
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    # Empty body = today
    response = requests.post(f"{BASE_URL}/increment-streak", headers=headers, json={})
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS")
        print(f"   Date: {data['learned_date']}")
        print(f"   Count: {data['count']}")
        print(f"   Qualified: {data['is_qualify']}")
        print(f"   Incremented: {data['incremented']} (should be False for first time)")
        
        if not data['incremented'] and data['count'] == 1:
            print("   ✅ Correct: New entry created with count = 1")
        else:
            print("   ⚠️  Note: Entry already existed or count != 1")
    else:
        print(f"❌ FAILED: {response.status_code}")
        print(response.json())

def test_increment_today_second_time():
    """Test incrementing today's streak again (should increment count)"""
    print("TEST 2: Increment Today's Streak (Second Time)")
    print("-" * 80)
    
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{BASE_URL}/increment-streak", headers=headers, json={})
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS")
        print(f"   Count: {data['count']}")
        print(f"   Incremented: {data['incremented']} (should be True)")
        
        if data['incremented'] and data['count'] >= 2:
            print(f"   ✅ Correct: Count incremented to {data['count']}")
        else:
            print("   ⚠️  Unexpected result")
    else:
        print(f"❌ FAILED: {response.status_code}")

def test_increment_specific_date():
    """Test incrementing streak for a specific date"""
    print("TEST 3: Increment Specific Date")
    print("-" * 80)
    
    # Use yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    body = {"learned_date": yesterday}
    
    response = requests.post(f"{BASE_URL}/increment-streak", headers=headers, json=body)
    
    print(f"Request Date: {yesterday}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS")
        print(f"   Date: {data['learned_date']}")
        print(f"   Count: {data['count']}")
        
        if data['learned_date'] == yesterday:
            print(f"   ✅ Correct: Date matches requested date")
        else:
            print(f"   ❌ Error: Date mismatch")
    else:
        print(f"❌ FAILED: {response.status_code}")

def test_qualification():
    """Test reaching qualification (count = 5)"""
    print("TEST 4: Test Qualification (Increment 5 times)")
    print("-" * 80)
    
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    # Use a specific test date
    test_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    body = {"learned_date": test_date}
    
    print(f"Incrementing {test_date} five times...")
    
    for i in range(1, 6):
        response = requests.post(f"{BASE_URL}/increment-streak", headers=headers, json=body)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Attempt {i}: count = {data['count']}, is_qualify = {data['is_qualify']}")
            
            if i == 5 and data['is_qualify']:
                print(f"\n🎉 SUCCESS: Qualified after 5 increments!")
                print(f"   Final count: {data['count']}")
                print(f"   is_qualify: {data['is_qualify']}")
                return
    
    print("\n⚠️  Note: May have already been qualified or encountered an error")

def test_without_authentication():
    """Test without Bearer token (should fail)"""
    print("TEST 5: Test Without Authentication")
    print("-" * 80)
    
    response = requests.post(
        f"{BASE_URL}/increment-streak",
        headers={"Content-Type": "application/json"},
        json={}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 401:
        print(f"\n✅ SUCCESS: Correctly rejected unauthorized request")
    else:
        print(f"\n❌ FAILED: Expected 401, got {response.status_code}")

def test_invalid_date_format():
    """Test with invalid date format (should fail)"""
    print("TEST 6: Test Invalid Date Format")
    print("-" * 80)
    
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    body = {"learned_date": "invalid-date"}
    
    response = requests.post(f"{BASE_URL}/increment-streak", headers=headers, json=body)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 400:
        print(f"\n✅ SUCCESS: Correctly rejected invalid date format")
    else:
        print(f"\n❌ FAILED: Expected 400, got {response.status_code}")

def test_check_today_status():
    """Check today's status after increments"""
    print("TEST 7: Check Today's Status (Verify Increments)")
    print("-" * 80)
    
    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }
    
    response = requests.get(f"{BASE_URL}/today-streak-status", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Current Status:")
        print(f"   Date: {data['date']}")
        print(f"   Count: {data['count']}")
        print(f"   Qualified: {data['is_qualify']}")
        print(f"   Progress: {(data['count'] / 5) * 100:.1f}%")

def run_all_tests():
    """Run all tests"""
    print("="*80)
    print("INCREMENT STREAK API TEST SUITE")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"JWT Token: {jwt_token[:20]}..." if len(jwt_token) > 20 else "NOT SET")
    print("="*80)
    
    if jwt_token == "YOUR_JWT_TOKEN_HERE":
        print("\n❌ ERROR: Please set your JWT token in the script")
        print("   Get your token by logging in via /api/v1/auth/google/login")
        return
    
    print_separator()
    test_increment_today_first_time()
    
    print_separator()
    test_increment_today_second_time()
    
    print_separator()
    test_increment_specific_date()
    
    print_separator()
    test_qualification()
    
    print_separator()
    test_without_authentication()
    
    print_separator()
    test_invalid_date_format()
    
    print_separator()
    test_check_today_status()
    
    print_separator()
    print("="*80)
    print("TEST SUITE COMPLETED")
    print("="*80)

if __name__ == "__main__":
    run_all_tests()


# Frontend Integration Examples
print("\n\n")
print("="*80)
print("FRONTEND INTEGRATION EXAMPLES")
print("="*80)

print("""
### JavaScript/TypeScript Example

async function incrementStreak(date = null) {
  const token = localStorage.getItem('jwt_token');
  const body = date ? { learned_date: date } : {};
  
  const response = await fetch('http://localhost:8000/api/v1/increment-streak', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  });
  
  const data = await response.json();
  
  if (data.is_qualify && data.count === 5) {
    alert('🎉 Congratulations! You qualified today!');
  } else {
    console.log(`Progress: ${data.count}/5`);
  }
  
  return data;
}

// Usage
await incrementStreak();  // Increment today
await incrementStreak('2025-10-10');  // Increment specific date


### React Component Example

import { useState } from 'react';

function ActivityButton() {
  const [streak, setStreak] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const handleActivity = async () => {
    setLoading(true);
    try {
      // 1. Perform activity
      await performActivity();
      
      // 2. Increment streak
      const response = await fetch('/api/v1/increment-streak', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      });
      
      const data = await response.json();
      setStreak(data);
      
      // 3. Show feedback
      if (data.is_qualify) {
        alert('🏆 Qualified!');
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div>
      <button onClick={handleActivity} disabled={loading}>
        {loading ? 'Processing...' : 'Complete Activity'}
      </button>
      
      {streak && (
        <div className="streak-display">
          <p>Count: {streak.count}/5</p>
          {streak.is_qualify && <span>🏆 Qualified!</span>}
        </div>
      )}
    </div>
  );
}


### After Generating Paragraph

async function handleGenerateParagraph() {
  try {
    // 1. Generate paragraph
    const paragraph = await fetch('/api/v1/generate-paragraph', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        language: 'English',
        vocabularies: ['hello', 'world'],
        length: 100,
        level: 'beginner'
      })
    }).then(r => r.json());
    
    // 2. Increment streak
    const streak = await fetch('/api/v1/increment-streak', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    }).then(r => r.json());
    
    // 3. Show results
    console.log('Paragraph generated:', paragraph);
    console.log('Streak updated:', streak);
    
    if (streak.is_qualify && streak.count === 5) {
      showCelebration('You just qualified! 🎉');
    }
    
  } catch (error) {
    console.error('Error:', error);
  }
}
""")
