import urllib.parse
import re
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
from .brains.planner_brain import PlannerBrain
from .safety.action_guard import ActionGuard
from .executor.desktop_executor import DesktopExecutor
from .brains.learning_manager import LearningManager
from .brains.shopping_agent import ShoppingAgent

from .intent_dispatcher import IntentDispatcher
from .logger import setup_logger

logger = setup_logger(__name__)

class CommandProcessor:
    def __init__(self, tts_manager, app_launcher, brain, calendar, notion, automator, 
                 system_control, command_classifier, file_manager, weather_manager, 
                 clipboard_screenshot, system_monitor, email_manager, greeting_service, music_manager, memory_manager, water_manager=None, connection_manager=None):

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
        self.water_manager = water_manager
        self.connection_manager = connection_manager
        self.search_manager = SearchManager()

        # Desktop Automation Components
        self.planner = PlannerBrain()
        self.guard = ActionGuard()
        self.executor = DesktopExecutor()
        self.learning_manager = LearningManager()
        self.shopping_agent = ShoppingAgent(self.brain, self.executor)

        
        self.wake_word = "aria"
        self.last_ui_action = None
        self.last_search_context = None # Store search results for follow-up questions
        self.last_intent_info = None # Store last executed intent for context corrections
        self.pending_music_suggestion = False # Track if we offered to play music
        self.stop_processing_flag = False # Flag to interrupt streaming/processing
        self.last_used_model_name = None # Track actual model used for generation
        
        # Pending states
        self.pending_automation_plan = None # Store plan awaiting confirmation
        
        # Short-term memory for context awareness (last 10 turns)
        self.conversation_history = []
        self.last_desktop_plan = None


        # Initialize Handlers
        self.music_handler = MusicHandler(self.tts_manager, self.music_manager)
        self.system_handler = SystemHandler(self.tts_manager, self.system_control, self.clipboard_screenshot, self.system_monitor)
        self.email_handler = EmailHandler(self.tts_manager, self.email_manager, self.brain)
        self.weather_handler = WeatherHandler(self.tts_manager, self.weather_manager, self.brain)
        self.file_handler = FileHandler(self.tts_manager, self.file_manager, self.automator, self.brain)
        self.notion_handler = NotionHandler(self.tts_manager, self.notion, self.brain)
        self.calendar_handler = CalendarHandler(self.tts_manager, self.calendar, self.brain)


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
                       "time_check", "date_check",
                       "wifi_on", "wifi_off", "wifi_check", "bluetooth_on", "bluetooth_off", "bluetooth_check"]:
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
        
        # Local Handlers (App & Web)
        self.dispatcher.register_handler("app_open", self.handle_app_open)
        self.dispatcher.register_handler("web_search", self.handle_web_search)
        self.dispatcher.register_handler("web_open", self.handle_web_open)
        
        # Development Tools
        self.dispatcher.register_handler("jupyter_open", self.handle_jupyter_open)

        # Desktop Automation
        self.dispatcher.register_handler("desktop_task", self.handle_desktop_task)
        
        # Shopping
        self.dispatcher.register_handler("shopping_task", self.handle_shopping_task)

    def _run_async_safely(self, coro):
        """Runs a coroutine safely, regardless of whether there is a running loop."""
        import asyncio
        import concurrent.futures
        
        try:
            # Check for running loop
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
            
        if loop and loop.is_running():
            # Run in a separate thread to avoid blocking the main loop context
            # or clashing with asyncio.run
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # We need to wrap the coroutine execution
                def run_coro():
                     return asyncio.run(coro)
                future = executor.submit(run_coro)
                return future.result()
        else:
            return asyncio.run(coro)

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
            search_results_list = self.search_manager.search(query)
            
            if search_results_list:
                # Convert list to string for LLM context
                formatted_results = "## Search Results:\n\n"
                for i, res in enumerate(search_results_list):
                   formatted_results += f"{i+1}. **{res['title']}**\n   {res['content']}\n   Source: {res['url']}\n\n"
                
                # Store context for follow-up questions
                self.last_search_context = formatted_results
                
                # Send UI Action to Display Cards
                self.last_ui_action = {
                    "type": "search_results",
                    "data": {
                        "results": search_results_list,
                        "query": query
                    }
                }
                
                # 2. Synthesize Answer using LLM
                self.tts_manager.speak("I found some results. Summarizing for you...")
                
                # Use the new search_context parameter in brain.ask
                answer = self.brain.ask(
                    f"Based on the search results, answer this query: {query}. VERY IMPORTANT: Cite sources using [1], [2] format at the end of sentences.", 
                    search_context=formatted_results
                )
                
                # Strip citations [1], [2] for speech
                clean_speech = re.sub(r'\[\d+\]', '', answer)
                self.tts_manager.speak(clean_speech)
                return answer
            else:
                self.tts_manager.speak("I couldn't find any results for that.")
                # Fallback to browser
                q = urllib.parse.quote_plus(query)
                self.safe_open_url(f"https://www.google.com/search?q={q}", "")
                return f"I couldn't find results for '{query}' here, so I opened Google for you."
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
            self.tts_manager.speak("I couldn't open Jupyter Notebook.")
            return f"Error opening Jupyter Notebook: {e}"

    def handle_desktop_task(self, text: str, intent: str, parameters: dict) -> str:
        """Handles desktop automation tasks via PlannerBrain."""
        self.tts_manager.speak("Analyzing desktop task...")
        
        # 1. Generate Plan
        import asyncio
        # Since this method is likely called synchronously, we might need to verify async execution
        # For now, we'll assume we can call async code or run it synchronously
        # But wait, existing handlers appear synchronous. 
        # Planner.generate_plan is async. We might need to run it in event loop.
        
        try:
            # Quick sync wrap for now
            plan = self._run_async_safely(self.planner.generate_plan(text))
            
            # 2. Validate Plan
            validation = self.guard.validate_plan(plan)
            if not validation["valid"]:
                logger.warning(f"Safety Gate blocked plan: {validation['reason']}")
                self.tts_manager.speak(f"I cannot execute that plan. {validation['reason']}")
                return f"Safety block: {validation['reason']}"
            
            # Save context
            self.last_desktop_plan = plan
            
            # 3. User Confirmation (Phase 1 rule: > 5 actions or high risk)
            # ALWAYS require confirmation for now to test UI
            action_count = len(plan.get("actions", []))
            self.tts_manager.speak(f"I've created a plan with {action_count} actions. Please review it.")
            
            self.pending_automation_plan = plan
            # Send UI Action
            self.last_ui_action = {
                "type": "desktop_confirmation",
                "data": plan
            }
            
            return "Please confirm the automation plan."
            
            # 4. Execute Plan (MOVED TO CONFIRMATION FLOW)
            # success = self._run_async_safely(self.executor.execute_plan(plan))
            
            # if success:
            #     return "Desktop task executed successfully."
            # else:
            #     self.tts_manager.speak("Something went wrong during execution.")
            #     return "Execution failed."
                
        except Exception as e:
            logger.error(f"Error in desktop task: {e}")
            self.tts_manager.speak("I encountered an error processing that task.")
            return f"Error: {e}"


    async def handle_shopping_task(self, text: str, intent: str, parameters: dict) -> str:
        """Handles shopping requests via ShoppingAgent."""
        product_query = text.replace("buy", "").replace("search for", "").replace("price of", "").replace("shop for", "").strip()
        
        self.tts_manager.speak(f"Shopping for {product_query}. I'll open some tabs for you to see.")
        
        # Define progress callback
        async def on_progress(data):
            # Send UI update
            if self.connection_manager:
                await self.connection_manager.broadcast({
                    "type": "shopping_status", 
                    "data": data 
                })
            # Also speak major updates? Maybe too chatty.
            msg = data.get("message", "")
            if "Found" in msg or "Comparing" in msg:
                 self.tts_manager.speak(msg, print_text=False)

        # Run Shopping Agent
        try:
            report = await self.shopping_agent.shop_for(product_query, on_progress)
            
            # Send Final Report to UI (Reuse search_results card or new type)
            self.last_ui_action = {
                "type": "markdown_report", 
                "data": {"title": f"Shopping Report: {product_query}", "content": report}
            }
            
            self.tts_manager.speak("I've finished the comparison. Check the report.")
            return report
            
        except Exception as e:
            logger.error(f"Shopping Task Failed: {e}")
            self.tts_manager.speak("Something went wrong while shopping.")
            return f"Error: {e}"

    async def handle_screen_query(self, text: str, intent: str, parameters: dict) -> str:
        """Handles visual queries about the screen content."""
        self.tts_manager.speak("Let me take a look at your screen...")
        
        try:
            # 1. Capture Screen
            if not self.executor.vision:
                return "I'm sorry, my vision system is not initialized."
                
            screenshot = self.executor.vision.capture_screen()
            
            # 2. Analyze
            if not screenshot:
                return "I couldn't capture the screen for some reason."
                
            # If user has a specific question ("What code is this?"), pass it.
            # Otherwise default to describe.
            prompt = text if len(text) > 10 else "Describe what is currently visible on my screen in detail."
            
            response = self.brain.analyze_image(screenshot, prompt)
            
            # 3. Output
            self.tts_manager.speak("Here is what I see.")
            return response
            
        except Exception as e:
            logger.error(f"Screen Query Failed: {e}")
            return f"I failed to analyze the screen: {e}"

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
            result = self.notion_handler.handle_interaction(text)
            if result:
                return result
            if self.notion_handler.has_pending_interaction():
                 return "Waiting for page selection."

        # 0.5. Desktop Automation Confirmation
        if self.pending_automation_plan:
            if any(x in text for x in ["yes", "proceed", "confirm", "do it", "run", "execute", "go ahead"]):
                self.tts_manager.speak("Executing plan.")
                plan = self.pending_automation_plan
                self.pending_automation_plan = None # Clear pending state
                
                # Execute Plan
                # Execute Plan with Progress Callback
                async def on_progress(idx, action, status, message=None):
                    if self.connection_manager:
                        await self.connection_manager.broadcast({
                            "type": "desktop_progress",
                            "data": {
                                "step_index": idx,
                                "action": action,
                                "status": status,
                                "message": message
                            }
                        })
                
                success = self._run_async_safely(self.executor.execute_plan(plan, on_update=on_progress))
                
                if success:
                    # Learn from success
                    # We use the text that GENERATED the plan. 
                    # But here 'text' is the confirmation "yes". 
                    # We need the original request.
                    # self.last_desktop_plan_request... needed.
                    if self.planner.last_request:
                        self.learning_manager.save_successful_plan(self.planner.last_request, plan)
                        
                    return "Desktop task executed successfully."
                else:
                    self.tts_manager.speak("Something went wrong during execution.")
                    return "Execution failed."
            elif any(x in text for x in ["no", "nope", "cancel", "don't", "stop"]):
                self.pending_automation_plan = None
                self.tts_manager.speak("Okay, automation cancelled.")
                return "Automation cancelled."
            else:
                 # If ambiguous, maybe let it fall through? Or force answer?
                 # For now, let's assume if they don't confirm, they might be asking something else.
                 # BUT, for safety, we should probably clear the plan if they change topic.
                 # Let's keep it simple: if they don't say yes/no, we keep pending? 
                 # No, better to clear it unless they are specifically interacting with it.
                 # Actually, similar to email, we might want to "wait" or allow "cancel". 
                 pass 

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

        # Update History (User)
        # We need to do this BEFORE classification so the classifier can see the *previous* context,
        # but the *current* message isn't technically "history" yet for classification purposes usually,
        # but for consistency we can append it after or treat it separately.
        # The classifier prompt handles "RECENT CONVERSATION HISTORY" separate from "USER COMMAND".
        # So we pass the history *before* appending the current text.
        
        history_to_use = conversation_history if conversation_history is not None else self.conversation_history

        # Classify the user's intent using the LLM (or use provided data)
        if intent_data:
            intent_results = intent_data
        else:
            intent_results = self.command_classifier.classify_intent(text, conversation_history=history_to_use)
            
        # Add User Message to History NOW (after classification usage)
        if conversation_history is None:
            self.conversation_history.append({"role": "user", "content": text})
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
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
            
            import inspect
            if inspect.iscoroutine(result):
                result = self._run_async_safely(result)
            
            if result:
                handled_any = True
                execution_responses.append(result)
                
                # Update Last Intent Info
                self.last_intent_info = {
                    "intent": intent,
                    "parameters": parameters,
                    "text": text,
                    "timestamp": datetime.datetime.now()
                }
                
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
            
            # Update History (System)
            if conversation_history is None:
                self.conversation_history.append({"role": "assistant", "content": final_response})
            
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
            # Determine actual model being used for UI feedback
            llm_instance = self.brain.get_llm(model_name)
            self.last_used_model_name = self.brain.get_model_name_from_llm(llm_instance)
            
            # --- TERMINAL OUTPUT FOR USER CHECK ---
            print(f"\n{'-'*40}")
            print(f"🤖 USING MODEL: {self.last_used_model_name}")
            print(f"   Requested: {model_name}")
            print(f"{'-'*40}\n")
            # --------------------------------------
            
            logger.info(f"Starting Streaming Response with {model_name} (Actual: {self.last_used_model_name})...")

            full_response = ""
            sentence_buffer = ""

            # Use stream_ask
            stream = self.brain.stream_ask(
                text, 
                model_name=model_name, 
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
            import traceback
            logger.error(f"Error in general_chat (streaming): {e}")
            traceback.print_exc()
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

