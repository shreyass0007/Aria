
import sys
# Force utf-8
sys.stdout.reconfigure(encoding='utf-8')
try:
    from pycaw.pycaw import AudioUtilities
    devices = AudioUtilities.GetSpeakers()
    print(f"DEVICE: {devices}")
    
    if hasattr(devices, '_dev'):
        raw_dev = devices._dev
        print(f"RAW_DEV TYPE: {type(raw_dev)}")
        print(f"RAW_DEV DIR: {dir(raw_dev)}")
        try:
            print(f"HAS ACTIVATE: {hasattr(raw_dev, 'Activate')}")
        except:
            print("Check failed")
    else:
        print("No _dev attribute")

except Exception as e:
    print(f"ERROR: {e}")
