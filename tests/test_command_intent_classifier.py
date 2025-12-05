import unittest
from unittest.mock import MagicMock, patch
from aria.command_intent_classifier import CommandIntentClassifier

class TestCommandIntentClassifier(unittest.TestCase):
    def setUp(self):
        self.mock_brain = MagicMock()
        self.classifier = CommandIntentClassifier(self.mock_brain)

    def test_fast_path_exact_match(self):
        # Test exact match fast path
        result = self.classifier.classify_intent("volume up")
        self.assertEqual(result["intent"], "volume_up")
        self.assertEqual(result["confidence"], 1.0)

    def test_fast_path_regex_volume(self):
        # Test regex fast path for volume
        result = self.classifier.classify_intent("set volume to 50")
        self.assertEqual(result["intent"], "volume_set")
        self.assertEqual(result["parameters"]["level"], 50)
        self.assertEqual(result["confidence"], 1.0)

        result = self.classifier.classify_intent("vset volume 20")
        self.assertEqual(result["intent"], "volume_set")
        self.assertEqual(result["parameters"]["level"], 20)
        self.assertEqual(result["confidence"], 1.0)

    def test_llm_classification_success(self):
        # Mock LLM response
        self.mock_brain.is_available.return_value = True
        mock_llm = MagicMock()
        self.mock_brain.get_llm.return_value = mock_llm
        
        # Mock invoke response
        mock_response = MagicMock()
        mock_response.content = '{"intent": "weather_check", "confidence": 0.9, "parameters": {"city": "Paris"}}'
        mock_llm.invoke.return_value = mock_response

        result = self.classifier.classify_intent("what is the weather in Paris")
        
        self.assertEqual(result["intent"], "weather_check")
        self.assertEqual(result["parameters"]["city"], "Paris")
        self.assertEqual(result["confidence"], 0.9)

    def test_llm_classification_fallback(self):
        # Mock LLM unavailable
        self.mock_brain.is_available.return_value = False
        
        result = self.classifier.classify_intent("some complex command")
        self.assertEqual(result["intent"], "none")

    def test_llm_classification_json_error(self):
        # Mock LLM returning bad JSON
        self.mock_brain.is_available.return_value = True
        mock_llm = MagicMock()
        self.mock_brain.get_llm.return_value = mock_llm
        
        mock_response = MagicMock()
        mock_response.content = 'This is not JSON'
        mock_llm.invoke.return_value = mock_response

        result = self.classifier.classify_intent("some command")
        self.assertEqual(result["intent"], "general_chat")

if __name__ == "__main__":
    unittest.main()
