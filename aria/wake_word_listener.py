try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import pvporcupine
except ImportError:
    pvporcupine = None

try:
    import pyaudio
except ImportError:
    pyaudio = None
    
import logging
import os
import struct
import threading
import time
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class WakeWordListener:
    def __init__(self, on_wake_word_detected, on_command_detected=None, access_key=None):
        """
        on_wake_word_detected: Callback when wake word is heard.
        on_command_detected: Callback with transcribed text.
        """
        self.on_wake_word_detected = on_wake_word_detected
        self.on_command_detected = on_command_detected
        self.access_key = access_key or os.getenv("PICOVOICE_ACCESS_KEY")
        
        self.porcupine = None
        self.pa = None
        self.audio_stream = None
        self.is_listening = False
        self.thread = None
        
        if not self.access_key:
             logger.error("Error: PICOVOICE_ACCESS_KEY not found.")
        
        if sr is None:
            logger.error("speech_recognition module not found.")

    def start(self):
        """Start listening for wake word in background."""
        # Hardware might not be ready, but we start the thread which will init it
        if self.is_listening:
            return

        # Explicit check before starting thread to avoid useless threads
        if not self.access_key or pvporcupine is None or pyaudio is None:
            logger.warning("Cannot start Wake Word Listener: Missing dependencies or keys.")
            return

        self.is_listening = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        logger.info("Wake Word Listener background thread started (Hardware initializing...)")

    def stop(self):
        """Stop listening."""
        self.is_listening = False
        if self.thread:
            self.thread.join(timeout=1.0)
        logger.info("Wake Word Listener stopped.")

    def _init_hardware(self):
        """Initializes microphone and Porcupine engine. returns True if success."""
        try:
            if self.porcupine is None:
                self.porcupine = pvporcupine.create(
                    access_key=self.access_key,
                    keywords=['jarvis', 'computer', 'alexa'] 
                )
                logger.info(f"Wake Word Engine Initialized. Keywords: Jarvis, Computer")
            
            if self.pa is None:
                self.pa = pyaudio.PyAudio()
                
            return True
        except Exception as e:
            # If access key is invalid or network error
            logger.error(f"Failed to initialize Wake Word hardware: {e}")
            return False

    def _listen_loop(self):
        if not self._init_hardware():
            self.is_listening = False
            return

        try:
            self._start_audio_stream()
            logger.info("Microphone Active. Listening for Wake Word...")

            while self.is_listening:
                if self.audio_stream is None: 
                     # Re-open if closed (e.g. after command listen)
                     self._start_audio_stream()

                pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)

                keyword_index = self.porcupine.process(pcm)

                if keyword_index >= 0:
                    logger.info(f"Wake Word Detected! (Index: {keyword_index})")
                    
                    # 1. Notify Backend (Wake Word)
                    if self.on_wake_word_detected:
                        self.on_wake_word_detected()
                    
                    # 2. Capture Command
                    if self.on_command_detected and sr:
                        self._capture_command()
                    else:
                        time.sleep(0.5) # Debounce 

        except Exception as e:
            logger.error(f"Error in Wake Word loop: {e}")
        finally:
            self._close_audio_stream()

    def _start_audio_stream(self):
        if self.audio_stream is not None: return
        self.audio_stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

    def _close_audio_stream(self):
        if self.audio_stream:
            self.audio_stream.close()
            self.audio_stream = None

    def _capture_command(self):
        """Pauses wake word listener and uses SR to capture command."""
        logger.info("Listening for command...")
        
        # Close stream to free mic for SR
        self._close_audio_stream()
        
        r = sr.Recognizer()
        with sr.Microphone() as source:
            # Quick adjust for ambient noise
            r.adjust_for_ambient_noise(source, duration=0.5)
            try:
                # Listen with timeout
                audio = r.listen(source, timeout=5.0, phrase_time_limit=10.0)
                logger.info("Processing command audio...")
                
                # Transcribe
                text = r.recognize_google(audio)
                logger.info(f"Command heard: '{text}'")
                
                if self.on_command_detected:
                    self.on_command_detected(text)
                    
            except sr.WaitTimeoutError:
                logger.info("No command heard (timeout).")
            except sr.UnknownValueError:
                logger.info("Could not understand audio.")
                if self.on_command_detected:
                    self.on_command_detected(None) # Notify failure/silence
            except Exception as e:
                logger.error(f"Error capturing command: {e}")
        
        # Re-opening stream happens in main loop
        logger.info("Resuming Wake Word listener...")
