import { state } from './state.js';
import { fetchAvailableModels, sendToBackend, getTTSStatus, setTTSStatus } from './api.js';
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
    loadTTSStatus();
    loadAvailableModels();
    loadModelPreference();
    displayWelcomeMessage();
});

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

function displayWelcomeMessage() {
    // Check if chat is empty
    const chatContainer = document.getElementById('chatContainer');
    if (chatContainer && chatContainer.children.length === 0) {
        addMessage('Hello! I am Aria. How can I help you today?', 'aria');
    }
}
