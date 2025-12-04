import os
import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base Paths
# This file is in aria/config.py, so parent is aria/, parent.parent is root
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

# Timezone Configuration
# Default to Indian Standard Time (IST) as per user preference
TIMEZONE_STR = os.getenv("ARIA_TIMEZONE", "Asia/Kolkata")
try:
    # Create a timezone object. 
    # Note: In Python 3.9+, zoneinfo is preferred, but for compatibility we can use simple offset or rely on libraries.
    # For now, we'll define a fixed offset for IST if not using a library like pytz/zoneinfo in this simple config.
    # However, calendar_manager uses: datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    # Let's standardize on that for now.
    IST_OFFSET = datetime.timedelta(hours=5, minutes=30)
    TIMEZONE = datetime.timezone(IST_OFFSET)
except Exception:
    TIMEZONE = datetime.timezone.utc

# Google API Configuration
GOOGLE_CREDENTIALS_FILE = ROOT_DIR / "credentials.json"
GOOGLE_TOKEN_FILE = ROOT_DIR / "token.pickle"
GOOGLE_SCOPES = ['https://www.googleapis.com/auth/calendar']

# Application Settings
USER_NAME = os.getenv("USER_NAME", "User")
WAKE_WORD = os.getenv("WAKE_WORD", "aria")

# Logging Configuration
LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE_PATH = LOG_DIR / "aria.log"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
