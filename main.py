import sys
import difflib
from aria_core import AriaCore

def main():
    aria = AriaCore()
    aria.speak("Welcome back. I am ready.")

    while True:
        try:
            # We're just listening for the wake word "Aria" here.
            # Once we hear it, we'll ask the user what they want.
            
            print("\nListening for 'Aria'...")
            
            # Listen for any sound/speech
            
            text = aria.listen()
            if not text:
                continue
                

                
            # Check if the user said the magic word
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