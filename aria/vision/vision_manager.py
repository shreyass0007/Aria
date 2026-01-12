import logging
import os
import sys
import platform
import shutil
from typing import Tuple, Optional, Dict
import difflib

import cv2
import numpy as np
import pytesseract
from PIL import Image
import pyautogui

logger = logging.getLogger(__name__)

# Try importing PaddleOCR (it might not be installed yet)
try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False
    logger.warning("PaddleOCR not installed. Falling back to Tesseract.")

class VisionManager:
    """
    Handles computer vision tasks for desktop automation:
    - Screen Capture
    - OCR (Text detection) - Uses PaddleOCR (default) or Tesseract (fallback)
    - Template Matching (Icon detection)
    """

    def __init__(self):
        self.use_paddle = PADDLE_AVAILABLE
        self.ocr_engine = None
        
        if self.use_paddle:
            self._setup_paddle()
        
        # Always setup Tesseract as fallback
        self._setup_tesseract()
        
    def _setup_paddle(self):
        """Initializes PaddleOCR engine."""
        try:
            # use_angle_cls=True for better accuracy used to be default
            # lang='en' for English
            logger.info("Initializing PaddleOCR... (this may take a moment)")
            # Suppress excessive Paddle logging
            logging.getLogger("ppocr").setLevel(logging.ERROR)
            
            self.ocr_engine = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
            logger.info("PaddleOCR initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to init PaddleOCR: {e}")
            self.use_paddle = False

    def _setup_tesseract(self):
        """Attempts to find and configure Tesseract executable."""
        # Check if tesseract is in PATH
        if shutil.which("tesseract"):
            return

        # Common Windows paths
        if platform.system() == "Windows":
            paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                os.path.join(os.getenv("LOCALAPPDATA", ""), r"Tesseract-OCR\tesseract.exe")
            ]
            
            for path in paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    logger.info(f"Tesseract found at: {path}")
                    return
            
            logger.warning("Tesseract-OCR not found. OCR features will fail if Paddle is also missing.")

    def capture_screen(self) -> Image.Image:
        """Captures the full screen and returns a PIL Image."""
        return pyautogui.screenshot()

    def find_text(self, text: str, exact_match: bool = False, fuzzy: bool = False) -> Optional[Tuple[int, int]]:
        """
        Finds the coordinates of the specified text on the screen.
        Returns (x, y) center coordinates or None.
        """
        if self.use_paddle and self.ocr_engine:
            return self._find_text_paddle(text, exact_match, fuzzy)
        else:
            return self._find_text_tesseract(text, exact_match, fuzzy)

    def _find_text_paddle(self, text: str, exact_match: bool = False, fuzzy: bool = False) -> Optional[Tuple[int, int]]:
        """Implementation using PaddleOCR."""
        screen = np.array(self.capture_screen())
        # Paddle expects BGR or RGB? usually handles it, but let's just pass array
        
        result = self.ocr_engine.ocr(screen, cls=True)
        
        target_text = text.lower()
        
        if not result or result[0] is None:
            logger.info(f"PaddleOCR found no text.")
            return None

        # Result structure: [ [ [ [x1,y1],[x2,y2],[x3,y3],[x4,y4] ], (text, confidence) ], ... ]
        for line in result[0]:
            box = line[0]
            txt_detect = line[1][0].lower()
            confidence = line[1][1]
            
            # Skip low confidence
            if confidence < 0.7:
                continue

            match = False
            if exact_match:
                match = txt_detect == target_text
            elif fuzzy:
                ratio = difflib.SequenceMatcher(None, target_text, txt_detect).ratio()
                match = ratio > 0.8
                if not match and (target_text in txt_detect):
                    match = True
            else:
                 match = target_text in txt_detect
            
            if match:
                # box is [ [x1,y1], [x2,y2], [x3,y3], [x4,y4] ]
                # Center X = (x1 + x2 + x3 + x4) / 4 ... or simpler: (min_x + max_x)//2
                xs = [pt[0] for pt in box]
                ys = [pt[1] for pt in box]
                
                center_x = int((min(xs) + max(xs)) / 2)
                center_y = int((min(ys) + max(ys)) / 2)
                
                logger.info(f"Text '{text}' found at ({center_x}, {center_y}) via PaddleOCR")
                return (center_x, center_y)
        
        logger.info(f"Text '{text}' not found (Paddle).")
        return None

    def _find_text_tesseract(self, text: str, exact_match: bool = False, fuzzy: bool = False) -> Optional[Tuple[int, int]]:
        """Legacy implementation using Tesseract."""
        screen = self.capture_screen()
        data = pytesseract.image_to_data(screen, output_type=pytesseract.Output.DICT)
        
        target_text = text.lower()
        
        n_boxes = len(data['text'])
        for i in range(n_boxes):
            detected_text = data['text'][i].lower()
            confidence = int(data['conf'][i])
            
            if confidence < 60:
                continue
                
            match = False
            if exact_match:
                match = detected_text == target_text
            elif fuzzy:
                ratio = difflib.SequenceMatcher(None, target_text, detected_text).ratio()
                match = ratio > 0.8
                if not match and len(detected_text) > 3 and target_text in detected_text:
                     match = True
            else:
                match = target_text in detected_text
            
            if match:
                (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                center_x = x + w // 2
                center_y = y + h // 2
                logger.info(f"Text '{text}' found at ({center_x}, {center_y}) via Tesseract")
                return (center_x, center_y)
        
        logger.info(f"Text '{text}' not found (Tesseract).")
        return None

    def find_template(self, template_path: str, threshold: float = 0.8) -> Optional[Tuple[int, int]]:
        """
        Finds a template image on the screen.
        Returns (x, y) center coordinates or None.
        """
        if not os.path.exists(template_path):
            logger.error(f"Template image not found: {template_path}")
            return None
            
        screen = np.array(self.capture_screen())
        screen_gray = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
        
        template = cv2.imread(template_path, 0)
        w, h = template.shape[::-1]
        
        res = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
    def capture_screen_base64(self) -> str:
        """Captures screen and returns base64 string."""
        import io
        import base64
        
        image = self.capture_screen()
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

