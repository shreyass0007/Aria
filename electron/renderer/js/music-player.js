/**
 * Music Player Module
 * Handles music playback UI and controls
 */

class MusicPlayer {
    constructor() {
        this.isPlaying = false;
        this.currentTrack = null;
        this.volume = 70;
        this.currentTime = 0;
        this.duration = 0;
        this.updateInterval = null;
        this.statusInterval = null;

        this.initElements();
        this.attachEventListeners();
    }

    initElements() {
        // Main containers
        this.fab = document.getElementById('musicFab');
        this.player = document.getElementById('musicPlayer');
        this.header = document.getElementById('musicPlayerHeader');
        this.closeBtn = document.getElementById('musicPlayerClose');
        this.expandBtn = document.getElementById('musicPlayerExpand');
        this.compactInfo = document.getElementById('compactTrackInfo');

        // Track info
        this.albumArt = document.getElementById('albumArt');
        this.trackTitle = document.getElementById('trackTitle');
        this.trackArtist = document.getElementById('trackArtist');

        // Progress
        this.progressBar = document.getElementById('progressBar');
        this.progressFill = document.getElementById('progressFill');
        this.currentTimeLabel = document.getElementById('currentTime');
        this.totalTimeLabel = document.getElementById('totalTime');

        // Controls
        this.playPauseBtn = document.getElementById('playPauseBtn');
        this.playIcon = document.getElementById('playIcon');
        this.pauseIcon = document.getElementById('pauseIcon');
        this.prevBtn = document.getElementById('prevBtn');
        this.nextBtn = document.getElementById('nextBtn');

        // Volume
        this.volumeSlider = document.getElementById('volumeSlider');
        this.volumeFill = document.getElementById('volumeFill');

        // Drag state
        this.isDragging = false;
        this.dragOffset = { x: 0, y: 0 };
        this.isExpanded = false;

        // FAB drag state
        this.isDraggingFab = false;
        this.fabDragOffset = { x: 0, y: 0 };
        this.wasDraggingFab = false;
    }

    attachEventListeners() {
        // FAB click - show player (only if not dragging)
        this.fab?.addEventListener('click', (e) => {
            if (!this.wasDraggingFab) {
                this.show();
            }
            this.wasDraggingFab = false;
        });

        // FAB drag functionality
        this.fab?.addEventListener('mousedown', (e) => this.startFabDrag(e));
        document.addEventListener('mousemove', (e) => {
            if (this.isDraggingFab) {
                this.dragFab(e);
            } else if (this.isDragging) {
                this.drag(e);
            }
        });
        document.addEventListener('mouseup', () => {
            this.stopFabDrag();
            this.stopDrag();
        });

        // Close button - hide player
        this.closeBtn?.addEventListener('click', () => this.hide());

        // Expand/Collapse button
        this.expandBtn?.addEventListener('click', () => this.toggleExpand());

        // Player header drag functionality
        this.header?.addEventListener('mousedown', (e) => this.startDrag(e));

        // Play/Pause
        this.playPauseBtn?.addEventListener('click', () => this.togglePlayPause());

        // Previous/Next
        this.prevBtn?.addEventListener('click', () => this.previous());
        this.nextBtn?.addEventListener('click', () => this.next());

        // Progress bar click
        this.progressBar?.addEventListener('click', (e) => this.seek(e));

        // Volume control
        this.volumeSlider?.addEventListener('click', (e) => this.setVolume(e));

        // Listen for music events from backend
        window.addEventListener('music-track-changed', (e) => this.onTrackChanged(e.detail));
        window.addEventListener('music-state-changed', (e) => this.onStateChanged(e.detail));
    }

    toggleExpand() {
        this.isExpanded = !this.isExpanded;
        if (this.isExpanded) {
            this.player.classList.remove('minimized');
            this.player.classList.add('expanded');
        } else {
            this.player.classList.remove('expanded');
            this.player.classList.add('minimized');
        }
    }

    // FAB Drag methods
    startFabDrag(e) {
        this.isDraggingFab = true;
        this.wasDraggingFab = false;
        const rect = this.fab.getBoundingClientRect();
        this.fabDragOffset = {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
        this.fab.style.transition = 'none';
        e.stopPropagation();
    }

    dragFab(e) {
        if (!this.isDraggingFab) return;

        this.wasDraggingFab = true;
        const x = e.clientX - this.fabDragOffset.x;
        const y = e.clientY - this.fabDragOffset.y;

        // Keep FAB within viewport
        const maxX = window.innerWidth - this.fab.offsetWidth;
        const maxY = window.innerHeight - this.fab.offsetHeight;

        const boundedX = Math.max(0, Math.min(x, maxX));
        const boundedY = Math.max(0, Math.min(y, maxY));

        this.fab.style.left = `${boundedX}px`;
        this.fab.style.top = `${boundedY}px`;
        this.fab.style.right = 'auto';
        this.fab.style.bottom = 'auto';
    }

    stopFabDrag() {
        if (this.isDraggingFab) {
            this.isDraggingFab = false;
            this.fab.style.transition = '';
        }
    }

    // Player Drag methods
    startDrag(e) {
        if (e.target.closest('.music-player-expand') || e.target.closest('.music-player-close')) {
            return; // Don't drag if clicking buttons
        }
        this.isDragging = true;
        const rect = this.player.getBoundingClientRect();
        this.dragOffset = {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
        this.player.style.transition = 'none';
    }

    drag(e) {
        if (!this.isDragging) return;

        const x = e.clientX - this.dragOffset.x;
        const y = e.clientY - this.dragOffset.y;

        // Keep player within viewport
        const maxX = window.innerWidth - this.player.offsetWidth;
        const maxY = window.innerHeight - this.player.offsetHeight;

        const boundedX = Math.max(0, Math.min(x, maxX));
        const boundedY = Math.max(0, Math.min(y, maxY));

        this.player.style.left = `${boundedX}px`;
        this.player.style.top = `${boundedY}px`;
        this.player.style.right = 'auto';
        this.player.style.bottom = 'auto';
    }

    stopDrag() {
        if (this.isDragging) {
            this.isDragging = false;
            this.player.style.transition = '';
        }
    }

    show() {
        this.player?.classList.add('visible');
        this.fab?.classList.add('hidden');
    }

    hide() {
        this.player?.classList.remove('visible');
        this.fab?.classList.remove('hidden');
        this.stopProgressTracking();
    }

    async togglePlayPause() {
        if (this.isPlaying) {
            await this.pause();
        } else {
            await this.resume();
        }
    }

    async pause() {
        try {
            console.log('[Music Player] Pause clicked, current state:', this.isPlaying);
            const response = await fetch('http://localhost:5000/music/pause', {
                method: 'POST'
            });
            if (response.ok) {
                const data = await response.json();
                console.log('[Music Player] Pause response:', data);
                // Use the actual state from backend
                this.updatePlayingState(data.is_playing || false);
            }
        } catch (error) {
            console.error('Error pausing music:', error);
        }
    }

    async resume() {
        try {
            console.log('[Music Player] Resume clicked, current state:', this.isPlaying);
            const response = await fetch('http://localhost:5000/music/resume', {
                method: 'POST'
            });
            if (response.ok) {
                const data = await response.json();
                console.log('[Music Player] Resume response:', data);
                // Use the actual state from backend
                this.updatePlayingState(data.is_playing || false);
            }
        } catch (error) {
            console.error('Error resuming music:', error);
        }
    }

    async previous() {
        console.log('Previous track requested');
    }

    async next() {
        console.log('Next track requested');
    }

    seek(event) {
        if (!this.duration) return;

        const rect = this.progressBar.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const percentage = x / rect.width;
        const seekTime = percentage * this.duration;

        console.log('Seeking to:', seekTime);
    }

    async setVolume(event) {
        const rect = this.volumeSlider.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const percentage = Math.max(0, Math.min(1, x / rect.width));
        const volume = Math.round(percentage * 100);

        try {
            const response = await fetch('http://localhost:5000/music/volume', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ volume })
            });

            if (response.ok) {
                this.updateVolume(volume);
            }
        } catch (error) {
            console.error('Error setting volume:', error);
        }
    }

    updateVolume(volume) {
        this.volumeFill.style.width = `${volume}%`;
    }

    updatePlayingState(isPlaying) {
        console.log('[Music Player] updatePlayingState called with:', isPlaying, 'current:', this.isPlaying);
        this.isPlaying = isPlaying;

        if (isPlaying) {
            this.playIcon.style.display = 'none';
            this.pauseIcon.style.display = 'block';
            this.albumArt?.classList.add('playing');
            this.fab?.classList.add('playing');
            console.log('[Music Player] UI set to PLAYING state');
        } else {
            this.playIcon.style.display = 'block';
            this.pauseIcon.style.display = 'none';
            this.albumArt?.classList.remove('playing');
            this.fab?.classList.remove('playing');
            console.log('[Music Player] UI set to PAUSED state');
        }
    }

    updateProgress(currentTime) {
        if (!this.duration) return;

        const percentage = (currentTime / this.duration) * 100;
        this.progressFill.style.width = `${percentage}%`;
        this.currentTimeLabel.textContent = this.formatTime(currentTime);
    }

    formatTime(seconds) {
        if (!seconds || isNaN(seconds)) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    startProgressTracking() {
        if (this.statusInterval) {
            clearInterval(this.statusInterval);
        }

        this.statusInterval = setInterval(async () => {
            if (!this.isPlaying) return;

            try {
                const response = await fetch('http://localhost:5000/music/status');
                if (response.ok) {
                    const status = await response.json();
                    if (status.current_time) {
                        this.updateProgress(status.current_time);
                    }
                    if (status.is_playing !== undefined) {
                        this.updatePlayingState(status.is_playing);
                    }
                }
            } catch (error) {
                console.error('Error fetching music status:', error);
            }
        }, 2000);
    }

    stopProgressTracking() {
        if (this.statusInterval) {
            clearInterval(this.statusInterval);
            this.statusInterval = null;
        }
    }

    onTrackChanged(trackInfo) {
        this.currentTrack = trackInfo;
        this.duration = trackInfo.duration || 0;

        const title = trackInfo.title || 'Unknown Track';
        const artist = trackInfo.artist || 'Unknown Artist';

        this.trackTitle.textContent = title;
        this.trackArtist.textContent = artist;
        this.compactInfo.textContent = `${title} - ${artist}`;
        this.totalTimeLabel.textContent = this.formatTime(this.duration);

        this.show();
        if (!this.isExpanded) {
            this.player.classList.add('minimized');
        }

        this.updatePlayingState(true);
        this.startProgressTracking();
    }

    onStateChanged(state) {
        this.updatePlayingState(state.isPlaying);
        if (state.currentTime !== undefined) {
            this.updateProgress(state.currentTime);
        }
    }
}

// Initialize music player when DOM is ready
let musicPlayerInstance = null;

function initMusicPlayer() {
    if (!musicPlayerInstance) {
        musicPlayerInstance = new MusicPlayer();
        window.musicPlayer = musicPlayerInstance;
        console.log('Music player initialized');
    }
    return musicPlayerInstance;
}

export { MusicPlayer, initMusicPlayer };
