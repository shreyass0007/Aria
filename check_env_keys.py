
import os
from dotenv import load_dotenv

load_dotenv()

keys_to_check = [
    "OPEN_AI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY"
]

print("Checking keys in .env:")
for key in keys_to_check:
    value = os.getenv(key)
    if value:
        print(f"{key}: PRESENT (Length: {len(value)})")
    else:
        print(f"{key}: MISSING")
