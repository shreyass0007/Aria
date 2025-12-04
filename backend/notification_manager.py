import datetime

class NotificationManager:
    def __init__(self, conversation_manager=None):
        self.conversation_manager = conversation_manager
        self.notifications = []

    def add_notification(self, title, message, type="info"):
        """
        Adds a notification and injects it into the conversation stream.
        """
        notification = {
            "id": len(self.notifications) + 1,
            "title": title,
            "message": message,
            "type": type,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.notifications.append(notification)
        print(f"Notification Added: {title} - {message}")

        # Inject into conversation if manager is available
        if self.conversation_manager:
            # We format it as a system message or a special bot message
            # For now, let's make it look like a bot message but with a distinct prefix
            formatted_msg = f"🔔 **{title}**\n{message}"
            
            # Add to history directly
            # FIX: ConversationManager.add_message requires conversation_id
            current_id = self.conversation_manager.get_current_conversation_id()
            if current_id:
                self.conversation_manager.add_message(current_id, "assistant", formatted_msg)
                print("Notification injected into conversation.")
            else:
                print("Notification NOT injected: No active conversation.")

    def get_notifications(self):
        return self.notifications

    def clear_notifications(self):
        self.notifications = []
