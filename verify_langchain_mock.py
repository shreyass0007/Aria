import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.append(os.getcwd())

# We need to mock dotenv before importing brain because it calls load_dotenv() at module level
with patch('dotenv.load_dotenv'):
    from brain import AriaBrain

class TestAriaBrain(unittest.TestCase):
    @patch('brain.ChatGoogleGenerativeAI')
    def test_ask(self, mock_llm_class):
        # Setup mock
        mock_llm_instance = MagicMock()
        mock_llm_class.return_value = mock_llm_instance
        mock_response = MagicMock()
        mock_response.content = "I am Aria."
        mock_llm_instance.invoke.return_value = mock_response

        # Patch os.getenv to return a dummy key
        with patch.dict(os.environ, {"GEMINI_API_KEY": "dummy_key"}):
            brain = AriaBrain()
            
            # Test ask
            response = brain.ask("Who are you?")
            self.assertEqual(response, "I am Aria.")
            # Check if invoke was called
            args, _ = mock_llm_instance.invoke.call_args
            self.assertEqual(args[0], "Who are you?")

    @patch('brain.ChatGoogleGenerativeAI')
    def test_parse_calendar_intent(self, mock_llm_class):
        # Setup mock
        mock_llm_instance = MagicMock()
        mock_llm_class.return_value = mock_llm_instance
        mock_response = MagicMock()
        mock_response.content = '{"summary": "Meeting", "start_time": "2023-10-27T10:00:00"}'
        mock_llm_instance.invoke.return_value = mock_response

        with patch.dict(os.environ, {"GEMINI_API_KEY": "dummy_key"}):
            brain = AriaBrain()
            
            # Test parse_calendar_intent
            intent = brain.parse_calendar_intent("Schedule a meeting")
            self.assertEqual(intent['summary'], "Meeting")
            # Check if invoke was called with a prompt (string)
            args, _ = mock_llm_instance.invoke.call_args
            self.assertIn("Schedule a meeting", args[0])

if __name__ == '__main__':
    unittest.main()
