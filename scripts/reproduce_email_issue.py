import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import threading

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock threading to prevent background threads
threading.Thread = MagicMock()

from aria_core import AriaCore

class TestEmailLogic(unittest.TestCase):
    @patch('aria_core.AriaBrain')
    @patch('aria_core.SpeechEngine')
    @patch('aria_core.AriaCore.speak') # Mock speak to prevent TTS
    @patch('aria_core.AriaCore.check_microphones') # Mock mic check
    def test_email_ui_action(self, MockCheckMics, MockSpeak, MockSpeechEngine, MockAriaBrain):
        # Setup mocks
        mock_brain = MockAriaBrain.return_value
        mock_brain.is_available.return_value = True
        
        # Initialize Core
        aria = AriaCore()
        
        # Mock the classifier attached to aria
        aria.command_classifier.classify_intent = MagicMock(return_value={
            "intent": "email_send",
            "confidence": 0.9,
            "parameters": {}
        })
        
        # Mock brain methods
        mock_brain.parse_email_intent.return_value = {
            "to": "test@example.com",
            "subject": "Test Subject",
            "body": "Hello world"
        }
        mock_brain.generate_email_draft.return_value = "Hi Test,\n\nHello world\n\nBest, User"
        
        # Execute command
        print("Executing command...")
        aria.process_command("send email to test@example.com about Test Subject saying Hello world")
        
        # Check if UI action was set
        self.assertIsNotNone(aria.last_ui_action)
        self.assertEqual(aria.last_ui_action['type'], 'email_confirmation')
        self.assertEqual(aria.last_ui_action['data']['to'], 'test@example.com')
        print("SUCCESS: UI Action set correctly!")
        print(aria.last_ui_action)

if __name__ == '__main__':
    unittest.main()
