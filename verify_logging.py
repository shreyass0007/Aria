import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from aria.music_library import MusicManager
    from aria.email_manager import EmailManager
    from aria import config
    print("Successfully imported MusicManager and EmailManager.")
except Exception as e:
    print(f"Failed to import managers: {e}")
    sys.exit(1)

# Check log file configuration
print(f"Log file path from config: {config.LOG_FILE_PATH}")

if os.path.exists(config.LOG_FILE_PATH):
    print("Log file exists.")
    try:
        size = os.path.getsize(config.LOG_FILE_PATH)
        print(f"Log file size: {size} bytes")
    except Exception as e:
        print(f"Could not get log file size: {e}")
else:
    print("Log file does not exist yet.")

print("Verification complete.")
