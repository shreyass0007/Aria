"""
Verification script for SystemControl (Volume and DND)
"""
import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aria.system_control import SystemControl

def verify_volume():
    print("\n--- Verifying Volume Control ---")
    sc = SystemControl()
    
    current_vol = sc.get_volume()
    print(f"Current Volume: {current_vol}%")
    
    if current_vol is None:
        print("ERROR: Could not get current volume.")
        return

    # Test Set Volume
    test_vol = 30
    print(f"Setting volume to {test_vol}%...")
    sc.set_volume(test_vol)
    time.sleep(1)
    new_vol = sc.get_volume()
    print(f"Volume after set: {new_vol}%")
    
    if abs(new_vol - test_vol) <= 1:
        print("PASS: Set volume worked.")
    else:
        print(f"FAIL: Set volume failed. Expected {test_vol}, got {new_vol}")

    # Restore Volume
    print(f"Restoring volume to {current_vol}%...")
    sc.set_volume(current_vol)
    print("Volume restored.")

def verify_dnd():
    print("\n--- Verifying Do Not Disturb (DND) ---")
    sc = SystemControl()
    
    # Check current status
    is_dnd = sc.get_dnd_status()
    print(f"Current DND Status: {'Enabled' if is_dnd else 'Disabled'}")
    
    # Toggle DND
    new_state = not is_dnd
    print(f"Toggling DND to {'Enabled' if new_state else 'Disabled'}...")
    result = sc.set_dnd(new_state)
    print(f"Result: {result}")
    
    # Check status again
    verification = sc.get_dnd_status()
    print(f"DND Status after toggle: {'Enabled' if verification else 'Disabled'}")
    
    if verification == new_state:
        print("PASS: DND toggle worked (Registry check).")
    else:
        print("FAIL: DND toggle failed (Registry logic might be incorrect for this OS version).")

    # Restore DND
    print(f"Restoring DND to {'Enabled' if is_dnd else 'Disabled'}...")
    sc.set_dnd(is_dnd)
    print("DND restored.")

if __name__ == "__main__":
    try:
        verify_volume()
        verify_dnd()
    except Exception as e:
        print(f"msg: {e}")
