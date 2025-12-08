"""
Vision Pipeline Module
Orchestrates the screen understanding process.
"""

import cv2
import numpy as np
from typing import Dict, Any, Optional
from pathlib import Path
import time

from aria.vision.screen_capture import ScreenCapture
from aria.vision.detector import ObjectDetector
from aria.vision.ocr import TextRecognizer
from aria.vision.layout import LayoutAnalyzer

class VisionPipeline:
    """
    Main entry point for screen understanding.
    """
    
    def __init__(self, use_gpu: bool = False):
        """
        Initialize the vision pipeline.
        
        Args:
            use_gpu: Whether to use GPU for inference.
        """
        self.capture = ScreenCapture()
        self.detector = ObjectDetector() # Defaults to yolov8n.pt
        self.ocr = TextRecognizer(use_gpu=use_gpu)
        self.layout = LayoutAnalyzer()
        
        self.last_analysis = None
        self.debug_dir = Path("d:/CODEING/PROJECTS/ARIA/logs/vision_debug")
        self.debug_dir.mkdir(parents=True, exist_ok=True)

    def analyze_screen(self, save_debug: bool = False) -> Dict[str, Any]:
        """
        Capture and analyze the current screen.
        
        Args:
            save_debug: Whether to save an annotated image for debugging.
            
        Returns:
            Dictionary containing analysis results.
        """
        start_time = time.time()
        
        # 1. Capture
        image = self.capture.capture()
        if image is None:
            return {"error": "Failed to capture screen"}
            
        # 2. Detect Objects
        objects = self.detector.detect(image)
        
        # 3. Recognize Text
        texts = self.ocr.recognize(image)
        
        # 4. Analyze Layout
        result = self.layout.analyze(objects, texts)
        
        # Add metadata
        result["timestamp"] = time.time()
        result["latency"] = time.time() - start_time
        result["resolution"] = image.shape[:2] # h, w
        
        self.last_analysis = result
        
        if save_debug:
            self._save_debug_image(image, objects, texts)
            
        return result

    def _save_debug_image(self, image: np.ndarray, objects: list, texts: list):
        """Draw detections and save to debug folder."""
        debug_img = image.copy()
        
        # Draw objects (Blue)
        for obj in objects:
            x1, y1, x2, y2 = obj['box']
            cv2.rectangle(debug_img, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(debug_img, obj['label'], (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
        # Draw text (Green)
        for text in texts:
            box = np.array(text['box']).astype(int)
            cv2.polylines(debug_img, [box], True, (0, 255, 0), 2)
            # cv2.putText(debug_img, text['text'], (box[0][0], box[0][1] - 5), 
            #            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
        timestamp = int(time.time())
        cv2.imwrite(str(self.debug_dir / f"analysis_{timestamp}.png"), debug_img)
