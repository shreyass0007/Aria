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
            print(f"CLASSIFIER DEBUG - Raw response: {content[:200]}...")
            
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
            print(f"Raw response was: {content if 'content' in locals() else 'No response'}")
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
        prompt = f"""You are a command intent classifier for a voice assistant.

Your task is to analyze the user's command and determine their intent.

USER COMMAND: "{user_text}"

AVAILABLE INTENTS:
{intent_descriptions}

CLASSIFICATION RULES:
1. Choose the MOST SPECIFIC intent that matches the user's command.
2. If the command is a general question or conversation (e.g., "tell me a joke", "who are you"), use "general_chat".
3. Extract relevant parameters.
4. Distinguish between "file_search" (local files) and "web_search" (Google).
   - "find resume on desktop" -> file_search
   - "search for python tutorials" -> web_search
5. For file operations, extract location as one of: desktop, downloads, documents, pictures, music, videos
   - "download section" or "in downloads" -> location: "downloads"
   - "on desktop" or "desktop area" -> location: "desktop"
6. For calendar queries, extract the date reference (e.g., "today", "tomorrow", "next friday", "april 13").
   - "what's my schedule for tomorrow?" -> intent: "calendar_query", parameters: {{"date_reference": "tomorrow"}}
   - "do i have any meetings on friday?" -> intent: "calendar_query", parameters: {{"date_reference": "friday"}}

EXAMPLES:
- "shutdown the computer" -> intent: "shutdown"
- "open youtube" -> intent: "web_open", parameters: {{"url": "https://youtube.com", "name": "YouTube"}}
- "open calculator" -> intent: "app_open", parameters: {{"app_name": "calculator"}}
- "play some taylor swift" -> intent: "music_play", parameters: {{"song": "taylor swift"}}
- "schedule meeting tomorrow at 5pm" -> intent: "calendar_create"
- "what's on my schedule?" -> intent: "calendar_query"
- "what do i have tomorrow?" -> intent: "calendar_query", parameters: {{"date_reference": "tomorrow"}}
- "summarize my notion page about goals" -> intent: "notion_query"
- "add milk to grocery list in notion" -> intent: "notion_create"
- "what time is it?" -> intent: "time_check"
- "search for pasta recipes" -> intent: "web_search", parameters: {{"query": "pasta recipes"}}
- "find all pdfs in downloads" -> intent: "file_search", parameters: {{"pattern": "*.pdf", "location": "downloads"}}
- "create file hi.txt in download section" -> intent: "file_create", parameters: {{"filename": "hi.txt", "location": "downloads"}}
- "create test.txt on desktop" -> intent: "file_create", parameters: {{"filename": "test.txt", "location": "desktop"}}
- " readme.md in documents" -> intent: "file_create", parameters: {{"filename": "readme.md", "location": "documents"}}
- "what's the weather in London" -> intent: "weather_check", parameters: {{"city": "London"}}
- "send an email to john@example.com about meeting" -> intent: "email_send"
- "take screenshot" -> intent: "screenshot_take"
- "take a screenshot" -> intent: "screenshot_take"
- "capture screen" -> intent: "screenshot_take"
- "tell me a joke" -> intent: "general_chat"

Return ONLY a JSON object with this exact structure:
{{{{
    "intent": "the_intent_name",
    "confidence": 0.95,
    "parameters": {{}}
}}}}
"""
        return prompt
