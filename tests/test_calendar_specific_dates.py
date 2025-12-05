import unittest
from unittest.mock import MagicMock
from aria.command_processor import CommandProcessor
from aria.calendar_manager import CalendarManager

class TestCalendarSpecificity(unittest.TestCase):
    def setUp(self):
        # Mock dependencies
        self.tts_manager = MagicMock()
        self.brain = MagicMock()
        self.calendar = MagicMock()
        self.command_classifier = MagicMock()
        
        # Initialize CommandProcessor with mocks
        self.processor = CommandProcessor(
            self.tts_manager, MagicMock(), self.brain, self.calendar, MagicMock(), 
            MagicMock(), MagicMock(), self.command_classifier, MagicMock(), 
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()
        )
        
        # Mock brain availability
        self.brain.is_available.return_value = True
        self.brain.get_llm.return_value = None # Disable LLM humanization for this test

    def test_specific_date_query(self):
        # Simulate intent: "What do I have on 2023-12-25?"
        intent_data = {
            "intent": "calendar_query",
            "parameters": {
                "target_date": "2023-12-25",
                "query_type": "events",
                "time_scope": "all_day"
            }
        }
        
        self.processor.process_command("what do i have on christmas", intent_data=intent_data)
        
        # Verify calendar called with specific date
        self.calendar.get_events_for_date.assert_called_with("2023-12-25", "all_day")

    def test_free_time_query(self):
        # Simulate intent: "When am I free tomorrow morning?"
        intent_data = {
            "intent": "calendar_query",
            "parameters": {
                "target_date": "tomorrow",
                "query_type": "free_time",
                "time_scope": "morning"
            }
        }
        
        self.processor.process_command("free time tomorrow morning", intent_data=intent_data)
        
        # Verify calendar called for free slots
        self.calendar.get_free_slots.assert_called_with("tomorrow", "morning")

    def test_default_upcoming_events(self):
        # Simulate intent: "What's on my calendar?" (no specific date)
        intent_data = {
            "intent": "calendar_query",
            "parameters": {}
        }
        
        self.processor.process_command("check calendar", intent_data=intent_data)
        
        # Verify default call (max_results=9)
        self.calendar.get_upcoming_events.assert_called_with(max_results=9)

if __name__ == '__main__':
    unittest.main()
