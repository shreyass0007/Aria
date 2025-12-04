import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest.mock import MagicMock, patch
from aria.command_processor import CommandProcessor

class TestHandlersComprehensive(unittest.TestCase):
    def setUp(self):
        # Mock all dependencies
        self.tts_manager = MagicMock()
        self.app_launcher = MagicMock()
        self.brain = MagicMock()
        self.calendar = MagicMock()
        self.notion = MagicMock()
        self.automator = MagicMock()
        self.system_control = MagicMock()
        self.command_classifier = MagicMock()
        self.file_manager = MagicMock()
        self.weather_manager = MagicMock()
        self.clipboard_screenshot = MagicMock()
        self.system_monitor = MagicMock()
        self.email_manager = MagicMock()
        self.greeting_service = MagicMock()
        self.music_manager = MagicMock()
        self.water_manager = MagicMock()

        self.processor = CommandProcessor(
            self.tts_manager, self.app_launcher, self.brain, self.calendar,
            self.notion, self.automator, self.system_control, self.command_classifier,
            self.file_manager, self.weather_manager, self.clipboard_screenshot,
            self.system_monitor, self.email_manager, self.greeting_service,
            self.music_manager, self.water_manager
        )

    def test_email_handler(self):
        # Test email draft creation
        intent_data = {"intent": "email_send", "confidence": 0.9, "parameters": {}}
        self.brain.parse_email_intent.return_value = {"to": "test@example.com", "subject": "Test", "body": "Hello"}
        self.brain.generate_email_draft.return_value = "Draft Body"
        
        self.processor.process_command("send email to test", intent_data=intent_data)
        
        self.assertIsNotNone(self.processor.pending_email)
        self.assertEqual(self.processor.pending_email["to"], "test@example.com")
        
        # Test confirmation
        self.processor.process_command("yes send it")
        self.email_manager.send_email.assert_called_with("test@example.com", "Test", "Draft Body")
        self.assertIsNone(self.processor.pending_email)

    def test_weather_handler(self):
        intent_data = {"intent": "weather_check", "confidence": 0.9, "parameters": {"city": "London"}}
        self.weather_manager.get_weather.return_value = "Sunny, 25C"
        
        self.processor.process_command("weather in London", intent_data=intent_data)
        
        self.weather_manager.get_weather.assert_called_with("London")

    def test_calendar_handler(self):
        intent_data = {"intent": "calendar_query", "confidence": 0.9, "parameters": {"target_date": "today"}}
        self.calendar.get_events_for_date.return_value = "No events"
        
        self.processor.process_command("what's on my calendar today", intent_data=intent_data)
        
        self.calendar.get_events_for_date.assert_called()

    def test_file_handler(self):
        intent_data = {"intent": "file_search", "confidence": 0.9, "parameters": {"pattern": "*.txt"}}
        self.file_manager.search_files.return_value = ["file1.txt"]
        
        self.processor.process_command("find text files", intent_data=intent_data)
        
        self.file_manager.search_files.assert_called()

    def test_notion_handler(self):
        intent_data = {"intent": "notion_query", "confidence": 0.9, "parameters": {}}
        self.brain.extract_notion_page_id.return_value = {"search_query": "Notes"}
        self.notion.search_pages_raw.return_value = [{"id": "1", "title": "Notes"}]
        self.notion.get_page_content.return_value = {"content": "Some content", "word_count": 10}
        
        self.processor.process_command("summarize notion page Notes", intent_data=intent_data)
        
        self.notion.search_pages_raw.assert_called_with("Notes")
        self.notion.search_pages_raw.assert_called_with("Notes")
        self.notion.get_page_content.assert_called_with("1")

    def test_notion_handler_multiple_results(self):
        intent_data = {"intent": "notion_query", "confidence": 0.9, "parameters": {}}
        self.brain.extract_notion_page_id.return_value = {"search_query": "Notes"}
        self.notion.search_pages_raw.return_value = [
            {"id": "1", "title": "Notes 1"},
            {"id": "2", "title": "Notes 2"}
        ]
        
        self.processor.process_command("summarize notion page Notes", intent_data=intent_data)
        
        # Verify speak was called with the aggregated message
        # We expect one call with the list
        call_args_list = self.tts_manager.speak.call_args_list
        found_list = False
        for args, _ in call_args_list:
            if "1. Notes 1" in args[0] and "2. Notes 2" in args[0]:
                found_list = True
                break
        self.assertTrue(found_list, "Did not find aggregated list in speak calls")
        
        # Verify return value
        result = self.processor.process_command("summarize notion page Notes", intent_data=intent_data)
        self.assertIn("1. Notes 1", result)
        self.assertIn("2. Notes 2", result)

if __name__ == '__main__':
    unittest.main()
