
import sys
import os
import threading
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aria.aria_core import AriaCore
from aria.command_processor import CommandProcessor

def test_interruption():
    print("Initializing Core...")
    # Mock components to avoid full startup
    core = AriaCore()
    
    # Mock TS Manager so we don't actually speak but track it
    class MockTTS:
        def __init__(self):
            self.on_speak = None
            self.tts_enabled = True
        def speak(self, text, print_text=True):
            print(f"MOCK TTS: {text}")
        def stop(self):
            print("MOCK TTS: STOPPED")

    core.tts_manager = MockTTS()
    core.command_processor.tts_manager = core.tts_manager
    
    print("\n--- Testing Streaming Interruption ---")
    
    # Define a long generating prompt
    prompt = "Tell me a very long story about a dragon."
    
    # Run processing effectively in a thread (simulate async)
    def run_process():
        print("Starting process_command...")
        core.process_command(prompt, model_name="gpt-4o-mini")
        print("process_command finished.")
        
    t = threading.Thread(target=run_process)
    t.start()
    
    time.sleep(2) # Let it start speaking some chunks
    
    print("\n!!! SIMULATING WAKE WORD INTERRUPTION !!!")
    core._on_wake_word()
    
    t.join()
    print("\nTest Complete.")

if __name__ == "__main__":
    test_interruption()
