
import sys
import os
import unittest
from unittest.mock import MagicMock

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aria.command_processor import CommandProcessor

class TestCommandProcessor(unittest.TestCase):
    def setUp(self):
        # Mock all dependencies
        self.tts_manager = MagicMock()
        self.app_launcher = MagicMock()
        self.brain = MagicMock()
        self.calendar = MagicMock()
        self.notion = MagicMock()
        self.automator = MagicMock()
        self.system_control = MagicMock()
        self.command_classifier = MagicMock()
        self.file_manager = MagicMock()
        self.weather_manager = MagicMock()
        self.clipboard_screenshot = MagicMock()
        self.system_monitor = MagicMock()
        self.email_manager = MagicMock()
        self.greeting_service = MagicMock()
        self.music_manager = MagicMock()
        
        # Setup return values for mocks to avoid NoneType errors
        self.music_manager.play_music.return_value = "Playing music"
        self.music_manager.pause.return_value = "Paused"
        self.music_manager.resume.return_value = "Resumed"
        self.music_manager.stop.return_value = "Stopped"
        self.music_manager.set_volume.return_value = "Volume set"
        
        self.system_control.lock_system.return_value = "System locked"
        self.system_control.minimize_all_windows.return_value = "Windows minimized"
        self.system_control.increase_volume.return_value = "Volume up"
        
        self.clipboard_screenshot.take_screenshot.return_value = "Screenshot taken"
        
        self.email_manager.get_unread_emails.return_value = "No unread emails"
        
        self.brain.ask.return_value = "LLM Response"
        
        # Instantiate CommandProcessor with mocks
        self.cp = CommandProcessor(
            self.tts_manager, self.app_launcher, self.brain, self.calendar, 
            self.notion, self.automator, self.system_control, self.command_classifier, 
            self.file_manager, self.weather_manager, self.clipboard_screenshot, 
            self.system_monitor, self.email_manager, self.greeting_service, 
            self.music_manager
        )

    def test_all_intents(self):
        test_cases = [
            ("shutdown", "shutdown computer", None),
            ("restart", "restart computer", None),
            ("lock", "lock screen", None),
            ("sleep", "sleep computer", None),
            ("focus_mode_on", "turn on focus mode", None),
            ("focus_mode_off", "turn off focus mode", None),
            ("minimize_all", "minimize all windows", None),
            ("volume_up", "volume up", None),
            ("volume_down", "volume down", None),
            ("volume_mute", "mute", None),
            ("volume_unmute", "unmute", None),
            ("screenshot_take", "take screenshot", None),
            ("clipboard_copy", "copy this", None),
            ("clipboard_read", "read clipboard", None),
            ("clipboard_clear", "clear clipboard", None),
            ("battery_check", "check battery", None),
            ("time_check", "what time is it", None),
            ("date_check", "what date is it", None),
            ("weather_check", "check weather", None),
            ("app_open", "open notepad", None),
            ("web_search", "search for cats", None),
            ("music_play", "play music", "music_playing"),
            ("music_pause", "pause music", None),
            ("music_resume", "resume music", None),
            ("music_stop", "stop music", None),
            ("email_check", "check emails", None),
            ("general_chat", "hello", None)
        ]
        
        print(f"\nTesting {len(test_cases)} intents...")
        failures = []
        
        for intent, text, expected_ui_type in test_cases:
            print(f"Testing {intent}...", end="")
            
            intent_data = {
                "intent": intent,
                "confidence": 1.0,
                "parameters": {"app_name": "notepad", "query": "cats", "song": "test song"}
            }
            
            try:
                self.cp.last_ui_action = None
                response = self.cp.process_command(text, intent_data=intent_data)
                
                if not isinstance(response, str) and not isinstance(response, MagicMock):
                    print(f" FAIL (Type: {type(response)})")
                    failures.append(f"{intent}: Returned {type(response)}")
                    continue
                    
                if not response:
                    print(f" FAIL (Empty)")
                    failures.append(f"{intent}: Returned empty string")
                    continue
                    
                if expected_ui_type:
                    if not self.cp.last_ui_action or self.cp.last_ui_action.get("type") != expected_ui_type:
                        print(f" FAIL (UI Action)")
                        failures.append(f"{intent}: Missing/Wrong UI action")
                        continue
                        
                print(" PASS")
            except Exception as e:
                print(f" ERROR ({e})")
                failures.append(f"{intent}: Exception {e}")
                
        if failures:
            print(f"\nFAILED: {len(failures)} intents failed.")
            for f in failures:
                print(f"- {f}")
            sys.exit(1)
        else:
            print("\nSUCCESS: All intents verified!")
            sys.exit(0)

if __name__ == "__main__":
    unittest.main()
