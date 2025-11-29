import os
import datetime
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarManager:
    def __init__(self):
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        # Get absolute path to the directory containing this script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        token_path = os.path.join(base_dir, 'token.pickle')
        creds_path = os.path.join(base_dir, 'credentials.json')
        
        print(f"DEBUG: CalendarManager paths: Base={base_dir}, Token={token_path}, Creds={creds_path}")
        
        if os.path.exists(token_path):
            print("DEBUG: Found token.pickle, attempting to load...")
            try:
                with open(token_path, 'rb') as token:
                    self.creds = pickle.load(token)
                print("DEBUG: token.pickle loaded successfully.")
            except Exception as e:
                print(f"DEBUG: Error loading token.pickle: {e}. Deleting invalid token.")
                self.creds = None
                try:
                    os.remove(token_path)
                except:
                    pass
        else:
            print("DEBUG: token.pickle not found.")
        
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            print("DEBUG: Credentials invalid or missing. Starting refresh/login flow...")
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    print("DEBUG: Refreshing expired token...")
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    self.creds = None
            
            if not self.creds:
                if os.path.exists(creds_path):
                    try:
                        print("DEBUG: Starting local server for new login...")
                        flow = InstalledAppFlow.from_client_secrets_file(
                            creds_path, SCOPES)
                        self.creds = flow.run_local_server(port=0)
                        # Save the credentials for the next run
                        print("DEBUG: Saving new token.pickle...")
                        with open(token_path, 'wb') as token:
                            pickle.dump(self.creds, token)
                    except Exception as e:
                        print(f"Error during authentication flow: {e}")
                        return
                else:
                    print(f"credentials.json not found at {creds_path}. Calendar features will be disabled.")
                    return

        try:
            self.service = build('calendar', 'v3', credentials=self.creds)
        except Exception as e:
            print(f"Error building calendar service: {e}")
            self.service = None

    def create_event(self, summary, start_time, end_time=None, description="Created by Aria"):
        """
        Creates an event in the primary calendar.
        start_time: ISO format string or datetime object
        end_time: ISO format string or datetime object (optional, defaults to start_time + 1h)
        """
        if not self.service:
            self.authenticate()
            
        if not self.service:
            return "Calendar service not available. Please check credentials."

        try:
            # Ensure we have valid datetime strings
            if isinstance(start_time, datetime.datetime):
                start_time = start_time.isoformat()
            
            if not end_time:
                # Default to 1 hour later if not specified
                start_dt = datetime.datetime.fromisoformat(start_time)
                end_dt = start_dt + datetime.timedelta(hours=1)
                end_time = end_dt.isoformat()
            elif isinstance(end_time, datetime.datetime):
                end_time = end_time.isoformat()

            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'Asia/Kolkata', # Defaulting to IST as per user location hint
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'Asia/Kolkata',
                },
            }

            event = self.service.events().insert(calendarId='primary', body=event).execute()
            
            # Format time for friendly display using the ORIGINAL start_time (not from Google's response)
            try:
                # Use the original start_time parameter to avoid timezone conversion issues
                if isinstance(start_time, str):
                    dt = datetime.datetime.fromisoformat(start_time)
                else:
                    dt = start_time
                formatted_time = dt.strftime("%A, %B %d at %I:%M %p")
            except:
                formatted_time = "the requested time"

            return f"✅ I've scheduled '{summary}' for {formatted_time}."
        except Exception as e:
            print(f"Calendar Create Error: {e}")
            return "I couldn't create the calendar event due to an error."

    def get_upcoming_events(self, max_results=5, start_date=None, end_date=None):
        """
        Gets upcoming events.
        If start_date and end_date are provided (datetime objects), filters by that range.
        Otherwise, defaults to 'now' onwards.
        """
        if not self.service:
            self.authenticate()

        if not self.service:
            return "Calendar service not available."

        try:
            if start_date:
                if start_date.tzinfo:
                    time_min = start_date.isoformat()
                else:
                    time_min = start_date.isoformat() + 'Z'
            else:
                time_min = datetime.datetime.utcnow().isoformat() + 'Z'
            
            time_max = None
            if end_date:
                if end_date.tzinfo:
                    time_max = end_date.isoformat()
                else:
                    time_max = end_date.isoformat() + 'Z'

            events_result = self.service.events().list(
                calendarId='primary', 
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results, 
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])

            if not events:
                return "No upcoming events found for this period."
            
            result_text = "Here are the events:\n"
            result_text = "Here are the events:\n"
            ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
            
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                # Format start time to be more readable
                try:
                    # Parse ISO format (handling Z or offset)
                    if 'Z' in start:
                        dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                    else:
                        dt = datetime.datetime.fromisoformat(start)
                    
                    # Convert to IST
                    dt_ist = dt.astimezone(ist)
                    
                    friendly_time = dt_ist.strftime("%I:%M %p")
                    friendly_date = dt_ist.strftime("%a, %b %d")
                    result_text += f"- {event['summary']} on {friendly_date} at {friendly_time}\n"
                except Exception as e:
                    print(f"Date parsing error: {e}")
                    result_text += f"- {event['summary']} at {start}\n"
                    
            return result_text
        except Exception as e:
            print(f"Calendar Fetch Error: {e}")
            return "I couldn't check your calendar right now."

    def get_events_for_date(self, target_date_str):
        """
        Get events for a specific date ('today', 'tomorrow', or YYYY-MM-DD).
        Filters out past events if querying for 'today'.
        """
        ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
        now = datetime.datetime.now(ist)
        
        if target_date_str == 'today':
            # Start from NOW, not midnight, to show only upcoming events
            start_date = now
            # End at midnight tonight
            end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif target_date_str == 'tomorrow':
            start_date = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            # Try parsing YYYY-MM-DD
            try:
                start_date = datetime.datetime.strptime(target_date_str, "%Y-%m-%d").replace(tzinfo=ist)
                end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            except:
                return self.get_upcoming_events() # Fallback

        # Convert to UTC for API
        start_utc = start_date.astimezone(datetime.timezone.utc)
        end_utc = end_date.astimezone(datetime.timezone.utc)
        
        return self.get_upcoming_events(max_results=10, start_date=start_utc, end_date=end_utc)

    def get_upcoming_events_raw(self, max_results=5):
        """
        Gets upcoming events as a list of dictionaries (raw data).
        Used for background scheduling checks.
        """
        if not self.service:
            self.authenticate()

        if not self.service:
            return []

        try:
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            events_result = self.service.events().list(
                calendarId='primary', 
                timeMin=now,
                maxResults=max_results, 
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
        except Exception as e:
            print(f"Calendar Raw Fetch Error: {e}")
            return []
