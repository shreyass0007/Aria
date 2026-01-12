
import platform
import logging
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass

from aria.executor.windows_adapter import WindowsAdapter
from aria.executor.macos_adapter import MacOSAdapter
from aria.executor.linux_adapter import LinuxAdapter
from aria.executor.error_types import ActionFailedError, AppNotFoundError, TimeoutError
from aria.vision.vision_manager import VisionManager
from aria.executor.state_monitor import DesktopStateMonitor
import time

from aria.logger import setup_desktop_logger

logger = setup_desktop_logger(__name__)

@dataclass
class ExecutionResult:
    status: str  # "success", "failed", "error"
    step_index: int
    action: str
    message: Optional[str] = None
    data: Optional[Any] = None

class DesktopExecutor:
    """
    Executes the desktop automation plans on the target OS.
    """
    MAX_RETRIES = 2
    RETRY_DELAY = 1.0

    def __init__(self):
        self.os_type = platform.system()
        self.adapter = self._get_adapter()
        try:
            self.vision = VisionManager()
            logger.info("VisionManager initialized")
        except Exception as e:
            logger.error(f"Failed to init VisionManager: {e}")
            self.vision = None
            
        try:
            self.state_monitor = DesktopStateMonitor()
            logger.info("DesktopStateMonitor initialized")
        except Exception as e:
            logger.error(f"Failed to init DesktopStateMonitor: {e}")
            self.state_monitor = None
            
        logger.info(f"DesktopExecutor initialized for {self.os_type}")

    def _get_adapter(self):
        if self.os_type == "Windows":
            return WindowsAdapter()
        elif self.os_type == "Darwin":
            return MacOSAdapter()
        elif self.os_type == "Linux":
            return LinuxAdapter()
        else:
            raise NotImplementedError(f"OS {self.os_type} not supported")

    async def execute_plan(self, plan: Dict[str, Any], on_update=None) -> bool:
        """
        Executes a validated plan.
        on_update: async callback(step_index, action_name, status, message=None)
        """
        logger.info("Starting plan execution")
        actions = plan.get("actions", [])
        
        for i, action in enumerate(actions):
            action_name = action.get("action")
            params = action.get("params", {})
            logger.info(f"Executing step {i+1}/{len(actions)}: {action_name} params={params}")
            
            # Notify Running
            if on_update:
                try:
                    await on_update(i, action_name, "running")
                except Exception as e:
                    logger.error(f"Error in on_update callback: {e}")

            # Execute with Retry
            result = await self._execute_action_with_retry(i, action_name, params)

            # Handle Result
            if result.status == "success":
                if on_update:
                    await on_update(i, action_name, "completed", message=result.message)
            else:
                logger.error(f"Step {i} failed: {result.message}")
                if on_update:
                    await on_update(i, action_name, "failed", message=result.message)
                return False
                
        logger.info("Plan executed successfully")
        return True

    async def _execute_action_with_retry(self, index: int, action_name: str, params: dict) -> ExecutionResult:
        """Executes a single action with retry logic."""
        last_error = None
        
        # Determine if action is safe to retry
        # Typing and clicking are generally safe to retry if they fail immediately
        # Opening apps might effectively be idempotent
        is_retriable = action_name in ["open_app", "click", "wait", "type"]
        retries = self.MAX_RETRIES if is_retriable else 0

        for attempt in range(retries + 1):
            try:
                success = self._execute_action_impl(action_name, params)
                if success:
                    return ExecutionResult(status="success", step_index=index, action=action_name)
                else:
                    # Logic failure (returned False but raised no exception)
                    last_error = "Action returned False"
            except ActionFailedError as e:
                last_error = str(e)
                # If explicitly marked as NOT recoverable, fail immediately
                if hasattr(e, 'recoverable') and not e.recoverable:
                    logger.error(f"Action {action_name} failed with unrecoverable error.")
                    return ExecutionResult(status="failed", step_index=index, action=action_name, message=last_error)
            except Exception as e:
                # Catch unexpected adapter errors
                last_error = f"Unexpected error: {str(e)}"
            
            logger.warning(f"Attempt {attempt+1}/{retries+1} failed for {action_name}: {last_error}")
            if attempt < retries:
                await asyncio.sleep(self.RETRY_DELAY)

        return ExecutionResult(status="failed", step_index=index, action=action_name, message=last_error)

    def _execute_action_impl(self, action_name: str, params: dict) -> bool:
        """Internal synchronous execution of the adapter action."""
        try:
            if action_name == "open_app":
                return self.adapter.open_app(params.get("name"))
            elif action_name == "close_app":
                return self.adapter.close_app(params.get("name"))
            elif action_name == "type":
                return self.adapter.type_text(params.get("text"))
            elif action_name == "press":
                return self.adapter.press_key(params.get("key"))
            elif action_name == "wait":
                return self.adapter.wait(params.get("seconds", 1.0))
            elif action_name == "click":
                return self.adapter.click(params.get("x"), params.get("y"))
            elif action_name == "read_screen":
                result = self.adapter.read_screen()
                logger.info(f"Screen read result: {result}")
                return True
            elif action_name == "get_active_window":
                title = self.state_monitor.get_active_window_title()
                logger.info(f"Active Window: {title}")
                return True
            elif action_name == "focus_window":
                title = params.get("title", "")
                logger.info(f"Focusing window: {title}")
                return self.state_monitor.focus_window(title)
            elif action_name == "click_text":
                text = params.get("text")
                logger.info(f"Attempting to click text: {text}")
                
                # 1. Try Standard Search
                coords = self.vision.find_text(text)
                
                # 2. Try Fuzzy Search (Self-Healing)
                if not coords:
                    logger.warning(f"Text '{text}' not found, retrying with fuzzy match...")
                    coords = self.vision.find_text(text, fuzzy=True)

                if coords:
                    return self.adapter.click(coords[0], coords[1])
                else:
                    raise ActionFailedError(f"Text '{text}' not found on screen", recoverable=True)
            elif action_name == "wait_for_text":
                text = params.get("text")
                timeout = params.get("timeout", 10)
                logger.info(f"Waiting for text: {text} (timeout={timeout}s)")
                
                start_time = time.time()
                while time.time() - start_time < timeout:
                    if self.vision.find_text(text):
                        return True
                    time.sleep(1.0)
                raise TimeoutError(f"Timed out waiting for text '{text}'")
            elif action_name == "analyze_screen":
                prompt = params.get("prompt", "Describe this screen.")
                logger.info(f"Analyzing screen with AI: {prompt}")
                
                # Capture screen
                img_b64 = self.vision.capture_screen_base64()
                
                # Call Brain (Lazy import to avoid circular dep)
                from aria.brain import AriaBrain
                brain = AriaBrain() # This might re-init, but it's lightweight due to lazy loading
                
                response = brain.ask_vision(prompt, img_b64)
                logger.info(f"Screen Analysis: {response}")
                return response # Return the string answer
            else:
                logger.warning(f"Unknown action: {action_name}")
                raise ActionFailedError(f"Unknown action: {action_name}")
        except Exception as e:
            # Wrap generic adapter exceptions
            raise ActionFailedError(f"Adapter error: {str(e)}") from e
