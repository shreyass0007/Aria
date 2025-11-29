
import asyncio
import datetime
from unittest.mock import MagicMock

# Mock the Aria class structure
class MockAria:
    def __init__(self):
        self.calendar = MagicMock()
        self.brain = MagicMock()
        self.speak = MagicMock()

aria = MockAria()

# Mock Brain to return a fake reminder
mock_llm = MagicMock()
mock_llm.invoke.return_value.content = "Hey Shreyas, your test event starts in 10 minutes!"
aria.brain.get_llm.return_value = mock_llm
aria.brain.is_available.return_value = True

# Mock Calendar to return an event starting in 10 minutes
now = datetime.datetime.utcnow()
start_time = now + datetime.timedelta(minutes=10)
mock_event = {
    'id': 'test_event_123',
    'summary': 'Test Meeting',
    'start': {'dateTime': start_time.isoformat() + 'Z'}
}
aria.calendar.get_upcoming_events_raw.return_value = [mock_event]

async def test_scheduler_logic():
    print("Testing Scheduler Logic...")
    
    # Replicating the logic from backend_fastapi.py
    
    events = aria.calendar.get_upcoming_events_raw(max_results=5)
    reminded_events = set()
    
    for event in events:
        event_id = event['id']
        summary = event['summary']
        start_str = event['start'].get('dateTime')
        
        # Logic from backend_fastapi.py
        if 'Z' in start_str:
            start_dt = datetime.datetime.fromisoformat(start_str.replace('Z', '+00:00')).replace(tzinfo=None)
        else:
            dt = datetime.datetime.fromisoformat(start_str)
            if dt.tzinfo:
                start_dt = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
            else:
                start_dt = dt
                
        time_diff = (start_dt - now).total_seconds() / 60
        
        print(f"Event: {summary}, Starts in: {time_diff:.2f} mins")
        
        if 0 < time_diff <= 30 and event_id not in reminded_events:
            print("✅ Condition Met: Event is within 30 mins!")
            
            # Simulate LLM call
            prompt = f"Event '{summary}' starts in {int(time_diff)} minutes."
            response = aria.brain.get_llm().invoke(prompt)
            reminder = response.content
            
            print(f"🗣️ Aria would say: '{reminder}'")
            aria.speak(reminder)
            reminded_events.add(event_id)
        else:
            print("❌ Condition Failed")

if __name__ == "__main__":
    asyncio.run(test_scheduler_logic())
