import sys
import os
sys.path.append(os.getcwd())

from brain import AriaBrain

try:
    print("Initializing AriaBrain...")
    brain = AriaBrain()
    print("AriaBrain initialized.")
    
    models = brain.get_available_models()
    print(f"Available models ({len(models)}):")
    for m in models:
        print(f" - {m['id']} ({m['name']})")
        
    print("\nChecking internal state:")
    print(f"gpt-5.1: {brain.llm_gpt_5_1}")
    print(f"claude-sonnet: {brain.llm_claude_sonnet}")
    print(f"claude-haiku: {brain.llm_claude_haiku}")
    print(f"claude-opus-4.5: {brain.llm_claude_opus_4_5}")
    print(f"claude-opus-4.1: {brain.llm_claude_opus_4_1}")
    
except Exception as e:
    print(f"Error: {e}")
