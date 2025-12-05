import unittest
from unittest.mock import MagicMock
from aria.intent_dispatcher import IntentDispatcher

class TestIntentDispatcher(unittest.TestCase):
    def setUp(self):
        self.dispatcher = IntentDispatcher()

    def test_register_handler(self):
        mock_handler = MagicMock()
        self.dispatcher.register_handler("test_intent", mock_handler)
        self.assertIn("test_intent", self.dispatcher.handlers)
        self.assertEqual(self.dispatcher.handlers["test_intent"], mock_handler)

    def test_dispatch_success(self):
        mock_handler = MagicMock(return_value="Success")
        mock_handler.__name__ = "mock_handler"
        self.dispatcher.register_handler("test_intent", mock_handler)
        
        result = self.dispatcher.dispatch("test_intent", "some text", {"param": 1})
        
        mock_handler.assert_called_once_with("some text", "test_intent", {"param": 1})
        self.assertEqual(result, "Success")

    def test_dispatch_no_handler(self):
        result = self.dispatcher.dispatch("unknown_intent", "text")
        self.assertIsNone(result)

    def test_dispatch_handler_error(self):
        mock_handler = MagicMock(side_effect=Exception("Test Error"))
        mock_handler.__name__ = "mock_handler_error"
        self.dispatcher.register_handler("error_intent", mock_handler)
        
        result = self.dispatcher.dispatch("error_intent", "text")
        
        self.assertTrue(result.startswith("I encountered an error"))
        self.assertIn("Test Error", result)

if __name__ == "__main__":
    unittest.main()
