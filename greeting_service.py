import datetime

class GreetingService:
    def __init__(self, calendar_manager, weather_manager=None, email_manager=None, brain=None):
        self.calendar = calendar_manager
        self.weather_manager = weather_manager
        self.email_manager = email_manager
        self.brain = brain

    def get_time_based_greeting(self):
        """Returns a time-based greeting, potentially enhanced with calendar events."""
        ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
        hour = datetime.datetime.now(ist).hour
        
        if 5 <= hour < 12:
            greeting = "Good morning, Shreyas"
        elif 12 <= hour < 17:
            greeting = "Good afternoon, Shreyas"
        elif 17 <= hour < 21:
            greeting = "Good evening, Shreyas"
        else:
            greeting = "Hello, Shreyas"
            
        # Optional: Add quick calendar context
        try:
            events = self.calendar.get_upcoming_events(max_results=1)
            if events and isinstance(events, list) and len(events) > 0:
                next_event = events[0]
                # Simple check if it's soon (logic can be improved)
                return f"{greeting}. Your next event is {next_event}."
        except Exception:
            pass
            
        return f"{greeting}. How can I help you?"

    def check_and_update_briefing_status(self):
        """
        Checks if the morning briefing should be shown.
        Returns True if:
        1. It is between 5 AM and 10 AM.
        2. Briefing has NOT been shown today.
        Updates the state file if returning True.
        """
        import json
        import os
        
        ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
        now = datetime.datetime.now(ist)
        hour = now.hour
        today_str = now.strftime("%Y-%m-%d")
        
        # 1. Check Time Window (5 AM - 10 AM)
        if not (5 <= hour < 10):
            return False
            
        # 2. Check State File
        state_file = "briefing_state.json"
        state = {}
        
        if os.path.exists(state_file):
            try:
                with open(state_file, "r") as f:
                    state = json.load(f)
            except Exception as e:
                print(f"Error reading briefing state: {e}")
                
        last_briefing_date = state.get("last_briefing_date")
        
        if last_briefing_date == today_str:
            return False # Already shown today
            
        # 3. Update State
        try:
            state["last_briefing_date"] = today_str
            with open(state_file, "w") as f:
                json.dump(state, f)
            return True
        except Exception as e:
            print(f"Error writing briefing state: {e}")
            return True # Default to showing it if we can't write state (fail open)

    def get_morning_briefing(self):
        """
        Generates a smart briefing ONLY if check_and_update_briefing_status() returns True.
        Otherwise returns None (signaling to use normal greeting).
        """
        # Check if we should show the briefing
        if not self.check_and_update_briefing_status():
            return None

        ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
        now = datetime.datetime.now(ist)
        
        # 1. Get Weather
        weather_info = "Weather data unavailable"
        if self.weather_manager:
            try:
                weather_info = self.weather_manager.get_weather("Pimpri, Maharashtra, India")
            except Exception as e:
                print(f"Briefing Error (Weather): {e}")

        # 2. Get Calendar (For TODAY)
        events_list = []
        try:
            events_list = self.calendar.get_events_for_date("today")
            if isinstance(events_list, str): # Handle "No events found" string
                events_list = []
        except Exception as e:
            print(f"Briefing Error (Calendar): {e}")

        # 3. Get Emails (Always relevant)
        email_count = 0
        if self.email_manager:
            try:
                messages = self.email_manager.list_messages(max_results=10, query="is:unread")
                if isinstance(messages, list):
                    email_count = len(messages)
            except Exception as e:
                print(f"Briefing Error (Email): {e}")

        # 4. Synthesize with Brain
        if self.brain:
            return self.brain.generate_briefing_summary(weather_info, events_list, email_count, mode="morning briefing")
        
        # Fallback
        return f"Good morning. Weather: {weather_info}. You have {len(events_list)} events today."
