
import sys
import os
import unittest
from unittest.mock import MagicMock

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aria.aria_core import AriaCore
from aria.command_intent_classifier import CommandIntentClassifier

class TestAriaIntents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Initializing AriaCore for testing...")
        # Mock dependencies to prevent real actions
        cls.aria = AriaCore()
        
        # MOCK EVERYTHING DANGEROUS OR NOISY
        cls.aria.tts_manager.speak = MagicMock()
        cls.aria.system_control.shutdown_system = MagicMock(return_value="System would shutdown")
        cls.aria.system_control.restart_system = MagicMock(return_value="System would restart")
        cls.aria.system_control.lock_system = MagicMock(return_value="System would lock")
        cls.aria.system_control.sleep_system = MagicMock(return_value="System would sleep")
        cls.aria.system_control.minimize_all_windows = MagicMock(return_value="Windows minimized")
        cls.aria.system_control.set_dnd = MagicMock(return_value="DND set")
        cls.aria.system_control.increase_volume = MagicMock(return_value="Volume up")
        cls.aria.system_control.decrease_volume = MagicMock(return_value="Volume down")
        cls.aria.system_control.set_volume = MagicMock(return_value="Volume set")
        cls.aria.system_control.mute = MagicMock(return_value="Muted")
        cls.aria.system_control.unmute = MagicMock(return_value="Unmuted")
        
        cls.aria.music_manager.play_music = MagicMock(return_value="Playing music")
        cls.aria.music_manager.pause = MagicMock(return_value="Paused")
        cls.aria.music_manager.resume = MagicMock(return_value="Resumed")
        cls.aria.music_manager.stop = MagicMock(return_value="Stopped")
        cls.aria.music_manager.set_volume = MagicMock(return_value="Volume set")
        
        cls.aria.app_launcher.open_desktop_app = MagicMock(return_value=True)
        cls.aria.clipboard_screenshot.take_screenshot = MagicMock(return_value="Screenshot taken")
        cls.aria.email_manager.send_email = MagicMock(return_value="Email sent")
        cls.aria.email_manager.get_unread_emails = MagicMock(return_value="No unread emails")
        
        # Mock Brain/LLM to avoid API calls and ensure deterministic classification
        # We will manually inject intent_data for testing process_command logic
        cls.aria.brain.ask = MagicMock(return_value="LLM Response")

    def test_intent_processing(self):
        """Test that process_command handles every intent correctly."""
        
        # List of intents to test with sample inputs
        # Format: (intent_name, sample_text, expected_ui_action_type)
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
            ("app_open", "open notepad", None), # Should return string
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
            print(f"Testing intent: {intent}...", end="")
            
            # Manually construct intent data to bypass classifier and test processor logic directly
            intent_data = {
                "intent": intent,
                "confidence": 1.0,
                "parameters": {"app_name": "notepad", "query": "cats", "song": "test song"}
            }
            
            try:
                # Clear previous UI action
                self.aria.command_processor.last_ui_action = None
                
                response = self.aria.command_processor.process_command(
                    text=text,
                    intent_data=intent_data
                )
                
                # CHECK 1: Response must be a string
                if not isinstance(response, str):
                    print(f" FAIL (Invalid return type: {type(response)})")
                    failures.append(f"{intent}: Returned {type(response)} instead of str")
                    continue
                    
                # CHECK 2: Response must not be empty
                if not response:
                    print(f" FAIL (Empty response)")
                    failures.append(f"{intent}: Returned empty string")
                    continue
                
                # CHECK 3: UI Action (if expected)
                if expected_ui_type:
                    ui_action = self.aria.command_processor.last_ui_action
                    if not ui_action:
                        print(f" FAIL (Missing UI action)")
                        failures.append(f"{intent}: Missing UI action")
                        continue
                    if ui_action.get("type") != expected_ui_type:
                        print(f" FAIL (Wrong UI type: {ui_action.get('type')})")
                        failures.append(f"{intent}: Wrong UI type")
                        continue
                
                print(" PASS")
                
            except Exception as e:
                print(f" ERROR ({e})")
                failures.append(f"{intent}: Raised exception {e}")

        print("\n" + "="*40)
        if failures:
            print(f"FAILED: {len(failures)} intents failed.")
            for f in failures:
                print(f"- {f}")
            sys.exit(1)
        else:
            print("SUCCESS: All intents verified successfully!")
            sys.exit(0)

if __name__ == "__main__":
    # Run the test manually
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAriaIntents)
    unittest.TextTestRunner(verbosity=0).run(suite)
