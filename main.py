import sys
import difflib
from aria_core import AriaCore

def main():
    aria = AriaCore()
    aria.speak("Welcome back. I am ready.")

    while True:
        try:
            # Wake word logic could be here or inside aria.listen()
            # For simplicity in this refactor, we'll just listen for commands directly 
            # or implement the wake word loop if desired.
            # The original main.py had a specific wake word loop.
            
            print("\nListening for Wake Word 'Aria'...")
            # We use aria.listen() but we need to check for wake word first.
            # Since aria.listen() records a phrase, we can check if that phrase is the wake word.
            
            text = aria.listen()
            if not text:
                continue
                
            # Simple wake word check
            if "aria" in text or "neo" in text:
                aria.speak("Yes?")
                cmd = aria.listen()
                if cmd:
                    aria.process_command(cmd)
            
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()