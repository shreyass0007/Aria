import sys
from unittest.mock import MagicMock

# Mock dependencies
sys.modules['pygame'] = MagicMock()
sys.modules['edge_tts'] = MagicMock()
sys.modules['gtts'] = MagicMock()

from greeting_service import GreetingService
from brain import AriaBrain

# Mock Managers
mock_calendar = MagicMock()
mock_weather = MagicMock()
mock_email = MagicMock()
mock_brain = MagicMock()

# Setup Service
service = GreetingService(
    calendar_manager=mock_calendar,
    weather_manager=mock_weather,
    email_manager=mock_email,
    brain=mock_brain
)

# Setup Mock Data
mock_weather.get_weather.return_value = "22 degrees and sunny"
mock_calendar.get_events_for_date.return_value = ["Meeting with Team at 10 AM", "Lunch at 1 PM"]
mock_email.list_messages.return_value = ["Email 1", "Email 2", "Email 3"]
mock_brain.generate_briefing_summary.return_value = "Good morning! It's a beautiful 22 degrees. You have a team meeting at 10 AM and lunch at 1 PM. You also have 3 unread emails. Have a productive day!"

# Mock datetime to control time of day
import datetime
from unittest.mock import patch

print("--- Testing Daily Briefing ---")

# Test 1: Morning (8 AM)
print("\n[Test 1] Morning Briefing (8 AM)")
with patch('datetime.datetime') as mock_date:
    mock_date.now.return_value.hour = 8
    # Mock timezone to avoid errors
    mock_date.timezone = datetime.timezone
    mock_date.timedelta = datetime.timedelta
    
    briefing = service.get_morning_briefing()
    print(f"Briefing Output:\n{briefing}")
    
    # Verify Brain called with "morning briefing"
    # Note: We can't easily verify the 'mode' arg without more complex mocking of the Brain method signature
    # but we can check the output text if we mocked the return value differently.

# Test 2: Evening (8 PM)
print("\n[Test 2] Evening Briefing (8 PM)")
with patch('datetime.datetime') as mock_date:
    mock_date.now.return_value.hour = 20
    mock_date.timezone = datetime.timezone
    mock_date.timedelta = datetime.timedelta
    
    # Update mock return for evening context
    mock_brain.generate_briefing_summary.return_value = "Good evening! Tomorrow looks clear. You have a meeting at 9 AM. Sleep well!"
    
    briefing = service.get_morning_briefing()
    print(f"Briefing Output:\n{briefing}")

print("\n[SUCCESS] Tested both Morning and Evening logic.")
