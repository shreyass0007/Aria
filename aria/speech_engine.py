import os
import torch
from faster_whisper import WhisperModel

class SpeechEngine:
    def __init__(self, model_size="base", device=None, compute_type="int8"):
        """
        Initializes the Faster-Whisper model.
        
        Args:
            model_size (str): Size of the model (tiny, base, small, medium, large-v2).
            device (str): "cuda" for GPU or "cpu". Auto-detected if None.
            compute_type (str): "float16" or "int8_float16" for GPU, "int8" for CPU.
        """
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"Initializing SpeechEngine with model='{model_size}', device='{device}'...")
        
        try:
            self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
            print("SpeechEngine initialized successfully.")
        except Exception as e:
            print(f"Error initializing SpeechEngine: {e}")
            self.model = None

    def transcribe(self, audio_source):
        """
        Transcribes audio from a file path or file-like object.
        
        Args:
            audio_source: Path to audio file or file-like object.
            
        Returns:
            str: The transcribed text.
        """
        if not self.model:
            print("SpeechEngine model not loaded.")
            return ""

        try:
            segments, info = self.model.transcribe(audio_source, beam_size=5)
            
            text = ""
            for segment in segments:
                text += segment.text
            
            return text.strip()
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""

if __name__ == "__main__":
    # Test
    engine = SpeechEngine()
    # Create a dummy file or use an existing one to test if needed
    print("SpeechEngine ready.")
