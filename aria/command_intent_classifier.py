"""
Command Intent Classifier for Aria
Uses LLM to understand user intent and map to specific system commands
"""

from typing import Dict, Any
import json
import re
from .brain import AriaBrain
from .logger import setup_logger

logger = setup_logger(__name__)

class CommandIntentClassifier:
    """Classifies user commands into intents using the LLM.
    Supports weather_check intent and provides fallback extraction.
    """

    # Define all supported command intents
    COMMAND_INTENTS = {
        # Power Management
        "shutdown": "Shut down the computer",
        "restart": "Restart the computer",
        "lock": "Lock the screen/workstation",
        "sleep": "Put computer to sleep",
        "cancel_shutdown": "Cancel pending shutdown/restart",
        # Focus & Window Management
        "focus_mode_on": "Turn on Focus Mode / Deep Work / Do Not Disturb",
        "focus_mode_off": "Turn off Focus Mode / Deep Work",
        "minimize_all": "Minimize all windows / Show desktop",
        # Volume Control
        "volume_up": "Increase system volume",
        "volume_down": "Decrease system volume",
        "volume_set": "Set volume to specific level",
        "volume_mute": "Mute system audio",
        "volume_unmute": "Unmute system audio",
        "volume_unmute": "Unmute system audio",
        "volume_check": "Check current volume level",
        # Brightness Control
        "brightness_up": "Increase screen brightness",
        "brightness_down": "Decrease screen brightness",
        "brightness_set": "Set screen brightness to level",
        "brightness_check": "Check status of screen brightness",
        # System Maintenance
        "recycle_bin_empty": "Empty the recycle bin",
        "recycle_bin_check": "Check recycle bin status",
        # Clipboard Operations
        "clipboard_copy": "Copy text to clipboard",
        "clipboard_read": "Read clipboard contents",
        "clipboard_clear": "Clear clipboard",
        # Screenshot Operations
        "screenshot_take": "Take a screenshot",
        # System Monitoring
        "battery_check": "Check battery status and percentage",
        "cpu_check": "Check CPU usage",
        "ram_check": "Check RAM/memory usage",
        "system_stats": "Get all system statistics (battery, CPU, RAM)",
        # File Automation
        "organize_downloads": "Organize downloads folder",
        "organize_desktop": "Organize desktop folder",
        # File Operations (CRUD)
        "file_create": "Create a new file",
        "file_read": "Read/view file contents",
        "file_info": "Get file information",
        "file_append": "Append content to a file",
        "file_replace": "Replace text in a file",
        "file_delete": "Delete a file or directory",
        "file_rename": "Rename a file or directory",
        "file_move": "Move a file to different location",
        "file_copy": "Copy a file or directory",
        "file_search": "Search for files (NOT web search)",
        # Web & Apps
        "web_open": "Open a website (YouTube, Instagram, etc.)",
        "app_open": "Open a desktop application",
        "web_search": "Search Google/Web for information",
        # Media
        "music_play": "Play music or specific song",
        "music_pause": "Pause currently playing music",
        "music_resume": "Resume paused music",
        "music_stop": "Stop music playback",
        "music_volume": "Set music volume",
        # Productivity
        "calendar_query": "Check schedule/events",
        "calendar_create": "Create a calendar event",
        "notion_query": "Search or summarize Notion pages",
        "notion_create": "Add item/page to Notion",
        # INFO
        "time_check": "Get current time",
        "date_check": "Get current date",
        "weather_check": "Check weather for a specific location",

        # Email
        "email_send": "Send an email",
        "email_check": "Check unread emails or inbox",
        # Water Reminder
        "water_reminder_start": "Start the water drinking reminder",
        "water_reminder_stop": "Stop the water drinking reminder",
        "water_reminder_interval": "Set water reminder frequency",
        # General
        "general_chat": "General conversation/questions (fallback)",
        # Development Tools
        "jupyter_open": "Open Jupyter Notebook"
    }

    # Fast Path Intents (Keyword -> Intent)
    # These bypass the LLM for instant response
    FAST_PATH_INTENTS = {
        "volume up": "volume_up",
        "louder": "volume_up",
        "increase volume": "volume_up",
        "volume down": "volume_down",
        "quieter": "volume_down",
        "decrease volume": "volume_down",
        "mute": "volume_mute",
        "silence": "volume_mute",
        "unmute": "volume_unmute",
        "set volume": "volume_set",
        "change volume": "volume_set",
        "change volume": "volume_set",
        "vset volume": "volume_set", # Handle user typo
        "brightness up": "brightness_up",
        "increase brightness": "brightness_up",
        "brighter": "brightness_up",
        "brightness down": "brightness_down",
        "decrease brightness": "brightness_down",
        "dimmer": "brightness_down",
        "check brightness": "brightness_check",
        "shutdown": "shutdown",
        "restart": "restart",
        "lock screen": "lock",
        "lock pc": "lock",
        "lock computer": "lock",
        "sleep": "sleep",
        "what time is it": "time_check",
        "current time": "time_check",
        "what date is it": "date_check",
        "todays date": "date_check",
        "empty recycle bin": "recycle_bin_empty",
        "check battery": "battery_check",
        "battery status": "battery_check",
        
        # WiFi & Bluetooth
        "wifi_on": "Enable WiFi (Admin)",
        "wifi_off": "Disable WiFi (Admin)",
        "wifi_check": "Check WiFi connection status",
        "bluetooth_on": "Enable Bluetooth Service (Admin)",
        "bluetooth_off": "Disable Bluetooth Service (Admin)",
        "bluetooth_check": "Check Bluetooth status",

        # System Monitoring Fast Paths
        "check system status": "system_stats",
        "system status": "system_stats",
        "system check": "system_stats",
        "check cpu": "cpu_check",
        "cpu usage": "cpu_check",
        "check ram": "ram_check",
        "ram usage": "ram_check",
        "memory usage": "ram_check",
        "check memory": "ram_check",
        
        # Network & Connectivity Fast Paths
        "wifi on": "wifi_on",
        "enable wifi": "wifi_on",
        "turn on wifi": "wifi_on",
        "wifi off": "wifi_off",
        "disable wifi": "wifi_off",
        "turn off wifi": "wifi_off",
        "check wifi": "wifi_check",
        "wifi status": "wifi_check",
        
        "bluetooth on": "bluetooth_on",
        "enable bluetooth": "bluetooth_on",
        "turn on bluetooth": "bluetooth_on",
        "turn on blutooth": "bluetooth_on",
        "turn on bulutooth": "bluetooth_on",
        "bluetooth off": "bluetooth_off",
        "disable bluetooth": "bluetooth_off",
        "turn off bluetooth": "bluetooth_off",
        "turn off blutooth": "bluetooth_off",
        "turn off bulutooth": "bluetooth_off",
        "check bluetooth": "bluetooth_check",
        "bluetooth status": "bluetooth_check",
    
        # Media Fast Paths
        "stop": "music_stop",
        "stop music": "music_stop",
        "stop playing": "music_stop",
        "pause": "music_pause",
        "resume": "music_resume",
        "next": "music_next", # Assuming intent exists or will default to none
        "next song": "music_next",

        # Common App Shortcuts
        "open calculator": "app_open",
        "calculator": "app_open",
        "open notepad": "app_open",
        "notepad": "app_open",
        "open browser": "web_open",
        "browser": "web_open",
        "open chrome": "app_open",
        "chrome": "app_open",
        
        # Jupyter Notebook Fast Paths
        "open jupyter": "jupyter_open",
        "open jupyter notebook": "jupyter_open",
        "jupyter notebook": "jupyter_open",
        "jupyter": "jupyter_open",
        "start jupyter": "jupyter_open",
        "launch jupyter": "jupyter_open",
        
        # Silence
        "quiet": "volume_mute",
        "shutup": "volume_mute",
        "shut up": "volume_mute",
    
        # Focus Mode Fast Paths
        "focus mode on": "focus_mode_on",
        "turn on focus mode": "focus_mode_on",
        "enable focus mode": "focus_mode_on",
        "start focus": "focus_mode_on",
        "activate focus mode": "focus_mode_on",
        "focus mode": "focus_mode_on",
        "focus mode off": "focus_mode_off",
        "turn off focus mode": "focus_mode_off",
        "disable focus mode": "focus_mode_off",
        "stop focus": "focus_mode_off",
        "deactivate focus mode": "focus_mode_off",

        # Brightness Fast Paths
        "max brightness": "brightness_set",
        "min brightness": "brightness_set",
        "brightness 100": "brightness_set",
        "brightness 0": "brightness_set",
        "brightness 50": "brightness_set",

        # Volume Fast Paths
        "max volume": "volume_set",
        "volume 100": "volume_set",
        "mute system": "volume_mute",
        "unmute system": "volume_unmute",
        
        # Email Fast Paths (CRITICAL - must go through confirmation flow)
        "send email": "email_send",
        "send mail": "email_send",
        "send an email": "email_send",
        "compose email": "email_send",
        "write email": "email_send",
        "write mail": "email_send",
        "draft email": "email_send",
        "email to": "email_send",
        "mail to": "email_send",
        "check email": "email_check",
        "check my email": "email_check",
        "check inbox": "email_check",
        "unread emails": "email_check"
    }

    def __init__(self, brain: AriaBrain):
        """Initialize with an AriaBrain instance."""
        self.brain = brain

    def classify_intent(self, user_text: str, conversation_history: list = None) -> list:
        """Classify the user's command into one or more intents.
        Returns a list of dicts, each with keys: intent, confidence, parameters.
        """
        # 1. FAST PATH: Check for exact keyword matches
        clean_text = user_text.lower().strip().replace("please", "").strip()
        # Remove punctuation
        clean_text = re.sub(r'[^\w\s]', '', clean_text)
        
        if clean_text in self.FAST_PATH_INTENTS:
            logger.info(f"FAST PATH TRIGGERED: {clean_text} -> {self.FAST_PATH_INTENTS[clean_text]}")
            return [{
                "intent": self.FAST_PATH_INTENTS[clean_text],
                "confidence": 1.0,
                "parameters": {}
            }]

        # 2. REGEX FAST PATH: Check for patterns (e.g. "set volume to 50")
        # Volume Set
        vol_match = re.search(r'(?:set|change|turn|vset) (?:the )?volume (?:to )?(\d+)', clean_text)
        if vol_match:
            level = int(vol_match.group(1))
            logger.info(f"REGEX PATH TRIGGERED: volume_set -> {level}")
            return [{
                "intent": "volume_set",
                "confidence": 1.0,
                "parameters": {"level": level}
            }]
        
        # Volume Set (Alternative: "volume 50")
        if re.match(r'^volume \d+$', clean_text):
             level = int(re.findall(r'\d+', clean_text)[0])
             logger.info(f"REGEX PATH TRIGGERED: volume_set -> {level}")
             return [{
                "intent": "volume_set",
                "confidence": 1.0,
                "parameters": {"level": level}
            }]

        # Brightness Set
        bright_match = re.search(r'(?:set|change|turn) (?:the )?brightness (?:to )?(\d+)', clean_text)
        if bright_match:
            level = int(bright_match.group(1))
            logger.info(f"REGEX PATH TRIGGERED: brightness_set -> {level}")
            return [{
                "intent": "brightness_set",
                "confidence": 1.0,
                "parameters": {"level": level}
            }]

        # Web Search Fast Path: Updates, News, Trends
        if re.search(r'(?:check|get|find|show|what are|any)?\s*(?:upcoming|latest|recent|new)\s+(?:updates|news|trends|developments)\s*(?:in|on|about)?', clean_text):
             logger.info(f"REGEX PATH TRIGGERED: web_search (updates/news)")
             return [{
                "intent": "web_search",
                "confidence": 1.0,
                "parameters": {"query": user_text}
            }]

        # Email Send Fast Path - CRITICAL: Catch all email send patterns
        email_patterns = [
            r'(?:send|write|compose|draft)\s+(?:an?\s+)?(?:email|mail)\s+to',
            r'(?:email|mail)\s+to\s+\S+',
            r'(?:send|write)\s+(?:a\s+)?(?:quick\s+)?(?:email|mail|message)\s+to'
        ]
        for pattern in email_patterns:
            if re.search(pattern, clean_text, re.IGNORECASE):
                logger.info(f"REGEX PATH TRIGGERED: email_send (pattern: {pattern})")
                return [{
                    "intent": "email_send",
                    "confidence": 1.0,
                    "parameters": {}
                }]

        if not self.brain.is_available():
            return [{"intent": "none", "confidence": 0.0, "parameters": {}}]

        prompt = self._build_classification_prompt(user_text, conversation_history)
        try:
            # Use Fast LLM for critical latency path
            llm = self.brain.get_fast_llm()
            if not llm:
                logger.error("Error: No LLM available")
                return [{"intent": "general_chat", "confidence": 0.0, "parameters": {}}]
                
            response = llm.invoke(prompt)
            content = response.content.strip()
            # print(f"CLASSIFIER DEBUG - Raw response: {content[:200]}...")
            
            # Use regex to find JSON object or list
            json_match = re.search(r"(\[.*\]|\{.*\})", content, re.DOTALL)
            if json_match:
                cleaned = json_match.group(0)
                parsed_result = json.loads(cleaned)
                
                # Normalize to list
                if isinstance(parsed_result, dict):
                    results = [parsed_result]
                elif isinstance(parsed_result, list):
                    results = parsed_result
                else:
                    results = []
            else:
                logger.warning("No JSON found in response")
                results = []
        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            try:
                logger.debug(f"Raw response was: {content[:100].encode('utf-8', errors='ignore').decode('utf-8') if 'content' in locals() else 'No response'}")
            except Exception:
                logger.debug("Raw response was: [Content with unicode]")
            return [{"intent": "general_chat", "confidence": 0.0, "parameters": {}}]

        final_intents = []
        
        # If no results or empty list, default to general_chat
        if not results:
             results = [{"intent": "general_chat", "confidence": 0.0, "parameters": {}}]

        for result in results:
            intent = result.get("intent", "general_chat")
            if intent not in self.COMMAND_INTENTS:
                intent = "general_chat"
            parameters = result.get("parameters", {})

            # Fallback extraction for weather_check if city missing
            if intent == "weather_check" and not parameters.get("city"):
                match = re.search(r"weather in ([a-zA-Z ]+)", user_text, re.IGNORECASE)
                if match:
                    parameters["city"] = match.group(1).strip()

            # Normalize location parameters for file operations
            if intent.startswith("file_") and "location" in parameters:
                location = parameters.get("location", "").lower()
                # Map various location phrases to standard shortcuts
                location_mapping = {
                    "download": "downloads",
                    "download section": "downloads",
                    "downloads folder": "downloads",
                    "downloads area": "downloads",
                    "desktop": "desktop", 
                    "document": "documents",
                    "documents folder": "documents",
                    "picture": "pictures",
                    "pictures folder": "pictures",
                    "music": "music",
                    "music folder": "music",
                    "video": "videos",
                    "videos folder": "videos"
                }
                for key, value in location_mapping.items():
                    if key in location:
                        parameters["location"] = value
                        break
            
            final_intents.append({"intent": intent, "confidence": result.get("confidence", 0.0), "parameters": parameters})

        return final_intents

    def _build_classification_prompt(self, user_text: str, conversation_history: list = None) -> str:
        """Construct the prompt for the LLM to classify the command."""
        intent_list = [f'  - "{intent}": {desc}' for intent, desc in self.COMMAND_INTENTS.items()]
        intent_descriptions = "\n".join(intent_list)
        
        # Get current date for context
        import datetime
        now = datetime.datetime.now()
        current_date_str = now.strftime("%A, %Y-%m-%d")
        
        # Add conversation history context
        history_str = ""
        if conversation_history:
            history_str = "\nRECENT CONVERSATION HISTORY:\n"
            for msg in conversation_history[-3:]: # Only last 3 messages for immediate context
                role = msg.get("role", "unknown").upper()
                content = msg.get("content", "")
                history_str += f"{role}: {content}\n"
        
        prompt = f"""You are a command intent classifier for a voice assistant.

Your task is to analyze the user's command and determine their intent.

CURRENT DATE: {current_date_str}
{history_str}
USER COMMAND: "{user_text}"

AVAILABLE INTENTS:
{intent_descriptions}

NEGATIVE CONSTRAINTS (CRITICAL):
1. Do NOT invent new intents. Use ONLY the ones listed above.
2. If the user asks for an action not listed in AVAILABLE INTENTS, output "general_chat".
3. Do NOT assume you can perform actions like "change settings", "update system", "install software", "change wallpaper", "change theme", "order food", or "book flights".
   **EXCEPTION**: You CAN control WiFi and Bluetooth (on/off/check).
4. If the user asks for "change wallpaper", "dark mode", or "system settings", use "general_chat".
5. If the user asks for "download X" (where X is a file/video from web), use "general_chat" (unless it matches a specific file automation intent).


CLASSIFICATION RULES:
1. Choose the MOST SPECIFIC intent that matches the user's command.
2. If the command is a general question or conversation (e.g., "tell me a joke", "who are you", "write code"), use "general_chat".
3. Extract relevant parameters into the "parameters" object.
4. **Distinguish between "file_search" and "web_search":**
   - "search for [filename]" or "find [file]" -> "file_search" (Local files)
   - "search for [topic]", "google [topic]", "who is [person]" -> "web_search" (Internet)
   - **CRITICAL:** If the user asks a question that requires REAL-TIME or EXTERNAL knowledge (e.g., "price of bitcoin", "who won the game", "latest news"), use "web_search", NOT "general_chat".
5. **Distinguish between "app_open" and "web_open":**
   - "open [app name]" (e.g., "open calculator", "open spotify") -> "app_open"
   - "open [website]" (e.g., "open youtube", "open google.com") -> "web_open"
   - If ambiguous (e.g., "open spotify"), prefer "app_open".
6. For 'calendar_query':
   - Extract 'target_date' in YYYY-MM-DD format if possible (resolve "today", "tomorrow", "next friday" based on CURRENT DATE).
   - Extract 'query_type': "events" (default) or "free_time" (if asking for empty slots/availability).
   - Extract 'time_scope': "morning" (5AM-12PM), "afternoon" (12PM-5PM), "evening" (5PM-9PM), or "all_day" (default).

7. **CONTEXTUAL CORRECTIONS (Review History):**
   - If the user says "no, schedule it today" or "actually, make it 5 PM", look at the **RECENT CONVERSATION HISTORY** to find the previous user command and intent.
   - If the previous command was "schedule meeting on Friday" and the user says "no, today", YOU MUST output a new `calendar_create` intent with the OLD parameters updated by the NEW information.
   - Example 1: 
     - History: User: "Set volume to 50" -> System: "Volume set."
     - User: "No, make it 80" -> Intent: `volume_set`, parameters: `{{"level": 80}}`
   - Example 2:
     - History: User: "Remind me to call Mom tomorrow" -> System: "Reminder set."
     - User: "Actually, change that to Friday" -> Intent: `calendar_create`, parameters: `{{"summary": "Call Mom", "start_time": "2023-10-27..."}}` (Merge "Call Mom" with new date).
   - Resolve pronouns like "it", "that", "him", "her" using history.

EXAMPLES:
- "create test.txt on desktop" -> intent: "file_create", parameters: {{"filename": "test.txt", "location": "desktop"}}
- "what's the weather in London" -> intent: "weather_check", parameters: {{"city": "London"}}
- "what do I have on Friday?" -> intent: "calendar_query", parameters: {{"target_date": "2023-10-27", "query_type": "events", "time_scope": "all_day"}}
- "when am I free tomorrow morning?" -> intent: "calendar_query", parameters: {{"target_date": "2023-10-28", "query_type": "free_time", "time_scope": "morning"}}
- "search for aria_logo.png" -> intent: "file_search", parameters: {{"pattern": "aria_logo.png", "location": "root"}}
- "find the budget report" -> intent: "file_search", parameters: {{"pattern": "budget report", "location": "documents"}}
- "search for python tutorials" -> intent: "web_search", parameters: {{"query": "python tutorials"}}
- "what is the price of bitcoin" -> intent: "web_search", parameters: {{"query": "price of bitcoin"}}
- "who won the super bowl" -> intent: "web_search", parameters: {{"query": "who won the super bowl"}}
- "open spotify" -> intent: "app_open", parameters: {{"app_name": "Spotify"}}
- "open youtube" -> intent: "web_open", parameters: {{"url": "https://youtube.com", "name": "YouTube"}}
- "play some jazz" -> intent: "music_play", parameters: {{"song": "jazz"}}
- "set volume to 50" -> intent: "volume_set", parameters: {{"level": 50}}
- "change my wallpaper" -> intent: "general_chat", parameters: {{}}
- "write a python script to sort a list" -> intent: "general_chat", parameters: {{}}
- "how do I center a div" -> intent: "general_chat", parameters: {{}}
- "summarize this notion page" -> intent: "notion_query", parameters: {{"query": "summarize this page"}}

- "send email to john@example.com to say hello" -> intent: "email_send", parameters: {{"to": "john@example.com", "subject": "Hello", "context": "greeting"}}
- "write mail to boss about project update" -> intent: "email_send", parameters: {{"to": "boss", "subject": "Project Update", "context": "project update"}}
- "check my emails" -> intent: "email_check", parameters: {{}}

**CRITICAL EMAIL RULE:** ANY command that mentions sending, composing, drafting, or writing an email MUST be classified as "email_send". Do NOT handle emails in general_chat.

6. **Distinguish between "file_search" and "web_search" (UPDATED):**
   - "search for [filename]" or "find [file]" -> "file_search" (Local files)
   - "search for [topic]", "google [topic]", "who is [person]" -> "web_search" (Internet)
   - **"check updates", "latest news", "trends in X", "upcoming X" -> "web_search"** (Real-time info)
   - **CRITICAL:** If the user asks for "updates", "news", "trends", "prices", "scores", or "weather" (if not specific format), it requires REAL-TIME knowledge. USE "web_search". Do NOT use "general_chat".

**CRITICAL WEB SEARCH TRIGGER:** If the user asks "check upcoming updates in [topic]" or "what is new in [topic]", this is a "web_search".

Return ONLY a JSON LIST of objects with this exact structure:
[
    {{
        "intent": "the_intent_name",
        "confidence": 0.95,
        "parameters": {{}}
    }}
]

If there are multiple distinct actions (e.g., "play music and set volume"), return multiple objects in the list in the order they should be executed.
"""
        return prompt
