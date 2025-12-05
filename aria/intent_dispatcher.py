from typing import Callable, Dict, Optional
from .logger import setup_logger

logger = setup_logger(__name__)

class IntentDispatcher:
    """
    Dispatches intents to registered handlers.
    """
    def __init__(self):
        self.handlers: Dict[str, Callable] = {}

    def register_handler(self, intent: str, handler: Callable):
        """
        Registers a handler function for a specific intent.
        Handler signature: handler(text: str, intent: str, parameters: dict) -> str | None
        """
        self.handlers[intent] = handler
        logger.debug(f"Registered handler for intent: {intent}")

    def dispatch(self, intent: str, text: str, parameters: dict = None) -> Optional[str]:
        """
        Dispatches the command to the registered handler.
        Returns the result string if handled, else None.
        """
        if parameters is None:
            parameters = {}

        handler = self.handlers.get(intent)
        if handler:
            logger.info(f"Dispatching intent '{intent}' to handler {handler.__name__}")
            try:
                return handler(text, intent, parameters)
            except Exception as e:
                logger.error(f"Error handling intent '{intent}': {e}")
                return f"I encountered an error while processing your request: {e}"
        
        return None
