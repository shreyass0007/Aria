import datetime
import sys
import os

# Ensure we can import from aria package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aria.calendar_manager import CalendarManager

def create_test_event():
    cal = CalendarManager()
    
    # Target: Today at 1:20 PM IST
    ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    now = datetime.datetime.now(ist)
    
    # 1. Important Event
    start_time_1 = now + datetime.timedelta(hours=2)
    end_time_1 = start_time_1 + datetime.timedelta(hours=1)
    
    event_1_summary = 'Important Strategy Meeting'
    event_1_description = 'Discussing Q4 goals.'
    
    # Using CalendarManager's create_event method
    print(f"Creating event 1: {event_1_summary} at {start_time_1.strftime('%I:%M %p')}...")
    result_1 = cal.create_event(
        summary=event_1_summary,
        start_time=start_time_1,
        end_time=end_time_1,
        description=event_1_description
    )
    print(result_1)
    
    # 2. Routine Event (Should be ignored/summarized briefly)
    start_time_2 = now + datetime.timedelta(hours=4)
    end_time_2 = start_time_2 + datetime.timedelta(hours=1)
    
    event_2_summary = 'Lunch'
    event_2_description = 'Eating food.'

    # Using CalendarManager's create_event method
    print(f"Creating event 2: {event_2_summary} at {start_time_2.strftime('%I:%M %p')}...")
    result_2 = cal.create_event(
        summary=event_2_summary,
        start_time=start_time_2,
        end_time=end_time_2,
        description=event_2_description
    )
    print(result_2)

if __name__ == "__main__":
    create_test_event()
