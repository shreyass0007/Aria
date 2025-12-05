import unittest
from unittest.mock import MagicMock, patch
from aria.email_manager import EmailManager
from aria.brain import AriaBrain
from aria.command_intent_classifier import CommandIntentClassifier

class TestEmailIntegration(unittest.TestCase):
    def setUp(self):
        self.brain = AriaBrain()
        self.classifier = CommandIntentClassifier(self.brain)
        
    def test_email_manager_mock(self):
        """Test EmailManager with mocked service."""
        with patch('email_manager.build') as mock_build, \
             patch('email_manager.EmailManager.authenticate') as mock_auth:
            
            mock_service = MagicMock()
            mock_build.return_value = mock_service
            
            manager = EmailManager()
            manager.service = mock_service # Force inject mock
            
            # Mock send response
            mock_service.users().messages().send().execute.return_value = {'id': '12345'}
            
            result = manager.send_email("test@example.com", "Test Subject", "Test Body")
            self.assertTrue("sent successfully" in result)
            
    def test_intent_classification(self):
        """Test if email commands are classified correctly."""
        if not self.brain.is_available():
            print("Skipping intent test (Brain not available)")
            return

        commands = [
            "send an email to john@example.com about meeting",
            "email sarah saying I'll be late",
            "send a mail to boss regarding project update"
        ]
        
        for cmd in commands:
            result = self.classifier.classify_intent(cmd)
            self.assertEqual(result['intent'], 'email_send', f"Failed for command: {cmd}")

    def test_brain_parsing(self):
        """Test if brain extracts email details correctly."""
        if not self.brain.is_available():
            print("Skipping parsing test (Brain not available)")
            return
            
        text = "send an email to john.doe@example.com about Project X saying the report is ready"
        details = self.brain.parse_email_intent(text)
        
        print(f"Parsed details: {details}")
        self.assertEqual(details.get('to'), 'john.doe@example.com')
        self.assertTrue('Project X' in details.get('subject', ''))
        self.assertTrue('report is ready' in details.get('body', ''))

    def test_draft_generation(self):
        """Test if brain generates a draft with sender name."""
        if not self.brain.is_available():
            print("Skipping draft test (Brain not available)")
            return
            
        sender = "Shreyas"
        draft = self.brain.generate_email_draft("boss@company.com", "Late", "I will be 10 mins late", sender_name=sender)
        print(f"Generated Draft: {draft}")
        self.assertTrue(len(draft) > 10)
        self.assertTrue("late" in draft.lower())
        self.assertTrue(sender in draft)

if __name__ == '__main__':
    unittest.main()
