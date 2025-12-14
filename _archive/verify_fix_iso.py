
import sys
import os
import ctypes
# Add project root to path
sys.path.append(os.path.abspath("d:/CODEING/PROJECTS/ARIA"))

import logging
# Mock logger to avoid import errors if logger.py has deps
class MockLogger:
    def info(self, msg): print(f"INFO: {msg}")
    def warning(self, msg): print(f"WARN: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")
    def debug(self, msg): pass

# Patch logger
import aria.system_control
aria.system_control.logger = MockLogger()

from aria.system_control import SystemControl

def verify():
    print("=== VERIFYING SYSTEM CONTROL FIXES (ISOLATED) ===")
    
    # 1. System Control
    try:
        sc = SystemControl()
        print("\n[System Control Check]")
        
        # Volume
        vol = sc.get_volume()
        print(f"Current Volume: {vol}%")
        if vol is not None:
            # Test set volume (small change to verify control)
            print("Volume Control: DETECTED")
        else:
            print("Volume Control: FAIL (None returned)")

        # Brightness
        bright = sc.get_brightness()
        print(f"Current Brightness: {bright}%")
        if bright is not None:
            print("Brightness Control: DETECTED")
        else:
            print("Brightness Control: FAIL or Not Supported")
            
    except Exception as e:
        print(f"System Control Initialization Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify()
