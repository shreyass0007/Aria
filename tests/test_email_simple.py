import unittest
from unittest.mock import MagicMock, patch
from aria.email_manager import EmailManager

class TestEmailSimple(unittest.TestCase):
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
            print(f"Result: {result}")
            self.assertTrue("sent successfully" in result)

if __name__ == '__main__':
    unittest.main()
