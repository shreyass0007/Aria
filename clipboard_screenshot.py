"""
Clipboard and Screenshot Module for Aria
Handles clipboard operations and screenshot capture
"""

import os
import pyperclip
from PIL import ImageGrab
from datetime import datetime
from pathlib import Path


class ClipboardScreenshot:
    """Provides clipboard and screenshot functionality for Windows:
    - Clipboard operations (copy, read, clear)
    - Screenshot capture with automatic or custom naming
    """

    def __init__(self):
        """Initialize the clipboard and screenshot handler."""
        # Set default screenshot directory to Desktop/Screenshots
        desktop = Path.home() / "Desktop"
        self.screenshot_dir = desktop / "Screenshots"
        
        # Create the Screenshots folder if it doesn't exist
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    # ==================== CLIPBOARD OPERATIONS ====================

    def copy_to_clipboard(self, text: str) -> str:
        """Copy text to the system clipboard.
        
        Args:
            text: The text to copy to clipboard
            
        Returns:
            Success or error message
        """
        try:
            if not text:
                return "No text provided to copy."
            
            pyperclip.copy(text)
            return f"Copied to clipboard: {text}"
        except Exception as e:
            return f"Failed to copy to clipboard: {str(e)}"

    def read_clipboard(self) -> str:
        """Read the current clipboard contents.
        
        Returns:
            The clipboard text or an error message
        """
        try:
            content = pyperclip.paste()
            
            if not content:
                return "Clipboard is empty."
            
            # Limit output length for voice feedback
            if len(content) > 200:
                preview = content[:200] + "..."
                return f"Clipboard contains: {preview}"
            else:
                return f"Clipboard contains: {content}"
        except Exception as e:
            return f"Failed to read clipboard: {str(e)}"

    def clear_clipboard(self) -> str:
        """Clear the system clipboard.
        
        Returns:
            Success or error message
        """
        try:
            pyperclip.copy("")
            return "Clipboard cleared successfully."
        except Exception as e:
            return f"Failed to clear clipboard: {str(e)}"

    # ==================== SCREENSHOT OPERATIONS ====================

    def take_screenshot(self, filename: str = None) -> str:
        """Capture a screenshot of the entire screen.
        
        Args:
            filename: Optional custom filename (without extension).
                     If not provided, uses pronounceable date/time format.
                     
        Returns:
            Success message with file path or error message
        """
        try:
            # Capture the screenshot
            screenshot = ImageGrab.grab()
            
            # Generate filename
            if filename:
                # Remove any existing extension and add .png
                filename = filename.replace('.png', '').replace('.jpg', '').replace('.jpeg', '')
                screenshot_path = self.screenshot_dir / f"{filename}.png"
            else:
                # Use pronounceable date/time format
                now = datetime.now()
                
                # Month names
                months = ['january', 'february', 'march', 'april', 'may', 'june',
                         'july', 'august', 'september', 'october', 'november', 'december']
                month = months[now.month - 1]
                
                # Day with suffix
                day = now.day
                
                # Time period (morning, afternoon, evening, night)
                hour = now.hour
                if 5 <= hour < 12:
                    time_period = 'morning'
                elif 12 <= hour < 17:
                    time_period = 'afternoon'
                elif 17 <= hour < 21:
                    time_period = 'evening'
                else:
                    time_period = 'night'
                
                # Hour in 12-hour format for uniqueness
                hour_12 = hour % 12
                if hour_12 == 0:
                    hour_12 = 12
                
                # Convert hour to word
                hour_words = ['twelve', 'one', 'two', 'three', 'four', 'five', 'six',
                             'seven', 'eight', 'nine', 'ten', 'eleven']
                hour_word = hour_words[hour_12 - 1] if hour_12 <= 12 else str(hour_12)
                
                # Minute for uniqueness
                minute = now.minute
                
                # Build filename: screenshot_november_23_evening_at_7_45
                filename = f"screenshot_{month}_{day}_{time_period}_at_{hour_word}"
                if minute > 0:
                    filename += f"_{minute}"
                
                screenshot_path = self.screenshot_dir / f"{filename}.png"
            
            # Save the screenshot
            screenshot.save(screenshot_path, "PNG")
            
            return f"Screenshot saved to {screenshot_path}"
        except Exception as e:
            return f"Failed to take screenshot: {str(e)}"

    def set_screenshot_directory(self, directory_path: str) -> str:
        """Change the default screenshot save directory.
        
        Args:
            directory_path: Path to the new screenshot directory
            
        Returns:
            Success or error message
        """
        try:
            new_dir = Path(directory_path)
            new_dir.mkdir(parents=True, exist_ok=True)
            self.screenshot_dir = new_dir
            return f"Screenshot directory changed to {new_dir}"
        except Exception as e:
            return f"Failed to change screenshot directory: {str(e)}"


if __name__ == "__main__":
    # Simple test of the module
    handler = ClipboardScreenshot()
    
    print("Testing Clipboard and Screenshot Module...")
    print("=" * 60)
    
    # Test clipboard copy
    print("\n1. Testing clipboard copy:")
    print(handler.copy_to_clipboard("Hello from Aria!"))
    
    # Test clipboard read
    print("\n2. Testing clipboard read:")
    print(handler.read_clipboard())
    
    # Test screenshot
    print("\n3. Testing screenshot:")
    print(handler.take_screenshot("test_screenshot"))
    
    # Test clipboard clear
    print("\n4. Testing clipboard clear:")
    print(handler.clear_clipboard())
    
    # Verify clipboard is empty
    print("\n5. Verifying clipboard is empty:")
    print(handler.read_clipboard())
    
    print("\n" + "=" * 60)
    print("Test complete!")
