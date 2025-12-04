from typing import Dict, Any, Optional
from .base_handler import BaseHandler
import datetime
from langchain_core.messages import HumanMessage, SystemMessage
from ..logger import setup_logger

logger = setup_logger(__name__)

class FileHandler(BaseHandler):
    def __init__(self, tts_manager, file_manager, automator, brain=None):
        super().__init__(tts_manager)
        self.file_manager = file_manager
        self.automator = automator
        self.brain = brain # Optional, for humanizing results

    def should_handle(self, intent: str) -> bool:
        file_intents = [
            "file_search", "file_create", "file_read", "file_info", 
            "file_append", "file_rename", "file_move", "file_copy", "file_delete",
            "organize_downloads", "organize_desktop"
        ]
        return intent in file_intents

    def _humanize_response(self, data_text: str, context: str) -> str:
        if not self.brain or not self.brain.is_available():
            return str(data_text)
        try:
            prompt = f"""
            You are Aria.
            Summarize the following FILE DATA for the user.
            Context: {context}
            
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
            return str(data_text)
        except Exception as e:
            logger.error(f"Error humanizing response: {e}")
            return str(data_text)

    def handle(self, text: str, intent: str, parameters: Dict[str, Any]) -> Optional[str]:
        # --- FILE AUTOMATION ---
        if intent == "organize_downloads":
            self.tts_manager.speak("Organizing Downloads...")
            result = self.automator.organize_folder(self.automator.get_downloads_folder())
            self.tts_manager.speak(result)
            return result
        elif intent == "organize_desktop":
            self.tts_manager.speak("Organizing Desktop...")
            result = self.automator.organize_folder(self.automator.get_desktop_folder())
            self.tts_manager.speak(result)
            return result

        # --- FILE OPERATIONS ---
        elif intent == "file_search":
            pattern = parameters.get("pattern")
            location = parameters.get("location")
            if pattern:
                results = self.file_manager.search_files(pattern, location)
                self.tts_manager.speak(self._humanize_response(str(results), f"search results for {pattern}"))
                return str(results)
            else:
                self.tts_manager.speak("What file are you looking for?")
                return "Please specify a file pattern."
        
        elif intent == "file_create":
            result = self.file_manager.create_file(parameters.get("filename"), parameters.get("content", ""), parameters.get("location"))
            self.tts_manager.speak(result)
            return result
        elif intent == "file_read":
            content = self.file_manager.read_file(parameters.get("filename"), parameters.get("location"))
            self.tts_manager.speak(f"Here is the content: {content[:100]}...") # Truncate for speech
            return content
        elif intent == "file_info":
            info = self.file_manager.get_file_info(parameters.get("filename"), parameters.get("location"))
            self.tts_manager.speak(self._humanize_response(str(info), "file information"))
            return str(info)
        elif intent == "file_append":
            result = self.file_manager.append_to_file(parameters.get("filename"), parameters.get("content"), parameters.get("location"))
            self.tts_manager.speak(result)
            return result
        elif intent == "file_rename":
            result = self.file_manager.rename_file(parameters.get("old_name"), parameters.get("new_name"), parameters.get("location"))
            self.tts_manager.speak(result)
            return result
        elif intent == "file_move":
            result = self.file_manager.move_file(parameters.get("filename"), parameters.get("destination"), parameters.get("location"))
            self.tts_manager.speak(result)
            return result
        elif intent == "file_copy":
            result = self.file_manager.copy_file(parameters.get("filename"), parameters.get("destination"), parameters.get("location"), parameters.get("new_name"))
            self.tts_manager.speak(result)
            return result
        elif intent == "file_delete":
            msg = f"I found '{parameters.get('filename')}'. Please delete it manually for safety."
            self.tts_manager.speak(msg)
            return msg
            
        return None
