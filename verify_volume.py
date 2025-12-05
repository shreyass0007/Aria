from aria.system_control import SystemControl
import time

def test_volume():
    print("Initializing SystemControl...")
    sys_control = SystemControl()
    
    if not sys_control.volume_interface:
        print("ERROR: Volume interface not initialized.")
        return

    print("Getting current volume...")
    current_vol = sys_control.get_volume()
    print(f"Current Volume: {current_vol}%")

    if current_vol is None:
        print("ERROR: Could not get volume.")
        return

    print("Setting volume to 50%...")
    result = sys_control.set_volume(50)
    print(f"Result: {result}")
    
    time.sleep(1)
    
    print(f"New Volume: {sys_control.get_volume()}%")
    
    print("Restoring volume...")
    sys_control.set_volume(current_vol)
    print(f"Restored Volume: {sys_control.get_volume()}%")

if __name__ == "__main__":
    try:
        test_volume()
    except Exception as e:
        print(f"Test failed with error: {e}")
