import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest.mock import MagicMock, patch
from aria.command_processor import CommandProcessor
from aria.handlers.music_handler import MusicHandler
from aria.handlers.system_handler import SystemHandler

class TestCommandDispatch(unittest.TestCase):
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
        self.water_manager = MagicMock()

        self.processor = CommandProcessor(
            self.tts_manager, self.app_launcher, self.brain, self.calendar,
            self.notion, self.automator, self.system_control, self.command_classifier,
            self.file_manager, self.weather_manager, self.clipboard_screenshot,
            self.system_monitor, self.email_manager, self.greeting_service,
            self.music_manager, self.water_manager
        )

    def test_music_handler_dispatch(self):
        # Test that music intents are routed to MusicHandler
        intent_data = {"intent": "music_play", "confidence": 0.9, "parameters": {"song": "Test Song"}}
        
        # We can't easily mock the internal handler instance without patching, 
        # but we can check if the underlying manager was called.
        
        self.processor.process_command("play music", intent_data=intent_data)
        
        # Verify music manager was called
        self.music_manager.play_music.assert_called()

    def test_system_handler_dispatch(self):
        # Test that system intents are routed to SystemHandler
        intent_data = {"intent": "volume_up", "confidence": 0.9, "parameters": {}}
        
        self.processor.process_command("volume up", intent_data=intent_data)
        
        # Verify system control was called
        self.system_control.increase_volume.assert_called()

    def test_system_handler_monitoring(self):
        # Test monitoring dispatch
        intent_data = {"intent": "cpu_check", "confidence": 0.9, "parameters": {}}
        self.system_monitor.get_cpu_usage.return_value = 50
        
        self.processor.process_command("check cpu", intent_data=intent_data)
        
        self.system_monitor.get_cpu_usage.assert_called()
        self.tts_manager.speak.assert_called()

if __name__ == '__main__':
    unittest.main()
