import vlc
import yt_dlp
import time
import threading
import os
import json
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
        
        # Queue Management
        self.queue = []
        self.current_index = -1
        
        # yt-dlp options for fastest audio extraction
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch5', # Get top 5 results
            'source_address': '0.0.0.0'
        }

        # Start background monitor
        self.monitor_thread = threading.Thread(target=self._monitor_playback, daemon=True)
        self.monitor_thread.start()

    def _monitor_playback(self):
        """Monitors playback status and auto-advances to next track."""
        while True:
            try:
                if self.is_playing_status:
                    state = self.player.get_state()
                    if state == vlc.State.Ended:
                        logger.info("Track ended, auto-advancing...")
                        self.next_track()
                        # Give it a moment to start playing effectively
                        time.sleep(2)
            except Exception as e:
                logger.error(f"Error in playback monitor: {e}")
            time.sleep(1)

    def _play_track(self, track_info):
        """Internal method to play a specific track info object."""
        try:
            url = track_info['url']
            title = track_info['title']
            
            self.current_track_info = track_info
            
            try:
                logger.info(f"Playing: {title}")
            except:
                pass
            
            # Stop current
            self.player.stop()
            
            media = self.instance.media_new(url)
            self.player.set_media(media)
            self.player.play()
            self.player.audio_set_volume(self.volume)
            
            # Update explicit state
            self.is_playing_status = True
            
            return f"Playing {title}"
        except Exception as e:
            logger.error(f"Error in _play_track: {e}")
            self.is_playing_status = False
            return f"Error playing track: {str(e)}"

    def _extract_metadata(self, video):
        """Robustly extracts title and artist from video data."""
        raw_title = video.get('title', "Unknown Track")
        try:
            raw_title = raw_title.encode('ascii', 'ignore').decode('ascii')
        except:
            pass
            
        artist = video.get('artist') or video.get('uploader') or video.get('creator') or video.get('channel')
        title = video.get('track') or raw_title

        # If artist is missing or generic, try parsing from title "Artist - Title"
        if not artist or "unknown" in str(artist).lower() or not title or title == raw_title:
            # Common separators: " - ", " – ", " : ", " | "
            separators = [" - ", " – ", ": ", "|"]
            for sep in separators:
                if sep in raw_title:
                    parts = raw_title.split(sep, 1)
                    parsed_artist = parts[0].strip()
                    parsed_title = parts[1].strip()
                    
                    # Heuristics: Artist usually isn't massive logic, but this helps
                    if not artist or "unknown" in str(artist).lower():
                        artist = parsed_artist
                    title = parsed_title
                    break
        
        # Clean up typical YouTube junk from title
        junk_terms = ["(Official Video)", "(Official Audio)", "[Official Video]", "(Lyrics)", "(Lyric Video)", "ft.", "feat."]
        if title:
            for term in junk_terms:
                if term in title:
                    title = title.replace(term, "").strip()
                if term.lower() in title.lower(): # Case insensitive check
                     title = title.replace(term, "").strip() # This might miss case, but simple enough logic
        
        return {
            'title': title or raw_title,
            'artist': artist or "Unknown Artist",
            'url': video.get('url'),
            'duration': video.get('duration'),
            'original_title': raw_title # Keep original for search contexts if needed
        }

    def load_playlist(self):
        """Loads the user's playlist from JSON."""
        playlist_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'data', 'my_playlist.json')
        if not os.path.exists(playlist_path):
            return []
        try:
            with open(playlist_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading playlist: {e}")
            return []

    def add_to_playlist(self, track_info=None):
        """Adds current or specified track to playlist."""
        track_to_add = track_info or self.current_track_info
        if not track_to_add or not track_to_add.get('url'):
            return "No track to add."
            
        playlist_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'data', 'my_playlist.json')
        
        try:
            # Ensure dir exists
            os.makedirs(os.path.dirname(playlist_path), exist_ok=True)
            
            existing = self.load_playlist()
            
            # Check for duplicates
            if any(t['url'] == track_to_add['url'] for t in existing):
                return "Track already in playlist."
                
            existing.append(track_to_add)
            
            with open(playlist_path, 'w') as f:
                json.dump(existing, f, indent=4)
                
            return f"Added '{track_to_add.get('title')}' to your playlist."
        except Exception as e:
            logger.error(f"Error saving playlist: {e}")
            return f"Error adding to playlist: {str(e)}"

    def _fetch_related_tracks(self, original_video):
        """Background task to fetch related tracks based on artist and style."""
        try:
            # Use our robust extraction
            meta = self._extract_metadata(original_video)
            artist = meta['artist']
            title = meta['title']
            original_id = original_video.get('id')
            
            if not artist or artist == "Unknown Artist":
                logger.warning(f"Could not determine artist for related tracks. Meta: {meta}")
                return

            logger.info(f"Fetching related tracks for: {title} by {artist}")
            
            new_tracks = []
            seen_urls = set()
            for q in self.queue:
                seen_urls.add(q['url'])

            def process_entries(entries, query_desc):
                for video in entries:
                    if not video: continue
                    if video.get('id') == original_id: continue
                    
                    # Extract nice metadata for the queue item too
                    vid_meta = self._extract_metadata(video)
                    
                    if vid_meta['url'] in seen_urls: continue
                    
                    # Ensure we have the query context
                    vid_meta['query'] = query_desc
                    
                    new_tracks.append(vid_meta)
                    seen_urls.add(vid_meta['url'])

            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # 1. Search for similar vibe/type
                type_query = f"songs like {title} {artist}"
                info_type = ydl.extract_info(f"ytsearch5:{type_query}", download=False)
                if 'entries' in info_type:
                    process_entries(info_type['entries'], "Similar Style")
                    
                # 2. Search for artist
                artist_query = f"{artist} official audio"
                info_artist = ydl.extract_info(f"ytsearch5:{artist_query}", download=False)
                if 'entries' in info_artist:
                     process_entries(info_artist['entries'], "Artist Mix")

            self.queue.extend(new_tracks)
            logger.info(f"Added {len(new_tracks)} tracks to queue.")
                
        except Exception as e:
            logger.error(f"Error fetching related tracks: {e}")

    def play_music(self, query: str):
        """Searches for a song on YouTube, plays it immediately, and fetches related tracks in background."""
        try:
            # Special Handling for "My Playlist"
            if query.lower() in ["my playlist", "my songs", "playlist"]:
                tracks = self.load_playlist()
                if not tracks:
                    return "Your playlist is empty. You can add songs to it!"
                
                self.queue = tracks
                self.current_index = 0
                
                # Play first track
                first = self.queue[0]
                result = self._play_track(first)
                
                # IMPORTANT: We do NOT start the related tracks thread here
                # because the user wants ONLY this playlist.
                
                return f"Playing your playlist ({len(tracks)} songs)."

            logger.info(f"Searching for: {query}")
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{query}", download=False)
                
                entries = []
                if 'entries' in info:
                    entries = list(info['entries'])
                else:
                    entries = [info]

                if not entries:
                    return "No results found."

                video = entries[0]
                
                # Use robust metadata extraction
                track_info = self._extract_metadata(video)
                track_info['query'] = query
                
                # Reset Queue with this single track first
                self.queue = [track_info]
                self.current_index = 0
                
                # Play immediately
                play_result = self._play_track(track_info)
                
                # Fetch related tracks in background
                threading.Thread(target=self._fetch_related_tracks, args=(video,), daemon=True).start()
                
                return f"{play_result} (loading smart queue...)"
                
        except Exception as e:
            logger.error(f"Error searching music: {e}")
            self.is_playing_status = False
            return f"Sorry, I couldn't find that. Error: {str(e)}"

    def next_track(self):
        """Plays the next track in the queue."""
        if self.current_index < len(self.queue) - 1:
            self.current_index += 1
            return self._play_track(self.queue[self.current_index])
        return "End of playlist."

    def previous_track(self):
        """Plays the previous track in the queue."""
        if self.current_index > 0:
            self.current_index -= 1
            return self._play_track(self.queue[self.current_index])
        # If at start, restart song
        if self.current_index == 0 and self.queue:
             return self._play_track(self.queue[0])
        return "No previous track."

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
            'artist': self.current_track_info.get('artist', "Unknown Artist"),
            'duration': self.current_track_info.get('duration', 0),
            'current_time': self.player.get_time() / 1000.0 if self.player.get_time() >= 0 else 0
        }

    def get_current_track(self):
        """Returns info about the current track."""
        if self.is_playing_status:
            return self.current_track_info.get('title', "Unknown Track")
        return "Nothing is playing."
