from calendar_manager import CalendarManager
import datetime

def list_calendars_and_events():
    cm = CalendarManager()
    if not cm.service:
        print("Failed to authenticate.")
        return

    print("Listing all calendars...")
    calendars = []
    page_token = None
    while True:
        calendar_list = cm.service.calendarList().list(pageToken=page_token).execute()
        for entry in calendar_list['items']:
            calendars.append((entry['summary'], entry['id']))
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
            
    print(f"Found {len(calendars)} calendars:")
    for name, cal_id in calendars:
        print(f" - {name} (ID: {cal_id})")
        
    print("\nChecking events for today (starting midnight)...")
    ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    now = datetime.datetime.now(ist)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    time_min = start_of_day.astimezone(datetime.timezone.utc).isoformat()
    
    print(f"Querying from: {time_min}")

    for name, cal_id in calendars:
        print(f"\nCalendar: {name} (ID: {cal_id})")
        try:
            # For debugging, just get upcoming events without timeMin for DBMS calendars
            if "DBMS" in name or "IOT" in name:
                print("  (Querying without timeMin for debug...)")
                events_result = cm.service.events().list(
                    calendarId=cal_id,
                    maxResults=10,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
            else:
                events_result = cm.service.events().list(
                    calendarId=cal_id,
                    timeMin=time_min,
                    maxResults=10,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                
            events = events_result.get('items', [])
            if not events:
                print("  No events found.")
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', '(No title)')
                print(f"  - {summary} at {start}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    list_calendars_and_events()
