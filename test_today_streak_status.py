"""
Test script for the today-streak-status API endpoint
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
# Replace with your actual JWT token
JWT_TOKEN = "your_jwt_token_here"

def test_today_streak_status():
    """Test getting today's streak status"""
    print("\n" + "="*60)
    print("TEST: Get Today's Streak Status")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}"
    }
    
    print("\n1. Getting today's streak status...")
    response = requests.get(
        f"{BASE_URL}/today-streak-status",
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Response:")
        print(json.dumps(data, indent=2))
        
        print(f"\n📊 Today's Streak Status:")
        print(f"   Date: {data['date']}")
        print(f"   Count: {data['count']}")
        print(f"   Is Qualify: {data['is_qualify']}")
        print(f"   Status: {data['status']}")
        
        # Validate current date
        today = datetime.utcnow().strftime('%Y-%m-%d')
        if data['date'] == today:
            print(f"\n✅ Date matches current date: {today}")
        else:
            print(f"\n⚠️  Date mismatch. Expected: {today}, Got: {data['date']}")
        
        # Check data consistency
        if data['count'] >= 5 and not data['is_qualify']:
            print("\n⚠️  Warning: count >= 5 but is_qualify is false")
        elif data['count'] >= 5 and data['is_qualify']:
            print("\n✅ Qualified! Count >= 5 and is_qualify is true")
        elif data['count'] < 5 and not data['is_qualify']:
            print(f"\n📈 Not qualified yet. Need {5 - data['count']} more paragraphs")
        
    else:
        print(f"❌ Failed to get streak status")
        print(f"Response: {response.text}")

def test_after_generating_paragraph():
    """Test streak status after generating a paragraph"""
    print("\n" + "="*60)
    print("TEST: Generate Paragraph and Check Streak")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # First, check current status
    print("\n1. Checking current streak status...")
    status_response = requests.get(
        f"{BASE_URL}/today-streak-status",
        headers=headers
    )
    
    if status_response.status_code == 200:
        before_data = status_response.json()
        print(f"Before: count={before_data['count']}, is_qualify={before_data['is_qualify']}")
        
        # Generate a paragraph to increment streak
        print("\n2. Generating a paragraph...")
        paragraph_data = {
            "vocabularies": ["test", "example"],
            "language": "English",
            "level": "beginner",
            "tone": "casual",
            "topic": "testing"
        }
        
        gen_response = requests.post(
            f"{BASE_URL}/generate-paragraph",
            headers=headers,
            json=paragraph_data
        )
        
        if gen_response.status_code == 200:
            print("✅ Paragraph generated successfully")
            
            # Check streak status again
            print("\n3. Checking streak status after generation...")
            after_response = requests.get(
                f"{BASE_URL}/today-streak-status",
                headers=headers
            )
            
            if after_response.status_code == 200:
                after_data = after_response.json()
                print(f"After: count={after_data['count']}, is_qualify={after_data['is_qualify']}")
                
                if after_data['count'] > before_data['count']:
                    print(f"\n✅ Count incremented from {before_data['count']} to {after_data['count']}")
                else:
                    print(f"\n⚠️  Count did not change: {before_data['count']} -> {after_data['count']}")
                
                if after_data['count'] >= 5:
                    if after_data['is_qualify']:
                        print("✅ Qualified! is_qualify is true")
                    else:
                        print("⚠️  Count >= 5 but is_qualify is still false")
            else:
                print("❌ Failed to get streak status after generation")
        else:
            print(f"❌ Failed to generate paragraph: {gen_response.status_code}")
            print(f"Response: {gen_response.text}")
    else:
        print("❌ Failed to get initial streak status")

def test_no_auth():
    """Test endpoint without authentication"""
    print("\n" + "="*60)
    print("TEST: Without Authentication")
    print("="*60)
    
    print("\nAttempting to access without token...")
    response = requests.get(f"{BASE_URL}/today-streak-status")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 401:
        print("✅ Correctly returned 401 Unauthorized")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"❌ Expected 401, got {response.status_code}")

def test_invalid_token():
    """Test endpoint with invalid token"""
    print("\n" + "="*60)
    print("TEST: Invalid Token")
    print("="*60)
    
    headers = {
        "Authorization": "Bearer invalid_token_123"
    }
    
    print("\nAttempting to access with invalid token...")
    response = requests.get(
        f"{BASE_URL}/today-streak-status",
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 401:
        print("✅ Correctly returned 401 for invalid token")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"❌ Expected 401, got {response.status_code}")

def display_integration_example():
    """Display frontend integration example"""
    print("\n" + "="*60)
    print("FRONTEND INTEGRATION EXAMPLE")
    print("="*60)
    
    print("""
JavaScript/TypeScript Example:
------------------------------

async function getTodayStreakStatus() {
  const token = localStorage.getItem('jwt_token');
  
  try {
    const response = await fetch('http://localhost:8000/api/v1/today-streak-status', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('Today\\'s Streak:', data);
      
      // Display to user
      document.getElementById('streak-count').textContent = data.count;
      document.getElementById('streak-date').textContent = data.date;
      
      if (data.is_qualify) {
        document.getElementById('qualify-badge').style.display = 'block';
      }
      
      // Show progress
      const progress = (data.count / 5) * 100;
      document.getElementById('progress-bar').style.width = `${progress}%`;
      
      return data;
    } else {
      console.error('Failed to get streak status:', response.status);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

// Call on page load
getTodayStreakStatus();

// Refresh after generating paragraph
async function generateParagraph(vocabularies) {
  // Generate paragraph...
  const result = await fetch('/api/v1/generate-paragraph', {...});
  
  if (result.ok) {
    // Refresh streak status
    const streakStatus = await getTodayStreakStatus();
    
    if (streakStatus.is_qualify) {
      showCelebration('You qualified today! 🎉');
    }
  }
}

React Component Example:
-----------------------

import { useState, useEffect } from 'react';

function StreakStatus() {
  const [streak, setStreak] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchStreakStatus();
  }, []);
  
  const fetchStreakStatus = async () => {
    const token = localStorage.getItem('jwt_token');
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/today-streak-status', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      const data = await response.json();
      setStreak(data);
    } catch (error) {
      console.error('Error fetching streak:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div className="streak-card">
      <h3>Today's Progress</h3>
      <div className="date">{streak.date}</div>
      <div className="count">
        <span className="number">{streak.count}</span>
        <span className="label">paragraphs</span>
      </div>
      <div className="progress">
        <div 
          className="progress-bar" 
          style={{ width: `${(streak.count / 5) * 100}%` }}
        />
      </div>
      {streak.is_qualify && (
        <div className="badge">✅ Qualified!</div>
      )}
      {!streak.is_qualify && (
        <div className="remaining">
          {5 - streak.count} more to qualify
        </div>
      )}
    </div>
  );
}
    """)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("TODAY STREAK STATUS API TEST SUITE")
    print("="*60)
    print("\n⚠️  Make sure to:")
    print("1. Update JWT_TOKEN with your actual token")
    print("2. Server is running on http://localhost:8000")
    print("3. You have a valid user account")
    
    while True:
        print("\n" + "="*60)
        print("Select a test:")
        print("="*60)
        print("1. Test Today's Streak Status (Basic)")
        print("2. Test After Generating Paragraph")
        print("3. Test Without Authentication")
        print("4. Test With Invalid Token")
        print("5. Show Frontend Integration Example")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            test_today_streak_status()
        elif choice == "2":
            test_after_generating_paragraph()
        elif choice == "3":
            test_no_auth()
        elif choice == "4":
            test_invalid_token()
        elif choice == "5":
            display_integration_example()
        elif choice == "6":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-6.")
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETED")
    print("="*60)
