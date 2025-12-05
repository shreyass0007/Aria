import warnings
# Suppress pkg_resources deprecation warning from pygame and others
warnings.filterwarnings("ignore", message=".*pkg_resources is deprecated.*")
from gtts import gTTS
import os
import pygame
import time
import threading
import queue
import re
import asyncio
import edge_tts
from .logger import setup_logger

logger = setup_logger(__name__)

class TTSManager:
    def __init__(self, on_speak=None):
        """
        on_speak: Callback function(text) to update GUI or logs when Aria speaks.
        """
        self.on_speak = on_speak
        self.tts_enabled = True
        self.tts_queue = queue.Queue()
        
        # Start TTS worker thread
        self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self.tts_thread.start()

    def set_tts_enabled(self, enabled: bool):
        """Enable or disable TTS output."""
        self.tts_enabled = enabled
        if not enabled:
            self.stop()

    def stop(self):
        """Stop current playback and clear queue (Interrupt)."""
        # 1. Clear Queue
        with self.tts_queue.mutex:
            self.tts_queue.queue.clear()
        
        # 2. Stop Pygame Mixer
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            # Unload to release file lock
            try:
                pygame.mixer.music.unload()
            except:
                pass
        
        logger.info("TTS Interrupted.")

    def _tts_worker(self):
        """Worker thread to handle TTS playback sequentially with Edge-TTS and gTTS fallback."""
        # Create a new event loop for this thread since edge-tts is async
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        logger.info("TTS Worker started")
        
        while True:
            text = self.tts_queue.get()
            # logger.debug(f"TTS Worker: Dequeued text: {text}") # Verbose
            if text is None:
                break
            
            try:
                # logger.debug(f"TTS Worker: Processing text: '{text[:50]}...'")
                pass
            except UnicodeEncodeError:
                pass
            
            # Create temp_voice folder if it doesn't exist
            voice_folder = "temp_voice"
            os.makedirs(voice_folder, exist_ok=True)
            
            filename = os.path.join(voice_folder, f"her_voice_{int(time.time())}_{id(text)}.mp3")
            
            edge_tts_success = False
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    # logger.debug(f"TTS Worker: Trying Edge-TTS (Attempt {attempt+1}/{max_retries})...")
                    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
                    
                    # Increased timeout to 10 seconds and added retries
                    loop.run_until_complete(
                        asyncio.wait_for(communicate.save(filename), timeout=10.0)
                    )
                    
                    # Verify file was actually created and has content
                    if os.path.exists(filename) and os.path.getsize(filename) > 0:
                        edge_tts_success = True
                        break
                    else:
                        logger.warning(f"Edge-TTS attempt {attempt+1} failed: File empty or not created")
                        
                except asyncio.TimeoutError:
                    logger.warning(f"Edge-TTS attempt {attempt+1} timed out (>10s)")
                except Exception as e:
                    logger.warning(f"Edge-TTS attempt {attempt+1} error: {e}")
                
                # Small delay before retry
                if attempt < max_retries - 1:
                    time.sleep(0.5)
            
            if not edge_tts_success:
                logger.warning("All Edge-TTS attempts failed, falling back to gTTS")
            
            if not edge_tts_success:
                try:
                    # Fallback to gTTS
                    logger.info("TTS Worker: Using gTTS fallback...")
                    tts = gTTS(text=text, lang="en", slow=False)
                    tts.save(filename)
                    logger.debug(f"TTS Worker: gTTS saved to {filename}")
                except Exception as e2:
                    logger.error(f"gTTS error: {e2}")
                    self.tts_queue.task_done()
                    continue
            
            try:
                # Play the audio file
                if os.path.exists(filename):
                    # print(f"TTS Worker: Playing audio file {filename} (size: {os.path.getsize(filename)} bytes)")
                    
                    # Lazy init pygame mixer
                    if not pygame.mixer.get_init():
                        try:
                            pygame.mixer.init()
                        except Exception as e:
                            logger.error(f"TTS Worker ERROR: Failed to initialize mixer: {e}")
                            self.tts_queue.task_done()
                            continue

                    pygame.mixer.music.load(filename)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                    # pygame.mixer.quit() # Don't quit, keep it alive
                    # print("TTS Worker: Audio playback complete")
                    
                    # Cleanup
                    try:
                        # Unload the file to release the lock on Windows
                        if pygame.mixer.get_init():
                            try:
                                pygame.mixer.music.unload()
                            except Exception as e:
                                logger.warning(f"TTS Worker WARNING: Failed to unload audio: {e}")
                        
                        # Small delay to ensure OS releases the handle
                        time.sleep(0.1)
                        
                        os.remove(filename)
                        # logger.debug(f"TTS Worker: Deleted {filename}")
                    except Exception as e:
                        logger.warning(f"TTS Worker WARNING: Failed to delete {filename}: {e}")
                else:
                    logger.error(f"TTS Worker ERROR: Audio file {filename} does not exist!")
            except Exception as e:
                logger.error(f"Audio playback error: {e}")
            finally:
                self.tts_queue.task_done()

    def _clean_text_for_audio(self, text):
        """Removes Markdown formatting for smoother TTS playback."""
        # Remove bold/italic markers (* or _)
        text = re.sub(r'[\*_]{1,3}', '', text)
        
        # Remove headers (#)
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        
        # Remove code backticks
        text = re.sub(r'`', '', text)
        
        # Remove links [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Remove list bullets (optional, but helps flow)
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
        
        return text.strip()

    def speak(self, text, print_text=True):
        if print_text:
            if self.on_speak:
                self.on_speak(text)
            
            try:
                logger.info(f"Aria said: {text}")
            except UnicodeEncodeError:
                logger.info(f"Aria said: {text.encode('ascii', 'replace').decode()}")
        
        # Clean text for audio
        clean_text = self._clean_text_for_audio(text)
        
        # Add to queue for background playback only if TTS is enabled
        if self.tts_enabled and clean_text:
            self.tts_queue.put(clean_text)
        else:
            # print(f"TTS: Not adding to queue. Enabled: {self.tts_enabled}, Text: {bool(clean_text)}")
            pass
