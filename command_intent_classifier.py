"""
Command Intent Classifier for Aria
Uses LLM to understand user intent and map to specific system commands
"""

from typing import Dict, Any
import json
import re
from brain import AriaBrain

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
        "volume_check": "Check current volume level",
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
        # Info
        "time_check": "Get current time",
        "date_check": "Get current date",
        "weather_check": "Check weather for a specific location",
        # Email
        "email_send": "Send an email",
        "email_check": "Check unread emails or inbox",
        # General
        "general_chat": "General conversation/questions (fallback)"
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
        "battery status": "battery_check"
    }

    def __init__(self, brain: AriaBrain):
        """Initialize with an AriaBrain instance."""
        self.brain = brain

    def classify_intent(self, user_text: str, conversation_history: list = None) -> Dict[str, Any]:
        """Classify the user's command into an intent.
        Returns a dict with keys: intent, confidence, parameters.
        """
        # 1. FAST PATH: Check for exact keyword matches
        clean_text = user_text.lower().strip().replace("please", "").strip()
        # Remove punctuation
        clean_text = re.sub(r'[^\w\s]', '', clean_text)
        
        if clean_text in self.FAST_PATH_INTENTS:
            print(f"⚡ FAST PATH TRIGGERED: {clean_text} -> {self.FAST_PATH_INTENTS[clean_text]}")
            return {
                "intent": self.FAST_PATH_INTENTS[clean_text],
                "confidence": 1.0,
                "parameters": {}
            }

        if not self.brain.is_available():
            return {"intent": "none", "confidence": 0.0, "parameters": {}}

        prompt = self._build_classification_prompt(user_text, conversation_history)
        try:
            llm = self.brain.get_llm()
            if not llm:
                print("Error: No LLM available")
                return {"intent": "general_chat", "confidence": 0.0, "parameters": {}}
                
            response = llm.invoke(prompt)
            content = response.content.strip()
            # print(f"CLASSIFIER DEBUG - Raw response: {content[:200]}...")
            
            # Use regex to find JSON object
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                cleaned = json_match.group(0)
                result = json.loads(cleaned)
            else:
                print("No JSON found in response")
                result = {}
        except Exception as e:
            print(f"Error classifying intent: {e}")
            try:
                print(f"Raw response was: {content[:100].encode('utf-8', errors='ignore').decode('utf-8') if 'content' in locals() else 'No response'}")
            except Exception:
                print("Raw response was: [Content with unicode]")
            return {"intent": "general_chat", "confidence": 0.0, "parameters": {}}

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

        return {"intent": intent, "confidence": result.get("confidence", 0.0), "parameters": parameters}

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
4. If the user asks for "change wallpaper", "dark mode", or "system settings", use "general_chat".
5. If the user asks for "download X" (where X is a file/video from web), use "general_chat" (unless it matches a specific file automation intent).
6. If the user asks "can you see this?" or "what is on my screen?", use "general_chat" (unless "screenshot_take" is explicitly requested).

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
- "change my wallpaper" -> intent: "general_chat", parameters: {{}}
- "write a python script to sort a list" -> intent: "general_chat", parameters: {{}}
- "how do I center a div" -> intent: "general_chat", parameters: {{}}
- "summarize this notion page" -> intent: "notion_query", parameters: {{"query": "summarize this page"}}

Return ONLY a JSON object with this exact structure:
{{{{
    "intent": "the_intent_name",
    "confidence": 0.95,
    "parameters": {{}}
}}}}
"""
        return prompt
