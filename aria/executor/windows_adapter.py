
import subprocess
import time
import pyautogui
import keyboard
import logging
import shutil
from aria.executor.error_types import AppNotFoundError

logger = logging.getLogger(__name__)

class WindowsAdapter:
    def open_app(self, name: str):
        logger.info(f"Opening app: {name}")
        
        # 1. Cleaner Name
        clean_name = name.lower().strip()
        
        # 2. Try Standard PATH / Executable Search
        executable_path = shutil.which(clean_name) or shutil.which(clean_name + ".exe")
        
        if executable_path:
            try:
                subprocess.Popen(executable_path, shell=True)
                time.sleep(2.0)
                return True
            except Exception:
                pass # Fall through to other methods
        
        # 3. Try 'start' command (Handles Registered Apps & Protocols)
        # This handles 'notepad', 'calc', and UWP apps like 'whatsapp:'
        try:
            logger.info(f"Attempting shell start for: {clean_name}")
            # Try as protocol first (e.g. "whatsapp:")
            subprocess.run(f"start {clean_name}:", shell=True, check=True) 
            time.sleep(2.0)
            return True
        except subprocess.CalledProcessError:
            pass

        try:
            # Try as standard shell command (e.g. "start chrome")
            subprocess.run(f"start {clean_name}", shell=True, check=True)
            time.sleep(2.0)
            return True
        except subprocess.CalledProcessError:
             logger.error(f"Failed to open app {clean_name} via shell")
             raise AppNotFoundError(f"Could not open application: {name}")

    def close_app(self, name: str):
        logger.info(f"Closing app: {name}")
        # Requires identifying process. For Phase 1, we might skip complex process logic
        # or use taskkill if name matches exe
        try:
            subprocess.run(f"taskkill /IM {name}.exe /F", shell=True, check=True)
            return True
        except subprocess.CalledProcessError:
            logger.warning(f"Could not close {name}, might not be running.")
            return False

    def type_text(self, text: str):
        logger.info(f"Typing text: {text}")
        pyautogui.write(text)
        return True

    def press_key(self, key: str):
        logger.info(f"Pressing key: {key}")
        pyautogui.press(key)
        return True

    def wait(self, seconds: float):
        logger.info(f"Waiting for {seconds} seconds")
        time.sleep(float(seconds))
        return True

    def click(self, x: int, y: int):
        logger.info(f"Clicking at {x}, {y}")
        pyautogui.click(x=x, y=y)
        return True
    
    def read_screen(self):
        logger.info("Reading screen")
        # For Phase 1, just returning a placeholder or screenshot path
        # Real implementation needs OCR
        return "Screen reading not implemented in Phase 1"
