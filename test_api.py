"""
Test the Flask Backend API
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"


def test_health():
    """Test API health"""
    print("\n🔍 Testing API Health...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        print(f"✅ Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"❌ Error: {e}")


def test_create_user():
    """Create test user"""
    print("\n👤 Creating Test User...")
    try:
        payload = {
            "user_id": "USER001",
            "name": "Dr. John Doe",
            "department": "ICU",
            "role": "Doctor"
        }
        response = requests.post(f"{API_URL}/users", json=payload, timeout=5)
        print(f"✅ Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"❌ Error: {e}")


def test_log_event():
    """Log test event"""
    print("\n📝 Logging Test Event...")
    try:
        payload = {
            "user_id": "USER001",
            "duration": 22.5,
            "status": "completed",
            "location": "ICU",
            "department": "Critical Care"
        }
        response = requests.post(f"{API_URL}/log", json=payload, timeout=5)
        print(f"✅ Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"❌ Error: {e}")


def test_get_logs():
    """Get events"""
    print("\n📊 Getting Events...")
    try:
        response = requests.get(f"{API_URL}/logs", timeout=5)
        print(f"✅ Status: {response.status_code}")
        data = response.json()
        print(f"Events: {data.get('count', 0)}")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_get_stats():
    """Get statistics"""
    print("\n📈 Getting Statistics...")
    try:
        response = requests.get(f"{API_URL}/stats", timeout=5)
        print(f"✅ Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("=" * 70)
    print("🏥 Hand Hygiene API Tests")
    print("=" * 70)
    
    test_health()
    test_create_user()
    test_log_event()
    test_get_logs()
    test_get_stats()
    
    print("\n" + "=" * 70)
    print("✅ Tests complete!")
    print("=" * 70)
