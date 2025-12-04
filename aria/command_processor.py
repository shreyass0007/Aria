import urllib.parse
import datetime
import difflib
from . import music_library
import os
import webbrowser
from langchain_core.messages import HumanMessage, SystemMessage
import random
from .search_manager import SearchManager
from .handlers.music_handler import MusicHandler
from .handlers.system_handler import SystemHandler
from .handlers.email_handler import EmailHandler
from .handlers.weather_handler import WeatherHandler
from .handlers.file_handler import FileHandler
from .handlers.notion_handler import NotionHandler
from .handlers.calendar_handler import CalendarHandler
from .logger import setup_logger

logger = setup_logger(__name__)

class CommandProcessor:
    def __init__(self, tts_manager, app_launcher, brain, calendar, notion, automator, 
                 system_control, command_classifier, file_manager, weather_manager, 
                 clipboard_screenshot, system_monitor, email_manager, greeting_service, music_manager, water_manager=None):
        self.tts_manager = tts_manager
        self.app_launcher = app_launcher
        self.brain = brain
        self.calendar = calendar
        self.notion = notion
        self.automator = automator
        self.system_control = system_control
        self.command_classifier = command_classifier
        self.file_manager = file_manager
        self.weather_manager = weather_manager
        self.clipboard_screenshot = clipboard_screenshot
        self.system_monitor = system_monitor
        self.email_manager = email_manager
        self.greeting_service = greeting_service
        self.greeting_service = greeting_service
        self.music_manager = music_manager
        self.water_manager = water_manager
        self.search_manager = SearchManager()
        
        self.wake_word = "aria"
        self.last_ui_action = None
        self.last_search_context = None # Store search results for follow-up questions
        self.pending_music_suggestion = False # Track if we offered to play music
        
        # Short-term memory for context awareness (last 10 turns)
        self.conversation_history = []

        # Initialize Handlers
        self.music_handler = MusicHandler(self.tts_manager, self.music_manager)
        self.system_handler = SystemHandler(self.tts_manager, self.system_control, self.clipboard_screenshot, self.system_monitor)
        self.email_handler = EmailHandler(self.tts_manager, self.email_manager, self.brain)
        self.weather_handler = WeatherHandler(self.tts_manager, self.weather_manager, self.brain)
        self.file_handler = FileHandler(self.tts_manager, self.file_manager, self.automator, self.brain)
        self.notion_handler = NotionHandler(self.tts_manager, self.notion, self.brain)
        self.calendar_handler = CalendarHandler(self.tts_manager, self.calendar, self.brain)


    def is_similar(self, a, b, threshold=0.8):
        return difflib.SequenceMatcher(None, a, b).ratio() >= threshold

    def safe_open_url(self, url: str, description: str = "") -> bool:
        try:
            ok = webbrowser.open(url)
            if not ok:
                self.tts_manager.speak("Sorry, I couldn't open that link.")
                return False
            if description:
                self.tts_manager.speak(description)
            return True
        except Exception as e:
            self.tts_manager.speak("Sorry, I couldn't open the link right now.")
            return False

    def _humanize_response(self, data_text: str, context: str = "calendar events") -> str:
        """Uses the LLM to convert raw data into a friendly, natural response."""
        if not self.brain or not self.brain.is_available():
            return data_text
            
        try:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            prompt = f"""
            You are Aria, a helpful AI assistant.
            The current time is {current_time}.
            
            Your task is to present the following SYSTEM DATA to the user.
            
            RULES:
            1. You MUST include the specific numbers, percentages, and details from the Raw Data.
            2. Do NOT be vague (e.g., avoid saying "It's running smoothly" without giving the % usage).
            3. Be friendly and conversational, but prioritize ACCURACY and DATA.
            4. If the data is a list of events, summarize them but include times and titles.
            
            Raw Data:
            {data_text}
            """
            llm = self.brain.get_llm()
            if llm:
                response = llm.invoke([
                    SystemMessage(content="You are Aria. Be friendly and concise."),
                    HumanMessage(content=prompt)
                ])
                result = response.content.strip()
                try:
                    logger.debug(f"Humanized response: {result.encode('utf-8', errors='ignore').decode('utf-8')}")
                except Exception:
                    logger.debug("Humanized response: [Content with emojis]")
                return result
            return data_text
        except Exception as e:
            logger.error(f"Error humanizing response: {e}")
            return data_text

    def _get_random_response(self, intent: str, context: str = "") -> str:
        """Returns a randomized response for simple intents."""
        responses = {
            "volume_up": [
                "Turning it up.", "Volume increased.", "Got it, louder.", "Boosting the volume."
            ],
            "volume_down": [
                "Turning it down.", "Volume decreased.", "Got it, quieter.", "Lowering the volume."
            ],
            "volume_mute": [
                "Muting audio.", "Silence.", "Sound off.", "Muted."
            ],
            "volume_unmute": [
                "Unmuting.", "Sound back on.", "Audio restored.", "Unmuted."
            ],
            "lock": [
                "Locking the screen.", "Securing the system.", "Locking up.", "Screen locked."
            ],
            "sleep": [
                "Going to sleep.", "Entering sleep mode.", "Goodnight.", "Sleeping now."
            ],
            "media_play": [
                f"Playing {context}.", f"Starting {context}.", f"Here is {context}.", f"Queuing up {context}."
            ],
            "app_open": [
                f"Opening {context}.", f"Launching {context}.", f"Starting {context} for you."
            ],
            "web_open": [
                f"Opening {context}.", f"Navigating to {context}.", f"Here's {context}."
            ]
        }
        
        options = responses.get(intent, [])
        if options:
            return random.choice(options)
        return f"Executing {intent}."

    def process_command(self, text: str, model_name: str = "openai", intent_data: dict = None, extra_data: dict = None, conversation_history: list = None, long_term_memory: list = None):
        text = text.lower().strip()
        if not text:
            return

        # PRIORITY: Check if user is responding to a Notion page selection prompt
        # This needs to be FIRST, before any other logic
        
        # PRIORITY: Check if user is responding to a Notion page selection prompt
        # This needs to be FIRST, before any other logic
        
        # 0. Email Confirmation
        if self.email_handler.has_pending_interaction():
            result = self.email_handler.handle_interaction(text, extra_data)
            if result:
                return result
            # If result is None, it might mean we fell through or cancelled.
            # If pending_email is now None, we proceed to normal classification.
            if not self.email_handler.has_pending_interaction():
                pass # Continue to normal processing
            else:
                return "Waiting for email confirmation."

        if self.notion_handler.has_pending_interaction():
            result = self.notion_handler.handle_interaction(text)
            if result:
                return result
            if self.notion_handler.has_pending_interaction():
                 return "Waiting for page selection."
        if self.pending_music_suggestion:
            if any(x in text for x in ["yes", "yep", "sure", "okay", "please", "do it"]):
                self.tts_manager.speak("Great! Playing a random hit for you.")
                # Pick a random popular song
                songs = ["Blinding Lights", "Levitating", "Shape of You", "Bohemian Rhapsody", "Stay", "As It Was", "Anti-Hero"]
                song = random.choice(songs)
                self.pending_music_suggestion = False
                return self.music_manager.play_music(song)
            elif any(x in text for x in ["no", "nope", "cancel", "don't"]):
                self.tts_manager.speak("Okay, maybe later.")
                self.pending_music_suggestion = False
                return "Music suggestion declined."
            else:
                # If they say something else, assume it's a new command or a song name
                # If it looks like a song name, we could try to play it, but let's fall through to normal intent classification
                self.pending_music_suggestion = False
                # Fall through

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
        if text == self.wake_word:
            greeting = self.greeting_service.get_time_based_greeting()
            self.tts_manager.speak(greeting)
            return greeting

        
        # If user says "WakeWord command...", strip it
        if text.startswith(self.wake_word + " "):
            text = text[len(self.wake_word):].strip()

        # Change Wake Word
        if "change wake word to" in text:
            new_word = text.replace("change wake word to", "").strip()
            if new_word:
                self.wake_word = new_word
                self.tts_manager.speak(f"Wake word changed to {self.wake_word}")
            return f"Wake word changed to {self.wake_word}"

        # Daily Briefing Trigger
        if any(x in text for x in ["good morning", "morning briefing", "daily briefing", "brief me"]):
            self.tts_manager.speak("Good morning! Gathering your briefing...")
            briefing = self.greeting_service.get_morning_briefing()
            self.tts_manager.speak(briefing)
            return briefing

        # Water Reminder Trigger
        if self.water_manager:
            if any(x in text for x in ["start water reminder", "remind me to drink water", "enable water reminder"]):
                msg = self.water_manager.start_monitoring()
                self.tts_manager.speak(msg)
                return msg
            elif any(x in text for x in ["stop water reminder", "disable water reminder", "cancel water reminder"]):
                msg = self.water_manager.stop_monitoring()
                self.tts_manager.speak(msg)
                return msg
            elif "water reminder" in text and ("every" in text or "min" in text):
                # Extract minutes
                import re
                minutes = re.findall(r'(\d+)\s*(?:minute|min|mins|minutes)', text)
                if minutes:
                    interval = int(minutes[0])
                    self.water_manager.set_interval(interval)
                    msg = self.water_manager.start_monitoring() # Restart with new interval
                    self.tts_manager.speak(msg)
                    return msg
                else:
                    self.tts_manager.speak("How many minutes should I set the reminder for?")
                    return "Please specify minutes."
            elif "drank water" in text or "i drank water" in text:
                msg = self.water_manager.reset_timer()
                self.tts_manager.speak(msg)
                return msg

        # Identity
        if any(x in text for x in ["who are you", "what is your name", "introduce yourself"]):
            # Use LLM for identity to be more natural
            response = self.brain.ask(text)
            self.tts_manager.speak(response)
            return response

        # Sing Song Request
        if any(x in text for x in ["sing a song", "sing song", "can you sing", "sing for me"]):
            self.tts_manager.speak("I wish I could sing! But I can play some music for you instead. Want me to play a random hit?")
            self.pending_music_suggestion = True
            return "Offered to play music."

        # Mode Switching
        if any(x in text for x in ["activate coder mode", "enable coder mode", "coder mode on", "switch to coder mode"]):
            msg = self.brain.set_mode("coder")
            self.tts_manager.speak(msg)
            self.last_ui_action = {"type": "mode_change", "data": {"mode": "coder"}}
            return msg
        elif any(x in text for x in ["activate study mode", "enable study mode", "study mode on", "switch to study mode"]):
            msg = self.brain.set_mode("study")
            self.tts_manager.speak(msg)
            self.last_ui_action = {"type": "mode_change", "data": {"mode": "study"}}
            return msg
        elif any(x in text for x in ["activate jarvis mode", "enable jarvis mode", "jarvis mode on", "switch to jarvis mode"]):
            msg = self.brain.set_mode("jarvis")
            self.tts_manager.speak(msg)
            self.last_ui_action = {"type": "mode_change", "data": {"mode": "jarvis"}}
            return msg
        elif any(x in text for x in ["normal mode", "reset mode", "exit mode", "disable mode", "mode off"]):
            msg = self.brain.set_mode("normal")
            self.tts_manager.speak(msg)
            self.last_ui_action = {"type": "mode_change", "data": {"mode": "normal"}}
            return msg

        # Clear Context / New Topic
        if any(x in text for x in ["new topic", "clear memory", "forget context", "start over"]):
            self.conversation_history = []
            self.tts_manager.speak("Okay, starting fresh. What's on your mind?")
            return "Context cleared."

        # ---------------------------------------------------------
        # CENTRALIZED INTENT CLASSIFICATION
        # ---------------------------------------------------------
        
        # Classify the user's intent using the LLM (or use provided data)
        if intent_data:
            intent_result = intent_data
        else:
            intent_result = self.command_classifier.classify_intent(text)
            
        intent = intent_result.get("intent")
        confidence = intent_result.get("confidence", 0.0)
        parameters = intent_result.get("parameters", {})
        
        logger.info(f"Intent: {intent}, Confidence: {confidence}, Params: {parameters}")
        
        # Dispatch based on intent
        
        if intent == "app_open":
            app_name = parameters.get("app_name")
            if app_name:
                self.tts_manager.speak(self._get_random_response("app_open", app_name))
                self.app_launcher.open_desktop_app(app_name)
            else:
                # Fallback
                target = text.replace("open", "").strip()
                self.tts_manager.speak(self._get_random_response("app_open", target))
                self.app_launcher.open_desktop_app(target)
                return f"Opening {target}."
            return f"Opening {app_name}."

        elif intent == "web_search":
            query = parameters.get("query")
            if not query:
                # Fallback extraction
                query = text.replace("google", "").replace("search", "").replace("for", "").strip()
            
            if query:
                self.tts_manager.speak(f"Searching for {query}...")
                
                # Resolve relative dates (yesterday, today, tomorrow) for better search accuracy
                query = self._resolve_relative_dates(query)
                logger.debug(f"Resolved query: {query}")

                # 1. Perform Real-Time Search
                search_results = self.search_manager.search(query)
                try:
                    logger.debug(f"Raw Search Results:\n{search_results.encode('utf-8', errors='ignore').decode('utf-8')}")
                except Exception:
                    logger.debug("Raw Search Results: [Content with unicode]")
                
                if search_results:
                    # Store context for follow-up questions
                    self.last_search_context = search_results
                    
                    # 2. Synthesize Answer using LLM
                    self.tts_manager.speak("I found some results. Summarizing for you...")
                    
                    # Use the new search_context parameter in brain.ask
                    answer = self.brain.ask(
                        f"Based on the search results, answer this query: {query}", 
                        search_context=search_results
                    )
                    
                    self.tts_manager.speak(answer)
                else:
                    self.tts_manager.speak("I couldn't find any results for that.")
                    # Fallback to browser
                    q = urllib.parse.quote_plus(query)
                    self.safe_open_url(f"https://www.google.com/search?q={q}", "")
            else:
                self.tts_manager.speak("What should I search for?")
                return "Please specify what to search for."
            return f"Searching for {query}."

        # --- MEDIA ---
        if self.music_handler.should_handle(intent):
            result = self.music_handler.handle(text, intent, parameters)
            if result:
                if intent == "music_play":
                     # Set UI action to show music player
                    track_info = self.music_manager.current_track_info
                    self.last_ui_action = {
                        "type": "music_playing",
                        "data": {
                            "track_info": track_info
                        }
                    }
                return result

        # --- SYSTEM CONTROL ---
        if self.system_handler.should_handle(intent):
            result = self.system_handler.handle(text, intent, parameters)
            if result:
                return result
        # --- EMAIL ---
        if self.email_handler.should_handle(intent):
            result = self.email_handler.handle(text, intent, parameters)
            if result:
                if intent == "email_send":
                    # Set UI action for frontend buttons
                    # We need to access pending_email from handler
                    pending = self.email_handler.pending_email
                    if pending:
                        self.last_ui_action = {
                            "type": "email_confirmation",
                            "data": {
                                "to": pending["to"],
                                "subject": pending["subject"],
                                "body": pending["body"]
                            }
                        }
                return result

        # --- WEATHER ---
        if self.weather_handler.should_handle(intent):
            result = self.weather_handler.handle(text, intent, parameters)
            if result:
                return result

        # --- FILE AUTOMATION & OPERATIONS ---
        if self.file_handler.should_handle(intent):
            result = self.file_handler.handle(text, intent, parameters)
            if result:
                return result

        # --- CALENDAR ---
        if self.calendar_handler.should_handle(intent):
            result = self.calendar_handler.handle(text, intent, parameters)
            if result:
                return result

        # --- NOTION ---
        if self.notion_handler.should_handle(intent):
            result = self.notion_handler.handle(text, intent, parameters)
            if result:
                return result

        # --- FALLBACK ---
        # If no specific intent matched, use LLM for general chat
        # Use ask() instead of query_llm() to leverage the new system prompt AND conversation history
        
        # Use passed history if available, else use internal
        history_to_use = conversation_history if conversation_history is not None else self.conversation_history
        
        # Add user message to internal history if not using external
        if conversation_history is None:
            self.conversation_history.append({"role": "user", "content": text})
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
        # Pass last_search_context to allow follow-up questions about previous search
        try:
            response = self.brain.ask(
                text, 
                conversation_history=history_to_use,
                long_term_context=long_term_memory,
                search_context=self.last_search_context
            )
            
            # Add assistant response to internal history if not using external
            if conversation_history is None:
                self.conversation_history.append({"role": "assistant", "content": response})
            
            self.tts_manager.speak(response)
            return response
        except Exception as e:
            print(f"Error in general_chat: {e}")
            return "I'm having trouble thinking right now. Please try again."

    def _resolve_relative_dates(self, text: str) -> str:
        """Replaces relative date terms (today, yesterday, tomorrow) with actual dates."""
        import datetime
        import re
        
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)
        
        date_format = "%b %d, %Y" # e.g., Nov 30, 2025
        
        # Case-insensitive replacements
        text = re.sub(r'\byesterday\b', yesterday.strftime(date_format), text, flags=re.IGNORECASE)
        text = re.sub(r'\btoday\b', today.strftime(date_format), text, flags=re.IGNORECASE)
        text = re.sub(r'\btomorrow\b', tomorrow.strftime(date_format), text, flags=re.IGNORECASE)
        
        return text

    @property
    def pending_email(self):
        return self.email_handler.pending_email

    @pending_email.setter
    def pending_email(self, value):
        self.email_handler.pending_email = value

    @property
    def pending_notion_pages(self):
        return self.notion_handler.pending_notion_pages

    @pending_notion_pages.setter
    def pending_notion_pages(self, value):
        self.notion_handler.pending_notion_pages = value
