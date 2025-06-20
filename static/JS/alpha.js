class SignLingoPlayer {
    constructor() {
        this.currentVideoIndex = 0;
        this.isLocalVideo = false;
        this.videoPlayer = null;
        this.localVideoElement = null;
        this.initializeApp();
    }

    // Set to true to use local videos
    config = {
        useLocalVideos: true,
        autoplay: false,
        enableKeyboardShortcuts: true
    };

    // Replace VIDEO_ID_* with actual YouTube IDs if needed
    videoData = [
        { id: 'A', title: ' A', duration: '0:15', thumbnail: '/static/letter_images/a.jpg', localPath: '/static/alpha_videos/a.mp4', completed: true },
        { id: 'B', title: 'B ', duration: '0:09', thumbnail: '/static/letter_images/b.jpg', localPath: '/static/alpha_videos/b.mp4', completed: true },
        { id: 'C', title: 'C ', duration: '0:9', thumbnail: '/static/letter_images/c.jpg', localPath: '/static/alpha_videos/c.mp4', completed: true },
        { id: 'D', title: 'D ', duration: '0:12', thumbnail: '/static/letter_images/d.jpg', localPath: '/static/alpha_videos/d.mp4', completed: true },
        { id: 'E', title: 'E ', duration: '0:11', thumbnail: '/static/letter_images/e.jpg', localPath: '/static/alpha_videos/e.mp4', completed: true },
        { id: 'F', title: 'F ', duration: '0:12', thumbnail: '/static/letter_images/f.jpg', localPath: '/static/alpha_videos/f.mp4', completed: true },
        { id: 'G', title: 'G ', duration: '0:12', thumbnail: '/static/letter_images/g.jpg', localPath: '/static/alpha_videos/g.mp4', completed: true },
        { id: 'H', title: 'H ', duration: '0:09', thumbnail: '/static/letter_images/h.jpg', localPath: '/static/alpha_videos/h.mp4', completed: true },
        { id: 'I', title: 'I ', duration: '0:09', thumbnail: '/static/letter_images/i.jpg', localPath: '/static/alpha_videos/i.mp4', completed: true },
        { id: 'J', title: 'J ', duration: '0:09', thumbnail: '/static/letter_images/j.jpg', localPath: '/static/alpha_videos/j.mp4', completed: true },
        { id: 'K', title: 'K ', duration: '0:16', thumbnail: '/static/letter_images/k.jpg', localPath: '/static/alpha_videos/k.mp4', completed: true },
        { id: 'L', title: 'L ', duration: '0:08', thumbnail: '/static/letter_images/l.jpg', localPath: '/static/alpha_videos/l.mp4', completed: true },
        { id: 'M', title: 'M ', duration: '0:13', thumbnail: '/static/letter_images/m.jpg', localPath: '/static/alpha_videos/m.mp4', completed: true },
        { id: 'N', title: 'N ', duration: '0:11', thumbnail: '/static/letter_images/n.jpg', localPath: '/static/alpha_videos/n.mp4', completed: true },
        { id: 'O', title: 'O ', duration: '0:08', thumbnail: '/static/letter_images/o.jpg', localPath: '/static/alpha_videos/o.mp4', completed: true },
        { id: 'P', title: 'P ', duration: '0:11', thumbnail: '/static/letter_images/p.jpg', localPath: '/static/alpha_videos/p.mp4', completed: true },
        { id: 'Q', title: 'Q ', duration: '0:11', thumbnail: '/static/letter_images/q.jpg', localPath: '/static/alpha_videos/q.mp4', completed: true },
        { id: 'R', title: 'R ', duration: '0:13', thumbnail: '/static/letter_images/r.jpg', localPath: '/static/alpha_videos/r.mp4', completed: true },
        { id: 'S', title: 'S ', duration: '0:13', thumbnail: '/static/letter_images/s.jpg', localPath: '/static/alpha_videos/s.mp4', completed: true },
        { id: 'T', title: 'T ', duration: '0:10', thumbnail: '/static/letter_images/t.jpg', localPath: '/static/alpha_videos/t.mp4', completed: true },
        { id: 'U', title: 'U ', duration: '0:06', thumbnail: '/static/letter_images/u.jpg', localPath: '/static/alpha_videos/u.mp4', completed: true },
        { id: 'V', title: 'V ', duration: '0:08', thumbnail: '/static/letter_images/v.jpg', localPath: '/static/alpha_videos/v.mp4', completed: true },
        { id: 'W', title: 'W ', duration: '0:09', thumbnail: '/static/letter_images/w.jpg', localPath: '/static/alpha_videos/w.mp4', completed: true },
        { id: 'X', title: 'X ', duration: '0:21', thumbnail: '/static/letter_images/x.jpg', localPath: '/static/alpha_videos/x.mp4', completed: true },
        { id: 'Y', title: 'Y ', duration: '0:09', thumbnail: '/static/letter_images/y.jpg', localPath: '/static/alpha_videos/y.mp4', completed: true },
        { id: 'Z', title: 'Z ', duration: '0:10', thumbnail: '/static/letter_images/z.jpg', localPath: '/static/alpha_videos/z.mp4', completed: true }
    ];

    initializeApp() {
        this.cacheElements();
        this.generateVideoList();
        this.bindEvents();
        this.initializeYear();
        this.loadVideo(0);
        this.updateNavigation();
        this.setupKeyboardShortcuts();
    }

    cacheElements() {
        this.videoContainer = document.querySelector('.video-container');
        this.videoPlayer = document.getElementById('video-player');
        this.videoTitle = document.getElementById('video-title');
        this.videoList = document.getElementById('video-list');
        this.prevBtn = document.getElementById('prev-btn');
        this.nextBtn = document.getElementById('next-btn');
        this.currentYear = document.getElementById('current-year');
    }

    generateVideoList() {
        this.videoList.innerHTML = '';
        this.videoData.forEach((vid, idx) => {
            const btn = document.createElement('button');
            btn.className = `video-card ${idx === 0 ? 'active' : ''}`;
            btn.dataset.index = idx;
            btn.innerHTML = `
                <div class="video-thumbnail">
                    <img src="${vid.thumbnail}" alt="${vid.id} thumbnail" loading="lazy"
                         onerror="this.src='/static/letter_images/default.jpg'"/>
                    <div class="play-overlay">
                        <svg class="play-icon" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M8 5v14l11-7z"/>
                        </svg>
                    </div>
                </div>
                <div class="video-info">
                    <h3>${vid.title}</h3>
                    <div class="video-meta">
                        <span>${vid.duration}</span>
                        ${vid.completed
                            ? `<svg class="completed-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                       d="M5 13l4 4L19 7"/>
                               </svg>` : ''
                        }
                    </div>
                </div>`;
            btn.addEventListener('click', () => this.selectVideo(idx));
            this.videoList.appendChild(btn);
        });
    }

    bindEvents() {
        this.prevBtn.addEventListener('click', () => this.previousVideo());
        this.nextBtn.addEventListener('click', () => this.nextVideo());
        window.addEventListener('resize', this.debounce(() => this.handleResize(), 200));
    }

    selectVideo(idx) {
        if (idx < 0 || idx >= this.videoData.length) return;
        this.currentVideoIndex = idx;
        this.loadVideo(idx);
        this.updateActiveCard(idx);
        this.updateNavigation();
        this.scrollToActiveCard();
    }

    loadVideo(idx) {
        const vid = this.videoData[idx];
        this.showLoadingState();

        console.log('Attempting to load video:', this.config.useLocalVideos ? vid.localPath : vid.youtubeUrl);

        if (this.config.useLocalVideos) {
            this.loadLocalVideo(vid);
        } else {
            this.loadYouTubeVideo(vid);
        }

        this.updateVideoTitle(vid.title);
        setTimeout(() => this.hideLoadingState(), 300);
    }

    loadLocalVideo(vid) {
        if (this.localVideoElement) this.localVideoElement.remove();

        if (this.videoPlayer) this.videoPlayer.style.display = 'none';

        this.localVideoElement = document.createElement('video');
        this.localVideoElement.src = vid.localPath;
        this.localVideoElement.controls = true;
        this.localVideoElement.autoplay = this.config.autoplay;
        this.localVideoElement.className = 'w-full h-full';
        this.localVideoElement.addEventListener('error', () => this.handleVideoError(vid));
        this.videoContainer.appendChild(this.localVideoElement);

        this.isLocalVideo = true;
    }

    loadYouTubeVideo(vid) {
        if (this.localVideoElement) {
            this.localVideoElement.remove();
            this.localVideoElement = null;
        }

        if (this.videoPlayer) {
            this.videoPlayer.style.display = 'block';
            const auto = this.config.autoplay ? '1' : '0';
            this.videoPlayer.src = `${vid.youtubeUrl}?autoplay=${auto}&rel=0&modestbranding=1`;
        }

        this.isLocalVideo = false;
    }

    updateVideoTitle(txt) {
        this.videoTitle.textContent = txt;
        this.videoTitle.classList.add('fade-in');
        setTimeout(() => this.videoTitle.classList.remove('fade-in'), 300);
    }

    updateActiveCard(idx) {
        this.videoList.querySelectorAll('.video-card').forEach(c => c.classList.remove('active'));
        const active = this.videoList.querySelector(`[data-index="${idx}"]`);
        if (active) active.classList.add('active');
    }

    updateNavigation() {
        this.prevBtn.disabled = this.currentVideoIndex === 0;
        this.nextBtn.disabled = this.currentVideoIndex === this.videoData.length - 1;
    }

    scrollToActiveCard() {
        const active = this.videoList.querySelector('.video-card.active');
        if (active) active.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    previousVideo() {
        if (this.currentVideoIndex > 0) this.selectVideo(this.currentVideoIndex - 1);
    }

    nextVideo() {
        if (this.currentVideoIndex < this.videoData.length - 1) this.selectVideo(this.currentVideoIndex + 1);
    }

    setupKeyboardShortcuts() {
        if (!this.config.enableKeyboardShortcuts) return;
        document.addEventListener('keydown', e => {
            if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return;
            if (e.key === 'ArrowLeft') this.previousVideo();
            if (e.key === 'ArrowRight') this.nextVideo();
            if (e.key === ' ') this.togglePlayPause();
            if (e.key === 'Escape') this.exitFullscreen();
        });
    }

    togglePlayPause() {
        if (this.isLocalVideo && this.localVideoElement) {
            this.localVideoElement.paused ? this.localVideoElement.play() : this.localVideoElement.pause();
        }
    }

    exitFullscreen() {
        if (document.fullscreenElement) document.exitFullscreen();
    }

    handleResize() {
        // Placeholder for responsiveness if needed
    }

    handleVideoError(vid) {
        alert(`Failed to load: ${vid.title}`);
        console.error('Video load error:', vid.localPath || vid.youtubeUrl);
        if (this.config.useLocalVideos) {
            this.config.useLocalVideos = false;
            this.loadYouTubeVideo(vid);
        }
    }

    showLoadingState() {
        this.videoContainer.classList.add('loading');
    }

    hideLoadingState() {
        this.videoContainer.classList.remove('loading');
    }

    initializeYear() {
        if (this.currentYear) this.currentYear.textContent = new Date().getFullYear();
    }

    debounce(fn, delay) {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => fn.apply(this, args), delay);
        };
    }
}

// Initialize the player once DOM is ready
window.addEventListener('DOMContentLoaded', () => {
    new SignLingoPlayer();
});
