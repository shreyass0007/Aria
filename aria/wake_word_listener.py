try:
    import pvporcupine
except ImportError:
    pvporcupine = None

try:
    import pyaudio
except ImportError:
    pyaudio = None

import struct
import os
import threading
import time
from dotenv import load_dotenv
from .logger import setup_logger

logger = setup_logger(__name__)

load_dotenv()

class WakeWordListener:
    def __init__(self, on_wake_word_detected, access_key=None):
        """
        on_wake_word_detected: Callback function to run when wake word is heard.
        """
        self.on_wake_word_detected = on_wake_word_detected
        self.access_key = access_key or os.getenv("PICOVOICE_ACCESS_KEY")
        
        if not self.access_key:
            logger.error("Error: PICOVOICE_ACCESS_KEY not found in environment variables.")
            self.porcupine = None
            return

        if pvporcupine is None:
            logger.error("pvporcupine module not found. Wake word listener disabled.")
            self.porcupine = None
            return

        try:
            # Use default keywords (Jarvis, Computer, etc.)
            # We can also use 'picovoice', 'bumblebee', etc.
            # For now, let's use 'jarvis' as it's a popular default.
            self.porcupine = pvporcupine.create(
                access_key=self.access_key,
                keywords=['jarvis', 'computer', 'alexa'] 
            )
            logger.info(f"Wake Word Listener initialized. Keywords: Jarvis, Computer")
        except Exception as e:
            logger.error(f"Failed to initialize Porcupine: {e}")
            self.porcupine = None

        if pyaudio is None:
            logger.error("pyaudio module not found. Wake word listener disabled.")
            self.pa = None
        else:
            self.pa = pyaudio.PyAudio()

        self.audio_stream = None
        self.is_listening = False
        self.thread = None

    def start(self):
        """Start listening for wake word in background."""
        if not self.porcupine:
            return
        
        if self.is_listening:
            return

        self.is_listening = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        logger.info("Wake Word Listener started...")

    def stop(self):
        """Stop listening."""
        self.is_listening = False
        if self.thread:
            self.thread.join(timeout=1.0)
        logger.info("Wake Word Listener stopped.")

    def _listen_loop(self):
        if not self.pa:
            return

        try:
            self.audio_stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )

            while self.is_listening:
                pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)

                keyword_index = self.porcupine.process(pcm)

                if keyword_index >= 0:
                    logger.info(f"Wake Word Detected! (Index: {keyword_index})")
                    if self.on_wake_word_detected:
                        self.on_wake_word_detected()
                        # Optional: Sleep briefly to avoid double trigger
                        time.sleep(0.5)

        except Exception as e:
            logger.error(f"Error in Wake Word loop: {e}")
        finally:
            if self.audio_stream:
                self.audio_stream.close()
                self.audio_stream = None

    def cleanup(self):
        self.stop()
        if self.porcupine:
            self.porcupine.delete()
        if self.pa:
            self.pa.terminate()
