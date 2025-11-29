
from calendar_manager import CalendarManager
import datetime
import traceback

def debug_calendar():
    print("Initializing CalendarManager...")
    try:
        cal = CalendarManager()
        print("Calling get_upcoming_events()...")
        result = cal.get_upcoming_events(max_results=3)
        print(f"Result: {result}")
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    debug_calendar()
