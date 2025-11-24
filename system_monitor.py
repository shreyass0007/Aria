"""
System Monitoring Module for Aria
Monitors battery, CPU, and RAM status
"""

import psutil
from datetime import timedelta


class SystemMonitor:
    """Provides system monitoring for Windows:
    - Battery monitoring (percentage, charging, time remaining)
    - CPU usage monitoring
    - RAM/Memory usage monitoring
    """

    def __init__(self):
        """Initialize the system monitor."""
        pass

    # ==================== BATTERY MONITORING ====================

    def get_battery_status(self) -> str:
        """Get comprehensive battery status with friendly suggestions.
        
        Returns:
            Formatted battery status message or error if battery not available
        """
        try:
            battery = psutil.sensors_battery()
            
            if battery is None:
                return "No battery detected. This appears to be a desktop computer."
            
            # Get battery details
            percent = battery.percent
            plugged = battery.power_plugged
            
            # Build status message
            status_parts = []
            
            # Battery percentage with emoji
            if percent >= 80:
                emoji = "🔋"
            elif percent >= 50:
                emoji = "🔋"
            elif percent >= 20:
                emoji = "🪫"
            else:
                emoji = "🪫"
            
            status_parts.append(f"{emoji} Battery: {percent}%")
            
            # Charging status with helpful suggestions
            if plugged:
                status_parts.append("⚡ Charging")
                
                # Time to full charge
                if battery.secsleft != psutil.POWER_TIME_UNLIMITED and battery.secsleft > 0:
                    time_left = str(timedelta(seconds=battery.secsleft))
                    # Convert to human-readable format
                    hours, remainder = divmod(battery.secsleft, 3600)
                    minutes, _ = divmod(remainder, 60)
                    if hours > 0:
                        time_str = f"{int(hours)} hour{'s' if hours != 1 else ''} and {int(minutes)} minute{'s' if minutes != 1 else ''}"
                    else:
                        time_str = f"{int(minutes)} minute{'s' if minutes != 1 else ''}"
                    status_parts.append(f"⏱️ Time to full charge: {time_str}")
                
                # Friendly message when nearly full
                if percent >= 95:
                    status_parts.append("💡 Your battery is almost full! You can unplug soon.")
                elif percent >= 80:
                    status_parts.append("✅ Battery is looking good!")
            else:
                status_parts.append("🔌 Not plugged in")
                
                # Time remaining on battery
                if battery.secsleft != psutil.POWER_TIME_UNLIMITED and battery.secsleft > 0:
                    hours, remainder = divmod(battery.secsleft, 3600)
                    minutes, _ = divmod(remainder, 60)
                    if hours > 0:
                        time_str = f"{int(hours)} hour{'s' if hours != 1 else ''} and {int(minutes)} minute{'s' if minutes != 1 else ''}"
                    else:
                        time_str = f"{int(minutes)} minute{'s' if minutes != 1 else ''}"
                    status_parts.append(f"⏱️ Battery time remaining: {time_str}")
                
                # Friendly warnings based on battery level
                if percent <= 10:
                    status_parts.append("⚠️ CRITICAL: Battery very low! Please plug in your charger immediately to avoid data loss.")
                elif percent <= 20:
                    status_parts.append("⚠️ Warning: Battery is running low. Consider plugging in soon!")
                elif percent <= 30:
                    status_parts.append("💡 Heads up: Battery is getting low. You might want to find a charger.")
                elif percent >= 80:
                    status_parts.append("✅ Battery is healthy! You're good to go for a while.")
            
            return "\n".join(status_parts)
            
        except Exception as e:
            return f"Unable to read battery status: {str(e)}"

    # ==================== CPU MONITORING ====================

    def get_cpu_usage(self) -> str:
        """Get current CPU usage percentage with helpful suggestions.
        
        Returns:
            Formatted CPU usage message
        """
        try:
            # Get CPU percentage (1 second interval for accuracy)
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Build response
            response_parts = []
            
            # Determine status based on usage
            if cpu_percent < 30:
                status = "Low usage"
                emoji = "💻"
                suggestion = "✅ Your system is running smoothly!"
            elif cpu_percent < 70:
                status = "Moderate usage"
                emoji = "💻"
                suggestion = "👍 CPU is working normally."
            else:
                status = "High usage"
                emoji = "🔥"
                if cpu_percent >= 90:
                    suggestion = "⚠️ CPU is running very hot! Consider closing some applications to improve performance."
                else:
                    suggestion = "💡 CPU is working hard. If things feel slow, try closing unused apps."
            
            response_parts.append(f"{emoji} CPU Usage: {cpu_percent}%")
            response_parts.append(f"📊 Status: {status}")
            
            # Get CPU frequency if available
            try:
                freq = psutil.cpu_freq()
                if freq:
                    freq_ghz = freq.current / 1000
                    response_parts.append(f"⚡ Frequency: {freq_ghz:.2f} GHz")
            except:
                pass
            
            response_parts.append(suggestion)
            
            return "\n".join(response_parts)
            
        except Exception as e:
            return f"Unable to read CPU usage: {str(e)}"

    # ==================== RAM MONITORING ====================

    def get_ram_usage(self) -> str:
        """Get current RAM/memory usage with helpful suggestions.
        
        Returns:
            Formatted RAM usage message
        """
        try:
            # Get memory info
            memory = psutil.virtual_memory()
            
            # Convert bytes to GB
            total_gb = memory.total / (1024 ** 3)
            used_gb = memory.used / (1024 ** 3)
            available_gb = memory.available / (1024 ** 3)
            percent = memory.percent
            
            # Build response
            response_parts = []
            
            # Determine status and suggestion
            if percent < 50:
                emoji = "🧠"
                status = "Good"
                suggestion = "✅ Plenty of memory available!"
            elif percent < 80:
                emoji = "🧠"
                status = "Moderate"
                suggestion = "👍 Memory usage is normal."
            elif percent < 90:
                emoji = "⚠️"
                status = "High usage"
                suggestion = "💡 RAM is getting full. Consider closing unused apps or browser tabs to free up memory."
            else:
                emoji = "⚠️"
                status = "Critical"
                suggestion = "⚠️ RAM is almost full! Close some applications to prevent slowdowns."
            
            response_parts.append(f"{emoji} RAM Usage: {used_gb:.1f} GB / {total_gb:.1f} GB ({percent}%)")
            response_parts.append(f"📊 Status: {status}")
            response_parts.append(f"✅ Available: {available_gb:.1f} GB")
            response_parts.append(suggestion)
            
            return "\n".join(response_parts)
            
        except Exception as e:
            return f"Unable to read RAM usage: {str(e)}"

    # ==================== COMBINED STATS ====================

    def get_all_stats(self) -> str:
        """Get all system statistics (battery, CPU, RAM).
        
        Returns:
            Formatted message with all system stats
        """
        try:
            stats = []
            stats.append("📊 SYSTEM STATISTICS")
            stats.append("━" * 40)
            
            # Battery (if available)
            battery = psutil.sensors_battery()
            if battery is not None:
                percent = battery.percent
                plugged = "⚡ Charging" if battery.power_plugged else "🔌 On Battery"
                stats.append(f"🔋 Battery: {percent}% ({plugged})")
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            stats.append(f"💻 CPU: {cpu_percent}%")
            
            # RAM
            memory = psutil.virtual_memory()
            used_gb = memory.used / (1024 ** 3)
            total_gb = memory.total / (1024 ** 3)
            stats.append(f"🧠 RAM: {used_gb:.1f} GB / {total_gb:.1f} GB ({memory.percent}%)")
            
            stats.append("━" * 40)
            
            return "\n".join(stats)
            
        except Exception as e:
            return f"Unable to read system statistics: {str(e)}"


if __name__ == "__main__":
    # Test the module
    monitor = SystemMonitor()
    
    print("Testing System Monitor Module...")
    print("=" * 60)
    
    print("\n1. Battery Status:")
    print(monitor.get_battery_status())
    
    print("\n2. CPU Usage:")
    print(monitor.get_cpu_usage())
    
    print("\n3. RAM Usage:")
    print(monitor.get_ram_usage())
    
    print("\n4. All System Stats:")
    print(monitor.get_all_stats())
    
    print("\n" + "=" * 60)
    print("Test complete!")
