
import subprocess
import ctypes
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

def test_brightness():
    print("Testing Get Brightness via PowerShell...")
    try:
        cmd = "(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightness).CurrentBrightness"
        result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
        print(f"Brightness Output: {result.stdout.strip()}")
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"Exception: {e}")

def test_volume():
    print("\nTesting Volume Fixing...")
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current = volume.GetMasterVolumeLevelScalar()
        print(f"Current Volume Scalar: {current}")
        print("Volume Interface successfully initialized!")
    except Exception as e:
        print(f"Volume Init Failed: {e}")

if __name__ == "__main__":
    test_brightness()
    test_volume()
