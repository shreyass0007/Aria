from fastapi import APIRouter, HTTPException, Depends
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.dependencies import get_system_monitor, get_aria_core
from aria.system_monitor import SystemMonitor
from aria.aria_core import AriaCore
from aria.logger import setup_logger
import traceback

logger = setup_logger(__name__)

router = APIRouter()

@router.get("/system/health")
def get_system_health(monitor: SystemMonitor = Depends(get_system_monitor)):
    try:
        battery = monitor.get_battery_status()
        cpu = monitor.get_cpu_usage()
        return {
            "battery": battery,
            "cpu": cpu,
            "status": "healthy" # Simplified
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/features")
def get_features_status(aria: AriaCore = Depends(get_aria_core)):
    return {
        "calendar": aria.calendar.service is not None,
        "gmail": aria.email.service is not None,
        "notion": aria.notion.client is not None,
        "memory": True, # Assuming memory is always on if initialized
        "voice": True
    }

@router.post("/system/vision/analyze")
def analyze_screen(save_debug: bool = False, aria: AriaCore = Depends(get_aria_core)):
    """Trigger screen analysis."""
    try:
        result = aria.analyze_screen(save_debug=save_debug)
        return result
    except Exception as e:
        logger.error(f"Error in analyze_screen: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
