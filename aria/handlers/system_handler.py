import random
import re
import datetime
from typing import Dict, Any, Optional
from .base_handler import BaseHandler
from ..logger import setup_logger

logger = setup_logger(__name__)

class SystemHandler(BaseHandler):
    def __init__(self, tts_manager, system_control, clipboard_screenshot, system_monitor):
        super().__init__(tts_manager)
        self.system_control = system_control
        self.clipboard_screenshot = clipboard_screenshot
        self.system_monitor = system_monitor

    def should_handle(self, intent: str) -> bool:
        system_intents = [
            "focus_mode_on", "focus_mode_off", "minimize_all",
            "screenshot", "screenshot_take", "lock_screen", "lock",
            "volume_up", "volume_down", "volume_set",
            "shutdown", "restart", "sleep", "cancel_shutdown",
            "recycle_bin_empty", "recycle_bin_check",
            "battery_check", "cpu_check", "ram_check", "system_stats",
            "battery_check", "cpu_check", "ram_check", "system_stats",
            "clipboard_copy", "clipboard_read", "clipboard_clear",
            "time_check", "date_check"
        ]
        return intent in system_intents

    def _get_random_response(self, intent: str, context: str = "") -> str:
        responses = {
            "volume_up": ["Turning it up.", "Volume increased.", "Got it, louder.", "Boosting the volume."],
            "volume_down": ["Turning it down.", "Volume decreased.", "Got it, quieter.", "Lowering the volume."],
            "lock": ["Locking the screen.", "Securing the system.", "Locking up.", "Screen locked."],
            "sleep": ["Going to sleep.", "Entering sleep mode.", "Goodnight.", "Sleeping now."]
        }
        options = responses.get(intent, [])
        if options:
            return random.choice(options)
        return f"Executing {intent}."

    def handle(self, text: str, intent: str, parameters: Dict[str, Any]) -> Optional[str]:
        # --- SYSTEM CONTROL ---
        if intent == "focus_mode_on":
            self.tts_manager.speak("Activating Focus Mode. Minimizing distractions.")
            self.system_control.set_dnd(True)
            self.system_control.minimize_all_windows()
            return "Focus Mode activated."
        elif intent == "focus_mode_off":
            self.tts_manager.speak("Deactivating Focus Mode.")
            self.system_control.set_dnd(False)
            return "Focus Mode deactivated."
        elif intent == "minimize_all":
            self.tts_manager.speak("Minimizing all windows.")
            self.system_control.minimize_all_windows()
            return "All windows minimized."

        elif intent == "screenshot" or intent == "screenshot_take":
            logger.debug("Executing screenshot handler")
            filename = parameters.get("filename", None)
            self.tts_manager.speak("Taking screenshot.")
            result = self.clipboard_screenshot.take_screenshot(filename)
            logger.debug(f"Screenshot result: {result}")
            return result

        elif intent == "lock_screen" or intent == "lock":
            logger.debug("Executing lock_screen handler")
            self.tts_manager.speak("Locking screen.")
            result = self.system_control.lock_system()
            logger.debug(f"Lock screen result: {result}")
            return result

        elif intent == "volume_up":
            self.system_control.increase_volume()
            self.tts_manager.speak(self._get_random_response("volume_up"))
            return "Volume increased."
        elif intent == "volume_down":
            self.system_control.decrease_volume()
            self.tts_manager.speak(self._get_random_response("volume_down"))
            return "Volume decreased."
        elif intent == "volume_set":
            level = parameters.get("level")
            if level:
                try:
                    # Remove non-numeric characters (e.g. "50%" -> "50")
                    clean_level = re.sub(r'[^\d]', '', str(level))
                    if clean_level:
                        vol = int(clean_level)
                        msg = self.system_control.set_volume(vol)
                        self.tts_manager.speak(msg)
                        return msg
                except ValueError:
                    pass # Fallthrough to regex extraction from full text
            
            # Fallback: Extract from full text
            nums = re.findall(r'\d+', text)
            if nums:
                vol = int(nums[-1])
                msg = self.system_control.set_volume(vol)
                self.tts_manager.speak(msg)
                return msg
            
            self.tts_manager.speak("What volume level?")
            return "Please specify volume level."

        elif intent == "shutdown":
            self.tts_manager.speak("Shutting down in 10 seconds. Say 'cancel shutdown' to abort.")
            self.system_control.shutdown_system(timer=10)
            return "Shutting down system."
        
        elif intent == "restart":
            self.tts_manager.speak("Restarting in 10 seconds. Say 'cancel restart' to abort.")
            self.system_control.restart_system(timer=10)
            return "Restarting system."
            
        elif intent == "sleep":
            self.system_control.sleep_system()
            self.tts_manager.speak(self._get_random_response("sleep"))
            return "System sleeping."
            
        elif intent == "cancel_shutdown":
            msg = self.system_control.cancel_shutdown()
            self.tts_manager.speak(msg)
            return msg
            
        elif intent == "recycle_bin_empty":
            self.tts_manager.speak("Emptying recycle bin...")
            msg = self.system_control.empty_recycle_bin()
            self.tts_manager.speak(msg)
            return msg
        elif intent == "recycle_bin_check":
            msg = self.system_control.get_recycle_bin_size()
            self.tts_manager.speak(msg)
            return msg

        # --- CLIPBOARD ---
        elif intent == "clipboard_copy":
            text_to_copy = parameters.get("text")
            if text_to_copy:
                self.clipboard_screenshot.copy_to_clipboard(text_to_copy)
                self.tts_manager.speak("Copied to clipboard.")
                return f"Copied '{text_to_copy}' to clipboard."
            else:
                self.tts_manager.speak("What should I copy?")
                return "Please specify text to copy."

        elif intent == "clipboard_read":
            content = self.clipboard_screenshot.read_clipboard()
            self.tts_manager.speak(f"Clipboard contains: {content}")
            return f"Clipboard: {content}"

        elif intent == "clipboard_clear":
            self.clipboard_screenshot.clear_clipboard()
            self.tts_manager.speak("Clipboard cleared.")
            return "Clipboard cleared."

        # --- SYSTEM MONITORING ---
        elif intent == "battery_check":
            status = self.system_monitor.get_battery_status()
            if status:
                response = f"Battery is at {status['percent']}% and {'plugged in' if status['power_plugged'] else 'on battery power'}."
            else:
                response = "I couldn't detect a battery. You might be on a desktop."
            self.tts_manager.speak(response)
            return response

        elif intent == "cpu_check":
            status = self.system_monitor.get_cpu_usage()
            response = f"Current CPU usage is {status}%."
            self.tts_manager.speak(response)
            return response

        elif intent == "ram_check":
            status = self.system_monitor.get_ram_usage()
            response = f"Current RAM usage is {status}%."
            self.tts_manager.speak(response)
            return response

        elif intent == "system_stats":
            stats = self.system_monitor.get_all_stats()
            response = "Here is your system status:\n"
            bat = stats.get("battery")
            if bat:
                response += f"- Battery: {bat['percent']}% ({'Plugged In' if bat['power_plugged'] else 'On Battery'})\n"
            else:
                response += "- Battery: Not detected\n"
            response += f"- CPU Usage: {stats.get('cpu')}%\n"
            response += f"- RAM Usage: {stats.get('ram')}%\n"
            self.tts_manager.speak("Here is your system status.")
            return response

        # --- TIME & DATE ---
        elif intent == "time_check":
            now = datetime.datetime.now()
            time_str = now.strftime("%I:%M %p")
            response = f"It is currently {time_str}."
            self.tts_manager.speak(response)
            return response

        elif intent == "date_check":
            now = datetime.datetime.now()
            date_str = now.strftime("%A, %B %d, %Y")
            response = f"Today is {date_str}."
            self.tts_manager.speak(response)
            return response

        return None
