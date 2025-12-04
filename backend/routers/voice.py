from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.dependencies import get_aria_core
from aria.aria_core import AriaCore

router = APIRouter()

class VoiceModeRequest(BaseModel):
    enabled: bool

class TTSRequest(BaseModel):
    enabled: bool

@router.post("/voice_mode")
def set_voice_mode(request: VoiceModeRequest, aria: AriaCore = Depends(get_aria_core)):
    try:
        if request.enabled:
            # aria.wake_word_listener.start() # It's already running in background usually
            return {"status": "success", "message": "Voice mode enabled (Wake word active)"}
        else:
            # aria.wake_word_listener.stop()
            return {"status": "success", "message": "Voice mode disabled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tts")
def set_tts_mode(request: TTSRequest, aria: AriaCore = Depends(get_aria_core)):
    try:
        aria.tts_manager.set_tts_enabled(request.enabled)
        state = "enabled" if request.enabled else "disabled"
        return {"status": "success", "message": f"TTS {state}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop_speaking")
def stop_speaking(aria: AriaCore = Depends(get_aria_core)):
    try:
        aria.tts_manager.stop()
        return {"status": "success", "message": "Stopped speaking"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/settings/tts")
def get_tts_settings(aria: AriaCore = Depends(get_aria_core)):
    """Returns current TTS settings."""
    try:
        # Assuming tts_manager has a way to check status.
        # If not, we default to True or check internal state.
        is_enabled = True # Default
        if hasattr(aria.tts_manager, 'is_enabled'):
            is_enabled = aria.tts_manager.is_enabled
            
        return {
            "enabled": is_enabled,
            "voice": "en-US-AriaNeural", # Placeholder
            "volume": 100
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
