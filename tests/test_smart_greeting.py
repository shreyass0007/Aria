
import os
import sys
from aria.aria_core import AriaCore
from unittest.mock import MagicMock

def test_smart_greeting():
    print("Initializing AriaCore (Mocking Speech)...")
    aria = AriaCore(on_speak=lambda x: print(f"SPEAK: {x}"))
    
    # Mock Calendar to return a fake event
    print("Mocking Calendar...")
    aria.calendar.get_upcoming_events = MagicMock(return_value="Here are your upcoming events:\n- Physics Exam at 10:00 AM")
    
    print("Testing Smart Greeting...")
    greeting = aria.get_time_based_greeting()
    print(f"\nRESULT: {greeting}")
    
    if "Exam" in greeting or "Physics" in greeting:
        print(" SUCCESS: Greeting mentions the event!")
    else:
        print(" FAILURE: Greeting did not mention the event (or LLM failed).")

if __name__ == "__main__":
    test_smart_greeting()
