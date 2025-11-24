import asyncio
import edge_tts
import pygame
import os
import time

import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

async def test_voice():
    print("Testing Edge TTS...")
    text = "Hello, this is a test of the Edge TTS system."
    voice = "en-US-AriaNeural"
    filename = "test_audio.mp3"
    
    try:
        print(f"Generating audio for: '{text}'")
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filename)
        print(f"Audio saved to {filename}")
        
        if os.path.exists(filename):
            print(f"File size: {os.path.getsize(filename)} bytes")
            
            print("Initializing Pygame mixer...")
            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            print("Playing audio...")
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            print("Playback finished.")
            pygame.mixer.quit()
            
            # os.remove(filename)
            print("Test complete.")
        else:
            print("Error: File was not created.")
            
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_voice())
