import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from system_control import SystemControl
from command_intent_classifier import CommandIntentClassifier

class TestAntiHallucination(unittest.TestCase):
    def setUp(self):
        self.system_control = SystemControl()
        self.mock_brain = MagicMock()
        self.classifier = CommandIntentClassifier(self.mock_brain)

    def test_system_control_methods_exist(self):
        """Verify new methods exist in SystemControl."""
        self.assertTrue(hasattr(self.system_control, 'set_dnd'))
        self.assertTrue(hasattr(self.system_control, 'minimize_all_windows'))

    @patch('system_control.winreg')
    def test_set_dnd(self, mock_winreg):
        """Verify set_dnd logic."""
        # Mock registry interactions
        mock_key = MagicMock()
        mock_winreg.OpenKey.return_value.__enter__.return_value = mock_key
        
        result = self.system_control.set_dnd(True)
        self.assertIn("Do Not Disturb enabled", result)
        mock_winreg.SetValueEx.assert_called()

    @patch('system_control.ctypes')
    def test_minimize_all(self, mock_ctypes):
        """Verify minimize_all logic."""
        mock_user32 = mock_ctypes.windll.user32
        
        result = self.system_control.minimize_all_windows()
        self.assertIn("All windows minimized", result)
        mock_user32.EnumWindows.assert_called()

    def test_classifier_negative_constraints(self):
        """Verify classifier prompt contains negative constraints."""
        prompt = self.classifier._build_classification_prompt("test")
        self.assertIn("NEGATIVE CONSTRAINTS", prompt)
        self.assertIn("Do NOT invent new intents", prompt)
        self.assertIn("output \"general_chat\"", prompt)

if __name__ == '__main__':
    unittest.main()
