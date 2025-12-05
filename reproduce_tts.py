import asyncio
import edge_tts
import time
import os

async def test_edge_tts(text):
    voice = "en-US-AriaNeural"
    output_file = f"test_voice_{int(time.time())}.mp3"
    communicate = edge_tts.Communicate(text, voice)
    
    print(f"Testing Edge TTS with text: '{text}'")
    start_time = time.time()
    try:
        await asyncio.wait_for(communicate.save(output_file), timeout=10.0)
        end_time = time.time()
        print(f"Success! Time taken: {end_time - start_time:.2f} seconds")
        print(f"File saved to: {output_file}")
        if os.path.exists(output_file):
            os.remove(output_file)
    except asyncio.TimeoutError:
        print("TimeoutError: Operation took longer than 10 seconds")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    short_text = "Hello, this is a test."
    long_text = "This is a longer text to test if the connection is stable and if the timeout is sufficient for processing larger chunks of text which might take more time to generate and download from the server."
    
    asyncio.run(test_edge_tts(short_text))
    asyncio.run(test_edge_tts(long_text))
