import asyncio
import edge_tts
import os

async def test_tts():
    text = "Hello, this is a test of Edge TTS."
    output_file = "test_edge_voice.mp3"
    
    print(f"Generating speech: '{text}'")
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    await communicate.save(output_file)
    
    if os.path.exists(output_file):
        print(f" Success! Audio saved to {output_file}")
        print(f"File size: {os.path.getsize(output_file)} bytes")
    else:
        print(" Failed to generate audio")

if __name__ == "__main__":
    asyncio.run(test_tts())
