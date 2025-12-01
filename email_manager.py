import os
import pickle
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token_gmail.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']

class EmailManager:
    def __init__(self):
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authenticates the user with Gmail API."""
        if os.path.exists('token_gmail.pickle'):
            with open('token_gmail.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing Gmail token: {e}")
                    self.creds = None
            
            if not self.creds:
                if os.path.exists('credentials.json'):
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            'credentials.json', SCOPES)
                        self.creds = flow.run_local_server(port=0)
                        # Save the credentials for the next run
                        with open('token_gmail.pickle', 'wb') as token:
                            pickle.dump(self.creds, token)
                    except Exception as e:
                        print(f"Error during Gmail authentication flow: {e}")
                        return
                else:
                    print("credentials.json not found. Email features will be disabled.")
                    return

        try:
            self.service = build('gmail', 'v1', credentials=self.creds)
        except Exception as e:
            print(f"Error building Gmail service: {e}")
            self.service = None

    def send_email(self, to, subject, body):
        """Sends an email using the Gmail API."""
        if not self.service:
            self.authenticate()
            
        if not self.service:
            return "Gmail service not available. Please check credentials."

        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            body = {'raw': raw_message}
            
            sent_message = self.service.users().messages().send(userId="me", body=body).execute()
            return f"✅ Email sent successfully to {to}."
        except HttpError as error:
            print(f"Gmail API Error: {error}")
            return "I encountered a problem with the Gmail service while sending the email."
        except Exception as e:
            print(f"Email Send Error: {e}")
            return "I couldn't send the email due to an unexpected error."

    def get_unread_emails(self, max_results=5):
        """Retrieves unread emails from the inbox."""
        if not self.service:
            self.authenticate()
            
        if not self.service:
            return "Gmail service not available."

        try:
            # List messages with label 'UNREAD'
            results = self.service.users().messages().list(userId='me', labelIds=['UNREAD'], maxResults=max_results).execute()
            messages = results.get('messages', [])

            if not messages:
                return "You have no unread emails."

            email_list = []
            for msg in messages:
                txt = self.service.users().messages().get(userId='me', id=msg['id']).execute()
                payload = txt['payload']
                headers = payload['headers']
                
                subject = "No Subject"
                sender = "Unknown Sender"
                
                for d in headers:
                    if d['name'] == 'Subject':
                        subject = d['value']
                    if d['name'] == 'From':
                        sender = d['value']
                
                snippet = txt.get('snippet', '')
                email_list.append(f"From: {sender}\nSubject: {subject}\nSnippet: {snippet}\n")

            return "\n---\n".join(email_list)
            
        except HttpError as error:
            print(f"Gmail API Error: {error}")
            return "I encountered a problem retrieving your emails."
    def search_emails(self, query, max_results=5):
        """Searches for emails matching the query."""
        if not self.service:
            self.authenticate()
            
        if not self.service:
            return "Gmail service not available."

        try:
            results = self.service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
            messages = results.get('messages', [])

            if not messages:
                return "No emails found matching your search."

            email_list = []
            for msg in messages:
                txt = self.service.users().messages().get(userId='me', id=msg['id']).execute()
                payload = txt['payload']
                headers = payload['headers']
                
                subject = "No Subject"
                sender = "Unknown Sender"
                
                for d in headers:
                    if d['name'] == 'Subject':
                        subject = d['value']
                    if d['name'] == 'From':
                        sender = d['value']
                
                snippet = txt.get('snippet', '')
                email_list.append(f"From: {sender}\nSubject: {subject}\nSnippet: {snippet}\n")

            return "\n---\n".join(email_list)
            
        except HttpError as error:
            print(f"Gmail API Error: {error}")
            return "I encountered a problem searching your emails."
        except Exception as e:
            print(f"Email Search Error: {e}")
            return "I couldn't search your emails due to an unexpected error."

if __name__ == "__main__":
    # Test the module
    email_manager = EmailManager()
    # email_manager.send_email("test@example.com", "Test Subject", "Test Body")
