import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, expected_status=200):
    url = f"{BASE_URL}{endpoint}"
    print(f"Testing {method} {endpoint}...", end=" ")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        if response.status_code == expected_status:
            print(f"✅ OK ({response.status_code})")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ FAILED ({response.status_code})")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def run_tests():
    print("Starting Route Verification...")
    
    # 1. General Routes
    test_endpoint("GET", "/")
    test_endpoint("GET", "/health")
    test_endpoint("GET", "/features")
    
    # 2. System Routes
    test_endpoint("GET", "/system/health")
    
    # 3. Music Routes
    test_endpoint("GET", "/music/status")
    # Test volume (safe)
    test_endpoint("POST", "/music", {"action": "volume", "volume": 50})
    
    # 4. Voice/TTS Routes
    test_endpoint("POST", "/voice_mode", {"enabled": False})
    test_endpoint("POST", "/tts", {"enabled": False}) # Disable to avoid noise during test
    test_endpoint("POST", "/stop_speaking")
    test_endpoint("GET", "/settings/tts") # New endpoint

    # 5. Dashboard/Frontend Routes (New)
    test_endpoint("GET", "/notifications")
    test_endpoint("GET", "/briefing")
    test_endpoint("GET", "/models/available")
    
    # 6. Chat Route (The big one)
    # We use a simple hello message
    print("\nTesting Chat (this might take a few seconds)...")
    test_endpoint("POST", "/message", {
        "message": "Hello, are you online?",
        "conversation_id": "test_verification_id"
    })
    
    print("\nVerification Complete.")

if __name__ == "__main__":
    run_tests()
