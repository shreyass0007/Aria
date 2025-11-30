import sys
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

# Setup Brain (Real)
brain = AriaBrain()

# Setup Processor (Real logic, mocked peripherals)
processor = CommandProcessor(
    tts_manager=MockTTS(),
    app_launcher=MagicMock(),
    brain=brain,
    calendar=MagicMock(),
    notion=MagicMock(),
    automator=MagicMock(),
    system_control=MagicMock(),
    command_classifier=MagicMock(),
    file_manager=MagicMock(),
    weather_manager=MagicMock(),
    clipboard_screenshot=MagicMock(),
    system_monitor=MagicMock(),
    email_manager=MagicMock(),
    greeting_service=MagicMock()
)

# Mock classifier to always return "general_chat" for these tests
# so it falls through to the brain.ask() logic
processor.command_classifier.classify_intent.return_value = {"intent": "general_chat", "confidence": 0.5}

print("--- Testing Context Awareness ---")

# Turn 1
print("\nUser: 'Who is the CEO of Tesla?'")
processor.process_command("Who is the CEO of Tesla?")

# Turn 2 (Follow-up)
print("\nUser: 'How old is he?'")
processor.process_command("How old is he?")

# Turn 3 (New Topic)
print("\nUser: 'New topic'")
processor.process_command("New topic")

# Turn 4 (Check if context is cleared)
print("\nUser: 'How old is he?' (Should be confused or ask 'Who?')")
processor.process_command("How old is he?")
