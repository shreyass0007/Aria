"""
OCR Module
Uses PaddleOCR to extract text from screen images.
"""

import logging
import numpy as np
from typing import List, Dict, Any

# Suppress PaddleOCR logging
logging.getLogger("ppocr").setLevel(logging.ERROR)

try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None
    print("PaddleOCR not installed or failed to import.")

class TextRecognizer:
    """
    Recognizes text in images using PaddleOCR.
    """
    
    def __init__(self, lang: str = 'en', use_gpu: bool = False):
        """
        Initialize the OCR engine.
        
        Args:
            lang: Language code (default 'en').
            use_gpu: Whether to use GPU acceleration.
        """
        if PaddleOCR:
            self.ocr = PaddleOCR(use_angle_cls=True, lang=lang, use_gpu=use_gpu, show_log=False)
        else:
            self.ocr = None

    def recognize(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Run OCR on an image.
        
        Args:
            image: BGR numpy array.
            
        Returns:
            List of dictionaries containing OCR results:
            [{'box': [[x1,y1], [x2,y1], [x2,y2], [x1,y2]], 'text': 'File', 'conf': 0.99}, ...]
        """
        if not self.ocr:
            return []

        try:
            # PaddleOCR expects the image path or numpy array
            result = self.ocr.ocr(image, cls=True)
            
            detections = []
            if not result or result[0] is None:
                return []

            for line in result[0]:
                # line structure: [box, (text, score)]
                # box: [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
                box = line[0]
                text, score = line[1]
                
                # Convert box points to int
                box = [[int(p[0]), int(p[1])] for p in box]
                
                detections.append({
                    "box": box,
                    "text": text,
                    "conf": score
                })
                
            return detections
            
        except Exception as e:
            print(f"Error during OCR: {e}")
            return []
