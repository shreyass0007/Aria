import { state } from './state.js';

export function createTitleBar() {
    const titleBar = document.createElement('div');
    titleBar.className = 'custom-title-bar';
    titleBar.innerHTML = `
        <div class="title-bar-draggable">
            <img src="aria_logo.png" alt="Aria" class="title-bar-icon">
            <span class="title-bar-title">Aria</span>
        </div>
        <div class="title-bar-controls">
            <button class="title-bar-btn" id="winMinimizeBtn" title="Minimize">
                <svg width="10" height="10" viewBox="0 0 10 10">
                    <line x1="0" y1="5" x2="10" y2="5" stroke="currentColor" stroke-width="1"/>
                </svg>
            </button>
            <button class="title-bar-btn" id="winMaximizeBtn" title="Maximize">
                <svg width="10" height="10" viewBox="0 0 10 10">
                    <rect x="1" y="1" width="8" height="8" stroke="currentColor" stroke-width="1" fill="none"/>
                </svg>
            </button>
            <button class="title-bar-btn title-bar-close" id="winCloseBtn" title="Close">
                <svg width="10" height="10" viewBox="0 0 10 10">
                    <line x1="1" y1="1" x2="9" y2="9" stroke="currentColor" stroke-width="1"/>
                    <line x1="9" y1="1" x2="1" y2="9" stroke="currentColor" stroke-width="1"/>
                </svg>
            </button>
        </div>
    `;

    document.body.insertBefore(titleBar, document.body.firstChild);

    document.getElementById('winMinimizeBtn').addEventListener('click', () => {
        window.api.windowMinimize();
    });

    document.getElementById('winMaximizeBtn').addEventListener('click', () => {
        window.api.windowMaximize();
    });

    document.getElementById('winCloseBtn').addEventListener('click', () => {
        window.api.windowClose();
    });
}

export function autoResizeTextarea(element) {
    element.style.height = 'auto';
    element.style.height = element.scrollHeight + 'px';

    if (element.scrollHeight > 120) {
        element.classList.add('scrollable');
    } else {
        element.classList.remove('scrollable');
    }
}

export function applyTheme(theme) {
    document.body.setAttribute('data-theme', theme);
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');
    if (themeIcon && themeText) {
        themeIcon.textContent = theme === 'light' ? '🌙' : '☀️';
        themeText.textContent = theme === 'light' ? 'Dark Mode' : 'Light Mode';
    }

    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.checked = theme === 'dark';
    }
}

export function applyColorTheme(theme) {
    document.body.setAttribute('data-color-theme', theme);

    document.querySelectorAll('.theme-option').forEach(opt => {
        opt.classList.remove('active');
    });
    const selectedOption = document.querySelector(`.theme-option[data-theme="${theme}"]`);
    if (selectedOption) {
        selectedOption.classList.add('active');
    }
}

export function updateModeBadge(mode) {
    const badge = document.getElementById('mode-badge');
    if (!badge) return;

    badge.textContent = mode.toUpperCase() + " MODE";
    badge.className = 'mode-badge'; // Reset classes

    if (mode === 'normal') {
        badge.classList.add('hidden');
    } else {
        badge.classList.remove('hidden');
        badge.classList.add(mode); // e.g., 'coder', 'study', 'jarvis'
    }
}
