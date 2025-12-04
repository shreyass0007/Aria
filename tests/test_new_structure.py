import sys
import os
import unittest

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestNewStructure(unittest.TestCase):
    def test_imports(self):
        """Test that all modules can be imported from their new locations."""
        try:
            from aria.aria_core import AriaCore
            from aria.brain import AriaBrain
            from aria.command_processor import CommandProcessor
            from aria.command_intent_classifier import CommandIntentClassifier
            from aria.calendar_manager import CalendarManager
            from aria.notion_manager import NotionManager
            from aria.email_manager import EmailManager
            from aria.music_library import MusicManager
            from aria.system_control import SystemControl
            from aria.system_monitor import SystemMonitor
            from aria.tts_manager import TTSManager
            from aria.speech_input import SpeechInput
            from aria.app_launcher import AppLauncher
            from aria.file_manager import FileManager
            from aria.weather_manager import WeatherManager
            from aria.clipboard_screenshot import ClipboardScreenshot
            from aria.proactive_manager import ProactiveManager
            from aria.greeting_service import GreetingService
            
            print("All aria modules imported successfully.")
        except ImportError as e:
            self.fail(f"Import failed: {e}")

    def test_backend_imports(self):
        """Test that backend modules can be imported."""
        try:
            from backend.main import app
            from backend.dependencies import init_dependencies
            from backend.routers import chat, voice, music, system, notion, general
            
            print("All backend modules imported successfully.")
        except ImportError as e:
            self.fail(f"Backend import failed: {e}")

if __name__ == '__main__':
    unittest.main()
