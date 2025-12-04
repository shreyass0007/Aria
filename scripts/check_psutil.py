
import psutil
import sys

def check_stats():
    print("--- PSUTIL DIAGNOSTIC ---")
    
    # Battery
    try:
        battery = psutil.sensors_battery()
        if battery:
            print(f"Battery: {battery.percent}% (Plugged: {battery.power_plugged})")
        else:
            print("Battery: None (Desktop?)")
    except Exception as e:
        print(f"Battery Error: {e}")

    # CPU
    try:
        print(f"CPU: {psutil.cpu_percent(interval=1)}%")
    except Exception as e:
        print(f"CPU Error: {e}")

    # RAM
    try:
        print(f"RAM: {psutil.virtual_memory().percent}%")
    except Exception as e:
        print(f"RAM Error: {e}")

if __name__ == "__main__":
    check_stats()
