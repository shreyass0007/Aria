import sys
import os
# Add current directory to path so we can import brain
sys.path.append(os.getcwd())

from brain import AriaBrain

def test_brain():
    print("Initializing AriaBrain with OpenAI...")
    brain = AriaBrain()
    
    if not brain.is_available():
        print("Brain is not available. Check API key.")
        return

    print("\nTesting ask()...")
    response = brain.ask("Hello, who are you?")
    print(f"Response: {response}")

    print("\nTesting parse_calendar_intent()...")
    intent = brain.parse_calendar_intent("Schedule a team meeting for next Friday at 2 PM")
    print(f"Intent: {intent}")

if __name__ == "__main__":
    test_brain()
