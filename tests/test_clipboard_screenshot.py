"""
Test script for clipboard and screenshot functionality
"""

from aria.clipboard_screenshot import ClipboardScreenshot
import time

def test_clipboard_and_screenshot():
    """Test all clipboard and screenshot operations."""
    print("=" * 70)
    print("TESTING CLIPBOARD AND SCREENSHOT MODULE")
    print("=" * 70)
    
    handler = ClipboardScreenshot()
    
    # Test 1: Clipboard Copy
    print("\n[TEST 1] Clipboard Copy")
    print("-" * 70)
    test_text = "Hello from Aria! This is a test message."
    result = handler.copy_to_clipboard(test_text)
    print(f"Result: {result}")
    print(" PASSED" if "Copied to clipboard" in result else " FAILED")
    time.sleep(0.5)
    
    # Test 2: Clipboard Read
    print("\n[TEST 2] Clipboard Read")
    print("-" * 70)
    result = handler.read_clipboard()
    print(f"Result: {result}")
    print(" PASSED" if test_text in result else " FAILED")
    time.sleep(0.5)
    
    # Test 3: Clipboard Clear
    print("\n[TEST 3] Clipboard Clear")
    print("-" * 70)
    result = handler.clear_clipboard()
    print(f"Result: {result}")
    print(" PASSED" if "cleared" in result.lower() else " FAILED")
    time.sleep(0.5)
    
    # Test 4: Verify Clipboard is Empty
    print("\n[TEST 4] Verify Clipboard Empty")
    print("-" * 70)
    result = handler.read_clipboard()
    print(f"Result: {result}")
    print(" PASSED" if "empty" in result.lower() else " FAILED")
    time.sleep(0.5)
    
    # Test 5: Screenshot (Auto-named)
    print("\n[TEST 5] Screenshot with Auto-naming")
    print("-" * 70)
    result = handler.take_screenshot()
    print(f"Result: {result}")
    print(" PASSED" if "Screenshot saved" in result else " FAILED")
    time.sleep(0.5)
    
    # Test 6: Screenshot (Custom name)
    print("\n[TEST 6] Screenshot with Custom Name")
    print("-" * 70)
    result = handler.take_screenshot("aria_test_screenshot")
    print(f"Result: {result}")
    print(" PASSED" if "aria_test_screenshot.png" in result else " FAILED")
    time.sleep(0.5)
    
    # Test 7: Copy multiline text
    print("\n[TEST 7] Copy Multiline Text")
    print("-" * 70)
    multiline = "Line 1\nLine 2\nLine 3"
    result = handler.copy_to_clipboard(multiline)
    print(f"Result: {result}")
    print(" PASSED" if "Copied to clipboard" in result else " FAILED")
    
    # Final Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print("All tests completed!")
    print("Check Desktop/Screenshots folder for screenshot files:")
    print(f"  - Screenshot directory: {handler.screenshot_dir}")
    print("\nManual verification needed:")
    print("  1. Check if screenshots were actually created")
    print("  2. Paste clipboard content (Ctrl+V) to verify multiline text")
    print("=" * 70)

if __name__ == "__main__":
    try:
        test_clipboard_and_screenshot()
    except Exception as e:
        print(f"\n ERROR: {e}")
        import traceback
        traceback.print_exc()
