
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.getcwd())

load_dotenv()

try:
    from aria.brain import AriaBrain
    print("Initializing AriaBrain...")
    brain = AriaBrain()
    print("Checking available models...")
    models = brain.get_available_models()
    print(f"Available Models: {models}")
    
    # Check env vars existence (do not print values)
    print(f"OPEN_AI_API_KEY present: {bool(os.getenv('OPEN_AI_API_KEY'))}")
    print(f"ANTHROPIC_API_KEY present: {bool(os.getenv('ANTHROPIC_API_KEY'))}")
    print(f"GOOGLE_API_KEY present: {bool(os.getenv('GOOGLE_API_KEY'))}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
