import datetime
import time
import ctypes
import winreg
import threading
from typing import List

class DeepWorkManager:
    def __init__(self, calendar_manager, tts_manager=None):
        self.calendar = calendar_manager
        self.tts = tts_manager
        self.is_deep_work_active = False
        self.check_interval = 60  # Check every minute
        self.stop_event = threading.Event()
        self.thread = None

    def start_monitoring(self):
        """Starts the background monitoring thread."""
        if self.thread and self.thread.is_alive():
            return
        
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print("Deep Work Monitor started.")

    def stop_monitoring(self):
        """Stops the background monitoring thread."""
        self.stop_event.set()
        if self.thread:
            self.thread.join()
        print("Deep Work Monitor stopped.")

    def _monitor_loop(self):
        """Background loop to check for Focus Time."""
        while not self.stop_event.is_set():
            try:
                self.check_and_activate()
            except Exception as e:
                print(f"Error in Deep Work Monitor: {e}")
            
            # Wait for check_interval or stop_event
            if self.stop_event.wait(self.check_interval):
                break

    def check_and_activate(self):
        """Checks calendar for 'Focus Time' and toggles Deep Work mode."""
        # Get current events
        # We need to check if we are CURRENTLY in a Focus Time event
        # The calendar manager's get_upcoming_events might not be precise enough for "right now" 
        # if we don't filter correctly, but let's try to use get_events_for_date('today') and parse.
        
        # Better approach: Use get_upcoming_events_raw and check time ranges
        events = self.calendar.get_upcoming_events_raw(max_results=10)
        
        now = datetime.datetime.now(datetime.timezone.utc)
        found_focus_time = False
        
        for event in events:
            summary = event.get('summary', '').lower()
            # Check for various trigger phrases
            trigger_phrases = ["focus time", "deep work", "focus session"]
            if any(phrase in summary for phrase in trigger_phrases):
                start = event['start'].get('dateTime')
                end = event['end'].get('dateTime')
                
                if start and end:
                    try:
                        # Parse ISO format
                        start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                        end_dt = datetime.datetime.fromisoformat(end.replace('Z', '+00:00'))
                        
                        # Check if now is within the event range
                        if start_dt <= now <= end_dt:
                            found_focus_time = True
                            break
                    except Exception as e:
                        print(f"Date parsing error in DeepWorkManager: {e}")

        if found_focus_time and not self.is_deep_work_active:
            self.activate_deep_work()
        elif not found_focus_time and self.is_deep_work_active:
            self.deactivate_deep_work()

    def activate_deep_work(self):
        """Enables DND and minimizes apps."""
        print("Activating Deep Work Mode...")
        self.is_deep_work_active = True
        
        if self.tts:
            self.tts.speak("Focus Time detected. Activating Deep Work mode.")
            
        self._set_dnd(True)
        self._minimize_distractions()

    def deactivate_deep_work(self):
        """Disables DND."""
        print("Deactivating Deep Work Mode...")
        self.is_deep_work_active = False
        
        if self.tts:
            self.tts.speak("Focus Time ended. Deactivating Deep Work mode.")
            
        self._set_dnd(False)

    def _set_dnd(self, enable: bool):
        """
        Toggles Windows Focus Assist / Do Not Disturb.
        Note: This uses a registry hack and might require Explorer restart or might not work on all Windows versions immediately.
        """
        try:
            # Registry path for Notifications
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Notifications\Settings"
            
            # 0 = Enabled (Notifications allowed), 1 = Disabled (No toasts) - Wait, logic might be inverted for "Toasts Enabled"
            # Actually, NOC_GLOBAL_SETTING_TOASTS_ENABLED: 1 = On, 0 = Off
            
            value = 0 if enable else 1
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "NOC_GLOBAL_SETTING_TOASTS_ENABLED", 0, winreg.REG_DWORD, value)
            
            print(f"DND set to {enable} (Registry updated)")
            
        except Exception as e:
            print(f"Failed to toggle DND: {e}")

    def _minimize_distractions(self):
        """Minimizes all windows except Aria and the Taskbar."""
        print("Minimizing distractions...")
        
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
                    
                # Minimize
                # SW_MINIMIZE = 6
                user32.ShowWindow(hwnd, 6)
                print(f"Minimized: {title}")
                
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_long)
        user32.EnumWindows(WNDENUMPROC(enum_handler), 0)

if __name__ == "__main__":
    # Test stub
    class MockCalendar:
        def get_upcoming_events_raw(self, max_results):
            # Return a fake event for testing
            now = datetime.datetime.now(datetime.timezone.utc)
            start = now - datetime.timedelta(minutes=10)
            end = now + datetime.timedelta(minutes=50)
            return [{
                'summary': 'Focus Time',
                'start': {'dateTime': start.isoformat().replace('+00:00', 'Z')},
                'end': {'dateTime': end.isoformat().replace('+00:00', 'Z')}
            }]

    print("Testing DeepWorkManager...")
    manager = DeepWorkManager(MockCalendar())
    manager.check_and_activate()
    time.sleep(2)
    manager.deactivate_deep_work()
