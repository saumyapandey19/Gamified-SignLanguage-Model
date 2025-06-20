
/// script.js - SignLingoPlayer Class
class SignLingoPlayer {
    constructor() {
        this.currentVideoIndex = 0;
        this.isLocalVideo = true;
        this.videoPlayer = null;
        this.localVideoElement = null;
        this.initializeApp();
    }

    videoData = [
        { id: 'Yes_No', title: 'Yes / No', duration: '0:15', thumbnail: '/static/phrases_images/yes.jpg', localPath: 'static/videos/yes_No.mp4', completed: true },
        { id: 'sorry', title: 'Sorry', duration: '0:15', thumbnail: '/static/phrases_images/sorry.jpg', localPath: 'static/videos/sorry.mp4', completed: true },
        { id: 'Hello', title: 'Hello', duration: '0:15', thumbnail: '/static/phrases_images/hello.jpg', localPath: 'static/videos/Hello.mp4', completed: true },
        { id: 'nicetomeetyou', title: 'Nice to Meet You', duration: '0:15', thumbnail: '/static/phrases_images/nice to meet you.jpg', localPath: 'static/videos/nicetomeetyou.mp4', completed: true },
        { id: 'please', title: 'Please', duration: '0:15', thumbnail: '/static/phrases_images/please.jpg', localPath: 'static/videos/please.mp4', completed: true },
        { id: 'thankyou', title: 'Thank You', duration: '0:15', thumbnail: '/static/phrases_images/thank you.jpg', localPath: 'static/videos/thankyou.mp4', completed: true }
    ];

    config = {
        useLocalVideos: true,
        autoplay: false,
        enableKeyboardShortcuts: true
    };

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
                    <img src="${vid.thumbnail}" alt="${vid.title}" class="w-full h-20 object-cover rounded" />
                </div>
                <div class="video-info">
                    <h3>${vid.title}</h3>
                    <div class="video-meta">
                        <span>${vid.duration}</span>
                        ${vid.completed ? `
                            <svg xmlns="http://www.w3.org/2000/svg"
                                 width="16" height="16"
                                 fill="currentColor"
                                 class="bi bi-check completed-icon"
                                 viewBox="0 0 16 16">
                                <path d="M10.97 4.97a.75.75 0 0 1 1.07 1.05
                                         l-3.99 4.99a.75.75 0 0 1-1.08.02
                                         L4.324 8.384a.75.75 0 1 1
                                         1.06-1.06l2.094 2.093
                                         3.473-4.425z"/>
                            </svg>` : ''}
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
        this.videoPlayer.addEventListener('error', () => this.handleVideoError(this.videoData[this.currentVideoIndex]));
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
        if (this.config.useLocalVideos) {
            this.loadLocalVideo(vid);
        } else {
            this.loadYouTubeVideo(vid);
        }
        this.updateVideoTitle(`${vid.id} for ${vid.title}`);
        setTimeout(() => this.hideLoadingState(), 300);
    }

    loadLocalVideo(vid) {
        if (this.localVideoElement) this.localVideoElement.remove();
        this.videoPlayer.style.display = 'none';
        this.localVideoElement = document.createElement('video');
        this.localVideoElement.src = vid.localPath;
        this.localVideoElement.controls = true;
        this.localVideoElement.autoplay = this.config.autoplay;
        this.localVideoElement.className = 'w-full h-auto max-h-[480px]';
        this.localVideoElement.addEventListener('error', () => this.handleVideoError(vid));
        this.videoContainer.appendChild(this.localVideoElement);
        this.isLocalVideo = true;
    }

    loadYouTubeVideo(vid) {
        if (this.localVideoElement) {
            this.localVideoElement.remove();
            this.localVideoElement = null;
        }
        this.videoPlayer.style.display = 'block';
        const auto = this.config.autoplay ? '1' : '0';
        this.videoPlayer.src = `${vid.youtubeUrl}?autoplay=${auto}&rel=0&modestbranding=1`;
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

    handleResize() {}

    handleVideoError(vid) {
        alert(`Error loading video: ${vid.title}`);
        console.error('Video error', vid);
        if (this.config.useLocalVideos && vid.youtubeUrl) {
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

    goToVideo(letterOrIndex) {
        let idx = -1;
        if (typeof letterOrIndex === 'string') {
            idx = this.videoData.findIndex(v => v.id.toUpperCase() === letterOrIndex.toUpperCase());
        } else if (typeof letterOrIndex === 'number') {
            idx = letterOrIndex;
        }
        if (idx >= 0 && idx < this.videoData.length) this.selectVideo(idx);
        else console.warn('goToVideo: invalid parameter', letterOrIndex);
    }

    debounce(fn, delay) {
        let t;
        return (...args) => {
            clearTimeout(t);
            t = setTimeout(() => fn.apply(this, args), delay);
        };
    }
}

window.addEventListener('DOMContentLoaded', () => {
    new SignLingoPlayer();
});
