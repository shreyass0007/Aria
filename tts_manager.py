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
            # Clear queue if disabled
            with self.tts_queue.mutex:
                self.tts_queue.queue.clear()

    def _tts_worker(self):
        """Worker thread to handle TTS playback sequentially with Edge-TTS and gTTS fallback."""
        # Create a new event loop for this thread since edge-tts is async
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        print("TTS Worker started")
        
        while True:
            text = self.tts_queue.get()
            # print(f"TTS Worker: Dequeued text: {text}") # Verbose
            if text is None:
                break
            
            try:
                # print(f"TTS Worker: Processing text: '{text[:50]}...'")
                pass
            except UnicodeEncodeError:
                pass
            
            # Create temp_voice folder if it doesn't exist
            voice_folder = "temp_voice"
            os.makedirs(voice_folder, exist_ok=True)
            
            filename = os.path.join(voice_folder, f"her_voice_{int(time.time())}_{id(text)}.mp3")
            
            edge_tts_success = False
            try:
                # print("TTS Worker: Trying Edge-TTS...")
                # Try Edge TTS first with timeout
                communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
                # Use wait_for to add a 3-second timeout
                loop.run_until_complete(
                    asyncio.wait_for(communicate.save(filename), timeout=3.0)
                )
                # print(f"TTS Worker: Edge-TTS saved to {filename}")
                edge_tts_success = True
                
            except asyncio.TimeoutError:
                print("Edge-TTS timeout (>3s), falling back to gTTS")
            except Exception as e:
                print(f"Edge-TTS error, falling back to gTTS: {e}")
            
            if not edge_tts_success:
                try:
                    # Fallback to gTTS
                    print("TTS Worker: Using gTTS fallback...")
                    tts = gTTS(text=text, lang="en", slow=False)
                    tts.save(filename)
                    print(f"TTS Worker: gTTS saved to {filename}")
                except Exception as e2:
                    print(f"gTTS error: {e2}")
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
                            print(f"TTS Worker ERROR: Failed to initialize mixer: {e}")
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
                                print(f"TTS Worker WARNING: Failed to unload audio: {e}")
                        
                        # Small delay to ensure OS releases the handle
                        time.sleep(0.1)
                        
                        os.remove(filename)
                        # print(f"TTS Worker: Deleted {filename}")
                    except Exception as e:
                        print(f"TTS Worker WARNING: Failed to delete {filename}: {e}")
                else:
                    print(f"TTS Worker ERROR: Audio file {filename} does not exist!")
            except Exception as e:
                print(f"Audio playback error: {e}")
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
                print(f"Aria said: {text}")
            except UnicodeEncodeError:
                print(f"Aria said: {text.encode('ascii', 'replace').decode()}")
        
        # Clean text for audio
        clean_text = self._clean_text_for_audio(text)
        
        # Add to queue for background playback only if TTS is enabled
        if self.tts_enabled and clean_text:
            self.tts_queue.put(clean_text)
        else:
            # print(f"TTS: Not adding to queue. Enabled: {self.tts_enabled}, Text: {bool(clean_text)}")
            pass
