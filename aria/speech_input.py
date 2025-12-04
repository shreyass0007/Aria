import speech_recognition as sr
import os
import time
import threading

from pathlib import Path

class SpeechInput:
    def __init__(self, tts_manager):
        self.tts_manager = tts_manager
        self.recognizer = sr.Recognizer()
        self.lock = threading.Lock()
        self.speech_engine = None

    def check_microphones(self):
        try:
            mics = sr.Microphone.list_microphone_names()
            print(f"Available Microphones: {mics}")
            if not mics:
                print("WARNING: No microphones found!")
        except Exception as e:
            print(f"Error listing microphones: {e}")

    def listen(self):
        # Acquire lock to ensure only one thread listens at a time
        with self.lock:
            try:
                with sr.Microphone() as source:
                    print("Listening...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                    self.recognizer.energy_threshold = 300
                    
                    # Listen for audio
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    
                    # Save temporary file for Whisper in temp_voice folder
                    voice_folder = Path("temp_voice")
                    voice_folder.mkdir(exist_ok=True)
                    temp_wav = voice_folder / f"temp_voice_{int(time.time())}.wav"
                    
                    with open(temp_wav, "wb") as f:
                        f.write(audio.get_wav_data())
                    
                    # Transcribe using Local Faster-Whisper
                    print("Transcribing locally...")
                    
                    # Lazy load SpeechEngine if not already loaded
                    if self.speech_engine is None:
                        try:
                            print("Initializing SpeechEngine (Lazy Load)...")
                            from .speech_engine import SpeechEngine
                            self.speech_engine = SpeechEngine(model_size="base")
                        except Exception as e:
                            print(f"Failed to initialize SpeechEngine: {e}")
                            self.tts_manager.speak("Sorry, I can't hear you right now. Voice engine failed to start.")
                            return ""

                    if self.speech_engine:
                        command = self.speech_engine.transcribe(str(temp_wav))
                    else:
                        command = ""
                    
                    # Cleanup
                    if temp_wav.exists():
                        temp_wav.unlink()
                        
                    print(f"User said: {command}")
                    return command.lower()
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                return ""
            except (AssertionError, AttributeError) as e:
                print(f"Microphone initialization error: {e}")
                return ""
            except Exception as e:
                print(f"Listen error: {e}")
                return ""
