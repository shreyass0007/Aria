// API Configuration
const API_URL = 'http://localhost:5000';

// State
let voiceModeActive = false;
let currentTheme = 'light';

// DOM Elements
const chatContainer = document.getElementById('chatContainer');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const voiceBtn = document.getElementById('voiceBtn');
const themeBtn = document.getElementById('themeBtn');
const settingsBtn = document.getElementById('settingsBtn');
const settingsModal = document.getElementById('settingsModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const clearChatBtn = document.getElementById('clearChatBtn');
const toggleThemeBtn = document.getElementById('toggleThemeBtn');
const aboutBtn = document.getElementById('aboutBtn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadTheme();
    displayWelcomeMessage();
});

// Event Listeners
function setupEventListeners() {
    sendBtn.addEventListener('click', handleSendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    // Auto-resize textarea
    messageInput.addEventListener('input', autoResizeTextarea);

    voiceBtn.addEventListener('click', handleToggleVoice);
    themeBtn.addEventListener('click', handleToggleTheme);
    settingsBtn.addEventListener('click', () => openModal());
    closeModalBtn.addEventListener('click', () => closeModal());
    clearChatBtn.addEventListener('click', handleClearChat);
    toggleThemeBtn.addEventListener('click', () => {
        handleToggleTheme();
        closeModal();
    });
    aboutBtn.addEventListener('click', handleAbout);

    // Close modal on overlay click
    settingsModal.addEventListener('click', (e) => {
        if (e.target === settingsModal) closeModal();
    });
}

// Auto-resize textarea
function autoResizeTextarea() {
    messageInput.style.height = 'auto';
    messageInput.style.height = messageInput.scrollHeight + 'px';

    // Add scrollable class if at max height
    if (messageInput.scrollHeight > 120) {
        messageInput.classList.add('scrollable');
    } else {
        messageInput.classList.remove('scrollable');
    }
}

// Message Handling
function handleSendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    // Clear input
    messageInput.value = '';

    // Reset height
    messageInput.style.height = 'auto';
    messageInput.classList.remove('scrollable');

    // Display user message
    addMessage(message, 'user');

    // Animate send button
    animateSendButton();

    // Send to backend
    sendMessageToBackend(message);
}

async function sendMessageToBackend(message) {
    try {
        const response = await fetch(`${API_URL}/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });

        const data = await response.json();

        if (data.response) {
            addMessage(data.response, 'aria');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        addMessage('Sorry, I encountered an error. Please make sure the backend is running.', 'aria');
    }
}

function addMessage(text, sender) {
    const messageWrapper = document.createElement('div');
    messageWrapper.className = 'message-wrapper';

    const message = document.createElement('div');
    message.className = `message ${sender}`;

    if (sender === 'aria') {
        // Add avatar for Aria with logo
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        const avatarImg = document.createElement('img');
        avatarImg.src = 'aria_logo.png';
        avatarImg.alt = 'Aria';
        avatar.appendChild(avatarImg);
        message.appendChild(avatar);
    }

    // Add message bubble
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;
    message.appendChild(bubble);

    messageWrapper.appendChild(message);
    chatContainer.appendChild(messageWrapper);

    // Scroll to bottom
    setTimeout(() => {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 50);
}

function animateSendButton() {
    sendBtn.style.transform = 'scale(0.9)';
    setTimeout(() => {
        sendBtn.style.transform = 'scale(1)';
    }, 150);
}

// Voice Mode
async function handleToggleVoice() {
    voiceModeActive = !voiceModeActive;

    if (voiceModeActive) {
        voiceBtn.classList.add('active');
        addMessage('🎙️ Voice mode active - Say "Aria" to start', 'aria');

        try {
            // Start voice listening
            await startVoiceMode();
        } catch (error) {
            console.error('Voice mode error:', error);
            voiceModeActive = false;
            voiceBtn.classList.remove('active');
        }
    } else {
        voiceBtn.classList.remove('active');
        addMessage('Voice mode deactivated', 'aria');
        stopVoiceMode();
    }
}

async function startVoiceMode() {
    try {
        const response = await fetch(`${API_URL}/voice/start`, {
            method: 'POST',
        });

        if (response.ok) {
            listenForVoiceInput();
        }
    } catch (error) {
        console.error('Error starting voice mode:', error);
    }
}

async function listenForVoiceInput() {
    if (!voiceModeActive) return;

    try {
        const response = await fetch(`${API_URL}/voice/listen`);
        const data = await response.json();

        if (data.text) {
            addMessage(data.text, 'user');
            sendMessageToBackend(data.text);
        }

        // Continue listening
        if (voiceModeActive) {
            setTimeout(() => listenForVoiceInput(), 1000);
        }
    } catch (error) {
        console.error('Error listening for voice:', error);
        if (voiceModeActive) {
            setTimeout(() => listenForVoiceInput(), 2000);
        }
    }
}

async function stopVoiceMode() {
    try {
        await fetch(`${API_URL}/voice/stop`, {
            method: 'POST',
        });
    } catch (error) {
        console.error('Error stopping voice mode:', error);
    }
}

// Theme Management
function handleToggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    applyTheme(currentTheme);
    saveTheme(currentTheme);
}

function applyTheme(theme) {
    document.body.setAttribute('data-theme', theme);
    themeBtn.textContent = theme === 'light' ? '🌙' : '☀️';
}

function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    currentTheme = savedTheme;
    applyTheme(currentTheme);
}

function saveTheme(theme) {
    localStorage.setItem('theme', theme);
}

// Modal Management
function openModal() {
    settingsModal.classList.add('active');
}

function closeModal() {
    settingsModal.classList.remove('active');
}

// Settings Actions
function handleClearChat() {
    chatContainer.innerHTML = '';
    addMessage('✨ Chat cleared', 'aria');
    closeModal();
}

function handleAbout() {
    addMessage('✨ Aria v2.0\nYour Premium AI Assistant\n\nDeveloped with ❤️ by Shreyas', 'aria');
    closeModal();
}

// Welcome Message
function displayWelcomeMessage() {
    setTimeout(() => {
        addMessage("Hello! I'm Aria, your AI assistant. How can I help you today?", 'aria');
    }, 500);
}

// Export for debugging
window.ariaApp = {
    addMessage,
    handleSendMessage,
    handleToggleVoice,
    handleToggleTheme
};
