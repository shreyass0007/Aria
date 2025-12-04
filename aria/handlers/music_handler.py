import random
from typing import Dict, Any, Optional
from .base_handler import BaseHandler

class MusicHandler(BaseHandler):
    def __init__(self, tts_manager, music_manager):
        super().__init__(tts_manager)
        self.music_manager = music_manager

    def should_handle(self, intent: str) -> bool:
        return intent.startswith("music_")

    def _get_random_response(self, intent: str, context: str = "") -> str:
        responses = {
            "music_play": [
                f"Playing {context}.", f"Starting {context}.", f"Here is {context}.", f"Queuing up {context}."
            ]
        }
        options = responses.get(intent, [])
        if options:
            return random.choice(options)
        return f"Executing {intent}."

    def handle(self, text: str, intent: str, parameters: Dict[str, Any]) -> Optional[str]:
        if intent == "music_play":
            song = parameters.get("song")
            if not song:
                song = text.replace("play", "", 1).strip()
            
            self.tts_manager.speak(self._get_random_response("music_play", song))
            
            # Use MusicManager for playback
            result = self.music_manager.play_music(song)
            self.tts_manager.speak(result)
            
            # Return result for UI action handling in processor
            return f"Playing {song}."

        elif intent == "music_pause":
            result = self.music_manager.pause()
            if isinstance(result, dict):
                result = result.get("message", "Music paused.")
            self.tts_manager.speak(result)
            return result

        elif intent == "music_resume" or intent == "music_unpause":
            result = self.music_manager.resume()
            if isinstance(result, dict):
                result = result.get("message", "Music resumed.")
            self.tts_manager.speak(result)
            return result

        elif intent == "music_stop":
            result = self.music_manager.stop()
            self.tts_manager.speak(result)
            return result
            
        elif intent == "music_volume":
            level = parameters.get("level")
            if level:
                try:
                    vol = int(level)
                    self.tts_manager.speak(self.music_manager.set_volume(vol))
                except ValueError:
                    self.tts_manager.speak("Invalid volume level.")
            return "Volume adjusted."
            
        return None
