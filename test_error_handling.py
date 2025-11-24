import unittest
from unittest.mock import MagicMock, patch
from email_manager import EmailManager
from calendar_manager import CalendarManager
from notion_manager import NotionManager

class TestErrorHandling(unittest.TestCase):

    @patch('email_manager.build')
    def test_email_error_handling(self, mock_build):
        """Test if EmailManager returns friendly error on exception."""
        # Setup mock to raise exception
        mock_service = MagicMock()
        mock_service.users().messages().send.side_effect = Exception("Critical Gmail Failure")
        mock_build.return_value = mock_service
        
        manager = EmailManager()
        # Mock authenticate to avoid real auth
        manager.authenticate = MagicMock()
        manager.service = mock_service
        
        result = manager.send_email("test@example.com", "Subject", "Body")
        print(f"Email Result: {result}")
        
        self.assertIn("I couldn't send the email", result)
        self.assertNotIn("Critical Gmail Failure", result)

    @patch('calendar_manager.build')
    def test_calendar_error_handling(self, mock_build):
        """Test if CalendarManager returns friendly error on exception."""
        mock_service = MagicMock()
        mock_service.events().insert.side_effect = Exception("API Quota Exceeded")
        mock_build.return_value = mock_service
        
        manager = CalendarManager()
        manager.authenticate = MagicMock()
        manager.service = mock_service
        
        result = manager.create_event("Meeting", "tomorrow at 10am")
        print(f"Calendar Result: {result}")
        
        self.assertIn("I couldn't create the calendar event", result)
        self.assertNotIn("API Quota Exceeded", result)

    @patch('notion_manager.Client')
    def test_notion_error_handling(self, mock_client_cls):
        """Test if NotionManager returns friendly error on exception."""
        mock_client = MagicMock()
        mock_client.pages.create.side_effect = Exception("Invalid Property")
        mock_client_cls.return_value = mock_client
        
        manager = NotionManager()
        manager.client = mock_client
        
        result = manager.create_page("New Task")
        print(f"Notion Result: {result}")
        
        self.assertIn("I couldn't create the page in Notion", result)
        self.assertNotIn("Invalid Property", result)

if __name__ == '__main__':
    unittest.main()
