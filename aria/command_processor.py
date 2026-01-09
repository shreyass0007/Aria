import urllib.parse
import datetime
import difflib
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
from .handlers.vision_handler import VisionHandler
from .intent_dispatcher import IntentDispatcher
from .logger import setup_logger

logger = setup_logger(__name__)

class CommandProcessor:
    def __init__(self, tts_manager, app_launcher, brain, calendar, notion, automator, 
                 system_control, command_classifier, file_manager, weather_manager, 
                 clipboard_screenshot, system_monitor, email_manager, greeting_service, music_manager, memory_manager, water_manager=None, vision_pipeline_factory=None):

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
        self.music_manager = music_manager
        self.memory_manager = memory_manager
        self.water_manager = water_manager
        self.search_manager = SearchManager()
        
        self.wake_word = "aria"
        self.last_ui_action = None
        self.last_search_context = None # Store search results for follow-up questions
        self.pending_music_suggestion = False # Track if we offered to play music
        self.stop_processing_flag = False # Flag to interrupt streaming/processing
        
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
        self.vision_handler = VisionHandler(self.tts_manager, self.brain, vision_pipeline_factory)

        # Initialize Intent Dispatcher
        self.dispatcher = IntentDispatcher()
        self._register_intents()

    def stop_current_processing(self):
        """Signals the processor to stop generating/speaking the current response."""
        self.stop_processing_flag = True
        self.tts_manager.stop()

    def _register_intents(self):
        """Registers all intents with the dispatcher."""
        # Music
        for intent in ["music_play", "music_pause", "music_resume", "music_stop", "music_volume"]:
            self.dispatcher.register_handler(intent, self.music_handler.handle)
        
        # System
        for intent in ["volume_up", "volume_down", "volume_mute", "volume_unmute", "lock", "sleep", 
                       "shutdown", "restart", "cancel_shutdown", "recycle_bin_empty", "recycle_bin_check", 
                       "screenshot_take", "clipboard_copy", "clipboard_read", "clipboard_clear", 
                       "battery_check", "cpu_check", "ram_check", "system_stats",
                       "time_check", "date_check"]:
            self.dispatcher.register_handler(intent, self.system_handler.handle)
            
        # Email
        for intent in ["email_send", "email_check"]:
            self.dispatcher.register_handler(intent, self.email_handler.handle)
            
        # Weather
        self.dispatcher.register_handler("weather_check", self.weather_handler.handle)
        
        # File
        for intent in ["file_create", "file_read", "file_info", "file_append", "file_replace", 
                       "file_delete", "file_rename", "file_move", "file_copy", "file_search", 
                       "organize_downloads", "organize_desktop"]:
            self.dispatcher.register_handler(intent, self.file_handler.handle)
            
        # Calendar
        for intent in ["calendar_query", "calendar_create"]:
            self.dispatcher.register_handler(intent, self.calendar_handler.handle)
            
        # Notion
        for intent in ["notion_query", "notion_create"]:
            self.dispatcher.register_handler(intent, self.notion_handler.handle)

        # Vision
        self.dispatcher.register_handler("screen_analysis", self.vision_handler.handle)

        # Local Handlers (App & Web)
        self.dispatcher.register_handler("app_open", self.handle_app_open)
        self.dispatcher.register_handler("web_search", self.handle_web_search)
        self.dispatcher.register_handler("web_open", self.handle_web_open)
        
        # Development Tools
        self.dispatcher.register_handler("jupyter_open", self.handle_jupyter_open)

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
            You are Aria, a close friend and assistant.
            The current time is {current_time}.
            
            Your task is to present the following SYSTEM DATA to your friend.
            
            RULES:
            1. You MUST include the specific numbers/details from the Raw Data.
            2. Be casual and chatty. Use "Looks like", "We're running", "Check this out".
            3. Don't be robotic.
            
            Raw Data:
            {data_text}
            """
            llm = self.brain.get_llm()
            if llm:
                response = llm.invoke([
                    SystemMessage(content="You are Aria. Be friendly and casual."),
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
            "app_open": [
                f"Opening {context} for you.", f"Launching {context}.", f"Starting {context}.", f"Here comes {context}.", f"Got it, opening {context}."
            ],
            "web_open": [
                f"Opening {context}.", f"Navigating to {context}.", f"Here's {context}.", f"Loading {context} now."
            ]
        }
        
        options = responses.get(intent, [])
        if options:
            return random.choice(options)
        return f"Executing {intent}."

    def handle_app_open(self, text: str, intent: str, parameters: dict) -> str:
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

    def handle_web_search(self, text: str, intent: str, parameters: dict) -> str:
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

    def handle_web_open(self, text: str, intent: str, parameters: dict) -> str:
        url = parameters.get("url")
        name = parameters.get("name", url)
        if url:
            self.tts_manager.speak(self._get_random_response("web_open", name))
            self.safe_open_url(url)
            return f"Opening {name}."
        return "No URL provided."

    def handle_jupyter_open(self, text: str, intent: str, parameters: dict) -> str:
        """Opens Jupyter Notebook at the configured directory."""
        import subprocess
        import os
        
        jupyter_dir = r"D:\CODEING"
        
        if not os.path.exists(jupyter_dir):
            self.tts_manager.speak("The coding directory was not found.")
            return "Directory not found."
        
        self.tts_manager.speak("Opening Jupyter Notebook.")
        
        try:
            # Start Jupyter Notebook in the specified directory
            subprocess.Popen(
                ["jupyter", "notebook"],
                cwd=jupyter_dir,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            return "Opening Jupyter Notebook."
        except FileNotFoundError:
            self.tts_manager.speak("Jupyter Notebook is not installed or not in the system path.")
            return "Jupyter Notebook not found. Please ensure it's installed."
        except Exception as e:
            logger.error(f"Error opening Jupyter Notebook: {e}")
            self.tts_manager.speak("I couldn't open Jupyter Notebook.")
            return f"Error opening Jupyter Notebook: {e}"

    def process_command(self, text: str, model_name: str = "openai", intent_data: dict = None, extra_data: dict = None, conversation_history: list = None, long_term_memory: list = None):
        text = text.lower().strip()
        if not text:
            return

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
            briefing = self.greeting_service.get_morning_briefing(force=True)
            if briefing:
                self.tts_manager.speak(briefing)
                return briefing
            else:
                fallback = "Good morning! I couldn't generate the full briefing, but I'm ready to help."
                self.tts_manager.speak(fallback)
                return fallback

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
        # Classify the user's intent using the LLM (or use provided data)
        if intent_data:
            intent_results = intent_data
        else:
            intent_results = self.command_classifier.classify_intent(text)
            
        # Ensure it's a list
        if isinstance(intent_results, dict):
            intent_results = [intent_results]
            
        execution_responses = []
        handled_any = False
        
        for intent_item in intent_results:
            intent = intent_item.get("intent")
            confidence = intent_item.get("confidence", 0.0)
            parameters = intent_item.get("parameters", {})
            
            logger.info(f"Processing Intent: {intent}, Confidence: {confidence}, Params: {parameters}")
            
            if intent == "general_chat" or intent == "none":
                continue

            # Dispatch using IntentDispatcher
            result = self.dispatcher.dispatch(intent, text, parameters)
            
            if result:
                handled_any = True
                execution_responses.append(result)
                
                # Handle UI Actions based on intent (Post-processing)
                if intent == "music_play":
                    track_info = self.music_manager.current_track_info
                    self.last_ui_action = {
                        "type": "music_playing",
                        "data": {
                            "track_info": track_info
                        }
                    }
                elif intent == "email_send":
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
        
        if handled_any:
            final_response = " ".join(execution_responses)
            # If we have multiple responses, maybe we don't want to speak them all if they are repetitive?
            # But for now, let's just join them.
            return final_response

        # --- FALLBACK ---
        # If no specific intent matched (or dispatcher returned None), use LLM for general chat
        # Use ask() instead of query_llm() to leverage the new system prompt AND conversation history
        
        # Use passed history if available, else use internal
        history_to_use = conversation_history if conversation_history is not None else self.conversation_history
        
        # --- LONG TERM MEMORY RETRIEVAL ---
        if long_term_memory is None and self.memory_manager:
            # Search for relevant past context based on user text
            logger.info("Searching long-term memory...")
            long_term_memory = self.memory_manager.search_relevant_context(text)

        
        # Add user message to internal history if not using external
        if conversation_history is None:
            self.conversation_history.append({"role": "user", "content": text})
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
        # Pass last_search_context to allow follow-up questions about previous search
        try:
            logger.info("Starting Streaming Response with GPT-4o-mini...")
            # Use 'gpt-4o-mini' for general chat to improve speed (or make it configurable)
            # Streaming Logic
            full_response = ""
            sentence_buffer = ""
            
            # Use stream_ask
            stream = self.brain.stream_ask(
                text, 
                model_name="gpt-4o-mini", # FAST MODEL
                conversation_history=history_to_use,
                long_term_context=long_term_memory,
                search_context=self.last_search_context
            )
            
            import re
            
            # Reset flag before starting
            self.stop_processing_flag = False
            
            for token in stream:
                # CHECK INTERRUPTION
                if self.stop_processing_flag:
                    logger.info("Command processing interrupted by new wake word.")
                    return "Interrupted."

                full_response += token
                sentence_buffer += token
                
                # Check for sentence delimiters
                if re.search(r'[.!?\n]\s*$', sentence_buffer):
                    chunk_to_speak = sentence_buffer.strip()
                    if chunk_to_speak:
                        self.tts_manager.speak(chunk_to_speak)
                        sentence_buffer = ""
            
            # Speak any remaining text
            if sentence_buffer.strip() and not self.stop_processing_flag:
                self.tts_manager.speak(sentence_buffer.strip())
            
            # Add assistant response to internal history if not using external
            if conversation_history is None:
                self.conversation_history.append({"role": "assistant", "content": full_response})
            
            # --- SAVE TO LONG TERM MEMORY ---
            if self.memory_manager:
                conversation_id = "default_session" 
                self.memory_manager.add_message(conversation_id, text, "user")
                self.memory_manager.add_message(conversation_id, full_response, "assistant")
            
            return full_response
        except Exception as e:
            logger.error(f"Error in general_chat (streaming): {e}")
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
        text = re.sub(r'\\byesterday\\b', yesterday.strftime(date_format), text, flags=re.IGNORECASE)
        text = re.sub(r'\\btoday\\b', today.strftime(date_format), text, flags=re.IGNORECASE)
        text = re.sub(r'\\btomorrow\\b', tomorrow.strftime(date_format), text, flags=re.IGNORECASE)
        
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

