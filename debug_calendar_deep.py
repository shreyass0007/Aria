import datetime
import os.path
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("No valid token found. Please authenticate via the main app first.")
            return None
    return build('calendar', 'v3', credentials=creds)

def main():
    service = get_service()
    if not service:
        return

    print("--- Listing All Calendars ---")
    page_token = None
    all_calendars = []
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            print(f"ID: {calendar_list_entry['id']}, Summary: {calendar_list_entry['summary']}")
            all_calendars.append(calendar_list_entry)
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    print("\n--- Searching for Missing Events (DBMS, IOT) ---")
    
    ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    now = datetime.datetime.now(ist)
    
    # Check for today
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    start_utc = start_of_day.astimezone(datetime.timezone.utc).isoformat()
    end_utc = end_of_day.astimezone(datetime.timezone.utc).isoformat()
    
    found_any = False
    
    for cal in all_calendars:
        cal_id = cal['id']
        cal_name = cal['summary']
        print(f"\nChecking Calendar: {cal_name} ({cal_id})")
        
        try:
            # Special check for DBMS calendar to see if *any* events exist
            if "DBMS" in cal_name:
                print(f"  (Deep check for {cal_name}: Checking next 30 days...)")
                end_future = (now + datetime.timedelta(days=30)).astimezone(datetime.timezone.utc).isoformat()
                events_result = service.events().list(
                    calendarId=cal_id, 
                    timeMin=start_utc,
                    timeMax=end_future,
                    singleEvents=True,
                    orderBy='startTime',
                    maxResults=10
                ).execute()
            else:
                events_result = service.events().list(
                    calendarId=cal_id, 
                    timeMin=start_utc,
                    timeMax=end_utc,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
            events = events_result.get('items', [])

            if not events:
                print("  No events found for today.")
            else:
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    summary = event.get('summary', 'No Title')
                    print(f"  - {summary} at {start}")
                    
                    if "DBMS" in summary.upper() or "IOT" in summary.upper():
                        print(f"    !!! FOUND MISSING EVENT: {summary} !!!")
                        found_any = True
                        
        except Exception as e:
            print(f"  Error accessing calendar: {e}")

    if not found_any:
        print("\n--- CONCLUSION ---")
        print("Could not find 'DBMS' or 'IOT' events on ANY accessible calendar.")
        print("Possible reasons:")
        print("1. They are on a different Google Account.")
        print("2. They are 'Tasks' or 'Reminders', not 'Events'.")
        print("3. They were deleted.")
    else:
        print("\n--- CONCLUSION ---")
        print("Found the missing events! See above for which calendar they belong to.")

if __name__ == '__main__':
    main()
