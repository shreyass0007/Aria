from typing import Optional
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aria.aria_core import AriaCore
from aria.conversation_manager import ConversationManager
from aria.memory_manager import MemoryManager
from aria.system_monitor import SystemMonitor
from aria.music_library import MusicManager
from backend.notification_manager import NotificationManager
from backend.websocket_manager import ConnectionManager


# Global instances
aria_core: Optional[AriaCore] = None
conversation_mgr: Optional[ConversationManager] = None
memory_mgr: Optional[MemoryManager] = None
system_monitor: Optional[SystemMonitor] = None
music_manager: Optional[MusicManager] = None
music_manager: Optional[MusicManager] = None
notification_mgr: Optional[NotificationManager] = None
connection_mgr: Optional[ConnectionManager] = None


def init_dependencies():
    global aria_core, conversation_mgr, memory_mgr, system_monitor, music_manager, notification_mgr, connection_mgr

    
    print("Initializing Global Dependencies...")
    
    # Initialize dependencies in correct order

    
    # Update notification manager with conversation manager if not already set (it is set above)
    # But wait, conversation_mgr is init AFTER notification_mgr above?
    # No, conversation_mgr is init at line 33 in original code.
    # Let's reorder everything properly.
    
    conversation_mgr = ConversationManager()
    conversation_mgr = ConversationManager()
    notification_mgr = NotificationManager(conversation_manager=conversation_mgr)
    connection_mgr = ConnectionManager()

    
    aria_core = AriaCore(
        on_speak=lambda text: print(f"Aria Speaking: {text}"),
        notification_manager=notification_mgr,
        connection_manager=connection_mgr
    )
    
    memory_mgr = MemoryManager()
    system_monitor = SystemMonitor()
    music_manager = aria_core.music_manager

    print("Global Dependencies Initialized.")

def get_notification_manager():
    return notification_mgr

def get_aria_core():
    return aria_core

def get_conversation_mgr():
    return conversation_mgr

def get_memory_mgr():
    return memory_mgr

def get_system_monitor():
    return system_monitor

def get_music_manager():
    return music_manager

def get_connection_manager():
    return connection_mgr

