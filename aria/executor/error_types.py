class DesktopAutomationError(Exception):
    """Base class for all desktop automation errors."""
    def __init__(self, message: str, step_index: int = None, action: str = None):
        super().__init__(message)
        self.message = message
        self.step_index = step_index
        self.action = action

class ActionFailedError(DesktopAutomationError):
    """Raised when a specific action fails to execute."""
    def __init__(self, message: str, step_index: int = None, action: str = None, recoverable: bool = False):
        super().__init__(message, step_index, action)
        self.recoverable = recoverable

class AppNotFoundError(DesktopAutomationError):
    """Raised when an application cannot be found or opened."""
    pass

class ValidationFailedError(DesktopAutomationError):
    """Raised when a plan or action fails validation."""
    pass

class TimeoutError(DesktopAutomationError):
    """Raised when an action times out."""
    pass
