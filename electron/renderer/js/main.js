import { state } from './state.js';
import { fetchAvailableModels, sendToBackend, getTTSStatus, setTTSStatus, waitForBackend } from './api.js';
import { createTitleBar, autoResizeTextarea, applyTheme, applyColorTheme } from './ui.js';
import { addMessage, showThinkingIndicator, removeThinkingIndicator, animateSendButton } from './chat.js';
import { handleToggleVoice } from './voice.js';
import { loadConversationHistory } from './history.js';
import { loadAllComponents } from './component-loader.js';

document.addEventListener('DOMContentLoaded', async () => {
    await loadAllComponents();
    createTitleBar();
    setupEventListeners();
    loadTheme();

    // Wait for backend to be ready before making API calls
    const backendReady = await waitForBackend();
    if (backendReady) {
        loadTTSStatus();
        loadAvailableModels();
    } else {
        console.error("Backend failed to initialize. Some features may not work.");
        // Optional: Show error in UI
    }

    loadModelPreference();
    loadModelPreference();
    displayWelcomeMessage();

    // Start polling for backend notifications (e.g. proactive reminders)
    setInterval(pollNotifications, 3000);
});

async function pollNotifications() {
    try {
        const response = await fetch('http://localhost:5000/notifications');
        const data = await response.json();

        if (data.status === 'success' && data.notifications && data.notifications.length > 0) {
            data.notifications.forEach(notification => {
                if (notification.type === 'assistant_message') {
                    addMessage(notification.content, 'aria');
                }
            });
        }
    } catch (error) {
        // Silent fail for polling errors to avoid console spam
    }
}

window.onerror = function (message, source, lineno, colno, error) {
    console.error('Global Error:', message, source, lineno, colno, error);
    // alert(`Error: ${message}`); // Optional: alert user
};

window.onunhandledrejection = function (event) {
    console.error('Unhandled Rejection:', event.reason);
};

function setupEventListeners() {
    const sendBtn = document.getElementById('sendBtn');
    const messageInput = document.getElementById('messageInput');
    const voiceBtn = document.getElementById('voiceBtn');
    const settingsBtn = document.getElementById('settingsBtn');
    const settingsModal = document.getElementById('settingsModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const clearChatBtn = document.getElementById('clearChatBtn');
    const toggleThemeBtn = document.getElementById('toggleThemeBtn');
    const aboutBtn = document.getElementById('aboutBtn');
    const newChatBtn = document.getElementById('newChatBtn');
    const historyBtn = document.getElementById('historyBtn');
    const closeHistoryBtn = document.getElementById('closeHistoryBtn');
    const ttsToggle = document.getElementById('ttsToggle');
    const darkModeToggle = document.getElementById('darkModeToggle');
    const modelSelector = document.getElementById('modelSelector');

    if (sendBtn) sendBtn.addEventListener('click', handleSendMessage);
    if (messageInput) {
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
            }
        });
        messageInput.addEventListener('input', () => autoResizeTextarea(messageInput));
    }

    if (voiceBtn) voiceBtn.addEventListener('click', handleToggleVoice);
    if (settingsBtn) settingsBtn.addEventListener('click', openModal);
    if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);
    if (clearChatBtn) clearChatBtn.addEventListener('click', handleClearChat);
    if (toggleThemeBtn) toggleThemeBtn.addEventListener('click', handleToggleTheme);
    if (aboutBtn) aboutBtn.addEventListener('click', handleAbout);
    if (newChatBtn) newChatBtn.addEventListener('click', handleNewChat);
    if (historyBtn) historyBtn.addEventListener('click', toggleHistory);
    if (closeHistoryBtn) closeHistoryBtn.addEventListener('click', toggleHistory);

    if (ttsToggle) {
        ttsToggle.addEventListener('change', handleToggleTTS);
    }

    if (darkModeToggle) {
        darkModeToggle.addEventListener('change', handleDarkModeToggle);
    }

    document.querySelectorAll('.theme-option').forEach(option => {
        option.addEventListener('click', () => handleColorThemeChange(option.dataset.theme));
    });

    // Custom model selector dropdown
    const modelSelectorBtn = document.getElementById('modelSelector');
    const modelDropdown = document.getElementById('modelDropdown');

    if (modelSelectorBtn && modelDropdown) {
        // Toggle dropdown
        modelSelectorBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            modelSelectorBtn.classList.toggle('active');
            modelDropdown.classList.toggle('active');
        });

        // Close dropdown on outside click
        document.addEventListener('click', (e) => {
            if (!modelSelectorBtn.contains(e.target) && !modelDropdown.contains(e.target)) {
                modelSelectorBtn.classList.remove('active');
                modelDropdown.classList.remove('active');
            }
        });
    }

    if (settingsModal) {
        settingsModal.addEventListener('click', (e) => {
            if (e.target === settingsModal) closeModal();
        });
    }
}

async function handleSendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    if (!message) return;

    messageInput.value = '';
    messageInput.style.height = 'auto';
    messageInput.classList.remove('scrollable');

    addMessage(message, 'user');
    animateSendButton();
    showThinkingIndicator();

    try {
        const data = await sendToBackend(message);
        removeThinkingIndicator();

        if (data.status === 'success') {
            if (data.conversation_id) {
                state.currentConversationId = data.conversation_id;
            }
            if (data.response) {
                addMessage(data.response, 'aria', data.ui_action);
            }
        } else {
            addMessage('Sorry, I encountered an error. Please make sure the backend is running.', 'aria');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        removeThinkingIndicator();
        addMessage('Sorry, I encountered an error.', 'aria');
    }
}

function openModal() {
    const settingsModal = document.getElementById('settingsModal');
    if (settingsModal) settingsModal.classList.add('active');
}

function closeModal() {
    const settingsModal = document.getElementById('settingsModal');
    if (settingsModal) settingsModal.classList.remove('active');
}

function handleClearChat() {
    const chatContainer = document.getElementById('chatContainer');
    if (chatContainer) chatContainer.innerHTML = '';
    displayWelcomeMessage();
    closeModal();
}

function handleAbout() {
    addMessage('Aria is an advanced AI assistant designed to help you with various tasks. Version 1.0.0', 'aria');
    closeModal();
}

function handleNewChat() {
    state.currentConversationId = null;
    handleClearChat();
}

function toggleHistory() {
    const historySidebar = document.getElementById('historySidebar');
    if (historySidebar) {
        const isOpening = !historySidebar.classList.contains('active');
        historySidebar.classList.toggle('active');

        // Load conversation history when opening the sidebar
        if (isOpening) {
            loadConversationHistory();
        }
    }
}

async function loadTTSStatus() {
    try {
        const data = await getTTSStatus();
        if (data.status === 'success') {
            const ttsToggle = document.getElementById('ttsToggle');
            if (ttsToggle) ttsToggle.checked = data.enabled;
        }
    } catch (error) {
        console.warn('Error loading TTS status:', error);
    }
}

async function handleToggleTTS() {
    const ttsToggle = document.getElementById('ttsToggle');
    if (!ttsToggle) return;
    const enabled = ttsToggle.checked;
    try {
        const data = await setTTSStatus(enabled);
        if (data.status !== 'success') {
            ttsToggle.checked = !enabled;
        }
    } catch (error) {
        ttsToggle.checked = !enabled;
    }
}

async function loadAvailableModels() {
    try {
        const data = await fetchAvailableModels();
        if (data.status === 'success') {
            const modelDropdown = document.getElementById('modelDropdown');
            if (modelDropdown) {
                modelDropdown.innerHTML = '';
                data.models.forEach(model => {
                    const option = document.createElement('div');
                    option.className = 'model-option';
                    option.setAttribute('data-value', model.id);
                    option.textContent = model.name;
                    option.addEventListener('click', () => handleModelChange(model.id, model.name));
                    modelDropdown.appendChild(option);
                });
                loadModelPreference();
            }
        }
    } catch (error) {
        console.warn('Error fetching models:', error);
    }
}

function loadModelPreference() {
    const savedModel = localStorage.getItem('selected_ai_model') || 'gpt-4o';
    state.currentModel = savedModel;

    // Find and get the model name
    const modelOptions = document.querySelectorAll('.model-option');
    modelOptions.forEach(option => {
        if (option.getAttribute('data-value') === savedModel) {
            const selectedModelSpan = document.getElementById('selectedModel');
            if (selectedModelSpan) {
                selectedModelSpan.textContent = option.textContent;
            }
            option.classList.add('selected');
        }
    });
}

function handleModelChange(modelId, modelName) {
    state.currentModel = modelId;
    localStorage.setItem('selected_ai_model', modelId);

    // Update selected model display
    const selectedModelSpan = document.getElementById('selectedModel');
    if (selectedModelSpan) {
        selectedModelSpan.textContent = modelName;
    }

    // Update selected class
    document.querySelectorAll('.model-option').forEach(opt => {
        opt.classList.remove('selected');
        if (opt.getAttribute('data-value') === modelId) {
            opt.classList.add('selected');
        }
    });

    // Close dropdown
    document.getElementById('modelSelector').classList.remove('active');
    document.getElementById('modelDropdown').classList.remove('active');
}

function handleToggleTheme() {
    state.currentTheme = state.currentTheme === 'light' ? 'dark' : 'light';
    applyTheme(state.currentTheme);
    localStorage.setItem('theme', state.currentTheme);
}

function handleDarkModeToggle() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    state.currentTheme = darkModeToggle.checked ? 'dark' : 'light';
    applyTheme(state.currentTheme);
    localStorage.setItem('theme', state.currentTheme);
}

function handleColorThemeChange(theme) {
    state.currentColorTheme = theme;
    applyColorTheme(theme);
    localStorage.setItem('colorTheme', theme);
}

function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    state.currentTheme = savedTheme;
    applyTheme(savedTheme);

    const savedColorTheme = localStorage.getItem('colorTheme') || 'violet';
    state.currentColorTheme = savedColorTheme;
    applyColorTheme(savedColorTheme);
}

// Time-based greeting like JARVIS
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

    // Context-aware messages like JARVIS
    const contextMessages = {
        morning: [
            "Ready to start the day?",
            "All systems are operational.",
            "How can I assist you today?",
            "Your schedule is ready for review.",
            "Let's conquer the world.",
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
            "Your digital workspace is prepared.",
            "Coffee's ready. What's first?",
            "Let's make magic happen today.",
            "The sun is up, and so are we.",
            "Your morning briefing is available.",
            "Time to seize the day.",
            "What masterpiece shall we create today?",
            "All systems fully charged and ready.",
            "Let's turn those dreams into plans.",
            "The future starts now.",
            "Your potential awaits activation.",
            "Ready to break new ground?",
            "Let's set the tone for an amazing day.",
            "What brilliant idea will spark today?",
            "Morning glory awaits.",
            "Let's build something incredible."
        ],
        afternoon: [
            "How is your day going?",
            "What can I help you with?",
            "All systems running smoothly.",
            "Ready when you are.",
            "Need a productivity boost?",
            "Let's keep the momentum going.",
            "Time to check off that to-do list.",
            "How can I assist this afternoon?",
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
            "Let's power through.",
            "At your service, as always.",
            "The day is yours to command.",
            "Peak performance hours are here.",
            "Let's capitalize on this momentum.",
            "What shall we accomplish next?",
            "Cruising through the day nicely.",
            "Your afternoon checkpoint is ready.",
            "Time to double down on success.",
            "How can I optimize your workflow?",
            "Let's keep this winning streak alive.",
            "Productivity levels looking excellent.",
            "The hustle continues.",
            "Let's make the most of these hours.",
            "Your focus is impressive today.",
            "Ready to crush some more goals?",
            "The afternoon grind awaits."
        ],
        evening: [
            "Welcome back. How can I help?",
            "Ready to wrap up the day?",
            "What do you need?",
            "At your service.",
            "Time to unwind or keep going?",
            "Let's review what you've accomplished.",
            "How was your day?",
            "Plans for the evening?",
            "Shall we tie up loose ends?",
            "Time to relax or power through?",
            "Today's work is nearly done.",
            "Let's finish strong.",
            "Anything left on your plate?",
            "Evening briefing ready.",
            "Time to reflect and recharge.",
            "You've earned a break.",
            "Let's close out the day properly.",
            "Standing by for evening tasks.",
            "Here to help you wind down.",
            "What can I do for you tonight?",
            "The golden hour approaches.",
            "Time to shift into evening mode.",
            "Let's recap today's victories.",
            "Sunset productivity activated.",
            "Evening operations standing by.",
            "Ready for whatever comes next?",
            "The day's final act begins.",
            "Time for reflection or action?",
            "Let's make this evening count.",
            "Winding down or ramping up?",
            "Your evening companion is here.",
            "Shall we celebrate today's wins?",
            "The twilight hours are yours.",
            "Ready for some evening magic?",
            "Let's end this day on a high note."
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
            "Here for you, no matter the hour.",
            "Let's make the most of this quiet time.",
            "The stars are out, and so are we.",
            "Darkness brings clarity sometimes.",
            "Working late again, I see.",
            "Your dedication is admirable.",
            "Let me help you through the night.",
            "Sleep is overrated anyway.",
            "The night shift begins.",
            "When do you sleep, exactly?",
            "Silent productivity mode enabled.",
            "Let's turn night into opportunity.",
            "The world sleeps, but we create.",
            "Midnight breakthrough incoming?",
            "The nocturnal genius awakens.",
            "Coffee or code? Both?",
            "These quiet hours are golden.",
            "Night mode: fully operational.",
            "The best ideas come after dark.",
            "Burning bright in the darkness.",
            "Let's own these midnight hours.",
            "Your nocturnal assistant reporting.",
            "The moon is our only witness.",
            "Late night brilliance in progress.",
            "The witching hour of productivity.",
            "Sleep later, create now.",
            "Darkness fuels innovation."
        ]
    };

    // Pick a random context message
    const messages = contextMessages[timeOfDay];
    const contextMsg = messages[Math.floor(Math.random() * messages.length)];

    return greeting + contextMsg;
}

async function displayWelcomeMessage() {
    // Check if chat is empty
    const chatContainer = document.getElementById('chatContainer');
    if (chatContainer && chatContainer.children.length === 0) {

        // Try to get Morning Briefing first
        try {
            const response = await fetch('http://localhost:5000/briefing');
            const data = await response.json();

            if (data.status === 'success' && data.briefing) {
                addMessage(data.briefing, 'aria');
                // Also speak it? The backend doesn't auto-speak this one, so we might want to trigger TTS here if needed.
                // But for now, let's just display it. The user can click to speak if they want, or we can send a TTS command.
                // Actually, let's make it speak automatically for that "Jarvis" feel.
                // We can do this by sending a hidden command or just letting the user read it.
                // Let's stick to text for now to be safe, or use the existing TTS toggle state.
            } else {
                // Fallback to generic
                const greeting = getTimeBasedGreeting();
                addMessage(greeting, 'aria');
            }
        } catch (e) {
            // Fallback to generic on error
            const greeting = getTimeBasedGreeting();
            addMessage(greeting, 'aria');
        }
    }
}

// DISABLED: Module loader system was removed
// Uncomment and restore module-loader.js and feature-config.js to re-enable
/*
async function loadOptionalModules() {
    console.log('🔌 Loading optional modules...');

    try {
        // Check backend feature availability
        const featureStatus = await checkAllFeaturesStatus();

        if (featureStatus.status !== 'success') {
            console.warn('⚠️ Could not check feature status, modules will not load');
            return;
        }

        const availableFeatures = featureStatus.features;
        console.log('Available features:', availableFeatures);

        // Module definitions
        const modules = [
            // Phase 2: Email Module
            {
                name: 'email',
                init: async () => {
                    const { initEmailModule } = await import('./modules/email.js');
                    return await initEmailModule();
                },
                options: { showErrorToUser: false }
            }

            // More modules will be added in future phases
        ];

        // Load all modules in parallel
        if (modules.length > 0) {
            const results = await moduleLoader.loadModules(modules);
            console.log(`✅ Loaded ${results.loaded}/${results.total} optional modules`);
        } else {
            console.log('ℹ️ No optional modules configured yet');
        }

    } catch (error) {
        console.error('Error loading optional modules:', error);
        // App continues normally even if module loading fails
    }
}
*/
