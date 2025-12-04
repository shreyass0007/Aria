import requests
import json

# Test the weather endpoint
response = requests.post(
    'http://localhost:5000/message',
    json={'message': 'what is the weather in London'}
)

print("="*60)
print("Weather API Test Result")
print("="*60)
print(f"Status Code: {response.status_code}")
print(f"\nFull Response:")
print(json.dumps(response.json(), indent=2))
print("="*60)
