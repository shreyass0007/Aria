import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from command_processor import CommandProcessor

class TestSearchIntegration(unittest.TestCase):
    def setUp(self):
        # Mock dependencies
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
        
        # Initialize CommandProcessor
        self.cp = CommandProcessor(
            self.tts_manager, self.app_launcher, self.brain, self.calendar, 
            self.notion, self.automator, self.system_control, self.command_classifier, 
            self.file_manager, self.weather_manager, self.clipboard_screenshot, 
            self.system_monitor, self.email_manager, self.greeting_service, self.music_manager
        )
        
        # Mock SearchManager inside CommandProcessor
        self.cp.search_manager = MagicMock()

    def test_web_search_intent(self):
        print("\nTesting 'web_search' intent...")
        
        # Setup
        query = "who won the super bowl 2024"
        intent_data = {
            "intent": "web_search",
            "confidence": 0.9,
            "parameters": {"query": query}
        }
        
        # Mock Search Results
        mock_results = "## Search Results:\n1. **Chiefs win Super Bowl**\n   The Kansas City Chiefs defeated the San Francisco 49ers..."
        self.cp.search_manager.search.return_value = mock_results
        
        # Mock Brain Response
        mock_answer = "The Kansas City Chiefs won the Super Bowl in 2024."
        self.cp.brain.ask.return_value = mock_answer
        
        # Execute
        self.cp.process_command("search for who won the super bowl", intent_data=intent_data)
        
        # Verify Search Called
        self.cp.search_manager.search.assert_called_with(query)
        print("✓ SearchManager.search called correctly")
        
        # Verify Context Stored
        self.assertEqual(self.cp.last_search_context, mock_results)
        print("✓ Search context stored correctly")
        
        # Verify Brain Called with Context
        self.cp.brain.ask.assert_called()
        call_args = self.cp.brain.ask.call_args
        self.assertIn(query, call_args[0][0]) # Query in prompt
        self.assertEqual(call_args[1]['search_context'], mock_results) # Context passed
        print("✓ Brain.ask called with search_context")
        
        # Verify TTS
        self.cp.tts_manager.speak.assert_any_call(mock_answer)
        print("✓ TTS spoke the answer")

    def test_follow_up_question(self):
        print("\nTesting follow-up question (context retention)...")
        
        # Setup Context
        mock_context = "Previous search results about Super Bowl..."
        self.cp.last_search_context = mock_context
        
        # Execute General Chat (Fallback)
        user_text = "what was the score?"
        self.cp.command_classifier.classify_intent.return_value = {"intent": "general_chat"}
        
        self.cp.process_command(user_text)
        
        # Verify Brain Called with Context
        self.cp.brain.ask.assert_called()
        call_args = self.cp.brain.ask.call_args
        self.assertEqual(call_args[1]['search_context'], mock_context)
        print("✓ Brain.ask called with stored search_context for follow-up")

if __name__ == "__main__":
    unittest.main()
