from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.dependencies import get_music_manager
from aria.music_library import MusicManager

router = APIRouter()

class MusicVolumeRequest(BaseModel):
    volume: int

class MusicControlRequest(BaseModel):
    action: str # play, pause, resume, stop, next, volume
    query: Optional[str] = None
    volume: Optional[int] = None

@router.post("/music/pause")
def pause_music(music_manager: MusicManager = Depends(get_music_manager)):
    return music_manager.pause()

@router.post("/music/resume")
def resume_music(music_manager: MusicManager = Depends(get_music_manager)):
    return music_manager.resume()

@router.post("/music/next")
def next_track(music_manager: MusicManager = Depends(get_music_manager)):
    result = music_manager.next_track()
    return {"status": "success", "message": result}

@router.post("/music/previous")
def previous_track(music_manager: MusicManager = Depends(get_music_manager)):
    result = music_manager.previous_track()
    return {"status": "success", "message": result}

@router.post("/music/volume")
def set_music_volume(request: MusicVolumeRequest, music_manager: MusicManager = Depends(get_music_manager)):
    return {"status": "success", "message": music_manager.set_volume(request.volume)}

@router.post("/music")
def control_music(request: MusicControlRequest, music_manager: MusicManager = Depends(get_music_manager)):
    try:
        action = request.action.lower()
        
        if action == "play":
            if not request.query:
                # If no query, try to resume
                return music_manager.resume()
            return {"status": "success", "message": music_manager.play_music(request.query)}
            
        elif action == "pause":
            return music_manager.pause()
            
        elif action == "resume":
            return music_manager.resume()
            
        elif action == "stop":
            return {"status": "success", "message": music_manager.stop()}
            
        elif action == "volume":
            if request.volume is None:
                raise HTTPException(status_code=400, detail="Volume level required")
            return {"status": "success", "message": music_manager.set_volume(request.volume)}
        
        elif action == "next":
             return {"status": "success", "message": music_manager.next_track()}
             
        elif action == "previous":
             return {"status": "success", "message": music_manager.previous_track()}
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
            
    except Exception as e:
        print(f"Music Control Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/music/status")
def get_music_status(music_manager: MusicManager = Depends(get_music_manager)):
    try:
        return music_manager.get_status()
    except Exception as e:
        print(f"Music Status Error: {e}")
        return {"is_playing": False, "track": "Error", "error": str(e)}
