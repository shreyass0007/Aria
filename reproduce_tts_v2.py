import asyncio
import edge_tts
import time
import os

async def test_edge_tts(text):
    voice = "en-US-AriaNeural"
    output_file = f"test_voice_{int(time.time())}.mp3"
    communicate = edge_tts.Communicate(text, voice)
    
    print(f"Testing Edge TTS with text: '{text[:20]}...'")
    start_time = time.time()
    try:
        await asyncio.wait_for(communicate.save(output_file), timeout=20.0)
        end_time = time.time()
        duration = end_time - start_time
        print(f"Success! Time taken: {duration:.2f} seconds")
        
        if os.path.exists(output_file):
            os.remove(output_file)
            
        return duration
    except asyncio.TimeoutError:
        print("TimeoutError: Operation took longer than 20 seconds")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

async def main():
    short_text = "Hello, this is a test."
    long_text = "This is a longer text to test if the connection is stable and if the timeout is sufficient for processing larger chunks of text which might take more time to generate and download from the server. We want to see if 3 seconds is enough."
    
    print("--- Starting Tests ---")
    t1 = await test_edge_tts(short_text)
    t2 = await test_edge_tts(long_text)
    print("--- Tests Finished ---")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Main Error: {e}")
