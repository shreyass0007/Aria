import time
import sys
import os
import asyncio

# Ensure aria is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aria.brain import AriaBrain
from aria.command_intent_classifier import CommandIntentClassifier

def test_latency():
    print("Initializing Brain...")
    brain = AriaBrain()
    classifier = CommandIntentClassifier(brain)
    
    # 1. Classification
    print("\n--- Testing Intent Classification (GPT-4o-mini) ---")
    
    # Use a typical command
    commands = [
        "Open calculator",
        "What time is it",
        "Play some music"
    ]
    
    for cmd in commands:
        start = time.time()
        result = classifier.classify_intent(cmd) 
        duration = time.time() - start
        
        intent = result[0]['intent'] if result else "None"
        print(f"Command: '{cmd}' -> Intent: '{intent}' took: {duration:.4f}s")
        if duration > 1.0:
            print("  [WARNING] Classification too slow!")
        else:
            print("  [PASS] Speed ok.")

    # 2. Streaming
    print("\n--- Testing Streaming (GPT-4o-mini) ---")
    start = time.time()
    
    print("Asking: 'Tell me a short story about a cat.'")
    stream = brain.stream_ask("Tell me a short story about a cat.", model_name="gpt-4o-mini")
    
    first_token_time = None
    full_text = ""
    
    for chunk in stream:
        if first_token_time is None:
            first_token_time = time.time()
            ttft = first_token_time - start
            print(f"Time To First Token (TTFT): {ttft:.4f}s")
            
        full_text += chunk
        
    total_duration = time.time() - start
    print(f"Total Response Duration: {total_duration:.4f}s")
    print(f"Total Tokens (approx chars): {len(full_text)}")
    
    if first_token_time and (first_token_time - start) < 1.0:
         print("  [PASS] TTFT < 1s")
    else:
         print("  [WARNING] TTFT slow!")

if __name__ == "__main__":
    test_latency()
