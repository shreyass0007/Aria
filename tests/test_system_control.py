"""
Test script for System Control Module
Tests volume control and recycle bin features safely (no power management tests)
"""

from aria.system_control import SystemControl
import time


def test_volume_control():
    """Test volume control features"""
    print("=" * 50)
    print("TESTING VOLUME CONTROL")
    print("=" * 50)
    
    controller = SystemControl()
    
    # Get current volume
    print("\n1. Getting current volume...")
    vol = controller.get_volume()
    print(f"   Current volume: {vol}%")
    
    # Check if muted
    muted = controller.is_muted()
    print(f"   Is muted: {muted}")
    
    # Save current volume for restoration
    original_volume = vol
    
    # Test setting volume
    print("\n2. Setting volume to 50%...")
    result = controller.set_volume(50)
    print(f"   {result}")
    time.sleep(1)
    print(f"   Verification: {controller.get_volume()}%")
    
    # Test increasing volume
    print("\n3. Increasing volume by 10%...")
    result = controller.increase_volume(10)
    print(f"   {result}")
    time.sleep(1)
    
    # Test decreasing volume
    print("\n4. Decreasing volume by 5%...")
    result = controller.decrease_volume(5)
    print(f"   {result}")
    time.sleep(1)
    
    # Test mute
    print("\n5. Testing mute...")
    result = controller.mute()
    print(f"   {result}")
    time.sleep(1)
    print(f"   Is muted: {controller.is_muted()}")
    
    # Test unmute
    print("\n6. Testing unmute...")
    result = controller.unmute()
    print(f"   {result}")
    time.sleep(1)
    
    # Restore original volume
    print(f"\n7. Restoring original volume ({original_volume}%)...")
    controller.set_volume(original_volume)
    print("   Volume restored")


def test_recycle_bin():
    """Test recycle bin features (read-only, no emptying)"""
    print("\n" + "=" * 50)
    print("TESTING RECYCLE BIN (READ-ONLY)")
    print("=" * 50)
    
    controller = SystemControl()
    
    # Check recycle bin size
    print("\n1. Checking recycle bin size...")
    result = controller.get_recycle_bin_size()
    print(f"   {result}")
    
    # NOTE: We won't test emptying the recycle bin automatically
    # to avoid accidentally deleting user data
    print("\n   (Skipping empty test for safety)")


def test_power_info():
    """Display power management info without executing"""
    print("\n" + "=" * 50)
    print("POWER MANAGEMENT COMMANDS (NOT TESTED)")
    print("=" * 50)
    
    print("\nAvailable power management commands:")
    print("  - lock_system(): Lock the workstation")
    print("  - sleep_system(): Put system to sleep")
    print("  - shutdown_system(timer): Shutdown with optional timer")
    print("  - restart_system(timer): Restart with optional timer")
    print("  - cancel_shutdown(): Cancel pending shutdown/restart")
    print("\nThese are NOT tested automatically for safety.")


if __name__ == "__main__":
    print("\n SYSTEM CONTROL MODULE TEST SUITE")
    print("Testing system control features safely...\n")
    
    try:
        # Test volume control
        test_volume_control()
        
        # Test recycle bin
        test_recycle_bin()
        
        # Show power management info
        test_power_info()
        
        print("\n" + "=" * 50)
        print(" ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n ERROR: {e}")
        import traceback
        traceback.print_exc()
