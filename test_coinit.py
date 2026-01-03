
import sys
import comtypes

def verify_with_explicit_init():
    print("Initializing COM...")
    try:
        comtypes.CoInitialize()
        print("COM Initialized.")
        
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL
        
        devices = AudioUtilities.GetSpeakers()
        print(f"Speakers Object: {devices}")
        
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        print("Activate SUCCESS")
        
        volume = interface.QueryInterface(IAudioEndpointVolume)
        print(f"Volume Object: {volume}")
        print(f"Current Scalar: {volume.GetMasterVolumeLevelScalar()}")
        
    except Exception as e:
        print(f"FATA_ERROR: {e}")

if __name__ == "__main__":
    verify_with_explicit_init()
