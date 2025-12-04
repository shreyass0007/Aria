import os
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
import uuid

load_dotenv()

class ConversationManager:
    def __init__(self):
        """Initialize MongoDB connection for conversation storage."""
        self.mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        self.db_name = "aria_conversations"
        self.client = None
        self.db = None
        self.current_conversation_id = None
        
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ismaster')
            self.db = self.client[self.db_name]
            print(f"[OK] MongoDB connected: {self.db_name}")
        except ConnectionFailure as e:
            print(f"[WARNING] MongoDB connection failed: {e}")
            print("Conversation history will not be saved.")
        except Exception as e:
            print(f"[ERROR] MongoDB initialization error: {e}")
    
    def is_connected(self):
        """Check if MongoDB is connected."""
        return self.client is not None and self.db is not None
    
    def create_conversation(self):
        """Create a new conversation session and return its ID."""
        if not self.is_connected():
            return None
        
        try:
            conversation_id = str(uuid.uuid4())
            conversation = {
                "_id": conversation_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "messages": [],
                "title": "New Conversation"  # Will be updated based on first message
            }
            self.db.conversations.insert_one(conversation)
            self.current_conversation_id = conversation_id
            print(f"[OK] Created conversation: {conversation_id}")
            return conversation_id
        except Exception as e:
            print(f"[ERROR] Error creating conversation: {e}")
            return None
    
    def add_message(self, conversation_id, role, content):
        """Add a message to a conversation. Role is 'user' or 'assistant'."""
        if not self.is_connected():
            return False
        
        try:
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow()
            }
            
            result = self.db.conversations.update_one(
                {"_id": conversation_id},
                {
                    "$push": {"messages": message},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            # Update title based on first user message
            conversation = self.db.conversations.find_one({"_id": conversation_id})
            if conversation and len(conversation.get("messages", [])) == 1 and role == "user":
                # Use first 50 chars of first message as title
                title = content[:50] + "..." if len(content) > 50 else content
                self.db.conversations.update_one(
                    {"_id": conversation_id},
                    {"$set": {"title": title}}
                )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"[ERROR] Error adding message: {e}")
            return False
    
    def get_conversation(self, conversation_id):
        """Retrieve a specific conversation with all messages."""
        if not self.is_connected():
            return None
        
        try:
            conversation = self.db.conversations.find_one({"_id": conversation_id})
            if conversation:
                # Convert datetime objects to ISO strings for JSON serialization
                conversation["created_at"] = conversation["created_at"].isoformat()
                conversation["updated_at"] = conversation["updated_at"].isoformat()
                for msg in conversation.get("messages", []):
                    msg["timestamp"] = msg["timestamp"].isoformat()
            return conversation
        except Exception as e:
            print(f"[ERROR] Error retrieving conversation: {e}")
            return None
    
    def list_conversations(self, limit=20):
        """Get recent conversations with metadata (excluding messages for performance)."""
        if not self.is_connected():
            return []
        
        try:
            conversations = list(
                self.db.conversations.find(
                    {},
                    {"_id": 1, "title": 1, "created_at": 1, "updated_at": 1, "messages": {"$slice": 1}}
                )
                .sort("updated_at", -1)
                .limit(limit)
            )
            
            # Format for JSON
            for conv in conversations:
                conv["created_at"] = conv["created_at"].isoformat()
                conv["updated_at"] = conv["updated_at"].isoformat()
                # Count messages
                full_conv = self.db.conversations.find_one({"_id": conv["_id"]}, {"messages": 1})
                conv["message_count"] = len(full_conv.get("messages", []))
            
            return conversations
        except Exception as e:
            print(f"[ERROR] Error listing conversations: {e}")
            return []
    
    def delete_conversation(self, conversation_id):
        """Delete a conversation."""
        if not self.is_connected():
            return False
        
        try:
            result = self.db.conversations.delete_one({"_id": conversation_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"[ERROR] Error deleting conversation: {e}")
            return False
    
    def rename_conversation(self, conversation_id, new_title):
        """Rename a conversation."""
        if not self.is_connected():
            return False
        
        try:
            result = self.db.conversations.update_one(
                {"_id": conversation_id},
                {"$set": {"title": new_title}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"[ERROR] Error renaming conversation: {e}")
            return False
    
    def get_current_conversation_id(self):
        """Get the current active conversation ID."""
        return self.current_conversation_id
    
    def set_current_conversation_id(self, conversation_id):
        """Set the current active conversation ID."""
        self.current_conversation_id = conversation_id
