import os
from typing import Dict, Any, Optional
from .base_handler import BaseHandler
from ..logger import setup_logger

logger = setup_logger(__name__)

class EmailHandler(BaseHandler):
    def __init__(self, tts_manager, email_manager, brain):
        super().__init__(tts_manager)
        self.email_manager = email_manager
        self.brain = brain
        self.pending_email = None

    def should_handle(self, intent: str) -> bool:
        return intent in ["email_send", "email_check"]

    def has_pending_interaction(self) -> bool:
        return self.pending_email is not None

    def handle_interaction(self, text: str, extra_data: Dict = None) -> Optional[str]:
        """Handles the confirmation flow for sending emails."""
        if not self.pending_email:
            return None

        # Check if user is issuing a NEW command instead of confirming
        if any(x in text for x in ["send mail", "send email", "draft email", "compose email"]):
            self.tts_manager.speak("Discarding previous draft and starting a new one.")
            self.pending_email = None
            return None # Fall through to normal intent processing
        
        elif any(x in text for x in ["yes", "send", "confirm", "okay", "sure"]):
            self.tts_manager.speak("Sending email...")
            
            # Update body if provided in extra_data
            if extra_data and extra_data.get("updated_body"):
                self.pending_email["body"] = extra_data.get("updated_body")
                logger.debug(f"Using updated email body: {self.pending_email['body']}")
            
            to = self.pending_email["to"]
            subject = self.pending_email["subject"]
            body = self.pending_email["body"]
            result = self.email_manager.send_email(to, subject, body)
            self.tts_manager.speak(result)
            self.pending_email = None
            return result
        elif any(x in text for x in ["no", "cancel", "don't send", "stop"]):
            self.tts_manager.speak("Email cancelled.")
            self.pending_email = None
            return "Email cancelled."
        else:
            self.tts_manager.speak("Please say 'yes' to send or 'no' to cancel.")
            return "Please confirm if you want to send the email."

    def handle(self, text: str, intent: str, parameters: Dict[str, Any]) -> Optional[str]:
        if intent == "email_send":
            # Extract details using brain if not already present
            email_details = self.brain.parse_email_intent(text)
            to = email_details.get("to")
            subject = email_details.get("subject")
            body_context = email_details.get("body")
            
            if to and subject and body_context:
                self.tts_manager.speak("Drafting your email...")
                user_name = os.getenv("USER_NAME", "User")
                draft_body = self.brain.generate_email_draft(to, subject, body_context, sender_name=user_name)
                
                if not subject or subject.lower() == "no subject":
                    subject = "Message from Aria"
                
                self.pending_email = {
                    "to": to,
                    "subject": subject,
                    "body": draft_body
                }
                
                self.tts_manager.speak("I have created a draft for you.")
                self.tts_manager.speak("Do you want to send it?")
                
                # Return result with UI action data
                # The processor will need to handle the UI action part if we don't return it here
                # But BaseHandler.handle returns string or None.
                # We might need a way to return UI actions.
                # For now, we'll return the status string, and the processor can check pending_email
                return "Email draft created."
            else:
                self.tts_manager.speak("I need more details. Who is it for, and what should I say?")
                return "Please provide more details for the email."

        elif intent == "email_check":
            self.tts_manager.speak("Checking your inbox...")
            emails = self.email_manager.get_unread_emails()
            
            if "no unread emails" in emails.lower():
                self.tts_manager.speak("You have no unread emails.")
            elif "problem" in emails.lower() or "error" in emails.lower():
                self.tts_manager.speak(emails)
            else:
                self.tts_manager.speak(f"Here are your latest unread emails:\n\n{emails}")
                # We don't have access to _humanize_response here easily unless we pass it or duplicate it.
                # For now, let's just speak the emails.
                # Or we can pass a helper.
            return "Checked unread emails."
        
        return None
