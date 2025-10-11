"""
Test script for Streak API endpoints
"""
import requests
import json
from datetime import datetime, timedelta

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

# Test JWT token (replace with your actual token)
JWT_TOKEN = "your_jwt_token_here"

headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

def test_create_streak():
    """Test creating a streak entry"""
    print("\n=== Test 1: Create Streak ===")
    
    # Test with today's date (default)
    url = f"{BASE_URL}/streak"
    data = {
        "step": 5
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test with specific date
    specific_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    data = {
        "learned_date": specific_date,
        "step": 3
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"\nCreating streak for {specific_date}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_get_streak_chain():
    """Test getting streak chain"""
    print("\n=== Test 2: Get Streak Chain ===")
    
    # Get streak chain for last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    url = f"{BASE_URL}/streak-chain"
    params = {
        "startday": start_date.strftime('%Y-%m-%d'),
        "endday": end_date.strftime('%Y-%m-%d')
    }
    
    response = requests.get(url, headers=headers, params=params)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Start Date: {data['start_date']}")
        print(f"End Date: {data['end_date']}")
        print(f"Total Days: {data['total_days']}")
        print(f"Completed Days: {data['completed_days']}")
        print(f"\nFirst 5 dates:")
        for date_info in data['dates'][:5]:
            status = "✅" if date_info['completed'] else "❌"
            print(f"  {date_info['date']}: {status}")
        print(f"\nLast 5 dates:")
        for date_info in data['dates'][-5:]:
            status = "✅" if date_info['completed'] else "❌"
            print(f"  {date_info['date']}: {status}")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_create_multiple_streaks():
    """Test creating multiple streak entries"""
    print("\n=== Test 3: Create Multiple Streaks ===")
    
    url = f"{BASE_URL}/streak"
    
    # Create streaks for last 7 days
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        data = {
            "learned_date": date,
            "step": i + 1
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"✅ Created streak for {date} with step {i + 1}")
        else:
            print(f"❌ Failed to create streak for {date}: {response.status_code}")

def test_get_short_streak_chain():
    """Test getting a short streak chain (7 days)"""
    print("\n=== Test 4: Get 7-Day Streak Chain ===")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=6)  # 7 days total
    
    url = f"{BASE_URL}/streak-chain"
    params = {
        "startday": start_date.strftime('%Y-%m-%d'),
        "endday": end_date.strftime('%Y-%m-%d')
    }
    
    response = requests.get(url, headers=headers, params=params)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nStreak Summary:")
        print(f"  Period: {data['start_date']} to {data['end_date']}")
        print(f"  Total Days: {data['total_days']}")
        print(f"  Completed Days: {data['completed_days']}")
        print(f"  Completion Rate: {(data['completed_days'] / data['total_days'] * 100):.1f}%")
        print(f"\nDaily Breakdown:")
        for date_info in data['dates']:
            status = "✅ Completed" if date_info['completed'] else "❌ Not completed"
            print(f"  {date_info['date']}: {status}")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_update_existing_streak():
    """Test updating an existing streak entry"""
    print("\n=== Test 5: Update Existing Streak ===")
    
    url = f"{BASE_URL}/streak"
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Create initial streak
    data = {
        "learned_date": today,
        "step": 1
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"Initial streak creation:")
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        print(f"  Step: {response.json()['step']}")
    
    # Update the same date with different step
    data = {
        "learned_date": today,
        "step": 10
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"\nUpdated streak:")
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        print(f"  Step: {response.json()['step']}")
        print(f"  ✅ Streak was updated successfully!")

def main():
    """Run all tests"""
    print("=" * 60)
    print("STREAK API TEST SUITE")
    print("=" * 60)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Token: {JWT_TOKEN[:20]}..." if len(JWT_TOKEN) > 20 else f"Token: {JWT_TOKEN}")
    
    # Check if JWT token is set
    if JWT_TOKEN == "your_jwt_token_here":
        print("\n⚠️  WARNING: Please set your JWT_TOKEN in the script!")
        print("   You can get a token by logging in through the API.")
        return
    
    try:
        # Run tests
        test_create_streak()
        test_get_streak_chain()
        test_create_multiple_streaks()
        test_get_short_streak_chain()
        test_update_existing_streak()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the API server.")
        print("   Please make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
