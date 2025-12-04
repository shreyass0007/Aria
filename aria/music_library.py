import vlc
import yt_dlp
import time
import threading
import os
from .logger import setup_logger

logger = setup_logger(__name__)

class MusicManager:
    """
    Manages music playback using yt-dlp for sourcing and VLC for playback.
    Allows headless streaming of YouTube audio.
    """
    def __init__(self):
        self.instance = vlc.Instance('--no-video')
        self.player = self.instance.media_player_new()
        self.current_track_info = {}
        self.volume = 70
        self.player.audio_set_volume(self.volume)
        # Explicit state tracking to handle VLC flakiness
        self.is_playing_status = False 
        
        # yt-dlp options for fastest audio extraction
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch',
            'source_address': '0.0.0.0'
        }

    def play_music(self, query: str):
        """Searches for a song on YouTube and plays it."""
        try:
            logger.info(f"Searching for: {query}")
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)
                if 'entries' in info and len(info['entries']) > 0:
                    video = info['entries'][0]
                else:
                    video = info

                url = video['url']
                title = video['title']
                try:
                    title = title.encode('ascii', 'ignore').decode('ascii')
                except:
                    title = "Unknown Track"
                
                duration = video.get('duration')
                self.current_track_info = {
                    'title': title,
                    'url': url,
                    'duration': duration
                }
                
                try:
                    logger.info(f"Playing: {title}")
                except:
                    pass
                
                self.stop()
                
                media = self.instance.media_new(url)
                self.player.set_media(media)
                self.player.play()
                self.player.audio_set_volume(self.volume)
                
                # Update explicit state
                self.is_playing_status = True
                
                return f"Playing {title}"
                
        except Exception as e:
            logger.error(f"Error playing music: {e}")
            self.is_playing_status = False
            return f"Sorry, I couldn't play that. Error: {str(e)}"

    def pause(self):
        """Pauses playback."""
        try:
            self.player.set_pause(1)
            self.is_playing_status = False
            return {"success": True, "message": "Music paused.", "is_playing": False}
        except Exception as e:
            return {"success": False, "message": f"Error pausing: {str(e)}", "is_playing": False}

    def resume(self):
        """Resumes playback."""
        try:
            state = self.player.get_state()
            if state in [vlc.State.Stopped, vlc.State.Ended, vlc.State.Error]:
                 self.player.play()
            else:
                self.player.set_pause(0)
            
            self.is_playing_status = True
            return {"success": True, "message": "Resuming music.", "is_playing": True}
        except Exception as e:
            return {"success": False, "message": f"Error resuming: {str(e)}", "is_playing": False}

    def stop(self):
        """Stops playback."""
        self.player.stop()
        self.is_playing_status = False
        return "Music stopped."

    def set_volume(self, level: int):
        """Sets volume (0-100)."""
        self.volume = max(0, min(100, level))
        if self.player:
            self.player.audio_set_volume(self.volume)
        return f"Music volume set to {self.volume}."

    def get_status(self):
        """Returns the current status including reliable playing state."""
        # Trust our explicit state if VLC is being weird (NothingSpecial), 
        # but if VLC explicitly says Stopped/Ended/Error, trust VLC.
        vlc_state = self.player.get_state()
        
        if vlc_state in [vlc.State.Stopped, vlc.State.Ended, vlc.State.Error]:
            self.is_playing_status = False
            
        return {
            'is_playing': self.is_playing_status,
            'track': self.current_track_info.get('title', "Unknown Track"),
            'duration': self.current_track_info.get('duration', 0),
            'current_time': self.player.get_time() / 1000.0 if self.player.get_time() >= 0 else 0
        }

    def get_current_track(self):
        """Returns info about the current track."""
        if self.is_playing_status:
            return self.current_track_info.get('title', "Unknown Track")
        return "Nothing is playing."
