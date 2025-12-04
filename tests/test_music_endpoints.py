import requests
import time

BASE_URL = "http://localhost:5000"

def test_music_endpoints():
    """Test music control endpoints"""
    
    print("Testing music endpoints...")
    
    # Test 1: Get music status
    print("\n1. Testing GET /music/status")
    try:
        response = requests.get(f"{BASE_URL}/music/status")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Set volume
    print("\n2. Testing POST /music/volume")
    try:
        response = requests.post(
            f"{BASE_URL}/music/volume",
            json={"volume": 50}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Pause (when nothing is playing)
    print("\n3. Testing POST /music/pause")
    try:
        response = requests.post(f"{BASE_URL}/music/pause")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Resume (when nothing is playing)
    print("\n4. Testing POST /music/resume")
    try:
        response = requests.post(f"{BASE_URL}/music/resume")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n✓ All endpoint tests completed!")

if __name__ == "__main__":
    # Wait a bit for backend to start if needed
    print("Waiting for backend to be ready...")
    time.sleep(2)
    
    try:
        health = requests.get(f"{BASE_URL}/health")
        if health.status_code == 200:
            print("✓ Backend is ready!")
            test_music_endpoints()
        else:
            print("✗ Backend not responding properly")
    except Exception as e:
        print(f"✗ Backend not accessible: {e}")
        print("\nPlease ensure the backend is running with: python backend_fastapi.py")
