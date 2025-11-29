import datetime

class GreetingService:
    def __init__(self, calendar_manager):
        self.calendar = calendar_manager

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

    def get_morning_briefing(self):
        """
        Generates a briefing summarizing today's important events.
        """
        ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
        hour = datetime.datetime.now(ist).hour
        
        if 5 <= hour < 12:
            greeting = "Good morning, Shreyas"
        elif 12 <= hour < 17:
            greeting = "Good afternoon, Shreyas"
        else:
            greeting = "Good evening, Shreyas"

        today_events = self.calendar.get_events_for_date("today")
        
        if "No events found" in today_events:
            return f"{greeting}. You have no events scheduled for today. Enjoy your free time!"
        
        # If it's a list (raw data), summarize it
        if isinstance(today_events, list):
            # Use LLM to summarize if available, but here we do simple string manip
            # Actually, AriaCore used self.brain for this in _humanize_response
            # But here we just return a string.
            # Let's keep it simple for now.
            try:
                return f"{greeting}. You have {len(today_events)} events today. The first one is {today_events[0]}."
            except Exception as e:
                print(f"Error generating briefing: {e}")
                return f"{greeting}. You have {len(today_events)} events today."
        
        return f"{greeting}. Here is your schedule: {today_events}"
