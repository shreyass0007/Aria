import sys
import os
import asyncio
from aria_core import AriaCore

# Mock the speak callback
def mock_speak(text):
    print(f"MOCK SPEAK: {text}")

def main():
    print("Initializing AriaCore...")
    aria = AriaCore(on_speak=mock_speak)
    
    message = "check to-do"
    print(f"\nProcessing message: '{message}'")
    
    # Simulate backend_fastapi.py logic
    if message.lower().strip() == "aria":
        intent_data = {"intent": "wake_word", "confidence": 1.0, "parameters": {}}
    else:
        print("Classifying intent...")
        intent_data = aria.command_classifier.classify_intent(message)
        print(f"Intent Data: {intent_data}")
        
    intent = intent_data.get("intent")
    print(f"Intent: {intent}")
    
    print("Processing command...")
    aria.process_command(message, model_name="openai", intent_data=intent_data)
    print("Done.")

if __name__ == "__main__":
    main()
