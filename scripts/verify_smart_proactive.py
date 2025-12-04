import sys
import os
import datetime
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from proactive_manager import ProactiveManager

def test_smart_proactive():
    print("--- Testing Smart Proactive Intelligence ---")
    
    # Mock dependencies
    mock_calendar = MagicMock()
    mock_system = MagicMock()
    mock_tts = MagicMock()
    mock_launcher = MagicMock()
    mock_brain = MagicMock()
    mock_weather = MagicMock()
    
    # Setup Weather Mock
    mock_weather.get_weather_summary.return_value = "It's sunny and 25 degrees."
    
    # Setup LLM Mock
    mock_llm = MagicMock()
    mock_brain.get_llm.return_value = mock_llm
    # Simulate LLM response for "Project Sync" -> "open_vscode"
    mock_llm.invoke.return_value.content = '{"action": "open_vscode", "reason": "Project work implies coding"}'
    
    # Create Manager
    manager = ProactiveManager(mock_calendar, mock_system, mock_tts, mock_launcher, mock_brain, mock_weather)
    
    # 1. Test Time Restriction (Outside Window)
    print("\n[Test 1] Time Restriction (11:00 AM)")
    # Create a real datetime object for 11 AM
    dt_11am = datetime.datetime(2023, 10, 27, 11, 0, 0)
    
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = dt_11am
        # We also need to mock side_effect for other calls if necessary, but return_value should work for .now()
        # However, datetime is immutable C-extension, so patching it is tricky.
        # Better approach: Patch the module where it's used, OR use freezegun (but we don't have it).
        # Let's try patching ProactiveManager's datetime usage if possible, or just ensure the mock works.
        
        # The issue is likely that 'datetime.datetime' class itself is mocked, so isinstance checks might fail 
        # or .now() isn't behaving as expected if not configured right.
        
        # Let's try a simpler approach: Mocking the method in the class is hard because it calls datetime.datetime.now() directly.
        # We will use a wrapper class for the mock.
        
        mock_datetime.now.return_value = dt_11am
        mock_datetime.side_effect = lambda *args, **kwargs: datetime.datetime(*args, **kwargs)
        
        manager.check_and_act()
        
        # Should NOT call weather or calendar
        mock_weather.get_weather_summary.assert_not_called()
        mock_calendar.get_upcoming_events_raw.assert_not_called()
        print("✅ Correctly ignored check outside 7-10 AM window.")

    # 2. Test Morning Briefing (Inside Window)
    print("\n[Test 2] Morning Briefing (8:00 AM)")
    dt_8am = datetime.datetime(2023, 10, 27, 8, 0, 0)
    
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = dt_8am
        mock_datetime.side_effect = lambda *args, **kwargs: datetime.datetime(*args, **kwargs)
        
        # Setup Calendar to return empty for now
        mock_calendar.get_upcoming_events_raw.return_value = []
        
        manager.check_and_act()
        
        # Should call weather
        mock_weather.get_weather_summary.assert_called_once()
        mock_tts.speak.assert_any_call("Good morning. It's sunny and 25 degrees.")
        print("✅ Correctly announced weather.")
        
        # Should NOT announce again if called immediately
        mock_weather.get_weather_summary.reset_mock()
        manager.check_and_act()
        mock_weather.get_weather_summary.assert_not_called()
        print("✅ Correctly skipped duplicate announcement.")

    # 3. Test Smart Event Analysis
    print("\n[Test 3] Smart Event Analysis")
    
    # We need to be careful with datetime arithmetic and mocks.
    # Instead of patching datetime.datetime globally which breaks arithmetic,
    # let's patch the ProactiveManager's _parse_dt method or just ensure the mock behaves.
    
    # A cleaner way for this specific test is to rely on the fact that we can control the inputs.
    # But since the code calls datetime.datetime.now(), we must patch it.
    
    with patch('datetime.datetime') as mock_datetime:
        # Configure the mock to behave like our fixed datetime
        mock_datetime.now.return_value = dt_8am
        mock_datetime.side_effect = lambda *args, **kwargs: datetime.datetime(*args, **kwargs)
        mock_datetime.fromisoformat = datetime.datetime.fromisoformat
        
        # IMPORTANT: When we do (start_dt - now), if 'now' is a MagicMock, it returns a MagicMock.
        # But our code expects a timedelta with .total_seconds().
        # The issue is that even with return_value set, sometimes the class mock interferes.
        
        # Let's try to make the mock return a real datetime object that we control.
        # We already did that with `return_value = dt_8am`.
        # The error suggests `time_until_start` calculation failed.
        
        # Let's mock the _parse_dt method of the manager to return a compatible object
        # OR just ensure that the event start time is compatible with the mocked now.
        
        event_start = dt_8am + datetime.timedelta(minutes=2)
        
        # We need to ensure that when the code calls datetime.datetime.now(), it gets dt_8am.
        # And when it subtracts, it works.
        
        # Let's try to patch the module level datetime in proactive_manager directly if possible?
        # No, it imports datetime.
        
        # Let's just mock the _parse_dt method to return a datetime that works with the mocked now.
        # Actually, if we just set the return value correctly, it should work.
        # The previous error was likely because `start_dt` was real but `now` was a Mock (or vice versa) in a way that failed.
        
        # Let's force the manager to use our time.
        # We can subclass/override for testing.
        
        # Override check_and_act's internal now? No.
        
        # Let's try this:
        # We will mock the `_parse_dt` to return a time that is 2 minutes ahead of `dt_8am`.
        # And we ensure `datetime.datetime.now()` returns `dt_8am`.
        
        mock_datetime.now.return_value = dt_8am
        
        # Mock an event
        mock_event = {
            'id': '123',
            'summary': 'Project Delta Sync',
            'start': {'dateTime': event_start.isoformat()}
        }
        mock_calendar.get_upcoming_events_raw.return_value = [mock_event]
        
        # We need to ensure that `start_dt - now` works. 
        # If `now` comes from the mock, it might be a MagicMock object if the patch isn't perfect.
        # But we set return_value to a real datetime.
        
        # The traceback showed "MagicMock" in the error, implying one operand was a mock.
        # This happens if `datetime.datetime` is mocked, then `datetime.datetime.now()` is called.
        
        # Let's try to use `wraps` to preserve real datetime behavior for everything except `now`.
        mock_datetime.now.return_value = dt_8am
        
        # Force the event loop to run
        manager.check_and_act()
        
        # Should call LLM
        mock_llm.invoke.assert_called()
        # Should trigger VS Code
        mock_launcher.open_desktop_app.assert_called_with("code")
        print("✅ Correctly used LLM to identify 'Project Sync' -> VS Code.")

if __name__ == "__main__":
    test_smart_proactive()
