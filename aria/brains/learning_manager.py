import json
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class LearningManager:
    """
    Manages the storage and retrieval of successful automation plans.
    Acts as Aria's "Muscle Memory" for desktop tasks.
    """
    def __init__(self, storage_path: str = None):
        if storage_path:
            self.storage_path = storage_path
        else:
            # Default to backend/data/successful_patterns.json
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_dir = os.path.join(base_dir, "backend", "data")
            os.makedirs(data_dir, exist_ok=True)
            self.storage_path = os.path.join(data_dir, "successful_patterns.json")
            
        self.patterns = self._load_patterns()
        logger.info(f"LearningManager initialized. Memory file: {self.storage_path}")

    def _load_patterns(self) -> Dict[str, Any]:
        """Loads patterns from disk."""
        if not os.path.exists(self.storage_path):
            return {}
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load patterns: {e}")
            return {}

    def _save_patterns(self):
        """Saves patterns to disk."""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.patterns, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save patterns: {e}")

    def get_proven_plan(self, user_request: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a proven plan for the given request.
        Uses exact match on lowercased request for now.
        """
        key = user_request.lower().strip()
        if key in self.patterns:
            logger.info(f"Recall: Found proven plan for '{key}'")
            return self.patterns[key]
        return None

    def save_successful_plan(self, user_request: str, plan: Dict[str, Any]):
        """
        Saves a plan as successful for a given request.
        """
        key = user_request.lower().strip()
        
        # Don't memorize simple failures or empty plans
        if not plan.get("actions"):
            return

        self.patterns[key] = plan
        self._save_patterns()
        logger.info(f"Learned: Saved new pattern for '{key}'")
