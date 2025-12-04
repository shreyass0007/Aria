from fastapi import APIRouter, HTTPException, Depends
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.dependencies import get_system_monitor, get_aria_core
from aria.system_monitor import SystemMonitor
from aria.aria_core import AriaCore

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
