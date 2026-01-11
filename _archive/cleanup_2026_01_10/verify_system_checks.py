
import sys
import time

# Force stdout to be utf-8
sys.stdout.reconfigure(encoding='utf-8')

try:
    from aria.system_control import SystemControl
except ImportError as e:
    print(f"CRITICAL: Import failed: {e}")
    sys.exit(1)

def verify_simple():
    print("STARTING_VERIFICATION")
    try:
        sc = SystemControl()
    except Exception as e:
        print(f"INIT_ERROR: {e}")
        return

    vol = sc.get_volume()
    print(f"VOLUME_INITIAL: {vol}")
    
    if vol is None:
        print("VOLUME_INTERFACE_NONE")
    else:
        target = 20
        print(f"SETTING_VOLUME_TO: {target}")
        sc.set_volume(target)
        time.sleep(1)
        new_vol = sc.get_volume()
        print(f"VOLUME_NEW: {new_vol}")
        
        if new_vol == target:
            print("VOLUME_TEST_PASS")
        else:
            print("VOLUME_TEST_FAIL")
            
        print(f"RESTORING_VOLUME: {vol}")
        sc.set_volume(vol)
    
    bright = sc.get_brightness()
    print(f"BRIGHTNESS_INITIAL: {bright}")
    print("VERIFICATION_COMPLETE")

if __name__ == "__main__":
    verify_simple()
