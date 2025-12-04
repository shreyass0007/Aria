from typing import Dict, Any, Optional
from .base_handler import BaseHandler
import datetime
import difflib
from langchain_core.messages import HumanMessage, SystemMessage
from ..logger import setup_logger

logger = setup_logger(__name__)

class CalendarHandler(BaseHandler):
    def __init__(self, tts_manager, calendar_manager, brain):
        super().__init__(tts_manager)
        self.calendar = calendar_manager
        self.brain = brain

    def should_handle(self, intent: str) -> bool:
        return intent in ["calendar_query", "calendar_create"]

    def is_similar(self, a, b, threshold=0.8):
        return difflib.SequenceMatcher(None, a, b).ratio() >= threshold

    def _humanize_response(self, data_text: str, context: str) -> str:
        if not self.brain or not self.brain.is_available():
            return data_text
        try:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            prompt = f"""
            You are Aria, a helpful AI assistant.
            The current time is {current_time}.
            
            Your task is to present the following CALENDAR DATA to the user.
            
            RULES:
            1. Summarize the events but include times and titles.
            2. Be friendly and conversational.
            
            Raw Data:
            {data_text}
            """
            llm = self.brain.get_llm()
            if llm:
                response = llm.invoke([
                    SystemMessage(content="You are Aria. Be friendly and concise."),
                    HumanMessage(content=prompt)
                ])
                return response.content.strip()
            return data_text
        except Exception as e:
            logger.error(f"Error humanizing response: {e}")
            return data_text

    def handle(self, text: str, intent: str, parameters: Dict[str, Any]) -> Optional[str]:
        if intent == "calendar_query":
            # 1. Extract parameters from LLM
            target_date = parameters.get("target_date")
            query_type = parameters.get("query_type", "events")
            time_scope = parameters.get("time_scope", "all_day")
            
            # 2. Fallback for legacy/fuzzy extraction if LLM missed it
            if not target_date:
                words = text.split()
                if any(self.is_similar(w, "today", 0.8) for w in words):
                    target_date = "today"
                elif any(self.is_similar(w, "tomorrow", 0.8) for w in words):
                    target_date = "tomorrow"
            
            # 3. Handle Free Time Query
            if query_type == "free_time":
                if not target_date: target_date = "today"
                response = self.calendar.get_free_slots(target_date, time_scope)
                self.tts_manager.speak(response)
                return response

            # 4. Handle Event Query
            if target_date:
                # Specific date query
                raw_data = self.calendar.get_events_for_date(target_date, time_scope)
                context_str = f"schedule for {target_date}"
                if time_scope != "all_day":
                    context_str += f" ({time_scope})"
                
                response = self._humanize_response(raw_data, context_str)
                self.tts_manager.speak(response)
            else:
                # Default: Upcoming events
                raw_data = self.calendar.get_upcoming_events(max_results=9)
                response = self._humanize_response(raw_data, "upcoming events")
                self.tts_manager.speak(response)
            return response

        elif intent == "calendar_create":
            self.tts_manager.speak("Checking calendar...")
            details = self.brain.parse_calendar_intent(text)
            if details.get("start_time"):
                result = self.calendar.create_event(details.get("summary"), details.get("start_time"), details.get("end_time"))
                self.tts_manager.speak(result)
                return result
            else:
                self.tts_manager.speak("I need a time for the event.")
                return "Please specify a time for the event."
        
        return None
