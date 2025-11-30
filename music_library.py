import vlc
import yt_dlp
import time
import threading
import os

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
        
        # yt-dlp options for fastest audio extraction
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch',
            'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
        }

    def play_music(self, query: str):
        """
        Searches for a song on YouTube and plays it.
        """
        try:
            print(f"Searching for: {query}")
            
            # Run search in a separate thread to avoid blocking
            # But for now, we'll do it synchronously to ensure we get the URL before returning
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)
                
                if 'entries' in info and len(info['entries']) > 0:
                    video = info['entries'][0]
                else:
                    video = info

                url = video['url']
                title = video['title']
                # Sanitize title to avoid Unicode errors on Windows
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
                
                # Safe print for Windows consoles
                try:
                    print(f"Playing: {title}")
                except UnicodeEncodeError:
                    print(f"Playing: {title.encode('utf-8', errors='ignore').decode('utf-8')}")
                
                # Stop current playback
                self.stop()
                
                # Create media and play
                media = self.instance.media_new(url)
                self.player.set_media(media)
                self.player.play()
                
                # Restore volume
                self.player.audio_set_volume(self.volume)
                
                return f"Playing {title}"
                
        except Exception as e:
            print(f"Error playing music: {e}")
            return f"Sorry, I couldn't play that. Error: {str(e)}"

    def pause(self):
        """Pauses playback."""
        if self.player.is_playing():
            self.player.pause()
            return "Music paused."
        return "Nothing is playing."

    def resume(self):
        """Resumes playback."""
        # VLC pause is a toggle, but we can check state
        state = self.player.get_state()
        if state == vlc.State.Paused:
            self.player.pause() # Toggle back to play
            return "Resuming music."
        elif state == vlc.State.Stopped:
            return "Music was stopped. You need to play something new."
        return "Music is already playing."

    def stop(self):
        """Stops playback."""
        self.player.stop()
        return "Music stopped."

    def set_volume(self, level: int):
        """Sets volume (0-100)."""
        self.volume = max(0, min(100, level))
        if self.player:
            self.player.audio_set_volume(self.volume)
        return f"Music volume set to {self.volume}."

    def get_current_track(self):
        """Returns info about the current track."""
        if self.player.is_playing() or self.player.get_state() == vlc.State.Paused:
            return self.current_track_info.get('title', "Unknown Track")
        return "Nothing is playing."
