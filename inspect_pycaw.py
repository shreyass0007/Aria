
import sys
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

def inspect_pycaw():
    print("Inspecting AudioUtilities...")
    try:
        devices = AudioUtilities.GetSpeakers()
        print(f"GetSpeakers returned type: {type(devices)}")
        print(f"Dir(devices): {dir(devices)}")
    except Exception as e:
        print(f"GetSpeakers FAILED: {e}")

if __name__ == "__main__":
    inspect_pycaw()
