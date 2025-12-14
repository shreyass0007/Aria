import unittest
from unittest.mock import MagicMock
from aria.handlers.system_handler import SystemHandler

class TestDNDHandler(unittest.TestCase):
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

    def test_focus_mode_on(self):
        # Test focus mode on
        result = self.handler.handle("turn on focus mode", "focus_mode_on", {})
        self.mock_sys_control.set_dnd.assert_called_with(True)
        self.mock_sys_control.minimize_all_windows.assert_called()
        self.assertEqual(result, "Focus Mode activated.")

    def test_focus_mode_off(self):
        # Test focus mode off
        result = self.handler.handle("turn off focus mode", "focus_mode_off", {})
        self.mock_sys_control.set_dnd.assert_called_with(False)
        self.assertEqual(result, "Focus Mode deactivated.")

if __name__ == '__main__':
    unittest.main()
