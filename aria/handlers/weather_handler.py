from typing import Dict, Any, Optional
from .base_handler import BaseHandler
from langchain_core.messages import HumanMessage, SystemMessage
import datetime
from ..logger import setup_logger

logger = setup_logger(__name__)

class WeatherHandler(BaseHandler):
    def __init__(self, tts_manager, weather_manager, brain):
        super().__init__(tts_manager)
        self.weather_manager = weather_manager
        self.brain = brain

    def should_handle(self, intent: str) -> bool:
        return intent == "weather_check"

    def _humanize_response(self, data_text: str, context: str) -> str:
        """Uses the LLM to convert raw data into a friendly, natural response."""
        if not self.brain or not self.brain.is_available():
            return data_text
            
        try:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            prompt = f"""
            You are Aria, a helpful AI assistant.
            The current time is {current_time}.
            
            Your task is to present the following SYSTEM DATA to the user.
            
            RULES:
            1. You MUST include the specific numbers, percentages, and details from the Raw Data.
            2. Be friendly and conversational, but prioritize ACCURACY and DATA.
            
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
        if intent == "weather_check":
            city = parameters.get("city")
            if not city:
                if " in " in text:
                    city = text.split(" in ")[-1].strip("?")
                else:
                    city = "Pimpri, Maharashtra, India"
                    self.tts_manager.speak(f"Checking weather for {city}...")
            
            weather_info = self.weather_manager.get_weather(city)
            humanized_weather = self._humanize_response(weather_info, f"current weather in {city}")
            self.tts_manager.speak(humanized_weather)
            return humanized_weather
        return None
