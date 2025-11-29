import asyncio
import edge_tts
from gtts import gTTS
import os

async def main():
    print("Testing 'en-US-AvaMultilingualNeural'...")
    try:
        communicate = edge_tts.Communicate("Hello world", "en-US-AvaMultilingualNeural")
        await communicate.save("test_ava.mp3")
        print("Edge TTS (Ava) success.")
    except Exception as e:
        print(f"Edge TTS (Ava) failed: {e}")

    print("\nTesting gTTS...")
    try:
        tts = gTTS(text="Hello world", lang="en", slow=False)
        tts.save("test_gtts.mp3")
        print("gTTS success.")
    except Exception as e:
        print(f"gTTS failed: {e}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
