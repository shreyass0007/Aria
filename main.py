import speech_recognition as sr
from gtts import gTTS  # Google Text To speech 
import os
import webbrowser   #to open external links
import wikipedia    # to link information
import music_library 
import sys          # to system related tasks
import difflib      #difference and similarity
import pygame
import time
import urllib.parse
from wikipedia.exceptions import DisambiguationError, PageError

def speak(text):                         
    print("Aria said:", text)     # whatever she speaks it will start with "Aria said"
    tts = gTTS(text=text, lang="en", slow=False)
    filename = "her_voice.mp3"
    tts.save(filename)       # Make her_voice.mp3
    
    # Initialize pygame mixer
    pygame.mixer.init()
    try:
        # Load and play the audio file
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        
        # Wait while the music is playing
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
    except Exception as e:
        print(f"Error playing sound: {e}")
    finally:
        # Clean up
        pygame.mixer.quit()
        if os.path.exists(filename):
            os.remove(filename)  # delete the file after playing
    
recognizer = sr.Recognizer()
INPUT_MODE = "voice"  # can be "voice" or "text"

def get_command() -> str:
    """Get command from user using current INPUT_MODE.
    Voice mode uses listen(); Text mode uses console input().
    Switch to text mode by saying 'text mode'/'typing mode'/'type mode'.
    Switch back to voice mode by typing '/voice'.
    """
    global INPUT_MODE
    if INPUT_MODE == "text":
        try:
            typed = input("Type your command (or /voice to switch back): ").strip()
            if typed.lower() == "/voice":
                INPUT_MODE = "voice"
                speak("Voice mode enabled.")
                return ""
            return typed.lower()
        except Exception as e:
            print(f"Text input error: {e}")
            return ""
    else:
        cmd = listen().strip()
        # Allow switching to text mode via voice
        if cmd in ("text mode", "typing mode", "type mode"):
            INPUT_MODE = "text"
            speak("Typing mode enabled. You can type your commands now.")
            return ""
        return cmd

def listen():
    with sr.Microphone() as source:   # collects the input
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)  # enhance input
        recognizer.energy_threshold = 300  # to remove unwanted noise from input
        recognizer.dynamic_energy_threshold = False 

        audio = recognizer.listen(source)     # records my voice

        try:
            command = recognizer.recognize_google(audio, language="en-in")    # intakes my input and then recognize it
            print("Shreyas said:", command)
            return command.lower()
        except sr.UnknownValueError:
            print("Recognizer could not understand the audio.")
            speak("Sorry, I could not understand.")
            return ""
        except sr.RequestError as e:
            print(f"Recognizer request error: {e}")
            speak("Speech service is unavailable right now.")
            return ""
        except Exception as e:
            print(f"Unexpected recognition error: {e}")
            speak("Sorry, something went wrong.")
            return ""

def safe_open_url(url: str, description: str = "") -> bool:
    """Open a URL in the default browser with basic error handling.
    Returns True if a URL open was attempted successfully.
    """
    try:
        ok = webbrowser.open(url)
        if not ok:
            speak("Sorry, I couldn't open that link.")
            return False
        if description:
            speak(description)
        return True
    except Exception as e:
        speak("Sorry, I couldn't open the link right now.")
        print(f"webbrowser error: {e}")
        return False


def handle_open_shortcuts(text: str) -> bool:
    """Handle quick open commands for known websites."""
    mappings = [
        (("open instagram", "instagram khol"), "https://instagram.com", "Opening Instagram"),
        (("open youtube", "youtube khol"), "https://youtube.com", "Opening YouTube"),
        (("open github", "coders ka adda"), "https://github.com", "Opening GitHub"),
        (("open linkedin", "demotivate kar"), "https://linkedin.com", "Opening LinkedIn"),
        (("play my playlist",), "https://youtu.be/AbkEmIgJMcU?si=V6ETJmVWDU2zOEtq", "Playing your playlist"),
    ]
    for keywords, url, desc in mappings:
        if any(k in text for k in keywords):
            return safe_open_url(url, desc)
    return False


def handle_google_search(text: str) -> bool:
    if ("google" in text) or ("search" in text):
        speak("Kya Search Karu")
        topic = listen().strip()
        if not topic:
            speak("Kuchh sunai nahi diya. Dobara boliye.")
            return True
        query = urllib.parse.quote_plus(topic)
        opened = safe_open_url(f"https://www.google.com/search?q={query}")
        if opened:
            speak(f"Here is what I found for {topic}")
        return True
    return False


def handle_smalltalk(text: str) -> bool:
    if "tum best ho" in text:
        speak("Thank You , Ye mere boss ki vajah se hai")
        return True
    if ("good bye" in text) or ("goodbye" in text):
        speak("Good Bye Guys , Have a nice day")
        return True
    return False


def handle_help(text: str) -> bool:
    """Provide a quick overview of supported commands."""
    if ("help" in text) or ("commands" in text) or ("what can you do" in text):
        speak(
            "You can say: open instagram, open youtube, open github, open linkedin, play my playlist, play <song name>, google search, tell me about <topic>, good bye, exit or quit."
        )
        return True
    return False


def handle_play_song(text: str) -> bool:
    if text.startswith("play"):
        song = text.replace("play", "", 1).strip()
        lib = getattr(music_library, "music", {}) or {}
        if not isinstance(lib, dict):
            lib = {}
        if song in lib:
            return safe_open_url(lib[song], f"Playing {song}")
        # Try fuzzy match
        # If we are very confident (>=0.8), auto play the best match; otherwise suggest.
        strong_candidates = difflib.get_close_matches(song, list(lib.keys()), n=1, cutoff=0.8)
        if strong_candidates:
            best = strong_candidates[0]
            return safe_open_url(lib[best], f"Playing {best}")
        # weaker suggestions
        weak_candidates = difflib.get_close_matches(song, list(lib.keys()), n=1, cutoff=0.6)
        if weak_candidates:
            best = weak_candidates[0]
            speak(f"Song not found. Did you mean {best}?")
        else:
            speak("Ye song play list mai nahi h")
        return True
    return False


def handle_information(text: str) -> bool:
    if ("information" in text) or ("tell me about" in text) or ("who is" in text):
        speak("Kya Jan na hai apko?")
        topic = listen().strip()
        if not topic:
            speak("Topic samajh nahi aaya. Dobara boliye.")
            return True
        try:
            info = wikipedia.summary(topic, sentences=2)
            speak(info)
        except DisambiguationError as e:
            options = ", ".join(e.options[:5])
            speak(f"Bahut saare results mile. Kya aap {options} me se kisi ke baare me pooch rahe the?")
        except PageError:
            speak("Mujhe uss topic par kuchh nahi mila.")
        except Exception as e:
            speak("Sorry, kuchh gadbad ho gayi.")
            print(f"wikipedia error: {e}")
        return True
    return False


def myCommand(c):
    text = c.lower().strip()
    # Order matters: quick site opens, search, smalltalk, music, info
    if handle_help(text):
        return
    if handle_open_shortcuts(text):
        return
    if handle_google_search(text):
        return
    if handle_smalltalk(text):
        return
    if handle_play_song(text):
        return
    if handle_information(text):
        return
    # Fallback
    speak("Sorry, main ye command nahi samajh payi.")
    
if __name__ == "__main__":
    speak("Welcome back Shreyas. How can I assist you today ?...")                     # Engine is heating up

    while True:
        try:
            with sr.Microphone() as source:           # listens to my voice
                print("Listening for wake word...")   # Wait for "Aria"
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)    # how much time it will listen and recognize the input
            word = recognizer.recognize_google(audio)  # Will Match the word
            print("Wake word heard:", word)
            # Speak back what was heard for confirmation
            speak(f"You said: {word}")
            # Normalize and fuzzy match the wake word to be more forgiving
            cleaned = "".join(ch for ch in word.lower() if ch.isalpha())
            similarity = difflib.SequenceMatcher(None, cleaned, "Neo").ratio()
            print(f"Wake word normalized: {cleaned} | similarity to 'Neo': {similarity:.2f}")
            if cleaned == "Neo" or similarity >= 0.44:
                speak("Yes Boss")                       # Speak Yes boss , if true
                
                while True:
                    # Get command using current input mode (voice or text)
                    command = get_command()
                    if command != "":
                        myCommand(command)
                        if "exit" in command or "quit" in command:
                            speak("Good bye boss , Aria Going offline.")    # to shut down Aria say "exit"
                            sys.exit(0) 

        except Exception as e:                           # display error as "e" not show red error
            print("Error:", e)                          