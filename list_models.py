import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("Error: ANTHROPIC_API_KEY not found.")
    exit(1)

try:
    client = anthropic.Anthropic(api_key=api_key)
    models = client.models.list()
    
    print(f"Found {len(models.data)} models:")
    for m in models.data:
        print(f"- {m.id} ({m.display_name})")
        
except Exception as e:
    print(f"Error listing models: {e}")
