import datetime
import time
import ctypes
import threading
import webbrowser
from typing import List

class ProactiveManager:
    def __init__(self, calendar_manager, system_control, tts_manager=None, app_launcher=None):
        self.calendar = calendar_manager
        self.system_control = system_control
        self.tts = tts_manager
        self.app_launcher = app_launcher
        self.is_deep_work_active = False
        self.check_interval = 60  # Check every minute
        self.stop_event = threading.Event()
        self.thread = None
        self.handled_events = set() # Track handled events to prevent double triggering

    def start_monitoring(self):
        """Starts the background monitoring thread."""
        if self.thread and self.thread.is_alive():
            return
        
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print("Proactive Monitor started.")

    def stop_monitoring(self):
        """Stops the background monitoring thread."""
        self.stop_event.set()
        if self.thread:
            self.thread.join()
        print("Proactive Monitor stopped.")

    def _monitor_loop(self):
        """Background loop to check for events."""
        while not self.stop_event.is_set():
            try:
                self.check_and_act()
            except Exception as e:
                print(f"Error in Proactive Monitor: {e}")
            
            # Wait for check_interval or stop_event
            if self.stop_event.wait(self.check_interval):
                break

    def check_and_act(self):
        """Checks calendar for upcoming events and triggers actions."""
        # Get upcoming events (raw data for precision)
        events = self.calendar.get_upcoming_events_raw(max_results=10)
        
        now = datetime.datetime.now(datetime.timezone.utc)
        
        # 1. Check for Deep Work (Focus Time) - Active State
        self._handle_deep_work_state(events, now)

        # 2. Check for Upcoming Meetings/Actions (Triggers)
        self._handle_upcoming_triggers(events, now)

    def _handle_deep_work_state(self, events, now):
        """Manages the continuous state of Deep Work (DND)."""
        found_focus_time = False
        for event in events:
            summary = event.get('summary', '').lower()
            if any(phrase in summary for phrase in ["focus time", "deep work", "focus session"]):
                if self._is_happening_now(event, now):
                    found_focus_time = True
                    break
        
        if found_focus_time and not self.is_deep_work_active:
            self.activate_deep_work()
        elif not found_focus_time and self.is_deep_work_active:
            self.deactivate_deep_work()

    def _handle_upcoming_triggers(self, events, now):
        """Checks for events starting soon (e.g., 5 mins) to trigger actions."""
        for event in events:
            event_id = event.get('id')
            if event_id in self.handled_events:
                continue

            start_dt = self._parse_dt(event['start'].get('dateTime'))
            if not start_dt:
                continue

            # Check if event is starting within 5 minutes (and hasn't started yet)
            time_until_start = (start_dt - now).total_seconds() / 60
            
            if 0 <= time_until_start <= 5:
                self._trigger_action_for_event(event)
                self.handled_events.add(event_id)

    def _trigger_action_for_event(self, event):
        """Executes actions based on event keywords."""
        summary = event.get('summary', '').lower()
        print(f"Triggering action for: {summary}")

        # Mapping: Keyword -> (Speech, Action)
        # We can expand this easily
        
        if "zoom" in summary:
            self._speak(f"You have a Zoom meeting in 5 minutes. Opening Zoom.")
            self.app_launcher.open_desktop_app("zoom")
            
        elif "teams" in summary:
            self._speak(f"You have a Teams meeting in 5 minutes. Opening Teams.")
            self.app_launcher.open_desktop_app("teams")
            
        elif "meet" in summary or "google meet" in summary:
            self._speak(f"You have a Google Meet in 5 minutes. Opening browser.")
            # Extract link if possible, otherwise just open meet.google.com
            webbrowser.open("https://meet.google.com")
            
        elif "discord" in summary:
            self._speak(f"You have a Discord call soon. Opening Discord.")
            self.app_launcher.open_desktop_app("discord")
            
        elif "coding" in summary or "dev" in summary:
            self._speak(f"Time to code. Opening VS Code.")
            self.app_launcher.open_desktop_app("code") # Assuming 'code' is the key for VS Code
            
        elif "gym" in summary or "workout" in summary:
            self._speak(f"Time for the gym! Get moving.")
            # Could play music here

    def _is_happening_now(self, event, now):
        start = self._parse_dt(event['start'].get('dateTime'))
        end = self._parse_dt(event['end'].get('dateTime'))
        if start and end:
            return start <= now <= end
        return False

    def _parse_dt(self, dt_str):
        if not dt_str: return None
        try:
            return datetime.datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except:
            return None

    def _speak(self, text):
        if self.tts:
            self.tts.speak(text)

    # --- Deep Work Helpers (Same as before) ---
    def activate_deep_work(self):
        print("Activating Deep Work Mode...")
        self.is_deep_work_active = True
        self._speak("Focus Time detected. Activating Deep Work mode.")
        self.system_control.set_dnd(True)
        self.system_control.minimize_all_windows()

    def deactivate_deep_work(self):
        print("Deactivating Deep Work Mode...")
        self.is_deep_work_active = False
        self._speak("Focus Time ended. Deactivating Deep Work mode.")
        self.system_control.set_dnd(False)


