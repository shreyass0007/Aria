from aria.speech_engine import SpeechEngine
import os

def test_speech():
    print("Testing SpeechEngine...")
    engine = SpeechEngine(model_size="base")
    
    # Check if test file exists
    test_file = "her_voice_1763923858.mp3"
    if not os.path.exists(test_file):
        print(f"Test file {test_file} not found. Please provide an audio file.")
        return

    print(f"Transcribing {test_file}...")
    text = engine.transcribe(test_file)
    print(f"Transcription: {text}")

if __name__ == "__main__":
    test_speech()
