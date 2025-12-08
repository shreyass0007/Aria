"""
Screen Capture Module
Handles capturing the screen content efficiently using mss.
"""

import mss
import numpy as np
import cv2
from typing import Optional, Tuple, Dict, Any

class ScreenCapture:
    """
    Captures screen content for analysis.
    Uses mss for high-performance capture.
    """
    
    def __init__(self):
        self.monitor_index = 1 # Primary monitor by default

    def capture(self, region: Optional[Dict[str, int]] = None) -> np.ndarray:
        """
        Capture the screen or a specific region.
        
        Args:
            region: Optional dictionary with 'top', 'left', 'width', 'height'.
                    If None, captures the full primary monitor.
                    
        Returns:
            numpy.ndarray: The captured image in BGR format (ready for OpenCV/YOLO).
        """
        try:
            with mss.mss() as sct:
                if region:
                    # mss requires specific keys
                    monitor = region
                else:
                    if self.monitor_index < len(sct.monitors):
                        monitor = sct.monitors[self.monitor_index]
                    else:
                        monitor = sct.monitors[1] # Fallback to 1st monitor (0 is all)

                # Capture
                screenshot = sct.grab(monitor)
                
                # Convert to numpy array
                img = np.array(screenshot)
                
                # mss returns BGRA, convert to BGR for compatibility
                img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
                return img_bgr
            
        except Exception as e:
            print(f"Error capturing screen: {e}")
            return None

    def get_monitors(self):
        """Return list of available monitors."""
        with mss.mss() as sct:
            return sct.monitors
