import sys
import os
import time
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aria.tts_manager import TTSManager

# Setup logging to see debug output
logging.basicConfig(level=logging.DEBUG)

def on_speak(text):
    print(f"Callback: Aria is speaking: {text}")

def main():
    print("Initializing TTSManager...")
    manager = TTSManager(on_speak=on_speak)
    
    text = "This is a test of the new retry logic and increased timeout for Edge TTS. We want to ensure it is reliable."
    
    print(f"Queuing text: {text}")
    manager.speak(text)
    
    print("Waiting for playback...")
    # Wait enough time for retries if needed
    time.sleep(15) 
    
    print("Stopping TTSManager...")
    manager.stop()
    print("Done.")

if __name__ == "__main__":
    main()
