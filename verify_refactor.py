import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("Importing AriaCore...")
    from aria_core import AriaCore
    print("AriaCore imported successfully.")

    print("Initializing AriaCore...")
    aria = AriaCore()
    print("AriaCore initialized successfully.")

    print("Checking components...")
    assert aria.tts_manager is not None, "TTSManager not initialized"
    assert aria.app_launcher is not None, "AppLauncher not initialized"
    assert aria.speech_input is not None, "SpeechInput not initialized"
    assert aria.greeting_service is not None, "GreetingService not initialized"
    assert aria.command_processor is not None, "CommandProcessor not initialized"
    print("All components initialized.")

    print("Checking properties...")
    print(f"Wake Word: {aria.wake_word}")
    aria.wake_word = "jarvis"
    assert aria.wake_word == "jarvis", "Failed to set wake word"
    print(f"New Wake Word: {aria.wake_word}")

    print(f"TTS Enabled: {aria.tts_enabled}")
    aria.set_tts_enabled(False)
    assert aria.tts_enabled == False, "Failed to disable TTS"
    print(f"TTS Enabled: {aria.tts_enabled}")

    print("Checking greeting...")
    greeting = aria.get_time_based_greeting()
    print(f"Greeting: {greeting}")

    print("Verification passed!")

except Exception as e:
    print(f"Verification failed: {e}")
    import traceback
    traceback.print_exc()
