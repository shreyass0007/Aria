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

    def __init__(self, brain: AriaBrain):
        """Initialize with an AriaBrain instance."""
        self.brain = brain

    def classify_intent(self, user_text: str) -> Dict[str, Any]:
        """Classify the user's command into an intent.
        Returns a dict with keys: intent, confidence, parameters.
        """
        if not self.brain.is_available():
            return {"intent": "none", "confidence": 0.0, "parameters": {}}

        prompt = self._build_classification_prompt(user_text)
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

    def _build_classification_prompt(self, user_text: str) -> str:
        """Construct the prompt for the LLM to classify the command."""
        intent_list = [f'  - "{intent}": {desc}' for intent, desc in self.COMMAND_INTENTS.items()]
        intent_descriptions = "\n".join(intent_list)
        
        # Get current date for context
        import datetime
        now = datetime.datetime.now()
        current_date_str = now.strftime("%A, %Y-%m-%d")
        
        prompt = f"""You are a command intent classifier for a voice assistant.

Your task is to analyze the user's command and determine their intent.

CURRENT DATE: {current_date_str}

USER COMMAND: "{user_text}"

AVAILABLE INTENTS:
{intent_descriptions}

NEGATIVE CONSTRAINTS:
1. Do NOT invent new intents.
2. If the user asks for an action not listed in AVAILABLE INTENTS, output "general_chat".
3. Do NOT assume you can perform actions like "change settings", "update system", "install software", "change wallpaper", "change theme", or "order food".
4. If the user asks for "change wallpaper" or "dark mode", use "general_chat".
5. If the user asks for "download X" (where X is a file/video from web), use "general_chat" (unless it matches a specific file automation intent).
6. If the user asks "can you see this?", use "general_chat".

CLASSIFICATION RULES:
1. Choose the MOST SPECIFIC intent that matches the user's command.
2. If the command is a general question or conversation (e.g., "tell me a joke", "who are you"), use "general_chat".
3. Extract relevant parameters.
4. Distinguish between "file_search" (local files) and "web_search" (Google).
5. For 'calendar_query':
   - Extract 'target_date' in YYYY-MM-DD format if possible (resolve "today", "tomorrow", "next friday" based on CURRENT DATE).
   - Extract 'query_type': "events" (default) or "free_time" (if asking for empty slots/availability).
   - Extract 'time_scope': "morning" (5AM-12PM), "afternoon" (12PM-5PM), "evening" (5PM-9PM), or "all_day" (default).

EXAMPLES:
- "create test.txt on desktop" -> intent: "file_create", parameters: {{"filename": "test.txt", "location": "desktop"}}
- "what's the weather in London" -> intent: "weather_check", parameters: {{"city": "London"}}
- "what do I have on Friday?" -> intent: "calendar_query", parameters: {{"target_date": "2023-10-27", "query_type": "events", "time_scope": "all_day"}}
- "when am I free tomorrow morning?" -> intent: "calendar_query", parameters: {{"target_date": "2023-10-28", "query_type": "free_time", "time_scope": "morning"}}
- "do I have any meetings this afternoon?" -> intent: "calendar_query", parameters: {{"target_date": "2023-10-26", "query_type": "events", "time_scope": "afternoon"}}

Return ONLY a JSON object with this exact structure:
{{{{
    "intent": "the_intent_name",
    "confidence": 0.95,
    "parameters": {{}}
}}}}
"""
        return prompt
