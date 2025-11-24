import requests
import json
import time

API_URL = "http://localhost:5000"

def test_model(model_name, prompt):
    print(f"\n--- Testing Model: {model_name} ---")
    payload = {
        "message": prompt,
        "model": model_name
    }
    try:
        start_time = time.time()
        response = requests.post(f"{API_URL}/message", json=payload)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: Success ({end_time - start_time:.2f}s)")
            print(f"Response: {data.get('response')}")
            return True
        else:
            print(f"Status: Failed ({response.status_code})")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def verify_all():
    print("Starting Multi-Model Verification...")
    
    # 1. Test OpenAI
    test_model("openai", "Who are you? (Short answer)")
    
    # 2. Test Gemini
    test_model("gemini", "Who are you? (Short answer)")
    
    # 3. Test Ollama (might fail if not running)
    print("\nNote: Ollama test requires Ollama running locally.")
    test_model("ollama", "Who are you? (Short answer)")

if __name__ == "__main__":
    verify_all()
