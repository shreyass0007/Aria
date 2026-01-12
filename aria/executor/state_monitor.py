import platform
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class DesktopStateMonitor:
    """
    Monitors the state of the desktop, including active windows and running applications.
    """
    def __init__(self):
        self.os_type = platform.system()
    
    def get_active_window_title(self) -> str:
        """Returns the title of the currently focused window."""
        try:
            if self.os_type == "Windows":
                return self._get_windows_active_window()
            elif self.os_type == "Darwin":
                # Placeholder for MacOS
                return "Unknown (MacOS)"
            elif self.os_type == "Linux":
                # Placeholder for Linux
                return "Unknown (Linux)"
            else:
                return "Unknown"
        except Exception as e:
            logger.error(f"Error getting active window: {e}")
            return "Unknown"

    def focus_window(self, title_substring: str, retries: int = 5) -> bool:
        """Brings a window containing `title_substring` to the foreground. Retries for startup."""
        logger.info(f"Attempting to focus window containing: '{title_substring}'")
        import time
        
        for i in range(retries):
            try:
                if self.os_type == "Windows":
                    if self._focus_windows_window(title_substring):
                        return True
            except Exception as e:
                logger.error(f"Error focusing window (attempt {i+1}): {e}")
            
            # Wait a bit before retrying (useful if app is just launching)
            time.sleep(1.0)
            
        logger.warning(f"No window found matching: {title_substring} after {retries} attempts")
        return False

    def _focus_windows_window(self, title_substring: str) -> bool:
        import ctypes
        user32 = ctypes.windll.user32
        
        # Callback for EnumWindows
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        
        target_hwnd = []
        
        def enum_window_callback(hwnd, lParam):
            length = user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            window_title = buff.value
            
            if user32.IsWindowVisible(hwnd) and length > 0:
                if title_substring.lower() in window_title.lower():
                    target_hwnd.append(hwnd)
                    return False # Stop enumeration
            return True
            
        user32.EnumWindows(WNDENUMPROC(enum_window_callback), 0)
        
        if target_hwnd:
            hwnd = target_hwnd[0]
            # Restore if minimized
            if user32.IsIconic(hwnd):
                user32.ShowWindow(hwnd, 9) # SW_RESTORE
            
            # Bring to front
            # Implementation trick for Windows 10/11 strict focus rules:
            # AttachThreadInput can trick the OS into allowing focus steal
            current_thread = ctypes.windll.kernel32.GetCurrentThreadId()
            target_thread = user32.GetWindowThreadProcessId(hwnd, None)
            
            user32.AttachThreadInput(current_thread, target_thread, True)
            user32.SetForegroundWindow(hwnd)
            user32.AttachThreadInput(current_thread, target_thread, False)
            return True
            
        logger.warning(f"No window found matching: {title_substring}")
        return False

    def _get_windows_active_window(self) -> str:
        import ctypes
        user32 = ctypes.windll.user32
        
        hwnd = user32.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value
