import unittest
from unittest.mock import MagicMock, patch
import datetime
from aria.deep_work_manager import DeepWorkManager

class TestDeepWorkManager(unittest.TestCase):
    def setUp(self):
        self.mock_calendar = MagicMock()
        self.mock_tts = MagicMock()
        self.manager = DeepWorkManager(self.mock_calendar, self.mock_tts)

    @patch('deep_work_manager.winreg')
    @patch('deep_work_manager.ctypes')
    def test_activate_deep_work(self, mock_ctypes, mock_winreg):
        # Setup mock event
        now = datetime.datetime.now(datetime.timezone.utc)
        start = now - datetime.timedelta(minutes=10)
        end = now + datetime.timedelta(minutes=50)
        
        self.mock_calendar.get_upcoming_events_raw.return_value = [{
            'summary': 'DBMS-focus session',
            'start': {'dateTime': start.isoformat().replace('+00:00', 'Z')},
            'end': {'dateTime': end.isoformat().replace('+00:00', 'Z')}
        }]

        # Run check
        self.manager.check_and_activate()

        # Verify
        self.assertTrue(self.manager.is_deep_work_active)
        self.mock_tts.speak.assert_called_with("Focus Time detected. Activating Deep Work mode.")
        
        # Verify Registry Call (DND)
        # We expect it to open the key and set the value
        mock_winreg.OpenKey.assert_called()
        mock_winreg.SetValueEx.assert_called()

        # Verify Window Minimization
        mock_ctypes.windll.user32.EnumWindows.assert_called()

    @patch('deep_work_manager.winreg')
    def test_deactivate_deep_work(self, mock_winreg):
        # Setup state
        self.manager.is_deep_work_active = True
        
        # Setup no events
        self.mock_calendar.get_upcoming_events_raw.return_value = []

        # Run check
        self.manager.check_and_activate()

        # Verify
        self.assertFalse(self.manager.is_deep_work_active)
        self.mock_tts.speak.assert_called_with("Focus Time ended. Deactivating Deep Work mode.")

if __name__ == '__main__':
    unittest.main()
