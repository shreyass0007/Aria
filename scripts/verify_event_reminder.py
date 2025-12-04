import sys
import os
import datetime
import time
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aria.proactive_manager import ProactiveManager

def test_event_reminder():
    print("Testing Event Reminder Logic...")
    
    # Mock dependencies
    mock_calendar = MagicMock()
    mock_tts = MagicMock()
    mock_brain = MagicMock()
    mock_app_launcher = MagicMock()
    
    # Setup ProactiveManager
    manager = ProactiveManager(
        calendar_manager=mock_calendar,
        system_control=MagicMock(),
        tts_manager=mock_tts,
        app_launcher=mock_app_launcher,
        brain=mock_brain,
        weather_manager=MagicMock()
    )
    
    # 1. Test Time Window (Should run now)
    print(f"Current time: {datetime.datetime.now()}")
    
    # 2. Mock an event starting in 2 minutes
    now = datetime.datetime.now()
    start_time = now + datetime.timedelta(minutes=2)
    end_time = now + datetime.timedelta(minutes=32)
    
    mock_event = {
        'id': 'test_event_123',
        'summary': 'Test Meeting with Team',
        'start': {'dateTime': start_time.isoformat()},
        'end': {'dateTime': end_time.isoformat()}
    }
    
    mock_calendar.get_upcoming_events_raw.return_value = [mock_event]
    
    # 3. Mock LLM response for "Smart Analysis"
    # The manager calls _analyze_and_trigger which calls the brain
    mock_llm = MagicMock()
    mock_brain.get_llm.return_value = mock_llm
    
    # Return a JSON string that triggers an action
    mock_llm.invoke.return_value.content = '{"action": "open_teams", "reason": "It is a team meeting"}'
    
    # 4. Run check_and_act
    print("Running check_and_act()...")
    manager.check_and_act()
    
    # 5. Verify results
    # Check if TTS spoke
    if mock_tts.speak.called:
        print("✅ TTS Speak called!")
        args = mock_tts.speak.call_args[0][0]
        print(f"   Spoke: '{args}'")
    else:
        print("❌ TTS Speak NOT called.")
        
    # Check if App Launcher triggered
    if mock_app_launcher.open_desktop_app.called:
        print("✅ App Launcher called!")
        args = mock_app_launcher.open_desktop_app.call_args[0][0]
        print(f"   App: '{args}'")
    else:
        print("❌ App Launcher NOT called.")

    # Verify Morning Briefing didn't run if it's afternoon
    if now.hour >= 11:
        # We can't easily check internal state without spying, but we can check if it spoke "Good morning"
        # The mock_tts.speak might have been called for the event, so we check call args
        for call in mock_tts.speak.call_args_list:
            if "Good morning" in call[0][0]:
                print("⚠️  Warning: Morning briefing triggered (might be expected if testing logic failed)")
        print("ℹ️  Checked morning briefing logic (should be skipped if > 11 AM)")

if __name__ == "__main__":
    test_event_reminder()
