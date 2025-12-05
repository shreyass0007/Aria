import unittest
from unittest.mock import MagicMock
import datetime
from aria.handlers.system_handler import SystemHandler

class TestDateTime(unittest.TestCase):
    def setUp(self):
        self.mock_tts = MagicMock()
        self.mock_sys_control = MagicMock()
        self.mock_clipboard = MagicMock()
        self.mock_monitor = MagicMock()
        self.handler = SystemHandler(
            self.mock_tts, 
            self.mock_sys_control, 
            self.mock_clipboard, 
            self.mock_monitor
        )

    def test_date_check(self):
        # Test that date_check returns a string containing the current year
        result = self.handler.handle("", "date_check", {})
        now = datetime.datetime.now()
        expected_year = str(now.year)
        expected_month = now.strftime("%B")
        
        print(f"Date Check Result: {result}")
        self.assertIn(expected_year, result)
        self.assertIn(expected_month, result)
        self.mock_tts.speak.assert_called()

    def test_time_check(self):
        # Test that time_check returns a string
        result = self.handler.handle("", "time_check", {})
        print(f"Time Check Result: {result}")
        self.assertIsNotNone(result)
        self.mock_tts.speak.assert_called()

if __name__ == '__main__':
    unittest.main()
