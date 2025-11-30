import datetime
import time
from unittest.mock import MagicMock
from proactive_manager import ProactiveManager

# Mock Dependencies
mock_calendar = MagicMock()
mock_tts = MagicMock()
mock_launcher = MagicMock()

# Setup Manager
manager = ProactiveManager(mock_calendar, mock_tts, mock_launcher)

# Mock Event: Zoom Meeting starting in 2 minutes
now = datetime.datetime.now(datetime.timezone.utc)
start = now + datetime.timedelta(minutes=2)
end = now + datetime.timedelta(minutes=32)

mock_event = {
    'id': 'test_event_1',
    'summary': 'Important Zoom Meeting',
    'start': {'dateTime': start.isoformat().replace('+00:00', 'Z')},
    'end': {'dateTime': end.isoformat().replace('+00:00', 'Z')}
}

mock_calendar.get_upcoming_events_raw.return_value = [mock_event]

print("--- Testing Proactive Actions ---")
print(f"Current Time (UTC): {now}")
print(f"Event Start (UTC): {start}")

# Run Check
manager.check_and_act()

# Verify Actions
print("\nVerifying Actions...")

# 1. TTS Announcement
if mock_tts.speak.called:
    print(f"[SUCCESS] TTS Spoke: {mock_tts.speak.call_args[0][0]}")
else:
    print("[FAIL] TTS did not speak.")

# 2. App Launch
if mock_launcher.open_desktop_app.called:
    app_name = mock_launcher.open_desktop_app.call_args[0][0]
    print(f"[SUCCESS] App Launcher called for: {app_name}")
    if app_name == "zoom":
        print("[SUCCESS] Correct app 'zoom' selected.")
    else:
        print(f"[FAIL] Wrong app selected: {app_name}")
else:
    print("[FAIL] App Launcher was not called.")
