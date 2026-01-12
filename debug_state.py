import time
from aria.executor.state_monitor import DesktopStateMonitor

def test_monitor():
    print("Initializing DesktopStateMonitor...")
    monitor = DesktopStateMonitor()
    
    print("\n--- Active Window Monitor (Ctrl+C to stop) ---")
    print("Please switch between windows to see if I detect them.")
    
    try:
        while True:
            title = monitor.get_active_window_title()
            print(f"Active Window: '{title}'")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    test_monitor()
