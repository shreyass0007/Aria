"""
Test script to verify Google Calendar integration.
This script tests:
1. Calendar authentication
2. Event creation
3. Event retrieval
"""

import datetime
from aria.calendar_manager import CalendarManager
from aria.brain import AriaBrain

def test_calendar_authentication():
    """Test if calendar authentication works."""
    print("=" * 60)
    print("TEST 1: Calendar Authentication")
    print("=" * 60)
    
    try:
        calendar = CalendarManager()
        if calendar.service:
            print(" SUCCESS: Calendar service authenticated!")
            print(f"   Service object: {calendar.service}")
            return calendar
        else:
            print(" FAILED: Calendar service not initialized")
            print("   This might mean credentials.json is missing or authentication failed.")
            return None
    except Exception as e:
        print(f" ERROR: {e}")
        return None

def test_event_retrieval(calendar):
    """Test retrieving upcoming events."""
    print("\n" + "=" * 60)
    print("TEST 2: Retrieve Upcoming Events")
    print("=" * 60)
    
    if not calendar:
        print("  SKIPPED: No calendar service available")
        return
    
    try:
        result = calendar.get_upcoming_events(max_results=5)
        print(" SUCCESS: Retrieved events")
        print(f"\n{result}")
    except Exception as e:
        print(f" ERROR: {e}")

def test_event_creation(calendar):
    """Test creating a calendar event."""
    print("\n" + "=" * 60)
    print("TEST 3: Create Calendar Event")
    print("=" * 60)
    
    if not calendar:
        print("  SKIPPED: No calendar service available")
        return
    
    try:
        # Create a test event for tomorrow at 2 PM
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
        
        result = calendar.create_event(
            summary="Aria Test Event",
            start_time=start_time,
            description="This is a test event created by Aria to verify calendar integration."
        )
        print(" SUCCESS: Event created")
        print(f"\n{result}")
    except Exception as e:
        print(f" ERROR: {e}")

def test_natural_language_parsing():
    """Test AI-powered natural language parsing for calendar events."""
    print("\n" + "=" * 60)
    print("TEST 4: Natural Language Parsing")
    print("=" * 60)
    
    try:
        brain = AriaBrain()
        
        test_commands = [
            "Schedule a meeting tomorrow at 3 PM",
            "Schedule dentist appointment next Friday at 10 AM",
            "Schedule team sync on Monday at 9:30 AM"
        ]
        
        for command in test_commands:
            print(f"\n Testing: \"{command}\"")
            result = brain.parse_calendar_intent(command)
            
            if result and result.get("summary"):
                print(f"    Parsed successfully:")
                print(f"      Title: {result.get('summary')}")
                print(f"      Start: {result.get('start_time')}")
                if result.get('end_time'):
                    print(f"      End: {result.get('end_time')}")
            else:
                print(f"    Failed to parse")
                
    except Exception as e:
        print(f" ERROR: {e}")

def main():
    print("\n" + " " * 20)
    print("GOOGLE CALENDAR INTEGRATION TEST")
    print(" " * 20 + "\n")
    
    # Test 1: Authentication
    calendar = test_calendar_authentication()
    
    # Test 2: Retrieve events
    test_event_retrieval(calendar)
    
    # Test 3: Create event
    test_event_creation(calendar)
    
    # Test 4: Natural language parsing
    test_natural_language_parsing()
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)
    print("\n TIP: Check your Google Calendar to verify the test event was created.")
    print(" TIP: If authentication opened a browser, make sure to grant permissions.\n")

if __name__ == "__main__":
    main()
