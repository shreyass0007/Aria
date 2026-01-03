
import sys
# Force utf-8
sys.stdout.reconfigure(encoding='utf-8')
try:
    from pycaw.pycaw import AudioUtilities
    devices = AudioUtilities.GetSpeakers()
    print(f"TYPE: {type(devices)}")
    print("DIR:")
    for d in dir(devices):
        print(f" - {d}")
except Exception as e:
    print(f"ERROR: {e}")
