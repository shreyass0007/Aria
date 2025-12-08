import warnings
import threading
# Suppress pkg_resources deprecation warning from pygame and others
warnings.filterwarnings("ignore", message=".*pkg_resources is deprecated.*")

from .brain import AriaBrain
from .calendar_manager import CalendarManager
from .notion_manager import NotionManager
from .file_automation import FileAutomator
from .system_control import SystemControl
from .command_intent_classifier import CommandIntentClassifier
from .file_manager import FileManager
from .weather_manager import WeatherManager
from .clipboard_screenshot import ClipboardScreenshot
from .system_monitor import SystemMonitor
from .email_manager import EmailManager
from .proactive_manager import ProactiveManager
from .music_library import MusicManager
from .wake_word_listener import WakeWordListener
from .water_manager import WaterManager

# New Modules
from .tts_manager import TTSManager
from .app_launcher import AppLauncher
from .speech_input import SpeechInput
from .greeting_service import GreetingService
from .command_processor import CommandProcessor
from .logger import setup_logger

logger = setup_logger(__name__)

class AriaCore:
    def __init__(self, on_speak=None, notification_manager=None):
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
        self.music_manager = MusicManager()
        
        # Alias for backward compatibility
        self.email = self.email_manager

        # Initialize New Modules
        self.tts_manager = TTSManager(on_speak=on_speak)
        self.app_launcher = AppLauncher(self.tts_manager)
        self.speech_input = SpeechInput(self.tts_manager)
        self.water_manager = WaterManager(
            tts_manager=self.tts_manager, 
            notification_manager=notification_manager,
            weather_manager=self.weather_manager,
            system_control=self.system_control
        )
        
        self.greeting_service = GreetingService(
            calendar_manager=self.calendar,
            weather_manager=self.weather_manager,
            email_manager=self.email_manager,
            brain=self.brain
        )
        self.proactive_manager = ProactiveManager(
            calendar_manager=self.calendar, 
            system_control=self.system_control, 
            tts_manager=self.tts_manager, 
            app_launcher=self.app_launcher,
            brain=self.brain,
            weather_manager=self.weather_manager,
            notification_manager=notification_manager
        )
        self.notification_manager = notification_manager
        self.proactive_manager.start_monitoring()
        
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
            greeting_service=self.greeting_service,
            music_manager=self.music_manager,
            water_manager=self.water_manager,
            vision_pipeline_factory=self.get_vision_pipeline
        )

        # Initialize Wake Word Listener
        self.wake_word_listener = WakeWordListener(on_wake_word_detected=self._on_wake_word)
        self.wake_word_listener.start()

        self.check_microphones()
        
        # Vision Pipeline (Lazy Loaded)
        self.vision_pipeline = None

    def get_vision_pipeline(self):
        """Lazy load the vision pipeline."""
        if self.vision_pipeline is None:
            logger.info("Initializing Vision Pipeline...")
            from aria.vision.pipeline import VisionPipeline
            self.vision_pipeline = VisionPipeline()
        return self.vision_pipeline

    def analyze_screen(self, save_debug: bool = False):
        """Analyze the current screen."""
        pipeline = self.get_vision_pipeline()
        return pipeline.analyze_screen(save_debug=save_debug)

    def _on_wake_word(self):
        """Callback when wake word is detected."""
        logger.info("🔴 Wake Word Detected! Interrupting and Listening...")
        
        # 1. Interrupt TTS
        self.tts_manager.stop()
        
        # 2. Play listening sound (optional, or just speak)
        # self.tts_manager.speak("Yes?", print_text=False) 
        
        # 3. Trigger Listening (This needs to be handled carefully to not block main thread if called from callback)
        # Since this is a callback from a thread, we can't block it too long.
        # But aria.listen() is blocking.
        # Ideally, we should signal the main loop or start a new thread for the interaction.
        # For now, let's try running it in a separate thread to avoid blocking the detector loop.
        # For now, let's try running it in a separate thread to avoid blocking the detector loop.
        threading.Thread(target=self._handle_voice_interaction, daemon=True).start()

    def _handle_voice_interaction(self):
        """Handles the voice interaction after wake word."""
        # Visual cue could be added here if we had UI access
        logger.info("🎤 Listening for command...")
        
        # We need to ensure we don't conflict with other listen calls
        # But for now, let's just call listen.
        user_text = self.listen()
        
        if user_text:
            logger.info(f"User said: {user_text}")
            # Process the command
            # We need to route this back to the main processor.
            # Since we are in the backend, we can call process_command directly.
            # BUT, we might want to use the smart router logic in backend_fastapi.
            # That logic is not easily accessible here.
            # So we will use the internal command_processor which is the core logic.
            
            # Classify first
            intent_data = self.command_classifier.classify_intent(user_text)
            
            # Process
            self.process_command(user_text, intent_data=intent_data)

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

    def process_command(self, text: str, model_name: str = "openai", intent_data: dict = None, extra_data: dict = None):
        self.command_processor.process_command(text, model_name, intent_data, extra_data)

    def safe_open_url(self, url: str, description: str = ""):
        return self.command_processor.safe_open_url(url, description)

    def index_apps(self):
        # Already handled by AppLauncher in background thread
        pass 

    def open_desktop_app(self, app_name: str):
        self.app_launcher.open_desktop_app(app_name)
