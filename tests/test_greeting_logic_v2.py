import unittest
from unittest.mock import MagicMock, patch
import datetime
import json
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aria.greeting_service import GreetingService

class TestGreetingLogicV2(unittest.TestCase):
    def setUp(self):
        self.calendar_mock = MagicMock()
        self.weather_mock = MagicMock()
        self.email_mock = MagicMock()
        self.brain_mock = MagicMock()
        
        self.service = GreetingService(
            calendar_manager=self.calendar_mock,
            weather_manager=self.weather_mock,
            email_manager=self.email_mock,
            brain=self.brain_mock
        )
        
        # Clean up state file
        if os.path.exists("briefing_state.json"):
            os.remove("briefing_state.json")

    def tearDown(self):
        if os.path.exists("briefing_state.json"):
            os.remove("briefing_state.json")

    @patch('greeting_service.datetime')
    def test_morning_first_run(self, mock_datetime):
        # Simulate 7 AM
        mock_now = datetime.datetime(2023, 10, 27, 7, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now
        mock_datetime.timezone = datetime.timezone
        mock_datetime.timedelta = datetime.timedelta

        # Mock brain response
        self.brain_mock.generate_briefing_summary.return_value = "Detailed Morning Briefing"

        # First call should return briefing
        result = self.service.get_morning_briefing()
        self.assertEqual(result, "Detailed Morning Briefing")
        
        # Verify state file created
        self.assertTrue(os.path.exists("briefing_state.json"))
        with open("briefing_state.json", "r") as f:
            state = json.load(f)
            self.assertEqual(state["last_briefing_date"], "2023-10-27")

    @patch('greeting_service.datetime')
    def test_morning_second_run(self, mock_datetime):
        # Simulate 7 AM
        mock_now = datetime.datetime(2023, 10, 27, 7, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now
        mock_datetime.timezone = datetime.timezone
        mock_datetime.timedelta = datetime.timedelta

        # Create state file simulating already shown
        with open("briefing_state.json", "w") as f:
            json.dump({"last_briefing_date": "2023-10-27"}, f)

        # Second call should return None
        result = self.service.get_morning_briefing()
        self.assertIsNone(result)

    @patch('greeting_service.datetime')
    def test_afternoon_run(self, mock_datetime):
        # Simulate 2 PM (14:00)
        mock_now = datetime.datetime(2023, 10, 27, 14, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now
        mock_datetime.timezone = datetime.timezone
        mock_datetime.timedelta = datetime.timedelta

        # Should return None regardless of state
        result = self.service.get_morning_briefing()
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
