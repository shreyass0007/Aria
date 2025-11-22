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
// const themeBtn = document.getElementById('themeBtn'); // Removed
const settingsBtn = document.getElementById('settingsBtn');
const settingsModal = document.getElementById('settingsModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const clearChatBtn = document.getElementById('clearChatBtn');
// const toggleThemeBtn = document.getElementById('toggleThemeBtn'); // Removed
const aboutBtn = document.getElementById('aboutBtn');
const newChatBtn = document.getElementById('newChatBtn');
const historyBtn = document.getElementById('historyBtn');
const historySidebar = document.getElementById('historySidebar');
const closeHistoryBtn = document.getElementById('closeHistoryBtn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadTheme();
    displayWelcomeMessage();
});

// Event Listeners
function setupEventListeners() {
    console.log('Setting up event listeners...');
    console.log('newChatBtn:', newChatBtn);
    console.log('historyBtn:', historyBtn);

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
    // themeBtn.addEventListener('click', handleToggleTheme); // Removed
    settingsBtn.addEventListener('click', () => openModal());
    closeModalBtn.addEventListener('click', () => closeModal());
    clearChatBtn.addEventListener('click', handleClearChat);
    /* toggleThemeBtn.addEventListener('click', () => {
        handleToggleTheme();
        closeModal();
    }); */ // Removed
    aboutBtn.addEventListener('click', handleAbout);
    newChatBtn.addEventListener('click', handleNewChat);
    historyBtn.addEventListener('click', toggleHistory);
    closeHistoryBtn.addEventListener('click', toggleHistory);

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
    // themeBtn.textContent = theme === 'light' ? '🌙' : '☀️'; // Removed
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

function handleNewChat() {
    console.log('New Chat clicked');
    chatContainer.innerHTML = '';
    addMessage('✨ New chat started! How can I help you?', 'aria');
}

function toggleHistory() {
    console.log('History toggled');
    historySidebar.classList.toggle('active');
    console.log('Sidebar active:', historySidebar.classList.contains('active'));
}

// Get time-based greeting like JARVIS
function getTimeBasedGreeting() {
    const hour = new Date().getHours();
    const userName = "Shreyas"; // You can make this dynamic if needed

    let greeting = "";
    let timeOfDay = "";

    if (hour >= 5 && hour < 12) {
        timeOfDay = "morning";
        greeting = `Good morning, ${userName}. `;
    } else if (hour >= 12 && hour < 17) {
        timeOfDay = "afternoon";
        greeting = `Good afternoon, ${userName}. `;
    } else if (hour >= 17 && hour < 21) {
        timeOfDay = "evening";
        greeting = `Good evening, ${userName}. `;
    } else {
        timeOfDay = "night";
        greeting = `Good night, ${userName}. `;
    }

    // Add context-aware messages like JARVIS
    const contextMessages = {
        morning: [
            "Ready to start the day?",
            "All systems are operational.",
            "How may I assist you today?",
            "Your schedule is ready for review.",
            "Time to conquer the world.",
            "Let's make today productive.",
            "What's on the agenda?",
            "Shall we begin?",
            "The world awaits your brilliance.",
            "Ready to tackle today's challenges?",
            "A fresh start awaits.",
            "Let's make things happen.",
            "Your productivity suite is ready.",
            "Time to turn ideas into reality.",
            "The early bird gets the worm.",
            "Rise and shine! Let's get to work.",
            "Another day, another opportunity.",
            "Ready to make today count?",
            "Let's start with a winning strategy.",
            "Your digital workspace is prepared."
        ],
        afternoon: [
            "How's your day going?",
            "What can I help you with?",
            "All systems running smoothly.",
            "Ready when you are.",
            "Need a productivity boost?",
            "Let's keep the momentum going.",
            "Time to check off that to-do list.",
            "How may I assist this afternoon?",
            "Still going strong?",
            "Let's finish what we started.",
            "Halfway through the day already.",
            "Need anything to stay on track?",
            "Keeping things efficient, as always.",
            "What's next on your list?",
            "Shall we continue?",
            "Your afternoon update is ready.",
            "Let's maintain that energy.",
            "Working hard, I see.",
            "Time to power through.",
            "At your service, as always."
        ],
        evening: [
            "Welcome back. How can I help?",
            "Ready to wrap up the day?",
            "What do you need?",
            "At your service.",
            "Time to unwind or keep going?",
            "Let's review what you've accomplished.",
            "How was your day?",
            "Ready for the evening?",
            "Shall we tie up loose ends?",
            "Time to relax or power through?",
            "The day's work is nearly done.",
            "Let's finish strong.",
            "What's left on your plate?",
            "Evening briefing ready.",
            "Time to reflect and recharge.",
            "You've earned a break.",
            "Let's close out the day properly.",
            "Standing by for evening tasks.",
            "Ready to help you wind down.",
            "What can I do for you tonight?"
        ],
        night: [
            "Burning the midnight oil?",
            "Still working? Let me help.",
            "How can I assist you tonight?",
            "Ready whenever you are.",
            "Late night session?",
            "The night is young.",
            "Inspiration strikes at odd hours.",
            "Night owl mode activated.",
            "I'm here, no matter the hour.",
            "Let's make the most of this quiet time.",
            "The stars are out, and so are we.",
            "Darkness brings clarity sometimes.",
            "Working late again, I see.",
            "Your dedication is admirable.",
            "Let me help you through the night.",
            "Sleep is overrated anyway.",
            "The night shift begins.",
            "When do you sleep, exactly?",
            "Midnight productivity mode enabled.",
            "Let's turn night into opportunity."
        ]
    };

    // Pick a random context message
    const messages = contextMessages[timeOfDay];
    const contextMsg = messages[Math.floor(Math.random() * messages.length)];

    return greeting + contextMsg;
}


// Welcome Message
async function displayWelcomeMessage() {
    setTimeout(async () => {
        try {
            // Fetch greeting from backend (which will also speak it)
            const response = await fetch(`${API_URL}/greeting`);
            const data = await response.json();

            if (data.status === 'success' && data.greeting) {
                addMessage(data.greeting, 'aria');
            } else {
                // Fallback to local greeting if backend fails
                const greeting = getTimeBasedGreeting();
                addMessage(greeting, 'aria');
            }
        } catch (error) {
            console.error('Error fetching greeting:', error);
            // Fallback to local greeting
            const greeting = getTimeBasedGreeting();
            addMessage(greeting, 'aria');
        }
    }, 500);
}


// Export for debugging
window.ariaApp = {
    addMessage,
    handleSendMessage,
    handleToggleVoice,
    handleToggleTheme
};
