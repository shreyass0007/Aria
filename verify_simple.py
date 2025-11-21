import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key length: {len(api_key) if api_key else 0}")

if not api_key:
    print("No API key found")
    exit(1)

try:
    api_key = api_key.strip()
    print(f"Key: {api_key[:4]}...{api_key[-4:]}")
    print(f"Key repr: {repr(api_key)}")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Hello")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
