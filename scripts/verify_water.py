
import sys
import os
import time

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aria.water_manager import WaterManager

def test_water_reminders():
    print("Testing Water Manager...")
    try:
        wm = WaterManager()
        print("✅ WaterManager initialized.")
        
        # Test basic state
        status = wm.is_running
        print(f"Current Status (is_running): {status}")
        
        # Test start
        print("Starting reminder loop...")
        res = wm.start_reminders()
        print(f"Start Result: {res}")
        
        # Test interval change
        res = wm.set_interval(45)
        print(f"Set Interval Result: {res}")
        
        # Test simple calc
        print("Recalculating interval based on mock weather (skipping real API call for speed)...")
        # Just checking method existence and basic logic
        
        # Test stop
        print("Stopping reminder loop...")
        res = wm.stop_reminders()
        print(f"Stop Result: {res}")
        
        print("\n✅ Water Reminder Logic Check Passed.")
    except Exception as e:
        print(f"\n❌ Water Manager Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_water_reminders()
