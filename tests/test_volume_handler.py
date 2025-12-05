import unittest
from unittest.mock import MagicMock
from aria.handlers.system_handler import SystemHandler

class TestVolumeHandler(unittest.TestCase):
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

    def test_volume_set_with_parameter(self):
        # Test with explicit parameter
        self.handler.handle("set volume to 50", "volume_set", {"level": 50})
        self.mock_sys_control.set_volume.assert_called_with(50)

    def test_volume_set_with_text_extraction(self):
        # Test extraction from text when parameter is missing
        self.handler.handle("set volume to 75", "volume_set", {})
        self.mock_sys_control.set_volume.assert_called_with(75)

    def test_volume_set_missing_level(self):
        # Test missing level
        result = self.handler.handle("set volume", "volume_set", {})
        self.assertEqual(result, "Please specify volume level.")
        self.mock_tts.speak.assert_called_with("What volume level?")

if __name__ == '__main__':
    unittest.main()
