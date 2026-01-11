from fastapi import APIRouter, HTTPException, Depends
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.dependencies import get_aria_core
from aria.aria_core import AriaCore

router = APIRouter()

@router.get("/notifications")
def get_notifications(aria: AriaCore = Depends(get_aria_core)):
    """
    Returns a list of notifications (e.g., unread emails, calendar events).
    """
    try:
        notifications = []
        
        # 1. Check Emails
        if aria.email and aria.email.service:
            # We can't easily get a list of dicts from the current get_unread_emails which returns a string.
            # But for now, let's just return a generic notification if there are unread emails.
            # Ideally, we should refactor EmailManager to return structured data.
            # For this fix, I'll try to use the internal service if possible or just parse the string/check count.
            # Let's use a simplified check or just return empty for now if we can't get structured data easily,
            # BUT the UI expects a list.
            
            # Let's try to fetch raw messages similar to get_unread_emails but return list
            # Retry logic for fetching emails
            max_retries = 3
            import time
            for attempt in range(max_retries):
                try:
                    results = aria.email.service.users().messages().list(userId='me', labelIds=['UNREAD'], maxResults=5).execute()
                    messages = results.get('messages', [])
                    for msg in messages:
                        # We need to fetch details to get subject/sender, which is slow.
                        # For a quick dashboard, maybe just count?
                        # The UI likely expects {id, title, message, type}.
                        notifications.append({
                            "id": msg['id'],
                            "title": "New Email",
                            "message": "You have an unread email.",
                            "type": "email"
                        })
                    break # Success, exit retry loop
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(1) # Wait 1 second before retrying
                    else:
                        print(f"Error fetching email notifications after {max_retries} attempts: {e}")

        # 2. Check Calendar (Upcoming events)
        # aria.calendar.get_upcoming_events() returns a string.
        # We might need to add a method to CalendarManager to return raw events.
        
        # 3. Get System/Proactive Notifications
        if aria.notification_manager:
            system_notifications = aria.notification_manager.get_notifications()
            notifications.extend(system_notifications)

        return {"status": "success", "notifications": notifications}
    except Exception as e:
        print(f"Error getting notifications: {e}")
        return {"status": "error", "message": str(e), "notifications": []}

@router.get("/briefing")
def get_briefing(aria: AriaCore = Depends(get_aria_core)):
    """
    Returns the daily briefing content.
    """
    try:
        # We can reuse the greeting service logic but force a full briefing
        # or just ask the LLM for a summary.
        # Let's use the greeting service if it has a method for it.
        # aria.greeting_service.get_greeting() returns a string.
        
        briefing_text = aria.greeting_service.get_greeting()
        
        return {"status": "success", "briefing": briefing_text}
    except Exception as e:
        return {"status": "error", "message": str(e)}
