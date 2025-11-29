import warnings
# Suppress pkg_resources deprecation warning from pygame and others
warnings.filterwarnings("ignore", message=".*pkg_resources is deprecated.*")

from brain import AriaBrain
from calendar_manager import CalendarManager
from notion_manager import NotionManager
from file_automation import FileAutomator
from system_control import SystemControl
from command_intent_classifier import CommandIntentClassifier
from file_manager import FileManager
from weather_manager import WeatherManager
from clipboard_screenshot import ClipboardScreenshot
from system_monitor import SystemMonitor
from system_monitor import SystemMonitor
from email_manager import EmailManager
from deep_work_manager import DeepWorkManager

# New Modules
from tts_manager import TTSManager
from app_launcher import AppLauncher
from speech_input import SpeechInput
from greeting_service import GreetingService
from command_processor import CommandProcessor

class AriaCore:
    def __init__(self, on_speak=None):
        """
        on_speak: Callback function(text) to update GUI or logs when Aria speaks.
        """
        # Initialize Core Components
        self.brain = AriaBrain()
        self.calendar = CalendarManager()
        self.notion = NotionManager()
        self.automator = FileAutomator()
        self.system_control = SystemControl()
        self.command_classifier = CommandIntentClassifier(self.brain)
        self.file_manager = FileManager()
        self.weather_manager = WeatherManager()
        self.clipboard_screenshot = ClipboardScreenshot()
        self.system_monitor = SystemMonitor()
        self.email_manager = EmailManager()
        
        # Alias for backward compatibility
        self.email = self.email_manager

        # Initialize New Modules
        self.tts_manager = TTSManager(on_speak=on_speak)
        self.app_launcher = AppLauncher(self.tts_manager)
        self.speech_input = SpeechInput(self.tts_manager)
        self.speech_input = SpeechInput(self.tts_manager)
        self.greeting_service = GreetingService(self.calendar)
        self.deep_work_manager = DeepWorkManager(self.calendar, self.tts_manager)
        self.deep_work_manager.start_monitoring()
        
        self.command_processor = CommandProcessor(
            tts_manager=self.tts_manager,
            app_launcher=self.app_launcher,
            brain=self.brain,
            calendar=self.calendar,
            notion=self.notion,
            automator=self.automator,
            system_control=self.system_control,
            command_classifier=self.command_classifier,
            file_manager=self.file_manager,
            weather_manager=self.weather_manager,
            clipboard_screenshot=self.clipboard_screenshot,
            system_monitor=self.system_monitor,
            email_manager=self.email_manager,
            greeting_service=self.greeting_service
        )

        self.check_microphones()

    # --- Properties for Backward Compatibility ---

    @property
    def on_speak(self):
        return self.tts_manager.on_speak

    @on_speak.setter
    def on_speak(self, callback):
        self.tts_manager.on_speak = callback

    @property
    def tts_enabled(self):
        return self.tts_manager.tts_enabled

    @property
    def wake_word(self):
        return self.command_processor.wake_word

    @wake_word.setter
    def wake_word(self, value):
        self.command_processor.wake_word = value

    @property
    def last_ui_action(self):
        return self.command_processor.last_ui_action

    @last_ui_action.setter
    def last_ui_action(self, value):
        self.command_processor.last_ui_action = value
        
    @property
    def pending_email(self):
        return self.command_processor.pending_email
        
    @pending_email.setter
    def pending_email(self, value):
        self.command_processor.pending_email = value

    # --- Delegated Methods ---

    def set_tts_enabled(self, enabled: bool):
        self.tts_manager.set_tts_enabled(enabled)

    def speak(self, text, print_text=True):
        self.tts_manager.speak(text, print_text)

    def listen(self):
        return self.speech_input.listen()

    def check_microphones(self):
        self.speech_input.check_microphones()

    def get_time_based_greeting(self):
        return self.greeting_service.get_time_based_greeting()

    def get_morning_briefing(self):
        return self.greeting_service.get_morning_briefing()

    def process_command(self, text: str, model_name: str = "openai", intent_data: dict = None):
        self.command_processor.process_command(text, model_name, intent_data)

    def safe_open_url(self, url: str, description: str = ""):
        return self.command_processor.safe_open_url(url, description)

    def index_apps(self):
        # Already handled by AppLauncher in background thread
        pass 

    def open_desktop_app(self, app_name: str):
        self.app_launcher.open_desktop_app(app_name)
