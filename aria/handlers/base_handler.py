from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseHandler(ABC):
    def __init__(self, tts_manager):
        self.tts_manager = tts_manager

    @abstractmethod
    def should_handle(self, intent: str) -> bool:
        """Returns True if this handler can handle the given intent."""
        pass

    @abstractmethod
    def handle(self, text: str, intent: str, parameters: Dict[str, Any]) -> Optional[str]:
        """Handles the intent and returns a response string or None."""
        pass
