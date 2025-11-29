import urllib.parse
import datetime
import difflib
import music_library
import os
import webbrowser
from langchain_core.messages import HumanMessage, SystemMessage
import random

class CommandProcessor:
    def __init__(self, tts_manager, app_launcher, brain, calendar, notion, automator, 
                 system_control, command_classifier, file_manager, weather_manager, 
                 clipboard_screenshot, system_monitor, email_manager, greeting_service):
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
        
        self.wake_word = "aria"
        self.pending_email = None
        self.pending_notion_pages = None
        self.last_ui_action = None

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
            prompt = f"""
            You are Aria, a helpful AI assistant.
            Convert the following raw data about {context} into a friendly, conversational response.
            Keep it concise (max 2 sentences) and natural.
            
            Raw Data:
            {data_text}
            """
            llm = self.brain.get_llm()
            if llm:
                response = llm.invoke([
                    SystemMessage(content="You are Aria. Be friendly and concise."),
                    HumanMessage(content=prompt)
                ])
                return response.content.strip()
            return data_text
        except Exception as e:
            print(f"Error humanizing response: {e}")
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

    def process_command(self, text: str, model_name: str = "openai", intent_data: dict = None):
        text = text.lower().strip()
        if not text:
            return

        # PRIORITY: Check if user is responding to a Notion page selection prompt
        # This needs to be FIRST, before any other logic
        
        # 0. Email Confirmation
        if self.pending_email:
            # CRITICAL FIX: Check if user is issuing a NEW command instead of confirming
            # If they say "send mail to..." or "draft email...", it's a new request, not a confirmation.
            if any(x in text for x in ["send mail", "send email", "draft email", "compose email"]):
                self.tts_manager.speak("Discarding previous draft and starting a new one.")
                self.pending_email = None
                # Fall through to intent classifier
            
            elif any(x in text for x in ["yes", "send", "confirm", "okay", "sure"]):
                self.tts_manager.speak("Sending email...")
                to = self.pending_email["to"]
                subject = self.pending_email["subject"]
                body = self.pending_email["body"]
                result = self.email_manager.send_email(to, subject, body)
                self.tts_manager.speak(result)
                self.pending_email = None
                return
            elif any(x in text for x in ["no", "cancel", "don't send", "stop"]):
                self.tts_manager.speak("Email cancelled.")
                self.pending_email = None
                return
            else:
                self.tts_manager.speak("Please say 'yes' to send or 'no' to cancel.")
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
                    self.tts_manager.speak(f"Great! Fetching {page_title}...")
                    page_data = self.notion.get_page_content(page_id)
                    
                    if page_data.get("status") == "error":
                        self.tts_manager.speak(page_data.get("error", "Unable to fetch the page."))
                        return
                    
                    content = page_data.get("content", "")
                    self.tts_manager.speak(f"Summarizing {page_title}...")
                    summary = self.brain.summarize_text(content, max_sentences=5)
                    
                    # Format structured output with clean markdown
                    word_count = page_data.get("word_count", 0)
                    
                    structured_output = f"""## 📄 Notion Page Summary

**Page:** {page_title}  
**Word Count:** {word_count} words

---

### 💡 Summary
{summary}

---
"""
                    self.tts_manager.speak(structured_output)
                    return
                else:
                    # Invalid selection
                    self.tts_manager.speak("I didn't understand your selection. Please say a number like 'one', 'two', or 'three'.")
                    # Don't clear pending_notion_pages - let them try again
                    return
                    
            except Exception as e:
                print(f"Error processing selection: {e}")
                self.pending_notion_pages = None
                self.tts_manager.speak("Sorry, I had trouble with that. Let's start over.")
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
        if text == self.wake_word:
            greeting = self.greeting_service.get_time_based_greeting()
            self.tts_manager.speak(greeting)
            return

        
        # If user says "WakeWord command...", strip it
        if text.startswith(self.wake_word + " "):
            text = text[len(self.wake_word):].strip()

        # Change Wake Word
        if "change wake word to" in text:
            new_word = text.replace("change wake word to", "").strip()
            if new_word:
                self.wake_word = new_word
                self.tts_manager.speak(f"Wake word changed to {self.wake_word}")
            else:
                self.tts_manager.speak("Change it to what?")
            return

        # Identity
        if any(x in text for x in ["who are you", "what is your name", "introduce yourself"]):
            # Use LLM for identity to be more natural
            self.tts_manager.speak(self.brain.ask(text))
            return

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
        
        print(f"DEBUG: Intent: {intent}, Confidence: {confidence}, Params: {parameters}")
        
        # Dispatch based on intent
        
        # --- WEB & APPS ---
        if intent == "web_open":
            url = parameters.get("url")
            name = parameters.get("name", "site")
            if url:
                self.tts_manager.speak(self._get_random_response("web_open", name))
                self.safe_open_url(url, "")
            else:
                # Fallback if URL not extracted
                target = text.replace("open", "").strip()
                if target:
                    self.tts_manager.speak(self._get_random_response("web_open", target))
                    self.safe_open_url(f"https://{target}.com", "")
                else:
                    self.tts_manager.speak("What website should I open?")
            return

        elif intent == "app_open":
            app_name = parameters.get("app_name")
            if app_name:
                self.tts_manager.speak(self._get_random_response("app_open", app_name))
                self.app_launcher.open_desktop_app(app_name)
            else:
                # Fallback
                target = text.replace("open", "").strip()
                self.tts_manager.speak(self._get_random_response("app_open", target))
                self.app_launcher.open_desktop_app(target)
            return

        elif intent == "web_search":
            query = parameters.get("query")
            if not query:
                # Fallback extraction
                query = text.replace("google", "").replace("search", "").replace("for", "").strip()
            
            if query:
                q = urllib.parse.quote_plus(query)
                self.tts_manager.speak(f"Searching for {query}...")
                self.safe_open_url(f"https://www.google.com/search?q={q}", "")
            else:
                self.tts_manager.speak("What should I search for?")
            return

        # --- MEDIA ---
        elif intent == "music_play":
            song = parameters.get("song")
            if not song:
                song = text.replace("play", "", 1).strip()
            
            self.tts_manager.speak(self._get_random_response("media_play", song))
            
            lib = getattr(music_library, "music", {}) or {}
            if song in lib:
                self.safe_open_url(lib[song], "")
            else:
                # Fuzzy match
                matches = difflib.get_close_matches(song, list(lib.keys()), n=1, cutoff=0.6)
                if matches:
                    self.safe_open_url(lib[matches[0]], "")
                else:
                    # Fallback to YouTube search
                    q = urllib.parse.quote_plus(song)
                    self.safe_open_url(f"https://www.youtube.com/results?search_query={q}", "")
            return

        # --- SYSTEM CONTROL ---
        elif intent == "volume_up":
            self.system_control.increase_volume()
            self.tts_manager.speak(self._get_random_response("volume_up"))
            return
        elif intent == "volume_down":
            self.system_control.decrease_volume()
            self.tts_manager.speak(self._get_random_response("volume_down"))
            return
        elif intent == "volume_set":
            level = parameters.get("level")
            if level:
                try:
                    vol = int(level)
                    self.system_control.set_volume(vol)
                    self.tts_manager.speak(f"Volume set to {vol}.")
                except ValueError:
                    self.tts_manager.speak("Please specify a valid volume level.")
            else:
                self.tts_manager.speak("Set volume to what level?")
            return
        elif intent == "volume_mute":
            self.system_control.mute_volume()
            self.tts_manager.speak(self._get_random_response("volume_mute"))
            return
        elif intent == "volume_unmute":
            self.system_control.unmute_volume()
            self.tts_manager.speak(self._get_random_response("volume_unmute"))
            return
        elif intent == "volume_check":
            # Not implemented in system_control yet, but good to have intent
            self.tts_manager.speak("Volume check not yet implemented.")
            return

        # --- EMAIL ---
        elif intent == "email_send":
            # Extract details using brain if not already present
            email_details = self.brain.parse_email_intent(text)
            to = email_details.get("to")
            subject = email_details.get("subject")
            body_context = email_details.get("body")
            
            if to and subject and body_context:
                self.tts_manager.speak("Drafting your email...")
                user_name = os.getenv("USER_NAME", "User")
                draft_body = self.brain.generate_email_draft(to, subject, body_context, sender_name=user_name)
                
                self.pending_email = {
                    "to": to,
                    "subject": subject,
                    "body": draft_body
                }
                
                self.tts_manager.speak("I have created a draft for you.")
                self.tts_manager.speak("Do you want to send it?")
                
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
                self.tts_manager.speak("I need more details. Who is it for, and what should I say?")
            return

        elif intent == "shutdown":
            self.tts_manager.speak("Shutting down in 10 seconds. Say 'cancel shutdown' to abort.")
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
                    self.tts_manager.speak(f"Checking weather for {city}...")
            
            weather_info = self.weather_manager.get_weather(city)
            # Use LLM to humanize the weather report
            humanized_weather = self._humanize_response(weather_info, f"current weather in {city}")
            self.tts_manager.speak(humanized_weather)
            return

        elif intent == "restart":
            self.tts_manager.speak("Restarting in 10 seconds. Say 'cancel restart' to abort.")
            self.system_control.restart_system(timer=10)
            return
        elif intent == "lock":
            self.system_control.lock_system()
            self.tts_manager.speak(self._get_random_response("lock"))
            return
        elif intent == "sleep":
            self.system_control.sleep_system()
            self.tts_manager.speak(self._get_random_response("sleep"))
            return
        elif intent == "cancel_shutdown":
            self.tts_manager.speak(self.system_control.cancel_shutdown())
            return
            
        elif intent == "recycle_bin_empty":
            self.tts_manager.speak("Emptying recycle bin...")
            self.tts_manager.speak(self.system_control.empty_recycle_bin())
            return
        elif intent == "recycle_bin_check":
            self.tts_manager.speak(self.system_control.get_recycle_bin_size())
            return

        # --- CLIPBOARD & SCREENSHOT ---
        elif intent == "clipboard_copy":
            text_to_copy = parameters.get("text")
            if text_to_copy:
                self.clipboard_screenshot.copy_to_clipboard(text_to_copy)
                self.tts_manager.speak("Copied to clipboard.")
            else:
                self.tts_manager.speak("What should I copy?")
            return

        elif intent == "clipboard_read":
            content = self.clipboard_screenshot.read_clipboard()
            self.tts_manager.speak(f"Clipboard contains: {content}")
            return

        elif intent == "clipboard_clear":
            self.clipboard_screenshot.clear_clipboard()
            self.tts_manager.speak("Clipboard cleared.")
            return

        elif intent == "screenshot_take":
            filename = parameters.get("filename", None)
            result = self.clipboard_screenshot.take_screenshot(filename)
            self.tts_manager.speak("Screenshot taken.")
            return

        # --- SYSTEM MONITORING ---
        elif intent == "battery_check":
            status = self.system_monitor.get_battery_status()
            self.tts_manager.speak(self._humanize_response(status, "battery status"))
            return

        elif intent == "cpu_check":
            status = self.system_monitor.get_cpu_usage()
            self.tts_manager.speak(self._humanize_response(status, "CPU usage"))
            return

        elif intent == "ram_check":
            status = self.system_monitor.get_ram_usage()
            self.tts_manager.speak(self._humanize_response(status, "RAM usage"))
            return

        elif intent == "system_stats":
            stats = self.system_monitor.get_all_stats()
            self.tts_manager.speak(self._humanize_response(stats, "system statistics"))
            return

        # --- FILE AUTOMATION ---
        elif intent == "organize_downloads":
            self.tts_manager.speak("Organizing Downloads...")
            result = self.automator.organize_folder(self.automator.get_downloads_folder())
            self.tts_manager.speak(result)
            return
        elif intent == "organize_desktop":
            self.tts_manager.speak("Organizing Desktop...")
            result = self.automator.organize_folder(self.automator.get_desktop_folder())
            self.tts_manager.speak(result)
            return

        # --- FILE OPERATIONS ---
        elif intent == "file_search":
            pattern = parameters.get("pattern")
            location = parameters.get("location")
            if pattern:
                results = self.file_manager.search_files(pattern, location)
                self.tts_manager.speak(self._humanize_response(results, f"search results for {pattern}"))
            else:
                self.tts_manager.speak("What file are you looking for?")
            return
        
        elif intent == "file_create":
            result = self.file_manager.create_file(parameters.get("filename"), parameters.get("content", ""), parameters.get("location"))
            self.tts_manager.speak(result)
            return
        elif intent == "file_read":
            content = self.file_manager.read_file(parameters.get("filename"), parameters.get("location"))
            self.tts_manager.speak(f"Here is the content: {content[:100]}...") # Truncate for speech
            return
        elif intent == "file_info":
            info = self.file_manager.get_file_info(parameters.get("filename"), parameters.get("location"))
            self.tts_manager.speak(self._humanize_response(info, "file information"))
            return
        elif intent == "file_append":
            result = self.file_manager.append_to_file(parameters.get("filename"), parameters.get("content"), parameters.get("location"))
            self.tts_manager.speak(result)
            return
        elif intent == "file_rename":
            result = self.file_manager.rename_file(parameters.get("old_name"), parameters.get("new_name"), parameters.get("location"))
            self.tts_manager.speak(result)
            return
        elif intent == "file_move":
            result = self.file_manager.move_file(parameters.get("filename"), parameters.get("destination"), parameters.get("location"))
            self.tts_manager.speak(result)
            return
        elif intent == "file_copy":
            result = self.file_manager.copy_file(parameters.get("filename"), parameters.get("destination"), parameters.get("location"), parameters.get("new_name"))
            self.tts_manager.speak(result)
            return
        elif intent == "file_delete":
            self.tts_manager.speak(f"I found '{parameters.get('filename')}'. Please delete it manually for safety.")
            return

        # --- PRODUCTIVITY ---
        elif intent == "time_check":
            ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
            current_time = datetime.datetime.now(ist).strftime("%I:%M %p")
            self.tts_manager.speak(f"It is {current_time}")
            return
        elif intent == "date_check":
            ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
            current_date = datetime.datetime.now(ist).strftime("%B %d, %Y")
            self.tts_manager.speak(f"Today is {current_date}")
            return
            
        elif intent == "calendar_query":
            # 1. Check for LLM-extracted date reference
            date_ref = parameters.get("date_reference", "").lower()
            
            # 2. Fallback to fuzzy match if no parameter (handling typos like "todya")
            if not date_ref:
                words = text.split()
                if any(self.is_similar(w, "today", 0.8) for w in words):
                    date_ref = "today"
                elif any(self.is_similar(w, "tomorrow", 0.8) for w in words):
                    date_ref = "tomorrow"

            # 3. Execute Query
            if date_ref == "today":
                raw_data = self.calendar.get_events_for_date("today")
                response = self._humanize_response(raw_data, "today's schedule")
                self.tts_manager.speak(response)
            elif date_ref == "tomorrow":
                raw_data = self.calendar.get_events_for_date("tomorrow")
                response = self._humanize_response(raw_data, "tomorrow's schedule")
                self.tts_manager.speak(response)
            else:
                # Default / Upcoming
                raw_data = self.calendar.get_upcoming_events()
                response = self._humanize_response(raw_data, "upcoming events")
                self.tts_manager.speak(response)
            return
        elif intent == "calendar_create":
            self.tts_manager.speak("Checking calendar...")
            details = self.brain.parse_calendar_intent(text)
            if details.get("start_time"):
                result = self.calendar.create_event(details.get("summary"), details.get("start_time"), details.get("end_time"))
                self.tts_manager.speak(result)
            else:
                self.tts_manager.speak("I need a time for the event.")
            return

        elif intent == "notion_query":
            if "summarize" in text or "summary" in text:
                # Extract search query
                page_info = self.brain.extract_notion_page_id(text)
                search_query = page_info.get("search_query")
                
                if not search_query:
                    search_query = text.replace("summarize", "").replace("summary", "").replace("page", "").replace("about", "").replace("of", "").strip()
                
                if search_query:
                    self.tts_manager.speak(f"Searching Notion for '{search_query}'...")
                    results = self.notion.search_page(search_query)
                    
                    if not results:
                        self.tts_manager.speak("No pages found.")
                        return
                    
                    if len(results) == 1:
                        # Exact match - summarize immediately
                        page_id = results[0]["id"]
                        page_title = results[0]["title"]
                        self.tts_manager.speak(f"Found {page_title}. Summarizing...")
                        
                        page_data = self.notion.get_page_content(page_id)
                        content = page_data.get("content", "")
                        summary = self.brain.summarize_text(content, max_sentences=5)
                        
                        word_count = page_data.get("word_count", 0)
                        structured_output = f"""## 📄 Notion Page Summary

**Page:** {page_title}  
**Word Count:** {word_count} words

---

### 💡 Summary
{summary}

---
"""
                        self.tts_manager.speak(structured_output)
                    else:
                        # Multiple matches - ask user to select
                        self.tts_manager.speak(f"I found {len(results)} pages. Which one?")
                        
                        # Store for next turn
                        self.pending_notion_pages = results
                        
                        # List options
                        for i, page in enumerate(results):
                            self.tts_manager.speak(f"{i+1}. {page['title']}")
                else:
                    self.tts_manager.speak("What page should I summarize?")
            return

        elif intent == "notion_create":
            self.tts_manager.speak("Creating Notion page...")
            # TODO: Implement creation logic
            self.tts_manager.speak("Notion page creation not fully implemented yet.")
            return

        # --- FALLBACK ---
        # If no specific intent matched, use LLM for general chat
        # Use ask() instead of query_llm() to leverage the new system prompt
        self.tts_manager.speak(self.brain.ask(text))
