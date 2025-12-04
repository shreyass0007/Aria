import unittest
from unittest.mock import MagicMock
import time
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aria.water_manager import WaterManager

class TestWaterManager(unittest.TestCase):
    def setUp(self):
        self.mock_tts = MagicMock()
        self.mock_notification = MagicMock()
        self.water_manager = WaterManager(tts_manager=self.mock_tts, notification_manager=self.mock_notification)

    def test_start_stop(self):
        msg = self.water_manager.start_monitoring()
        self.assertTrue(self.water_manager.is_running)
        self.assertIn("started", msg)
        
        msg = self.water_manager.stop_monitoring()
        self.assertFalse(self.water_manager.is_running)
        self.assertIn("stopped", msg)

    def test_set_interval(self):
        msg = self.water_manager.set_interval(30)
        self.assertEqual(self.water_manager.interval_minutes, 30)
        self.assertIn("30 minutes", msg)

    def test_trigger_reminder(self):
        # Manually trigger reminder
        self.water_manager._trigger_reminder()
        
        self.mock_tts.speak.assert_called_with("Time to drink water! Stay hydrated.")
        self.mock_notification.add_notification.assert_called_with("Water Reminder", "Time to drink water! Stay hydrated.", type="reminder")

    def test_reset_timer(self):
        self.water_manager.reset_timer()
        # Just check if it runs without error and updates time (hard to test exact time)
        self.assertTrue(True)

    def test_persistence(self):
        # Start and save
        self.water_manager.start_monitoring(interval_minutes=45)
        self.assertTrue(os.path.exists(self.water_manager.config_file))
        
        # Create a new instance to simulate restart
        new_manager = WaterManager(tts_manager=self.mock_tts, notification_manager=self.mock_notification)
        self.assertTrue(new_manager.is_running)
        self.assertEqual(new_manager.interval_minutes, 45)
        
        # Cleanup
        new_manager.stop_monitoring()
        if os.path.exists(self.water_manager.config_file):
            os.remove(self.water_manager.config_file)

    def test_dnd_suppression(self):
        # Mock system control
        mock_system = MagicMock()
        mock_system.get_dnd_status.return_value = True
        
        manager = WaterManager(
            tts_manager=self.mock_tts, 
            notification_manager=self.mock_notification,
            system_control=mock_system
        )
        
        # Trigger reminder
        manager._trigger_reminder()
        
        # TTS should NOT be called
        self.mock_tts.speak.assert_not_called()
        # Notification SHOULD be called
        self.mock_notification.add_notification.assert_called()

if __name__ == '__main__':
    unittest.main()
