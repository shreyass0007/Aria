import datetime
import time
import ctypes
import threading
import webbrowser
import json
from typing import List
from .logger import setup_logger

logger = setup_logger(__name__)

class ProactiveManager:
    def __init__(self, calendar_manager, system_control, tts_manager=None, app_launcher=None, brain=None, weather_manager=None, notification_manager=None):
        self.calendar = calendar_manager
        self.system_control = system_control
        self.tts = tts_manager
        self.app_launcher = app_launcher
        self.brain = brain
        self.weather = weather_manager
        self.notification_manager = notification_manager
        
        self.is_deep_work_active = False
        self.check_interval = 60  # Check every minute
        self.stop_event = threading.Event()
        self.thread = None
        self.handled_30min = set() 
        self.handled_5min = set()
        
        # State for daily actions
        self.last_weather_date = None

    def start_monitoring(self):
        """Starts the background monitoring thread."""
        if self.thread and self.thread.is_alive():
            return
        
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.info("Proactive Monitor started.")

    def stop_monitoring(self):
        """Stops the background monitoring thread."""
        self.stop_event.set()
        if self.thread:
            self.thread.join()
        logger.info("Proactive Monitor stopped.")

    def _monitor_loop(self):
        """Background loop to check for events."""
        while not self.stop_event.is_set():
            try:
                self.check_and_act()
            except Exception as e:
                logger.error(f"Error in Proactive Monitor: {e}")
            
            # Wait for check_interval or stop_event
            if self.stop_event.wait(self.check_interval):
                break

    def check_and_act(self):
        """Checks calendar and time to trigger actions."""
        now = datetime.datetime.now()
        
        # 1. TIME RESTRICTION: Run between 5 AM and 11 PM
        if not (5 <= now.hour < 23):
            # If it's outside the window, just return.
            return

        # 2. MORNING BRIEFING (Weather) - Only before 11 AM
        self._handle_morning_briefing(now)

        # 3. CALENDAR CHECKS (Smart Analysis)
        # Get upcoming events
        events = self.calendar.get_upcoming_events_raw(max_results=5)
        
        # Check for Deep Work (Focus Time)
        self._handle_deep_work_state(events, now)

        # Check for Upcoming Meetings/Actions
        self._handle_upcoming_triggers(events, now)

    def _handle_morning_briefing(self, now):
        """Announces weather once per morning (before 11 AM)."""
        # Only run briefing if it's morning (before 11 AM)
        if now.hour >= 11:
            return

        today_str = now.strftime("%Y-%m-%d")
        
        if self.last_weather_date != today_str:
            # Haven't announced today yet
            logger.info("Triggering Morning Briefing...")
            
            if self.weather:
                weather_info = self.weather.get_weather_summary()
                greeting = f"Good morning. {weather_info}"
                self._speak(greeting)
                if self.notification_manager:
                    self.notification_manager.add_notification("Morning Briefing", greeting, type="info")
            else:
                self._speak("Good morning.")
                
            self.last_weather_date = today_str

    def _handle_deep_work_state(self, events, now):
        """Manages the continuous state of Deep Work (DND)."""
        # Convert now to timezone-aware if needed, or rely on _is_happening_now logic
        # For simplicity, we pass 'now' which is local naive, and _is_happening_now handles comparison
        
        found_focus_time = False
        for event in events:
            summary = event.get('summary', '').lower()
            # Still use keywords for Focus Time as it's a specific mode
            if any(phrase in summary for phrase in ["focus time", "deep work", "focus session"]):
                if self._is_happening_now(event, now):
                    found_focus_time = True
                    break
        
        if found_focus_time and not self.is_deep_work_active:
            self.activate_deep_work()
        elif not found_focus_time and self.is_deep_work_active:
            self.deactivate_deep_work()

    def _handle_upcoming_triggers(self, events, now):
        """Checks for events starting soon and uses LLM to decide action."""
        for event in events:
            event_id = event.get('id')

            start_dt = self._parse_dt(event['start'].get('dateTime'))
            if not start_dt:
                continue

            # Check if event is starting within 5 minutes
            # Ensure start_dt is timezone aware/naive compatible with now
            if start_dt.tzinfo:
                now_aware = datetime.datetime.now(start_dt.tzinfo)
                time_until_start = (start_dt - now_aware).total_seconds() / 60
            else:
                time_until_start = (start_dt - now).total_seconds() / 60
            
            # 1. 30-Minute Warning (Window: 25 to 30 mins)
            if 25 <= time_until_start <= 30:
                if event_id not in self.handled_30min:
                    self._trigger_30min_warning(event, time_until_start)
                    self.handled_30min.add(event_id)

            # 2. 5-Minute Warning (Window: 0 to 5 mins)
            elif 0 <= time_until_start <= 5:
                if event_id not in self.handled_5min:
                    # SMART ANALYSIS (Existing logic)
                    self._analyze_and_trigger(event, time_until_start)
                    self.handled_5min.add(event_id)

    def _trigger_30min_warning(self, event, minutes_left):
        """Simple heads-up for ~30 mins before."""
        summary = event.get('summary', 'an event')
        minutes = int(round(minutes_left))
        logger.info(f"Triggering 30-min warning for: {summary} (in {minutes} mins)")
        message = f"Heads up. You have {summary} in {minutes} minutes."
        self._speak(message)
        if self.notification_manager:
            self.notification_manager.add_notification(f"Upcoming Event: {summary}", message, type="reminder")

    def _analyze_and_trigger(self, event, minutes_left):
        """Uses LLM to analyze the event and decide on an action."""
        summary = event.get('summary', '')
        logger.info(f"Analyzing event with LLM: {summary}")
        
        if not self.brain:
            logger.warning("No brain available for analysis.")
            return

        prompt = f"""
        Analyze this calendar event: "{summary}"
        Determine if I should open a specific application or perform an action.
        
        Available Actions:
        - "open_zoom": For Zoom meetings.
        - "open_teams": For Microsoft Teams meetings.
        - "open_meet": For Google Meet.
        - "open_discord": For Discord calls.
        - "open_vscode": For coding, development, or project work.
        - "none": No specific app needed.

        Return ONLY a JSON object:
        {{
            "action": "action_name",
            "reason": "short explanation"
        }}
        """
        
        try:
            llm = self.brain.get_llm()
            if llm:
                response = llm.invoke(prompt).content.strip()
                # Clean markdown if present
                response = response.replace("```json", "").replace("```", "").strip()
                
                data = json.loads(response)
                action = data.get("action", "none")
                
                if action != "none":
                    self._execute_smart_action(action, summary, minutes_left)
                else:
                    # Even if no app action, speak the reminder if it's the 5-min warning
                    minutes = int(round(minutes_left))
                    msg = f"You have {summary} in {minutes} minutes."
                    self._speak(msg)
                    if self.notification_manager:
                        self.notification_manager.add_notification(f"Upcoming Event: {summary}", msg, type="reminder")
                    
        except Exception as e:
            logger.error(f"LLM Analysis failed: {e}")

    def _execute_smart_action(self, action, summary, minutes_left):
        """Executes the action determined by the LLM."""
        logger.info(f"Executing Smart Action: {action}")
        minutes = int(round(minutes_left))
        
        if action == "open_zoom":
            msg = f"You have a Zoom meeting: {summary} in {minutes} minutes. Opening Zoom."
            self._speak(msg)
            if self.notification_manager:
                self.notification_manager.add_notification(f"Zoom Meeting: {summary}", msg, type="action")
            self.app_launcher.open_desktop_app("zoom")
            
        elif action == "open_teams":
            msg = f"You have a Teams meeting: {summary} in {minutes} minutes. Opening Teams."
            self._speak(msg)
            if self.notification_manager:
                self.notification_manager.add_notification(f"Teams Meeting: {summary}", msg, type="action")
            self.app_launcher.open_desktop_app("teams")
            
        elif action == "open_meet":
            msg = f"You have a Google Meet: {summary} in {minutes} minutes. Opening browser."
            self._speak(msg)
            if self.notification_manager:
                self.notification_manager.add_notification(f"Google Meet: {summary}", msg, type="action")
            webbrowser.open("https://meet.google.com")
            
        elif action == "open_discord":
            msg = f"You have a Discord call in {minutes} minutes. Opening Discord."
            self._speak(msg)
            if self.notification_manager:
                self.notification_manager.add_notification(f"Discord Call", msg, type="action")
            self.app_launcher.open_desktop_app("discord")
            
        elif action == "open_vscode":
            msg = f"Time to code: {summary} in {minutes} minutes. Opening VS Code."
            self._speak(msg)
            if self.notification_manager:
                self.notification_manager.add_notification(f"Coding Session: {summary}", msg, type="action")
            self.app_launcher.open_desktop_app("code")

    def _is_happening_now(self, event, now):
        start = self._parse_dt(event['start'].get('dateTime'))
        end = self._parse_dt(event['end'].get('dateTime'))
        
        if start and end:
            # Handle timezone comparison
            if start.tzinfo:
                now = datetime.datetime.now(start.tzinfo)
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

    # --- Deep Work Helpers ---
    def activate_deep_work(self):
        logger.info("Activating Deep Work Mode...")
        self.is_deep_work_active = True
        msg = "Focus Time detected. Activating Deep Work mode."
        self._speak(msg)
        if self.notification_manager:
            self.notification_manager.add_notification("Deep Work Mode", msg, type="system")
        self.system_control.set_dnd(True)
        self.system_control.minimize_all_windows()

    def deactivate_deep_work(self):
        logger.info("Deactivating Deep Work Mode...")
        self.is_deep_work_active = False
        msg = "Focus Time ended. Deactivating Deep Work mode."
        self._speak(msg)
        if self.notification_manager:
            self.notification_manager.add_notification("Deep Work Mode", msg, type="system")
        self.system_control.set_dnd(False)


