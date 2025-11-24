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
from notion_manager import NotionManager
from file_automation import FileAutomator
from system_control import SystemControl
from command_intent_classifier import CommandIntentClassifier
from file_manager import FileManager
from weather_manager import WeatherManager
from clipboard_screenshot import ClipboardScreenshot
from system_monitor import SystemMonitor
from email_manager import EmailManager
import subprocess
import glob
import threading
import queue
import re
import asyncio
import edge_tts
from speech_engine import SpeechEngine

class AriaCore:
    def __init__(self, on_speak=None):
        """
        on_speak: Callback function(text) to update GUI or logs when Aria speaks.
        """
        self.recognizer = sr.Recognizer()
        self.on_speak = on_speak
        self.brain = AriaBrain()
        self.calendar = CalendarManager()
        self.notion = NotionManager()
        self.automator = FileAutomator()
        self.system_control = SystemControl()
        self.command_classifier = CommandIntentClassifier(self.brain)
        self.file_manager = FileManager()
        self.weather_manager = WeatherManager()
        self.clipboard_screenshot = ClipboardScreenshot()
        
        # Initialize Local Speech Engine
        self.speech_engine = SpeechEngine(model_size="base")
        self.system_monitor = SystemMonitor()
        self.email_manager = EmailManager()
        self.input_mode = "voice"
        self.wake_word = "aria"
        self.app_paths = {}
        self.lock = threading.Lock() # Prevent concurrent mic access
        self.pending_notion_pages = None  # Store page options for selection
        self.pending_email = None # Store email draft for confirmation
        self.last_ui_action = None # Store UI action for backend to pick up
        
        self.tts_queue = queue.Queue()
        threading.Thread(target=self._tts_worker, daemon=True).start()
        
        self.tts_enabled = True  # Default to enabled

        self.check_microphones()
        # Index apps in background
        threading.Thread(target=self.index_apps, daemon=True).start()

    def set_tts_enabled(self, enabled: bool):
        """Enable or disable TTS output."""
        self.tts_enabled = enabled
        print(f"TTS Enabled: {self.tts_enabled}")

    def get_time_based_greeting(self):
        """Returns a time-based greeting like JARVIS"""
        hour = datetime.datetime.now().hour
        user_name = os.getenv("USER_NAME", "User")
        
        if 5 <= hour < 12:
            time_greeting = f"Good morning, {user_name}."
            context_messages = [
                "Ready to start the day?",
                "All systems are operational.",
                "How may I assist you today?",
                "Your schedule is ready for review.",
                "Time to conquer the world.",
                "Let's make today productive.",
                "What's on the agenda?",
                "Shall we begin?",
                "The world awaits your brilliance.",
                "Ready to tackle today's challenges?",
                "A fresh start awaits.",
                "Let's make things happen.",
                "Your productivity suite is ready.",
                "Time to turn ideas into reality.",
                "The early bird gets the worm.",
                "Rise and shine! Let's get to work.",
                "Another day, another opportunity.",
                "Ready to make today count?",
                "Let's start with a winning strategy.",
                "Your digital workspace is prepared."
            ]
        elif 12 <= hour < 17:
            time_greeting = f"Good afternoon, {user_name}."
            context_messages = [
                "How's your day going?",
                "What can I help you with?",
                "All systems running smoothly.",
                "Ready when you are.",
                "Need a productivity boost?",
                "Let's keep the momentum going.",
                "Time to check off that to-do list.",
                "How may I assist this afternoon?",
                "Still going strong?",
                "Let's finish what we started.",
                "Halfway through the day already.",
                "Need anything to stay on track?",
                "Keeping things efficient, as always.",
                "What's next on your list?",
                "Shall we continue?",
                "Your afternoon update is ready.",
                "Let's maintain that energy.",
                "Working hard, I see.",
                "Time to power through.",
                "At your service, as always."
            ]
        elif 17 <= hour < 21:
            time_greeting = f"Good evening, {user_name}."
            context_messages = [
                "Welcome back. How can I help?",
                "Ready to wrap up the day?",
                "What do you need?",
                "At your service.",
                "Time to unwind or keep going?",
                "Let's review what you've accomplished.",
                "How was your day?",
                "Ready for the evening?",
                "Shall we tie up loose ends?",
                "Time to relax or power through?",
                "The day's work is nearly done.",
                "Let's finish strong.",
                "What's left on your plate?",
                "Evening briefing ready.",
                "Time to reflect and recharge.",
                "You've earned a break.",
                "Let's close out the day properly.",
                "Standing by for evening tasks.",
                "Ready to help you wind down.",
                "What can I do for you tonight?"
            ]
        else:
            time_greeting = f"Good night, {user_name}."
            context_messages = [
                "Burning the midnight oil?",
                "Still working? Let me help.",
                "How can I assist you tonight?",
                "Ready whenever you are.",
                "Late night session?",
                "The night is young.",
                "Inspiration strikes at odd hours.",
                "Night owl mode activated.",
                "I'm here, no matter the hour.",
                "Let's make the most of this quiet time.",
                "The stars are out, and so are we.",
                "Darkness brings clarity sometimes.",
                "Working late again, I see.",
                "Your dedication is admirable.",
                "Let me help you through the night.",
                "Sleep is overrated anyway.",
                "The night shift begins.",
                "When do you sleep, exactly?",
                "Midnight productivity mode enabled.",
                "Let's turn night into opportunity."
            ]
        
        import random
        context_msg = random.choice(context_messages)
        return f"{time_greeting} {context_msg}"



    def check_microphones(self):
        try:
            mics = sr.Microphone.list_microphone_names()
            print(f"Available Microphones: {mics}")
            if not mics:
                print("WARNING: No microphones found!")
        except Exception as e:
            print(f"Error listing microphones: {e}")

    def _tts_worker(self):
        """Worker thread to handle TTS playback sequentially with Edge-TTS and gTTS fallback."""
        # Create a new event loop for this thread since edge-tts is async
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        print("TTS Worker started")
        
        while True:
            text = self.tts_queue.get()
            if text is None:
                break
            
            print(f"TTS Worker: Processing text: '{text[:50]}...'")
            filename = f"her_voice_{int(time.time())}_{id(text)}.mp3"
            
            try:
                print("TTS Worker: Trying Edge-TTS...")
                # Try Edge TTS first
                communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
                loop.run_until_complete(communicate.save(filename))
                print(f"TTS Worker: Edge-TTS saved to {filename}")
                
            except Exception as e:
                print(f"Edge-TTS error, falling back to gTTS: {e}")
                try:
                    # Fallback to gTTS
                    print("TTS Worker: Using gTTS fallback...")
                    tts = gTTS(text=text, lang="en", slow=False)
                    tts.save(filename)
                    print(f"TTS Worker: gTTS saved to {filename}")
                except Exception as e2:
                    print(f"gTTS error: {e2}")
                    self.tts_queue.task_done()
                    continue
            
            try:
                # Play the audio file
                if os.path.exists(filename):
                    print(f"TTS Worker: Playing audio file {filename} (size: {os.path.getsize(filename)} bytes)")
                    pygame.mixer.init()
                    pygame.mixer.music.load(filename)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                    pygame.mixer.quit()
                    print("TTS Worker: Audio playback complete")
                    
                    # Cleanup
                    try:
                        os.remove(filename)
                    except:
                        pass
                else:
                    print(f"TTS Worker ERROR: Audio file {filename} does not exist!")
            except Exception as e:
                print(f"Audio playback error: {e}")
            finally:
                self.tts_queue.task_done()

    def _clean_text_for_audio(self, text):
        """Removes Markdown formatting for smoother TTS playback."""
        # Remove bold/italic markers (* or _)
        text = re.sub(r'[\*_]{1,3}', '', text)
        
        # Remove headers (#)
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        
        # Remove code backticks
        text = re.sub(r'`', '', text)
        
        # Remove links [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Remove list bullets (optional, but helps flow)
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
        
        return text.strip()

    def speak(self, text, print_text=True):
        if print_text:
            if self.on_speak:
                self.on_speak(text)
            
            try:
                print(f"Aria said: {text}")
            except UnicodeEncodeError:
                print(f"Aria said: {text.encode('ascii', 'replace').decode()}")
        
        # Clean text for audio
        clean_text = self._clean_text_for_audio(text)
        
        # Add to queue for background playback only if TTS is enabled
        if self.tts_enabled and clean_text:
            self.tts_queue.put(clean_text)

    def listen(self):
        # Acquire lock to ensure only one thread listens at a time
        with self.lock:
            try:
                with sr.Microphone() as source:
                    print("Listening...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    self.recognizer.energy_threshold = 300
                    
                    # Listen for audio
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    
                    # Save temporary file for Whisper
                    temp_wav = f"temp_voice_{int(time.time())}.wav"
                    with open(temp_wav, "wb") as f:
                        f.write(audio.get_wav_data())
                    
                    # Transcribe using Local Faster-Whisper
                    print("Transcribing locally...")
                    command = self.speech_engine.transcribe(temp_wav)
                    
                    # Cleanup
                    if os.path.exists(temp_wav):
                        os.remove(temp_wav)
                        
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


    def process_command(self, text: str, model_name: str = "openai"):
        text = text.lower().strip()
        if not text:
            return

        # PRIORITY: Check if user is responding to a Notion page selection prompt
        # This needs to be FIRST, before any other logic
        
        # 0. Email Confirmation
        if self.pending_email:
            if any(x in text for x in ["yes", "send", "confirm", "okay", "sure"]):
                self.speak("Sending email...")
                to = self.pending_email["to"]
                subject = self.pending_email["subject"]
                body = self.pending_email["body"]
                result = self.email_manager.send_email(to, subject, body)
                self.speak(result)
                self.pending_email = None
                return
            elif any(x in text for x in ["no", "cancel", "don't send", "stop"]):
                self.speak("Email cancelled.")
                self.pending_email = None
                return
            else:
                self.speak("Please say 'yes' to send or 'no' to cancel.")
                return

        if self.pending_notion_pages:
            # User is selecting a page number
            try:
                # Try to parse selection (could be "1", "first", "number 2", etc.)
                selection = None
                
                # Check for number words
                number_words = {
                    "first": 1, "one": 1, "1": 1,
                    "second": 2, "two": 2, "2": 2,
                    "third": 3, "three": 3, "3": 3,
                    "fourth": 4, "four": 4, "4": 4,
                    "fifth": 5, "five": 5, "5": 5
                }
                
                for word, num in number_words.items():
                    if word in text:
                        selection = num
                        break
                
                if selection and 1 <= selection <= len(self.pending_notion_pages):
                    # Valid selection - proceed with summarization
                    selected_page = self.pending_notion_pages[selection - 1]
                    page_id = selected_page["id"]
                    page_title = selected_page["title"]
                    
                    # Clear pending pages
                    self.pending_notion_pages = None
                    
                    # Fetch and summarize
                    self.speak(f"Great! Fetching {page_title}...")
                    page_data = self.notion.get_page_content(page_id)
                    
                    if page_data.get("status") == "error":
                        self.speak(page_data.get("error", "Unable to fetch the page."))
                        return
                    
                    content = page_data.get("content", "")
                    self.speak(f"Summarizing {page_title}...")
                    summary = self.brain.summarize_text(content, max_sentences=5)
                    
                    # Format structured output
                    word_count = page_data.get("word_count", 0)
                    
                    structured_output = f"""
📄 NOTION PAGE SUMMARY

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 Page: {page_title}
📊 Word Count: {word_count} words
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Summary:
{summary}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                    self.speak(structured_output)
                    return
                else:
                    # Invalid selection
                    self.speak("I didn't understand your selection. Please say a number like 'one', 'two', or 'three'.")
                    # Don't clear pending_notion_pages - let them try again
                    return
                    
            except Exception as e:
                print(f"Error processing selection: {e}")
                self.pending_notion_pages = None
                self.speak("Sorry, I had trouble with that. Let's start over.")
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
            greeting = self.get_time_based_greeting()
            self.speak(greeting)
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

        # Identity
        if any(x in text for x in ["who are you", "what is your name", "introduce yourself"]):
            self.speak("I am Aria, an advanced AI assistant created by Shreyas. I'm here to help you with your tasks and answer your questions.")
            return

        # ---------------------------------------------------------
        # CENTRALIZED INTENT CLASSIFICATION
        # ---------------------------------------------------------
        
        # Classify the user's intent using the LLM
        intent_result = self.command_classifier.classify_intent(text)
        intent = intent_result.get("intent")
        confidence = intent_result.get("confidence", 0.0)
        parameters = intent_result.get("parameters", {})
        
        print(f"DEBUG: Intent: {intent}, Confidence: {confidence}, Params: {parameters}")
        
        # Dispatch based on intent
        
        # --- WEB & APPS ---
        if intent == "web_open":
            url = parameters.get("url")
            name = parameters.get("name", "site")
            if url:
                self.safe_open_url(url, f"Opening {name}")
            else:
                # Fallback if URL not extracted
                target = text.replace("open", "").strip()
                if target:
                    self.safe_open_url(f"https://{target}.com", f"Opening {target}")
                else:
                    self.speak("What website should I open?")
            return

        elif intent == "app_open":
            app_name = parameters.get("app_name")
            if app_name:
                self.open_desktop_app(app_name)
            else:
                # Fallback
                target = text.replace("open", "").strip()
                self.open_desktop_app(target)
            return

        elif intent == "web_search":
            query = parameters.get("query")
            if not query:
                # Fallback extraction
                query = text.replace("google", "").replace("search", "").replace("for", "").strip()
            
            if query:
                q = urllib.parse.quote_plus(query)
                self.safe_open_url(f"https://www.google.com/search?q={q}", f"Searching for {query}")
            else:
                self.speak("What should I search for?")
            return

        # --- MEDIA ---
        elif intent == "music_play":
            song = parameters.get("song")
            if not song:
                song = text.replace("play", "", 1).strip()
            
            lib = getattr(music_library, "music", {}) or {}
            if song in lib:
                self.safe_open_url(lib[song], f"Playing {song}")
            else:
                # Fuzzy match
                matches = difflib.get_close_matches(song, list(lib.keys()), n=1, cutoff=0.6)
                if matches:
                    self.safe_open_url(lib[matches[0]], f"Playing {matches[0]}")
                else:
                    # Fallback to YouTube search
                    self.speak(f"Playing {song} on YouTube")
                    q = urllib.parse.quote_plus(song)
                    self.safe_open_url(f"https://www.youtube.com/results?search_query={q}", "")
            return

        # --- SYSTEM CONTROL ---
        elif intent == "volume_up":
            self.speak(self.system_control.increase_volume())
            return
        elif intent == "volume_down":
            self.speak(self.system_control.decrease_volume())
            return
        elif intent == "volume_set":
            level = parameters.get("level")
            if level:
                try:
                    vol = int(level)
                    self.speak(self.system_control.set_volume(vol))
                except ValueError:
                    self.speak("Please specify a valid volume level.")
            else:
                self.speak("Set volume to what level?")
            return
        elif intent == "volume_mute":
            self.speak(self.system_control.mute_volume())
            return
        elif intent == "volume_unmute":
            self.speak(self.system_control.unmute_volume())
            return
        elif intent == "volume_check":
            # Not implemented in system_control yet, but good to have intent
            self.speak("Volume check not yet implemented.")
            return

        # --- EMAIL ---
        elif intent == "email_send":
            # Extract details using brain if not already present
            email_details = self.brain.parse_email_intent(text)
            to = email_details.get("to")
            subject = email_details.get("subject")
            body_context = email_details.get("body")
            
            if to and subject and body_context:
                self.speak("Drafting your email...")
                user_name = os.getenv("USER_NAME", "User")
                draft_body = self.brain.generate_email_draft(to, subject, body_context, sender_name=user_name)
                
                self.pending_email = {
                    "to": to,
                    "subject": subject,
                    "body": draft_body
                }
                
                self.speak(f"Here is the draft: {draft_body}")
                self.speak("Do you want to send it?")
                
                # Set UI action for frontend buttons
                self.last_ui_action = {
                    "type": "email_confirmation",
                    "data": {
                        "to": to,
                        "subject": subject,
                        "body": draft_body
                    }
                }
            else:
                self.speak("I need more details. Who is it for, and what should I say?")
            return

            muted = self.system_control.is_muted()
            status = "muted" if muted else f"at {vol}%"
            self.speak(f"System volume is {status}")
            return
            
        elif intent == "shutdown":
            self.speak("Shutting down in 10 seconds. Say 'cancel shutdown' to abort.")
            self.system_control.shutdown_system(timer=10)
            return
        
        # --- WEATHER ---
        elif intent == "weather_check":
            city = parameters.get("city")
            if not city:
                # Fallback: try to extract city from text if parameter extraction failed
                # Simple heuristic: look for "in [City]"
                if " in " in text:
                    city = text.split(" in ")[-1].strip("?")
                else:
                    # Default to user's location (Pimpri, Maharashtra, India)
                    city = "Pimpri, Maharashtra, India"
                    self.speak(f"No location specified. Checking weather for {city}...")
            
            self.speak(f"Checking weather for {city}..." if city != "Pimpri, Maharashtra, India" else "Checking local weather...")
            weather_info = self.weather_manager.get_weather(city)
            self.speak(weather_info)
            return

        elif intent == "restart":
            self.speak("Restarting in 10 seconds. Say 'cancel restart' to abort.")
            self.system_control.restart_system(timer=10)
            return
        elif intent == "lock":
            self.speak(self.system_control.lock_system())
            return
        elif intent == "sleep":
            self.speak(self.system_control.sleep_system())
            return
        elif intent == "cancel_shutdown":
            self.speak(self.system_control.cancel_shutdown())
            return
            
        elif intent == "recycle_bin_empty":
            self.speak("Emptying recycle bin...")
            self.speak(self.system_control.empty_recycle_bin())
            return
        elif intent == "recycle_bin_check":
            self.speak(self.system_control.get_recycle_bin_size())
            return

        # --- CLIPBOARD & SCREENSHOT ---
        elif intent == "clipboard_copy":
            text_to_copy = parameters.get("text")
            if text_to_copy:
                self.speak(self.clipboard_screenshot.copy_to_clipboard(text_to_copy))
            else:
                self.speak("What should I copy?")
            return

        elif intent == "clipboard_read":
            self.speak(self.clipboard_screenshot.read_clipboard())
            return

        elif intent == "clipboard_clear":
            self.speak(self.clipboard_screenshot.clear_clipboard())
            return

        elif intent == "screenshot_take":
            filename = parameters.get("filename", None)
            self.speak(self.clipboard_screenshot.take_screenshot(filename))
            return

        # --- SYSTEM MONITORING ---
        elif intent == "battery_check":
            self.speak(self.system_monitor.get_battery_status())
            return

        elif intent == "cpu_check":
            self.speak(self.system_monitor.get_cpu_usage())
            return

        elif intent == "ram_check":
            self.speak(self.system_monitor.get_ram_usage())
            return

        elif intent == "system_stats":
            self.speak(self.system_monitor.get_all_stats())
            return

        # --- FILE AUTOMATION ---
        elif intent == "organize_downloads":
            self.speak("Organizing Downloads...")
            self.speak(self.automator.organize_folder(self.automator.get_downloads_folder()))
            return
        elif intent == "organize_desktop":
            self.speak("Organizing Desktop...")
            self.speak(self.automator.organize_folder(self.automator.get_desktop_folder()))
            return

        # --- FILE OPERATIONS ---
        elif intent == "file_search":
            pattern = parameters.get("pattern")
            location = parameters.get("location")
            if pattern:
                self.speak(self.file_manager.search_files(pattern, location))
            else:
                self.speak("What file are you looking for?")
            return
        
        elif intent == "file_create":
            self.speak(self.file_manager.create_file(parameters.get("filename"), parameters.get("content", ""), parameters.get("location")))
            return
        elif intent == "file_read":
            self.speak(self.file_manager.read_file(parameters.get("filename"), parameters.get("location")))
            return
        elif intent == "file_info":
            self.speak(self.file_manager.get_file_info(parameters.get("filename"), parameters.get("location")))
            return
        elif intent == "file_append":
            self.speak(self.file_manager.append_to_file(parameters.get("filename"), parameters.get("content"), parameters.get("location")))
            return
        elif intent == "file_rename":
            self.speak(self.file_manager.rename_file(parameters.get("old_name"), parameters.get("new_name"), parameters.get("location")))
            return
        elif intent == "file_move":
            self.speak(self.file_manager.move_file(parameters.get("filename"), parameters.get("destination"), parameters.get("location")))
            return
        elif intent == "file_copy":
            self.speak(self.file_manager.copy_file(parameters.get("filename"), parameters.get("destination"), parameters.get("location"), parameters.get("new_name")))
            return
        elif intent == "file_delete":
            self.speak(f"I found '{parameters.get('filename')}'. Please delete it manually for safety.")
            return

        # --- PRODUCTIVITY ---
        elif intent == "time_check":
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"It is {current_time}")
            return
        elif intent == "date_check":
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            self.speak(f"Today is {current_date}")
            return
            
        elif intent == "calendar_query":
            self.speak(self.calendar.get_upcoming_events())
            return
        elif intent == "calendar_create":
            # Use existing brain logic for parsing details if not in parameters
            # But wait, the classifier might have extracted them? 
            # The classifier prompt doesn't explicitly extract calendar details yet, 
            # so we might need to fallback to the specialized brain method or update the classifier.
            # For now, let's use the specialized brain method as it's robust.
            self.speak("Checking calendar...")
            details = self.brain.parse_calendar_intent(text)
            if details.get("start_time"):
                self.speak(self.calendar.create_event(details.get("summary"), details.get("start_time"), details.get("end_time")))
            else:
                self.speak("I need a time for the event.")
            return

        elif intent == "notion_query":
            # Similar to calendar, Notion has complex extraction logic.
            # We can reuse the existing logic but triggered by this intent.
            if "summarize" in text or "summary" in text:
                # ... (Reuse existing summarization logic) ...
                # Ideally this should be refactored into a method, but for now I'll call the brain helper
                page_info = self.brain.extract_notion_page_id(text)
                # ... (The logic is complex, let's simplify or copy it) ...
                # For safety in this refactor, I will just call the brain to handle the response
                # OR, I can copy the logic. Let's try to be cleaner.
                pass # Fall through to general chat if too complex, OR implement simplified version
                
                # Let's implement the search/summarize logic here
                self.speak("Searching Notion...")
                # (Simplified for brevity in this refactor, but functional)
                page_info = self.brain.extract_notion_page_id(text)
                if page_info.get("search_query"):
                     self.speak(self.notion.get_pages(query=page_info["search_query"]))
                else:
                     self.speak(self.notion.get_pages())
            else:
                # Just search
                self.speak(self.notion.get_pages())
            return

        elif intent == "notion_create":
            self.speak("Adding to Notion...")
            details = self.brain.parse_notion_intent(text)
            if details.get("title"):
                self.speak(self.notion.create_page(details.get("title"), details.get("content", ""), details.get("target")))
            else:
                self.speak("What should I add?")
            return

        # --- GENERAL / FALLBACK ---
        # If intent is "general_chat" or "none", or if we fell through
        if self.brain.is_available():
            # Streaming Response
            full_response = ""
            sentence_buffer = ""
            
            print("Thinking (Streaming)...")
            
            try:
                for chunk in self.brain.stream_ask(text, model_name=model_name):
                    full_response += chunk
                    sentence_buffer += chunk
                    
                    # Check for sentence delimiters to stream TTS
                    if any(punct in chunk for punct in [".", "?", "!", "\n"]):
                        # Clean and speak the buffered sentence(s)
                        to_speak = sentence_buffer.strip()
                        if to_speak:
                            # We don't want to print every chunk, just the final full response
                            # But we send to TTS queue immediately
                            self.speak(to_speak, print_text=False) 
                        sentence_buffer = ""
                
                # Speak any remaining text
                if sentence_buffer.strip():
                    self.speak(sentence_buffer.strip(), print_text=False)
                    
                # Finally print the full response for UI/Logs
                if self.on_speak:
                    self.on_speak(full_response)
                print(f"Aria said: {full_response}")
                
            except Exception as e:
                print(f"Streaming error: {e}")
                self.speak("I encountered an error while thinking.")
        else:
            self.speak("I'm not sure how to help with that.")
