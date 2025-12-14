
import subprocess
import sys

def inspect_pycaw():
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        print(f"Imported AudioUtilities: {AudioUtilities}")
        devices = AudioUtilities.GetSpeakers()
        print(f"Devices type: {type(devices)}")
        print(f"Devices dir: {dir(devices)}")
    except Exception as e:
        print(f"Pycaw Error: {e}")

def test_brightness_ps():
    cmd = "powershell -Command \"Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightness | Select-Object -ExpandProperty CurrentBrightness\""
    print(f"Running: {cmd}")
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"STDOUT: '{res.stdout.strip()}'")
        print(f"STDERR: '{res.stderr.strip()}'")
    except Exception as e:
        print(f"PS Error: {e}")

if __name__ == "__main__":
    inspect_pycaw()
    test_brightness_ps()
