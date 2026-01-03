"""
System Control Module for Aria  
Handles volume control, power management, and system maintenance
"""

import os
import subprocess
import ctypes
import winreg
from pycaw.pycaw import AudioUtilities
import winshell
from pathlib import Path
from .logger import setup_logger

logger = setup_logger(__name__)


class SystemControl:
    """
    Provides system-level control for Windows:
    - Volume management (set, increase, decrease, mute, unmute)
    - Power management (lock, sleep, shutdown, restart)
    - System maintenance (empty recycle bin)
    """
    
    def __init__(self):
        """Initialize the system controller and audio interface."""
        self.volume_interface = None
        self._init_audio_interface()
    
    # ==================== INITIALIZATION ====================

    def _init_audio_interface(self):
        """Initialize the audio volume control interface."""
        try:
            # Proper initialization using pycaw and comtypes
            import comtypes
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            
            # Ensure COM is initialized for this thread
            try:
                comtypes.CoInitialize()
            except:
                pass # Already initialized
            
            devices = AudioUtilities.GetSpeakers()
            
            # Handle pycaw 2024+ wrapper which hides Activate inside _dev
            if hasattr(devices, 'Activate'):
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            elif hasattr(devices, '_dev') and hasattr(devices._dev, 'Activate'):
                interface = devices._dev.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            else:
                logger.warning("Could not find Activate method on AudioDevice")
                self.volume_interface = None
                return

            self.volume_interface = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
            logger.info("Audio interface initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize audio interface: {e}")
            self.volume_interface = None

    # ==================== BRIGHTNESS CONTROL ====================

    def get_brightness(self):
        """Get current screen brightness (0-100)."""
        try:
            cmd = "powershell -Command \"(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightness).CurrentBrightness\""
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if result.returncode == 0 and result.stdout.strip().isdigit():
                return int(result.stdout.strip())
            return None
        except Exception as e:
            logger.error(f"Error getting brightness: {e}")
            return None

    def set_brightness(self, level: int):
        """Set screen brightness (0-100)."""
        try:
            level = max(0, min(100, level))
            # WmiSetBrightness(Timeout, Brightness)
            cmd = f"powershell -Command \"(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {level})\""
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                return f"Brightness set to {level}%"
            else:
                return "Failed to set brightness. This feature works best on laptops."
        except Exception as e:
            return f"Error setting brightness: {str(e)}"

    def increase_brightness(self, increment: int = 10):
        """Increase screen brightness."""
        current = self.get_brightness()
        if current is None:
            return "Brightness control not available."
        new_level = min(100, current + increment)
        return self.set_brightness(new_level)

    def decrease_brightness(self, decrement: int = 10):
        """Decrease screen brightness."""
        current = self.get_brightness()
        if current is None:
            return "Brightness control not available."
        new_level = max(0, current - decrement)
        return self.set_brightness(new_level)

    # ==================== VOLUME CONTROL ====================
    
    def get_volume(self):
        """Get current system volume level (0-100)."""
        if not self.volume_interface:
            return None
        try:
            current_volume = self.volume_interface.GetMasterVolumeLevelScalar()
            return int(current_volume * 100)
        except Exception as e:
            logger.error(f"Error getting volume: {e}")
            return None
    
    def set_volume(self, level: int):
        """Set system volume to specific level (0-100)."""
        if not self.volume_interface:
            return "Volume control is not available on this system."
        try:
            level = max(0, min(100, level))
            volume_scalar = level / 100.0
            self.volume_interface.SetMasterVolumeLevelScalar(volume_scalar, None)
            return f"Volume set to {level}%"
        except Exception as e:
            return f"Error setting volume: {str(e)}"
    
    def increase_volume(self, increment: int = 10):
        """Increase system volume."""
        current = self.get_volume()
        if current is None:
            return "Volume control is not available."
        new_level = min(100, current + increment)
        self.set_volume(new_level)
        return f"Volume increased to {new_level}%"
    
    def decrease_volume(self, decrement: int = 10):
        """Decrease system volume."""
        current = self.get_volume()
        if current is None:
            return "Volume control is not available."
        new_level = max(0, current - decrement)
        self.set_volume(new_level)
        return f"Volume decreased to {new_level}%"
    
    def mute(self):
        """Mute system audio."""
        if not self.volume_interface:
            return "Volume control is not available on this system."
        try:
            self.volume_interface.SetMute(1, None) # 1 for True
            return "System muted"
        except Exception as e:
            return f"Error muting system: {str(e)}"
    
    def unmute(self):
        """Unmute system audio."""
        if not self.volume_interface:
            return "Volume control is not available on this system."
        try:
            self.volume_interface.SetMute(0, None) # 0 for False
            current = self.get_volume()
            return f"System unmuted (Volume: {current}%)"
        except Exception as e:
            return f"Error unmuting system: {str(e)}"
    
    def is_muted(self):
        """Check if system is muted."""
        if not self.volume_interface:
            return False
        try:
            return bool(self.volume_interface.GetMute())
        except Exception:
            return False
    
    # ==================== POWER MANAGEMENT ====================
    
    def lock_system(self):
        """Lock the Windows workstation."""
        try:
            ctypes.windll.user32.LockWorkStation()
            return "Locking workstation"
        except Exception as e:
            return f"Error locking system: {str(e)}"
    
    def sleep_system(self):
        """Put system into sleep mode."""
        try:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return "Putting system to sleep"
        except Exception as e:
            return f"Error putting system to sleep: {str(e)}"
    
    def shutdown_system(self, timer: int = 0):
        """Shutdown the system."""
        try:
            if timer > 0:
                subprocess.run(["shutdown", "/s", "/t", str(timer)], check=True)
                return f"System will shutdown in {timer} seconds"
            else:
                subprocess.run(["shutdown", "/s", "/t", "0"], check=True)
                return "Shutting down system now"
        except Exception as e:
            return f"Error shutting down system: {str(e)}"
    
    def restart_system(self, timer: int = 0):
        """Restart the system."""
        try:
            if timer > 0:
                subprocess.run(["shutdown", "/r", "/t", str(timer)], check=True)
                return f"System will restart in {timer} seconds"
            else:
                subprocess.run(["shutdown", "/r", "/t", "0"], check=True)
                return "Restarting system now"
        except Exception as e:
            return f"Error restarting system: {str(e)}"
    
    def cancel_shutdown(self):
        """Cancel pending shutdown/restart."""
        try:
            subprocess.run(["shutdown", "/a"], check=True)
            return "Shutdown/restart cancelled"
        except Exception as e:
            return f"Error cancelling shutdown: {str(e)}"
    
    # ==================== SYSTEM MAINTENANCE ====================
    
    def empty_recycle_bin(self):
        """Empty the Windows recycle bin."""
        try:
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            return "Recycle bin emptied successfully"
        except Exception as e:
            return f"Error emptying recycle bin: {str(e)}"
    
    def get_recycle_bin_size(self):
        """Get current status and size of recycle bin."""
        try:
            # Get item count using winshell
            bin_items = list(winshell.recycle_bin())
            item_count = len(bin_items)
            
            # Calculate size using os.walk (much faster than PowerShell)
            try:
                recycle_bin_path = Path("C:/$Recycle.Bin")
                total_size = 0
                
                # Walk through all files in recycle bin
                if recycle_bin_path.exists():
                    for file_path in recycle_bin_path.rglob('*'):
                        try:
                            if file_path.is_file():
                                total_size += file_path.stat().st_size
                        except (OSError, PermissionError):
                            # Skip files we can't access
                            continue
                
                # Convert to human-readable format
                size_mb = total_size / (1024 * 1024)
                
                if size_mb < 0.01:
                    # Very small, just show count
                    return f"Recycle bin contains {item_count} items"
                elif size_mb < 1024:
                    return f"Recycle bin contains {item_count} items ({size_mb:.2f} MB)"
                else:
                    size_gb = size_mb / 1024
                    return f"Recycle bin contains {item_count} items ({size_gb:.2f} GB)"
                    
            except Exception as e:
                # Fallback to just count
                logger.warning(f"Could not calculate size: {e}")
                return f"Recycle bin contains {item_count} items"
                
        except Exception as e:
            return f"Error checking recycle bin: {str(e)}"


    # ==================== WINDOWS & FOCUS MANAGEMENT ====================

    def set_dnd(self, enable: bool):
        """
        Toggles Windows Focus Assist / Do Not Disturb.
        """
        try:
            # Registry path for Notifications
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Notifications\Settings"
            
            # NOC_GLOBAL_SETTING_TOASTS_ENABLED: 1 = On (Notifications allowed), 0 = Off (DND)
            value = 0 if enable else 1
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "NOC_GLOBAL_SETTING_TOASTS_ENABLED", 0, winreg.REG_DWORD, value)
            
            state = "enabled" if enable else "disabled"
            return f"Do Not Disturb {state}"
            
        except Exception as e:
            return f"Failed to toggle DND: {str(e)}"

    def get_dnd_status(self):
        """Checks if Do Not Disturb is enabled."""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Notifications\Settings"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "NOC_GLOBAL_SETTING_TOASTS_ENABLED")
                # 0 = DND On, 1 = DND Off
                return value == 0
        except Exception:
            # Default to False if key doesn't exist
            return False

    def minimize_all_windows(self):
        """Minimizes all windows except Aria and the Taskbar."""
        try:
            user32 = ctypes.windll.user32
            
            def enum_handler(hwnd, ctx):
                if user32.IsWindowVisible(hwnd):
                    length = user32.GetWindowTextLengthW(hwnd)
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    title = buff.value
                    
                    # Skip essential windows
                    if not title or title == "Program Manager":
                        return True
                    
                    # Check for Aria (assuming window title contains "Aria")
                    if "Aria" in title:
                        return True
                        
                    # Minimize (SW_MINIMIZE = 6)
                    user32.ShowWindow(hwnd, 6)
                    
                return True
    
            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_long)
            user32.EnumWindows(WNDENUMPROC(enum_handler), 0)
            return "All windows minimized"
        except Exception as e:
            return f"Error minimizing windows: {str(e)}"


if __name__ == "__main__":
    controller = SystemControl()
    print("Testing System Control Module...")
    print(f"Current Volume: {controller.get_volume()}%")
    print(f"Is Muted: {controller.is_muted()}") 
    print(f"Recycle Bin: {controller.get_recycle_bin_size()}")
