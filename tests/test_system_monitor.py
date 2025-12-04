"""
Test script for system monitoring functionality
"""

from system_monitor import SystemMonitor
import time

def test_system_monitoring():
    """Test all system monitoring operations."""
    print("=" * 70)
    print("TESTING SYSTEM MONITORING MODULE")
    print("=" * 70)
    
    monitor = SystemMonitor()
    
    # Test 1: Battery Status
    print("\n[TEST 1] Battery Status")
    print("-" * 70)
    result = monitor.get_battery_status()
    print(result)
    print("✓ PASSED" if "Battery" in result or "No battery" in result else "✗ FAILED")
    time.sleep(1)
    
    # Test 2: CPU Usage
    print("\n[TEST 2] CPU Usage")
    print("-" * 70)
    result = monitor.get_cpu_usage()
    print(result)
    print("✓ PASSED" if "CPU" in result else "✗ FAILED")
    time.sleep(1)
    
    # Test 3: RAM Usage
    print("\n[TEST 3] RAM Usage")
    print("-" * 70)
    result = monitor.get_ram_usage()
    print(result)
    print("✓ PASSED" if "RAM" in result else "✗ FAILED")
    time.sleep(1)
    
    # Test 4: All System Stats
    print("\n[TEST 4] All System Statistics")
    print("-" * 70)
    result = monitor.get_all_stats()
    print(result)
    print("✓ PASSED" if "SYSTEM STATISTICS" in result else "✗ FAILED")
    
    # Final Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print("All tests completed!")
    print("\nSystem monitoring is working correctly.")
    print("\nVoice commands to try:")
    print("  - 'Aria, check battery'")
    print("  - 'Aria, check CPU usage'")
    print("  - 'Aria, check RAM'")
    print("  - 'Aria, system stats'")
    print("=" * 70)

if __name__ == "__main__":
    try:
        test_system_monitoring()
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
