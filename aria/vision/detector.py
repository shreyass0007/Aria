"""
Object Detection Module
Uses YOLOv8 to detect objects on the screen.
"""

import os
from ultralytics import YOLO
import numpy as np
from typing import List, Dict, Any

class ObjectDetector:
    """
    Detects objects in images using YOLO models.
    """
    
    def __init__(self, model_path: str = "yolov8n.pt"):
        """
        Initialize the detector.
        
        Args:
            model_path: Path to the YOLO model file. 
                        Defaults to 'yolov8n.pt' (nano) for speed.
                        Downloads automatically if not found.
        """
        # Ensure we use the D drive for models if possible, or just let ultralytics handle it.
        # We can set the working directory for downloads if needed, but default is usually fine.
        self.model = YOLO(model_path)
        
        # Warmup
        # self.model.info() 

    def detect(self, image: np.ndarray, conf_threshold: float = 0.25) -> List[Dict[str, Any]]:
        """
        Run detection on an image.
        
        Args:
            image: BGR numpy array (from cv2/mss).
            conf_threshold: Confidence threshold for detections.
            
        Returns:
            List of dictionaries containing detection results:
            [{'box': [x1, y1, x2, y2], 'class': 'person', 'conf': 0.95}, ...]
        """
        try:
            results = self.model(image, conf=conf_threshold, verbose=False)
            
            detections = []
            for result in results:
                boxes = result.boxes.cpu().numpy()
                for box in boxes:
                    r = box.xyxy[0].astype(int).tolist() # x1, y1, x2, y2
                    cls_id = int(box.cls[0])
                    cls_name = result.names[cls_id]
                    conf = float(box.conf[0])
                    
                    detections.append({
                        "box": r,
                        "class": cls_name,
                        "conf": conf,
                        "label": f"{cls_name} {conf:.2f}"
                    })
            
            return detections
            
        except Exception as e:
            print(f"Error during object detection: {e}")
            return []
