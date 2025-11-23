"""
Test the structured formatting in Aria's chat
"""

import requests
import json

API_URL = "http://localhost:5000"

# Test message with structured formatting
test_message = """
📄 FORMATTING TEST

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 This is a test message
📊 Testing: Line breaks and emojis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Content:
Line 1: Normal text
Line 2: With spacing
Line 3: And emojis ✨

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

print("Sending formatted test message to check UI display...")
print("\nExpected output in UI:")
print(test_message)
print("\nSending to backend...")

try:
    response = requests.post(
        f"{API_URL}/message",
        json={"message": "test formatting"},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        print("\n✅ Backend is responding")
        print("Now type in Aria's chat: 'summarize notion page The Pursuit of Happiness'")
        print("You should see structured formatting with:")
        print("  • Line breaks preserved")
        print("  • Emojis displayed")
        print("  • Box drawing characters aligned")
    else:
        print(f"\n❌ Error: {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Error connecting to backend: {e}")
    print("Make sure the backend is running (npm start should have started it)")
