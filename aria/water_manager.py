import datetime
import threading
import time
import json
import os
from .logger import setup_logger

logger = setup_logger(__name__)

class WaterManager:
    def __init__(self, tts_manager=None, notification_manager=None, weather_manager=None, system_control=None):
        self.tts = tts_manager
        self.notification_manager = notification_manager
        self.weather_manager = weather_manager
        self.system_control = system_control
        
        self.interval_minutes = 90  # Default 90 minutes
        self.is_running = False
        self.thread = None
        self.stop_event = threading.Event()
        self.last_drink_time = datetime.datetime.now()
        
        # Persistence file
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "water_config.json")
        self._load_state()

    def _load_state(self):
        """Loads state from config file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.interval_minutes = data.get("interval_minutes", 90)
                    should_run = data.get("is_running", False)
                    
                    if should_run:
                        logger.info("Restoring Water Reminder state: Running")
                        self.start_monitoring()
            except Exception as e:
                logger.error(f"Failed to load water config: {e}")

    def _save_state(self):
        """Saves state to config file."""
        try:
            data = {
                "interval_minutes": self.interval_minutes,
                "is_running": self.is_running
            }
            with open(self.config_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Failed to save water config: {e}")

    def start_monitoring(self, interval_minutes=None):
        """Starts the water reminder monitor."""
        if interval_minutes:
            self.interval_minutes = interval_minutes
            
        if self.is_running:
            # If already running, just update state file to be sure
            self._save_state()
            logger.info("Water Monitor already running.")
            return "Water reminder is already active."
            
        self.stop_event.clear()
        self.is_running = True
        self.last_drink_time = datetime.datetime.now()
        
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        
        self._save_state()
        
        msg = f"Water reminder started. I will remind you every {self.interval_minutes} minutes."
        logger.info(msg)
        return msg

    def stop_monitoring(self):
        """Stops the water reminder monitor."""
        if not self.is_running:
            self._save_state() # Ensure consistent state
            return "Water reminder is not running."
            
        self.stop_event.set()
        if self.thread and self.thread != threading.current_thread():
            self.thread.join(timeout=2)
            
        self.is_running = False
        self._save_state()
        
        msg = "Water reminder stopped."
        logger.info(msg)
        return msg

    def set_interval(self, minutes):
        """Sets the reminder interval."""
        try:
            self.interval_minutes = int(minutes)
            self._save_state()
            return f"Water reminder interval set to {self.interval_minutes} minutes."
        except ValueError:
            return "Invalid interval. Please provide a number."

    def reset_timer(self):
        """Resets the timer (user drank water)."""
        self.last_drink_time = datetime.datetime.now()
        return "Great! Timer reset."

    def _monitor_loop(self):
        """Background loop to check time."""
        logger.info("Water Monitor Loop Started")
        
        while not self.stop_event.is_set():
            # Check every minute
            if self.stop_event.wait(60):
                break
                
            now = datetime.datetime.now()
            
            # ADAPTIVE LOGIC
            current_interval = self.interval_minutes
            
            # 1. Weather Adaptation
            if self.weather_manager:
                try:
                    # We need a way to get cached temp without making API calls every minute
                    # WeatherManager caches for 10 mins, so calling get_weather is safe-ish,
                    # but we need a city. Let's assume default city or last known.
                    # For now, let's just check if we have cached data for "Pimpri, Maharashtra, India" (default)
                    # Or better, add a method to WeatherManager to get last known temp.
                    # Since we can't easily modify WeatherManager right now without context, 
                    # let's skip complex API calls here to avoid rate limits if cache expires.
                    # Ideally, ProactiveManager updates weather.
                    pass
                except Exception:
                    pass

            elapsed = (now - self.last_drink_time).total_seconds() / 60
            
            if elapsed >= current_interval:
                self._trigger_reminder()
                self.last_drink_time = now

    def _trigger_reminder(self):
        """Triggers the reminder notification."""
        msg = "Time to drink water! Stay hydrated."
        logger.info("Triggering Water Reminder")
        
        # 2. Activity Adaptation (DND Check)
        is_dnd = False
        if self.system_control:
            is_dnd = self.system_control.get_dnd_status()
            
        if is_dnd:
            logger.info("DND is active. Suppressing voice reminder.")
            # Only send notification (silent)
            if self.notification_manager:
                self.notification_manager.add_notification("Water Reminder", msg, type="reminder")
        else:
            # Normal mode
            if self.tts:
                self.tts.speak(msg)
            if self.notification_manager:
                self.notification_manager.add_notification("Water Reminder", msg, type="reminder")
