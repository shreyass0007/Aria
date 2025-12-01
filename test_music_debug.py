import requests
import json

BASE_URL = "http://localhost:5000"

def test_music_controls():
    """Test music pause/resume endpoints"""
    
    print("=" * 50)
    print("Testing Music Control Endpoints")
    print("=" * 50)
    
    # Test 1: Check backend health
    print("\n1. Checking backend health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   ✓ Backend is running: {response.json()}")
    except Exception as e:
        print(f"   ✗ Backend error: {e}")
        return
    
    # Test 2: Get music status
    print("\n2. Getting music status...")
    try:
        response = requests.get(f"{BASE_URL}/music/status")
        status = response.json()
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {json.dumps(status, indent=2)}")
        print(f"   Is Playing: {status.get('is_playing')}")
        print(f"   Current Track: {status.get('track')}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: Try to pause
    print("\n3. Testing PAUSE endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/music/pause")
        result = response.json()
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {json.dumps(result, indent=2)}")
        
        # Check if response has is_playing field
        if 'is_playing' in result:
            print(f"   ✓ Response includes 'is_playing': {result['is_playing']}")
        else:
            print(f"   ✗ Response missing 'is_playing' field!")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 4: Try to resume
    print("\n4. Testing RESUME endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/music/resume")
        result = response.json()
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {json.dumps(result, indent=2)}")
        
        # Check if response has is_playing field
        if 'is_playing' in result:
            print(f"   ✓ Response includes 'is_playing': {result['is_playing']}")
        else:
            print(f"   ✗ Response missing 'is_playing' field!")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_music_controls()
