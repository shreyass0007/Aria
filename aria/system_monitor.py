import psutil
import time
from .logger import setup_logger

logger = setup_logger(__name__)

class SystemMonitor:
    def __init__(self):
        self.battery_threshold = 25
        self.cpu_threshold = 90
        self.last_alert_time = 0
        self.alert_cooldown = 300  # 5 minutes cooldown between alerts

    def get_battery_status(self):
        """
        Returns battery status: {"percent": int, "power_plugged": bool}
        Returns None if no battery is installed (desktop).
        """
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    "percent": battery.percent,
                    "power_plugged": battery.power_plugged
                }
            return None
        except Exception as e:
            logger.error(f"Error reading battery: {e}")
            return None

    def get_cpu_usage(self):
        """
        Returns CPU usage percentage.
        """
        try:
            return psutil.cpu_percent(interval=1)
        except Exception as e:
            logger.error(f"Error reading CPU: {e}")
            return 0

    def check_health(self):
        """
        Checks system health and returns a list of alert messages if thresholds are breached.
        Respects a cooldown period to avoid spamming.
        """
        alerts = []
        current_time = time.time()

        # Check cooldown
        if current_time - self.last_alert_time < self.alert_cooldown:
            return alerts

        # Check Battery
        battery = self.get_battery_status()
        if battery:
            if not battery["power_plugged"] and battery["percent"] <= self.battery_threshold:
                alerts.append(f"Heads up, your battery is low at {battery['percent']}%. You might want to plug in.")

        # Check CPU
        cpu = self.get_cpu_usage()
        if cpu >= self.cpu_threshold:
            alerts.append(f"System warning: CPU usage is high at {cpu}%.")

        if alerts:
            self.last_alert_time = current_time

        return alerts

    def get_ram_usage(self):
        """
        Returns RAM usage percentage.
        """
        try:
            return psutil.virtual_memory().percent
        except Exception as e:
            logger.error(f"Error reading RAM: {e}")
            return 0

    def get_all_stats(self):
        """
        Returns a dictionary containing all system statistics.
        """
        return {
            "battery": self.get_battery_status(),
            "cpu": self.get_cpu_usage(),
            "ram": self.get_ram_usage()
        }

if __name__ == "__main__":
    monitor = SystemMonitor()
    print("Battery:", monitor.get_battery_status())
    print("CPU:", monitor.get_cpu_usage())
    print("Health Check:", monitor.check_health())
