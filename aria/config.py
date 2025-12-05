import os
import datetime
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # Base Paths
    BASE_DIR: Path = Path(__file__).resolve().parent
    ROOT_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent)

    # Timezone
    ARIA_TIMEZONE: str = "Asia/Kolkata"
    
    @property
    def TIMEZONE(self) -> datetime.timezone:
        # Simple fixed offset for IST (UTC+5:30) to avoid pytz dependency for now
        # In a real app, use zoneinfo
        if self.ARIA_TIMEZONE == "Asia/Kolkata":
            return datetime.timezone(datetime.timedelta(hours=5, minutes=30))
        return datetime.timezone.utc

    # Google API
    GOOGLE_CREDENTIALS_FILE: Path = Field(default_factory=lambda: Path("credentials.json"))
    GOOGLE_TOKEN_FILE: Path = Field(default_factory=lambda: Path("token.pickle"))
    GOOGLE_SCOPES: List[str] = ['https://www.googleapis.com/auth/calendar']

    # Application Settings
    USER_NAME: str = "User"
    WAKE_WORD: str = "aria"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_DIR_NAME: str = "logs"
    LOG_FILE_NAME: str = "aria.log"

    @property
    def LOG_DIR(self) -> Path:
        path = self.ROOT_DIR / self.LOG_DIR_NAME
        path.mkdir(exist_ok=True)
        return path

    @property
    def LOG_FILE_PATH(self) -> Path:
        return self.LOG_DIR / self.LOG_FILE_NAME

    # Environment loading
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate settings
settings = Settings()

# Export variables for backward compatibility
BASE_DIR = settings.BASE_DIR
ROOT_DIR = settings.ROOT_DIR
TIMEZONE = settings.TIMEZONE
GOOGLE_CREDENTIALS_FILE = settings.ROOT_DIR / settings.GOOGLE_CREDENTIALS_FILE
GOOGLE_TOKEN_FILE = settings.ROOT_DIR / settings.GOOGLE_TOKEN_FILE
GOOGLE_SCOPES = settings.GOOGLE_SCOPES
USER_NAME = settings.USER_NAME
WAKE_WORD = settings.WAKE_WORD
LOG_DIR = settings.LOG_DIR
LOG_FILE_PATH = settings.LOG_FILE_PATH
LOG_LEVEL = settings.LOG_LEVEL
TIMEZONE_STR = settings.ARIA_TIMEZONE

