import sys
import os
from unittest.mock import MagicMock

# Mock dependencies
sys.modules['pygame'] = MagicMock()
sys.modules['edge_tts'] = MagicMock()
sys.modules['gtts'] = MagicMock()

from command_processor import CommandProcessor
from brain import AriaBrain

# Mock TTS Manager
class MockTTS:
    def speak(self, text, print_text=True):
        print(f"ARIA SPOKE: {text}")

# Mock other managers
mock_app_launcher = MagicMock()
mock_calendar = MagicMock()
mock_notion = MagicMock()
mock_automator = MagicMock()
mock_system_control = MagicMock()
mock_classifier = MagicMock()
mock_file_manager = MagicMock()
mock_weather = MagicMock()
mock_clipboard = MagicMock()
mock_monitor = MagicMock()
mock_email = MagicMock()
mock_greeting = MagicMock()

# Setup Brain with real API key if available, else mock
brain = AriaBrain()

# Setup Processor
processor = CommandProcessor(
    tts_manager=MockTTS(),
    app_launcher=mock_app_launcher,
    brain=brain,
    calendar=mock_calendar,
    notion=mock_notion,
    automator=mock_automator,
    system_control=mock_system_control,
    command_classifier=mock_classifier,
    file_manager=mock_file_manager,
    weather_manager=mock_weather,
    clipboard_screenshot=mock_clipboard,
    system_monitor=mock_monitor,
    email_manager=mock_email,
    greeting_service=mock_greeting
)

print("--- Testing Randomized Responses ---")
# Test Volume Up (should be random)
print("Command: 'increase volume'")
processor.process_command("increase volume", intent_data={"intent": "volume_up", "confidence": 1.0})

# Test Web Open (should be random)
print("\nCommand: 'open google'")
processor.process_command("open google", intent_data={"intent": "web_open", "parameters": {"url": "https://google.com", "name": "Google"}})

print("\n--- Testing LLM Humanization (Weather) ---")
# Mock Weather Data
mock_weather.get_weather.return_value = "The weather in London is 15 degrees Celsius with clouds."
print("Command: 'weather in London'")
processor.process_command("weather in London", intent_data={"intent": "weather_check", "parameters": {"city": "London"}})

print("\n--- Testing General Chat (System Prompt) ---")
print("Command: 'who are you'")
processor.process_command("who are you")
