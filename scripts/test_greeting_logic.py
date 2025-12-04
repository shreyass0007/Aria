
import unittest
from unittest.mock import MagicMock, patch, mock_open
import datetime
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aria.greeting_service import GreetingService

class TestGreetingService(unittest.TestCase):
    def setUp(self):
        self.calendar_mock = MagicMock()
        self.service = GreetingService(self.calendar_mock)

    @patch('aria.greeting_service.datetime')
    @patch('builtins.open', new_callable=mock_open, read_data='{"last_briefing_date": "2025-12-01"}')
    @patch('aria.greeting_service.os.path.exists')
    def test_briefing_should_show_at_8am_new_day(self, mock_exists, mock_file, mock_datetime):
        # Setup: 8 AM, different date in file
        mock_exists.return_value = True
        
        # Mock datetime.now() to return 8 AM
        mock_now = MagicMock()
        mock_now.hour = 8
        mock_now.strftime.return_value = "2025-12-03"
        mock_datetime.datetime.now.return_value = mock_now
        mock_datetime.timezone = datetime.timezone
        mock_datetime.timedelta = datetime.timedelta

        # Test
        should_show = self.service.check_and_update_briefing_status()
        print(f"Test 8AM New Day: {should_show}")
        self.assertTrue(should_show)

    @patch('aria.greeting_service.datetime')
    def test_briefing_should_not_show_at_11am(self, mock_datetime):
        # Setup: 11 AM
        mock_now = MagicMock()
        mock_now.hour = 11
        mock_datetime.datetime.now.return_value = mock_now
        mock_datetime.timezone = datetime.timezone
        mock_datetime.timedelta = datetime.timedelta

        # Test
        should_show = self.service.check_and_update_briefing_status()
        print(f"Test 11AM: {should_show}")
        self.assertFalse(should_show)

    @patch('aria.greeting_service.datetime')
    @patch('builtins.open', new_callable=mock_open, read_data='{"last_briefing_date": "2025-12-03"}')
    @patch('aria.greeting_service.os.path.exists')
    def test_briefing_should_not_show_if_already_shown(self, mock_exists, mock_file, mock_datetime):
        # Setup: 8 AM, SAME date in file
        mock_exists.return_value = True
        
        mock_now = MagicMock()
        mock_now.hour = 8
        mock_now.strftime.return_value = "2025-12-03" # Same as file
        mock_datetime.datetime.now.return_value = mock_now
        mock_datetime.timezone = datetime.timezone
        mock_datetime.timedelta = datetime.timedelta

        # Test
        should_show = self.service.check_and_update_briefing_status()
        print(f"Test 8AM Already Shown: {should_show}")
        self.assertFalse(should_show)

if __name__ == '__main__':
    unittest.main()
