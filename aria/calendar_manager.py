import os
import datetime
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from . import config

class CalendarManager:
    def __init__(self):
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Shows basic usage of the Google Calendar API."""
        token_path = config.GOOGLE_TOKEN_FILE
        creds_path = config.GOOGLE_CREDENTIALS_FILE
        
        if os.path.exists(token_path):
            try:
                with open(token_path, 'rb') as token:
                    self.creds = pickle.load(token)
            except Exception as e:
                print(f"DEBUG: Error loading token.pickle: {e}. Deleting invalid token.")
                self.creds = None
                try:
                    os.remove(token_path)
                except:
                    pass
        
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    self.creds = None
            
            if not self.creds:
                if os.path.exists(creds_path):
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            str(creds_path), config.GOOGLE_SCOPES)
                        self.creds = flow.run_local_server(port=0)
                        # Save the credentials for the next run
                        with open(token_path, 'wb') as token:
                            pickle.dump(self.creds, token)
                    except Exception as e:
                        print(f"Error during authentication flow: {e}")
                        return
                else:
                    print(f"credentials.json not found at {creds_path}. Calendar features will be disabled.")
                    return

        if not self.creds:
            print("❌ DEBUG: No credentials found. Skipping service build.")
            return

        try:
            import httplib2
            import certifi
            from google_auth_httplib2 import AuthorizedHttp
            
            http = httplib2.Http(ca_certs=certifi.where())
            authorized_http = AuthorizedHttp(self.creds, http=http)
            self.service = build('calendar', 'v3', http=authorized_http)
            print("✅ Calendar service built successfully with custom SSL context.")
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
                    'timeZone': config.TIMEZONE_STR,
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': config.TIMEZONE_STR,
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

    def get_upcoming_events(self, max_results=9, start_date=None, end_date=None):
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
            
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                # Format start time to be more readable
                try:
                    # Parse ISO format (handling Z or offset)
                    if 'Z' in start:
                        dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                    else:
                        dt = datetime.datetime.fromisoformat(start)
                    
                    # Convert to configured timezone
                    dt_local = dt.astimezone(config.TIMEZONE)
                    
                    friendly_time = dt_local.strftime("%I:%M %p")
                    friendly_date = dt_local.strftime("%a, %b %d")
                    result_text += f"- {event['summary']} on {friendly_date} at {friendly_time}\n"
                except Exception as e:
                    print(f"Date parsing error: {e}")
                    result_text += f"- {event['summary']} at {start}\n"
                    
            return result_text
        except Exception as e:
            print(f"Calendar Fetch Error: {e}")
            return "I couldn't check your calendar right now."

    def get_events_for_date(self, target_date_str, time_scope="all_day"):
        """
        Get events for a specific date ('today', 'tomorrow', or YYYY-MM-DD).
        Filters out past events if querying for 'today'.
        Supports time_scope: 'morning', 'afternoon', 'evening', 'all_day'.
        """
        now = datetime.datetime.now(config.TIMEZONE)
        
        if target_date_str == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif target_date_str == 'tomorrow':
            start_date = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            try:
                start_date = datetime.datetime.strptime(target_date_str, "%Y-%m-%d").replace(tzinfo=config.TIMEZONE)
                end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            except:
                return self.get_upcoming_events() # Fallback

        # Apply Time Scope
        if time_scope == "morning":
            # 5 AM to 12 PM
            start_date = start_date.replace(hour=5, minute=0)
            end_date = start_date.replace(hour=11, minute=59)
        elif time_scope == "afternoon":
            # 12 PM to 5 PM
            start_date = start_date.replace(hour=12, minute=0)
            end_date = start_date.replace(hour=16, minute=59)
        elif time_scope == "evening":
            # 5 PM to 9 PM
            start_date = start_date.replace(hour=17, minute=0)
            end_date = start_date.replace(hour=21, minute=59)
        
        # Convert to UTC for API
        start_utc = start_date.astimezone(datetime.timezone.utc)
        end_utc = end_date.astimezone(datetime.timezone.utc)
        
        return self.get_upcoming_events(max_results=9, start_date=start_utc, end_date=end_utc)

    def get_free_slots(self, target_date_str, time_scope="all_day"):
        """
        Calculates free time slots for a specific date and time scope.
        """
        if not self.service:
            self.authenticate()
            
        now = datetime.datetime.now(config.TIMEZONE)
        
        # Determine base date range
        if target_date_str == 'today':
            base_date = now
        elif target_date_str == 'tomorrow':
            base_date = now + datetime.timedelta(days=1)
        else:
            try:
                base_date = datetime.datetime.strptime(target_date_str, "%Y-%m-%d").replace(tzinfo=config.TIMEZONE)
            except:
                base_date = now

        # Define working hours / scope boundaries
        day_start_hour = 9 # 9 AM
        day_end_hour = 21 # 9 PM
        
        start_dt = base_date.replace(hour=day_start_hour, minute=0, second=0, microsecond=0)
        end_dt = base_date.replace(hour=day_end_hour, minute=0, second=0, microsecond=0)

        if time_scope == "morning":
            start_dt = base_date.replace(hour=6, minute=0)
            end_dt = base_date.replace(hour=12, minute=0)
        elif time_scope == "afternoon":
            start_dt = base_date.replace(hour=12, minute=0)
            end_dt = base_date.replace(hour=17, minute=0)
        elif time_scope == "evening":
            start_dt = base_date.replace(hour=17, minute=0)
            end_dt = base_date.replace(hour=21, minute=0)

        # Ensure we don't look in the past if it's today
        if target_date_str == 'today' and start_dt < now:
            start_dt = now
            if start_dt >= end_dt:
                return "That time has already passed."

        # Fetch events for this range
        start_utc = start_dt.astimezone(datetime.timezone.utc)
        end_utc = end_dt.astimezone(datetime.timezone.utc)
        
        try:
            events_result = self.service.events().list(
                calendarId='primary', 
                timeMin=start_utc.isoformat(),
                timeMax=end_utc.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
        except Exception as e:
            return f"Error checking calendar: {e}"

        # Calculate gaps
        free_slots = []
        current_pointer = start_dt
        
        for event in events:
            # Parse event start/end
            start_str = event['start'].get('dateTime')
            end_str = event['end'].get('dateTime')
            if not start_str or not end_str: continue # Skip all-day events for gap calc (simplified)
            
            if 'Z' in start_str:
                ev_start = datetime.datetime.fromisoformat(start_str.replace('Z', '+00:00')).astimezone(config.TIMEZONE)
                ev_end = datetime.datetime.fromisoformat(end_str.replace('Z', '+00:00')).astimezone(config.TIMEZONE)
            else:
                ev_start = datetime.datetime.fromisoformat(start_str).astimezone(config.TIMEZONE)
                ev_end = datetime.datetime.fromisoformat(end_str).astimezone(config.TIMEZONE)

            # Check for gap
            if ev_start > current_pointer:
                gap_duration = (ev_start - current_pointer).total_seconds() / 60
                if gap_duration >= 15: # Minimum 15 min slot
                    free_slots.append((current_pointer, ev_start))
            
            # Move pointer
            if ev_end > current_pointer:
                current_pointer = ev_end

        # Check final gap
        if current_pointer < end_dt:
            gap_duration = (end_dt - current_pointer).total_seconds() / 60
            if gap_duration >= 15:
                free_slots.append((current_pointer, end_dt))

        if not free_slots:
            return f"You are fully booked during the {time_scope}."
        
        # Format output
        response = f"Here are your free slots for {time_scope}:\n"
        for start, end in free_slots:
            response += f"- {start.strftime('%I:%M %p')} to {end.strftime('%I:%M %p')}\n"
            
        return response

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

    def get_current_event(self):
        """
        Gets the event happening right now.
        """
        if not self.service:
            self.authenticate()

        if not self.service:
            return None

        try:
            now = datetime.datetime.now(config.TIMEZONE)
            
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            start_utc = start_of_day.astimezone(datetime.timezone.utc)
            end_utc = end_of_day.astimezone(datetime.timezone.utc)
            
            events_result = self.service.events().list(
                calendarId='primary', 
                timeMin=start_utc.isoformat(),
                timeMax=end_utc.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            for event in events:
                start_str = event['start'].get('dateTime')
                end_str = event['end'].get('dateTime')
                
                if not start_str or not end_str:
                    continue # All day events or missing time
                    
                # Parse
                if 'Z' in start_str:
                    start_dt = datetime.datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                    end_dt = datetime.datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                else:
                    start_dt = datetime.datetime.fromisoformat(start_str)
                    end_dt = datetime.datetime.fromisoformat(end_str)
                
                # Convert now to same tz if needed, but simple comparison works if both aware
                if start_dt <= now <= end_dt:
                    return f"Right now, you have: {event['summary']} (until {end_dt.astimezone(config.TIMEZONE).strftime('%I:%M %p')})"
            
            # If no current event, find next one
            for event in events:
                start_str = event['start'].get('dateTime')
                if not start_str: continue
                
                if 'Z' in start_str:
                    start_dt = datetime.datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                else:
                    start_dt = datetime.datetime.fromisoformat(start_str)
                    
                if start_dt > now:
                     return f"You are free right now. Next up is {event['summary']} at {start_dt.astimezone(config.TIMEZONE).strftime('%I:%M %p')}."

            return "You have no more events scheduled for today."
            
        except Exception as e:
            print(f"Calendar Current Event Error: {e}")
            return "I couldn't check your current status."
