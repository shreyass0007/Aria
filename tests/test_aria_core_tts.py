import time
from aria_core import AriaCore

def main():
    print("Initializing AriaCore...")
    aria = AriaCore()
    
    print("Testing speak()...")
    aria.speak("Hello, this is a test of the Aria Core TTS system.")
    
    # Give it some time to process the queue
    time.sleep(10)
    print("Test complete.")

if __name__ == "__main__":
    main()
