import speech_recognition as sr
from gtts import gTTS
import os
import webbrowser
import datetime
import wikipedia
import music_library
import sys
import difflib
import pygame
import time
import urllib.parse
from wikipedia.exceptions import DisambiguationError, PageError
from brain import AriaBrain
from calendar_manager import CalendarManager
import subprocess
import glob
import threading

class AriaCore:
    def __init__(self, on_speak=None):
        """
        on_speak: Callback function(text) to update GUI or logs when Aria speaks.
        """
        self.recognizer = sr.Recognizer()
        self.on_speak = on_speak
        self.brain = AriaBrain()
        self.calendar = CalendarManager()
        self.input_mode = "voice"
        self.wake_word = "aria"
        self.app_paths = {}
        self.lock = threading.Lock() # Prevent concurrent mic access
        self.check_microphones()
        # Index apps in background
        threading.Thread(target=self.index_apps, daemon=True).start()

    def check_microphones(self):
        try:
            mics = sr.Microphone.list_microphone_names()
            print(f"Available Microphones: {mics}")
            if not mics:
                print("WARNING: No microphones found!")
        except Exception as e:
            print(f"Error listing microphones: {e}")

    def speak(self, text):
        if self.on_speak:
            self.on_speak(text)
        
        print(f"Aria said: {text}")
        
        # Audio output
        try:
            tts = gTTS(text=text, lang="en", slow=False)
            filename = "her_voice.mp3"
            if os.path.exists(filename):
                os.remove(filename)
            tts.save(filename)
            
            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            pygame.mixer.quit()
            if os.path.exists(filename):
                os.remove(filename)
        except Exception as e:
            print(f"Audio error: {e}")

    def listen(self):
        # Acquire lock to ensure only one thread listens at a time
        with self.lock:
            try:
                with sr.Microphone() as source:
                    print("Listening...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    self.recognizer.energy_threshold = 300
                    
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    command = self.recognizer.recognize_google(audio, language="en-in")
                    print(f"User said: {command}")
                    return command.lower()
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                return ""
            except (AssertionError, AttributeError) as e:
                print(f"Microphone initialization error: {e}")
                return ""
            except Exception as e:
                print(f"Listen error: {e}")
                return ""

    def safe_open_url(self, url: str, description: str = "") -> bool:
        try:
            ok = webbrowser.open(url)
            if not ok:
                self.speak("Sorry, I couldn't open that link.")
                return False
            if description:
                self.speak(description)
            return True
        except Exception as e:
            self.speak("Sorry, I couldn't open the link right now.")
            return False

    def index_apps(self):
        """Scans Start Menu for .lnk files to build an app index."""
        print("Indexing apps...")
        paths = [
            os.path.join(os.getenv('ProgramData'), r'Microsoft\Windows\Start Menu\Programs'),
            os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs')
        ]
        
        for path in paths:
            # Walk through all subdirectories
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(".lnk"):
                        # Clean name: "Google Chrome.lnk" -> "google chrome"
                        name = file.lower().replace(".lnk", "")
                        full_path = os.path.join(root, file)
                        self.app_paths[name] = full_path
        print(f"Indexed {len(self.app_paths)} apps.")

    def open_desktop_app(self, app_name: str):
        app_name = app_name.lower()
        
        # 1. Exact Match
        if app_name in self.app_paths:
            try:
                self.speak(f"Opening {app_name}")
                os.startfile(self.app_paths[app_name])
                return
            except Exception as e:
                print(f"Error opening {app_name}: {e}")

        # 2. Substring Match (e.g. "chrome" -> "google chrome")
        # Find all apps that contain the query
        substring_matches = [name for name in self.app_paths if app_name in name]
        if substring_matches:
            # Sort by length to find the most relevant (shortest) match
            # e.g. "chrome" prefers "google chrome" over "google chrome remote desktop"
            best_match = sorted(substring_matches, key=len)[0]
            try:
                self.speak(f"Opening {best_match}")
                os.startfile(self.app_paths[best_match])
                return
            except Exception as e:
                print(f"Error opening {best_match}: {e}")

        # 3. Fuzzy Match (Stricter)
        matches = difflib.get_close_matches(app_name, list(self.app_paths.keys()), n=1, cutoff=0.8)
        if matches:
            best_match = matches[0]
            try:
                self.speak(f"Opening {best_match}")
                os.startfile(self.app_paths[best_match])
                return
            except Exception as e:
                print(f"Error opening {best_match}: {e}")

        # 4. Fallback to System Command (e.g. notepad, calc)
        try:
            self.speak(f"Attempting to open {app_name}")
            os.startfile(app_name) # Works for things in PATH
        except Exception:
            self.speak(f"I couldn't find or open {app_name}.")

    def is_similar(self, a, b, threshold=0.8):
        return difflib.SequenceMatcher(None, a, b).ratio() >= threshold

    def process_command(self, text: str):
        text = text.lower().strip()
        if not text:
            return

        # Normalize Verbs (Fix typos like "opn", "ply")
        words = text.split()
        if words:
            if self.is_similar(words[0], "open", 0.75): # Lower threshold for short words
                words[0] = "open"
            elif self.is_similar(words[0], "play", 0.75):
                words[0] = "play"
            elif self.is_similar(words[0], "google", 0.8):
                words[0] = "google"
            elif self.is_similar(words[0], "search", 0.8):
                words[0] = "search"
            text = " ".join(words)

        # 0. Wake Word Handling
        # If user says just the wake word
        # If user says just the wake word
        if text == self.wake_word:
            self.speak("Welcome back Shreyas. How can I help you today?")
            return
        
        # If user says "WakeWord command...", strip it
        if text.startswith(self.wake_word + " "):
            text = text[len(self.wake_word):].strip()

        # Change Wake Word
        if "change wake word to" in text:
            new_word = text.replace("change wake word to", "").strip()
            if new_word:
                self.wake_word = new_word
                self.speak(f"Wake word changed to {self.wake_word}")
            else:
                self.speak("Change it to what?")
            return

        # 1. Help
        if any(x in text for x in ["help", "commands", "what can you do"]):
            self.speak("You can say: open instagram, open youtube, play music, google something, or just chat with me.")
            return

        # 2. Check for "open" commands - prioritize desktop apps over websites
        if text.startswith("open "):
            target = text.replace("open ", "").strip()
            
            # First, check if it's a known desktop app
            if target in self.app_paths or any(target in app_name for app_name in self.app_paths):
                self.open_desktop_app(target)
                return
        
        # 3. Website Shortcuts (only if not a desktop app)
        mappings = [
            (("open instagram", "instagram khol"), "https://instagram.com", "Opening Instagram"),
            (("open youtube", "youtube khol"), "https://youtube.com", "Opening YouTube"),
            (("open github", "coders ka adda"), "https://github.com", "Opening GitHub"),
            (("open linkedin", "demotivate kar"), "https://linkedin.com", "Opening LinkedIn"),
            (("open twitter", "open x"), "https://twitter.com", "Opening Twitter"),
            (("open facebook",), "https://facebook.com", "Opening Facebook"),
            (("open reddit",), "https://reddit.com", "Opening Reddit"),
            (("open amazon",), "https://amazon.in", "Opening Amazon"),
            (("open netflix",), "https://netflix.com", "Opening Netflix"),
            (("open spotify",), "https://spotify.com", "Opening Spotify"),
            (("open gmail", "open mail"), "https://gmail.com", "Opening Gmail"),
            (("open whatsapp",), "https://web.whatsapp.com", "Opening WhatsApp"),
            (("play my playlist",), "https://youtu.be/U52IJSyHa24?si=X5ICjA348_HahghB", "Playing your playlist"),
        ]
        for keywords, url, desc in mappings:
            for k in keywords:
                # Check exact match OR fuzzy match of the whole phrase
                if k in text or self.is_similar(text, k, 0.85):
                    self.safe_open_url(url, desc)
                    return
        
        # 4. Smart website detection for any other site
        if text.startswith("open "):
            target = text.replace("open ", "").strip()
            
            # At this point, we know it's not a desktop app, so try as website
            # Handle common patterns like "open google.com" or just "open google"
            if target:
                # If user said "open google.com", use it directly
                if "." in target and len(target.split(".")[-1]) <= 4:
                    url = f"https://{target}" if not target.startswith("http") else target
                    self.safe_open_url(url, f"Opening {target}")
                else:
                    # Assume .com domain
                    url = f"https://{target}.com"
                    self.safe_open_url(url, f"Opening {target}")
                return

        # 3. Google Search
        if "google" in text or "search" in text:
            # Extract query if present, else ask
            # Simple heuristic: if text is just "google" or "search", ask. 
            # If "google python", search python.
            query = text.replace("google", "").replace("search", "").strip()
            if not query:
                self.speak("What should I search for?")
                # In a GUI event loop, we can't easily block for 'listen' here without freezing UI.
                # For now, we'll just return. The user should say "google <topic>"
                return 
            
            q = urllib.parse.quote_plus(query)
            self.safe_open_url(f"https://www.google.com/search?q={q}", f"Searching for {query}")
            return

        # 4. Music
        if text.startswith("play"):
            song = text.replace("play", "", 1).strip()
            lib = getattr(music_library, "music", {}) or {}
            if song in lib:
                self.safe_open_url(lib[song], f"Playing {song}")
                return
            # Fuzzy match
            matches = difflib.get_close_matches(song, list(lib.keys()), n=1, cutoff=0.6)
            if matches:
                self.safe_open_url(lib[matches[0]], f"Playing {matches[0]}")
            else:
                self.speak("Song not found in library.")
            return

        # 5. Wikipedia (Removed to let Brain handle it)
        # if any(x in text for x in ["information", "tell me about", "who is"]):
        #     topic = text.replace("information", "").replace("tell me about", "").replace("who is", "").strip()
        #     if not topic:
        #         self.speak("What topic?")
        #         return
        #     try:
        #         info = wikipedia.summary(topic, sentences=2)
        #         self.speak(info)
        #     except Exception:
        #         self.speak("I couldn't find information on that.")
        #     return

        # 5. Date and Time
        if "time" in text:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"The current time is {current_time}")
            return
        if "date" in text:
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            self.speak(f"Today's date is {current_date}")
            return

        # 6. Calendar / Scheduling
        if any(x in text for x in ["schedule", "remind me", "calendar", "meeting", "appointment"]):
            # Check if it's a list request
            if any(x in text for x in ["what do i have", "my schedule", "upcoming events"]):
                events_text = self.calendar.get_upcoming_events()
                self.speak(events_text)
                return
            
            # Otherwise, assume it's a creation request
            self.speak("Checking my calendar...")
            details = self.brain.parse_calendar_intent(text)
            if details and details.get("start_time"):
                summary = details.get("summary", "Untitled Event")
                start_time = details.get("start_time")
                end_time = details.get("end_time")
                
                # Confirm with user (optional, but good practice)
                # For now, we'll just do it and confirm success
                result = self.calendar.create_event(summary, start_time, end_time)
                self.speak(result)
            else:
                self.speak("I couldn't understand the time or details for that event.")
            return

        # 7. Smalltalk / Exit
        if "tum best ho" in text:
            self.speak("Thank you!")
            return
        if "exit" in text or "quit" in text:
            self.speak("Goodbye!")
            sys.exit(0)

        # 7. Agentic Brain (Fallback)
        if self.brain.is_available():
            response = self.brain.ask(text)
            self.speak(response)
        else:
            self.speak("I didn't understand that command.")
