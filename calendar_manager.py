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
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    self.creds = None
            
            if not self.creds:
                if os.path.exists('credentials.json'):
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            'credentials.json', SCOPES)
                        self.creds = flow.run_local_server(port=0)
                        # Save the credentials for the next run
                        with open('token.pickle', 'wb') as token:
                            pickle.dump(self.creds, token)
                    except Exception as e:
                        print(f"Error during authentication flow: {e}")
                        return
                else:
                    print("credentials.json not found. Calendar features will be disabled.")
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

    def get_upcoming_events(self, max_results=5):
        """Gets the next few upcoming events."""
        if not self.service:
            self.authenticate()

        if not self.service:
            return "Calendar service not available."

        try:
            now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
            events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                                maxResults=max_results, singleEvents=True,
                                                orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                return "No upcoming events found."
            
            result_text = "Here are your upcoming events:\n"
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                result_text += f"- {event['summary']} at {start}\n"
            return result_text
        except Exception as e:
            print(f"Calendar Fetch Error: {e}")
            return "I couldn't check your calendar right now."
