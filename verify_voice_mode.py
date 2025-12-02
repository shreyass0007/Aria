import sys
import os
import time
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from wake_word_listener import WakeWordListener
from tts_manager import TTSManager

def test_voice_mode():
    print("--- Testing Voice Mode 2.0 ---")
    
    # 1. Test TTS Interruption
    print("\n[Test 1] TTS Interruption")
    tts = TTSManager()
    tts.set_tts_enabled(True)
    
    # Queue some text
    tts.speak("This is a long sentence that should be interrupted.")
    tts.speak("This sentence should never be spoken.")
    
    time.sleep(0.5) # Let it start
    
    print("Interrupting now!")
    tts.stop()
    
    # Verify queue is empty
    if tts.tts_queue.empty():
        print("✅ TTS Queue cleared successfully.")
    else:
        print("❌ TTS Queue NOT cleared.")

    # 2. Test Wake Word Initialization
    print("\n[Test 2] Wake Word Listener")
    
    def on_wake():
        print("✅ Callback triggered!")

    listener = WakeWordListener(on_wake_word_detected=on_wake)
    
    if listener.porcupine:
        print("✅ Porcupine initialized successfully.")
        listener.start()
        print("Listener started. Waiting 2 seconds...")
        time.sleep(2)
        listener.stop()
        print("Listener stopped.")
    else:
        print("❌ Porcupine failed to initialize (Check AccessKey).")

if __name__ == "__main__":
    test_voice_mode()
