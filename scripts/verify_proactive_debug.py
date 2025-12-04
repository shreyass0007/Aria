import sys
import os
import datetime
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from calendar_manager import CalendarManager
from proactive_manager import ProactiveManager

def test_proactive_components():
    print("--- Testing Calendar Manager ---")
    try:
        calendar = CalendarManager()
        if not os.path.exists('credentials.json'):
            print("❌ credentials.json NOT FOUND. Calendar will not work.")
        else:
            print("✅ credentials.json found.")
            
        events = calendar.get_upcoming_events_raw(max_results=5)
        print(f"Events found: {len(events)}")
        for event in events:
            print(f" - {event.get('summary')} at {event.get('start')}")
            
    except Exception as e:
        print(f"❌ Calendar Error: {e}")
        return

    print("\n--- Testing Proactive Manager Logic ---")
    # Mock dependencies
    mock_system = MagicMock()
    mock_tts = MagicMock()
    mock_launcher = MagicMock()
    
    # Create manager
    manager = ProactiveManager(calendar, mock_system, mock_tts, mock_launcher)
    
    # Force a check
    print("Running check_and_act()...")
    try:
        manager.check_and_act()
        print("✅ check_and_act() completed without error.")
    except Exception as e:
        print(f"❌ Proactive Manager Error: {e}")

if __name__ == "__main__":
    test_proactive_components()
