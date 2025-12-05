import sys
import os
sys.path.append(os.getcwd())

try:
    from aria import config
    print("Successfully imported aria.config")
    
    print(f"BASE_DIR: {config.BASE_DIR}")
    print(f"ROOT_DIR: {config.ROOT_DIR}")
    print(f"TIMEZONE: {config.TIMEZONE}")
    print(f"GOOGLE_CREDENTIALS_FILE: {config.GOOGLE_CREDENTIALS_FILE}")
    print(f"USER_NAME: {config.USER_NAME}")
    print(f"WAKE_WORD: {config.WAKE_WORD}")
    print(f"LOG_DIR: {config.LOG_DIR}")
    print(f"LOG_FILE_PATH: {config.LOG_FILE_PATH}")
    print(f"LOG_LEVEL: {config.LOG_LEVEL}")
    
    # Check if settings object is available
    print(f"Settings Object: {config.settings}")
    
except Exception as e:
    print(f"Configuration Verification Failed: {e}")
    import traceback
    traceback.print_exc()
