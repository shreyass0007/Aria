// API Configuration
const API_URL = 'http://localhost:5000';

// State
let voiceModeActive = false;
let currentTheme = 'light';
let currentColorTheme = 'violet'; // violet, ocean, sunset, forest
let currentConversationId = null;
let currentModel = 'gpt-4o'; // Current AI model

// DOM Elements
const chatContainer = document.getElementById('chatContainer');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const voiceBtn = document.getElementById('voiceBtn');
const settingsBtn = document.getElementById('settingsBtn');
const settingsModal = document.getElementById('settingsModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const clearChatBtn = document.getElementById('clearChatBtn');
const toggleThemeBtn = document.getElementById('toggleThemeBtn');
const themeIcon = document.getElementById('themeIcon');
const themeText = document.getElementById('themeText');
const aboutBtn = document.getElementById('aboutBtn');
const newChatBtn = document.getElementById('newChatBtn');
const historyBtn = document.getElementById('historyBtn');
const historySidebar = document.getElementById('historySidebar');
const closeHistoryBtn = document.getElementById('closeHistoryBtn');
const ttsToggle = document.getElementById('ttsToggle');
const modelSelector = document.getElementById('modelSelector');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Add custom title bar for frameless window
    createTitleBar();
    setupEventListeners();
    loadTheme();
    loadTTSStatus(); // Load TTS status
    fetchAvailableModels(); // Load available AI models
    loadModelPreference(); // Load saved model
    displayWelcomeMessage();
});

// ==================== CODE BLOCK HELPERS ====================

/**
 * Parse message text and convert markdown code blocks to HTML
 * Supports both fenced code blocks (```) and inline code (`)
 */
function parseMessageWithCode(text) {
    // Parse fenced code blocks first (```language\ncode\n```)
    // Updated regex to handle both \n and \r\n line endings
    text = text.replace(/```(\w+)?\s*[\r\n]+([\s\S]*?)```/g, (match, language, code) => {
        const lang = language || 'plaintext';
        return `<code-block data-language="${lang}">${escapeHtml(code.trim())}</code-block>`;
    });

    // Parse inline code (`code`)
    text = text.replace(/`([^`]+)`/g, (match, code) => {
        return `<code class="inline-code">${escapeHtml(code)}</code>`;
    });

    // Parse markdown links
    text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" style="color: #4f46e5; text-decoration: underline;">$1</a>');

    // Parse line breaks
    text = text.replace(/\n/g, '<br>');

    return text;
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Create a formatted code block with syntax highlighting and copy button
 */
function createCodeBlock(code, language) {
    const container = document.createElement('div');
    container.className = 'code-block-container';

    // Header with language and copy button
    const header = document.createElement('div');
    header.className = 'code-block-header';

    const langLabel = document.createElement('span');
    langLabel.className = 'code-block-language';
    langLabel.textContent = language || 'plaintext';

    const copyBtn = document.createElement('button');
    copyBtn.className = 'code-copy-btn';
    copyBtn.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
        </svg>
        <span class="copy-text">Copy</span>
    `;
    copyBtn.onclick = () => copyCodeToClipboard(code, copyBtn);

    header.appendChild(langLabel);
    header.appendChild(copyBtn);

    // Code content with syntax highlighting
    const pre = document.createElement('pre');
    const codeElement = document.createElement('code');
    codeElement.className = `language-${language || 'plaintext'}`;
    codeElement.textContent = code;

    // Apply syntax highlighting if hljs is available
    if (window.hljs) {
        try {
            if (language && hljs.getLanguage(language)) {
                codeElement.innerHTML = hljs.highlight(code, { language }).value;
            } else {
                codeElement.innerHTML = hljs.highlightAuto(code).value;
            }
        } catch (e) {
            console.error('Highlight.js error:', e);
        }
    }

    pre.appendChild(codeElement);

    container.appendChild(header);
    container.appendChild(pre);

    return container;
}

/**
 * Copy code to clipboard and show feedback
 */
function copyCodeToClipboard(code, button) {
    navigator.clipboard.writeText(code).then(() => {
        // Visual feedback
        const originalHTML = button.innerHTML;
        button.classList.add('copied');
        button.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            <span class="copy-text">Copied!</span>
        `;

        setTimeout(() => {
            button.classList.remove('copied');
            button.innerHTML = originalHTML;
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy code:', err);
    });
}


// Create Custom Title Bar
function createTitleBar() {
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

    // Insert at beginning of body
    document.body.insertBefore(titleBar, document.body.firstChild);

    // Add window control event listeners
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

// Event Listeners


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
    settingsBtn.addEventListener('click', () => openModal());

    if (closeModalBtn) closeModalBtn.addEventListener('click', () => closeModal());
    if (clearChatBtn) clearChatBtn.addEventListener('click', handleClearChat);
    if (toggleThemeBtn) toggleThemeBtn.addEventListener('click', handleToggleTheme);
    if (aboutBtn) aboutBtn.addEventListener('click', handleAbout);
    if (newChatBtn) newChatBtn.addEventListener('click', handleNewChat);
    if (historyBtn) historyBtn.addEventListener('click', toggleHistory);
    if (closeHistoryBtn) closeHistoryBtn.addEventListener('click', toggleHistory);

    // TTS Toggle Listener
    if (ttsToggle) {
        ttsToggle.addEventListener('change', handleToggleTTS);
    }

    // Dark Mode Toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('change', handleDarkModeToggle);
    }

    // Color Theme Options
    const themeOptions = document.querySelectorAll('.theme-option');
    themeOptions.forEach(option => {
        option.addEventListener('click', () => handleColorThemeChange(option.dataset.theme));
    });

    // Model Selector
    if (modelSelector) {
        modelSelector.addEventListener('change', handleModelChange);
    }

    // Close modal on overlay click
    if (settingsModal) {
        settingsModal.addEventListener('click', (e) => {
            if (e.target === settingsModal) closeModal();
        });
    }
}

// TTS Management
async function loadTTSStatus(retries = 3, delay = 1000) {
    try {
        const response = await fetch(`${API_URL}/settings/tts`);
        if (!response.ok) throw new Error('Failed to fetch TTS status');
        const data = await response.json();

        if (data.status === 'success') {
            const ttsToggle = document.getElementById('ttsToggle');
            if (ttsToggle) ttsToggle.checked = data.enabled;
        }
    } catch (error) {
        console.warn(`Error loading TTS status (retries left: ${retries}):`, error);
        if (retries > 0) {
            setTimeout(() => loadTTSStatus(retries - 1, delay * 2), delay);
        }
    }
}

async function handleToggleTTS() {
    if (!ttsToggle) return;

    const enabled = ttsToggle.checked;
    try {
        const response = await fetch(`${API_URL}/settings/tts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ enabled }),
        });

        const data = await response.json();
        if (data.status !== 'success') {
            // Revert if failed
            ttsToggle.checked = !enabled;
            console.error('Failed to update TTS status:', data.error);
        }
    } catch (error) {
        console.error('Error updating TTS status:', error);
        ttsToggle.checked = !enabled; // Revert
    }
}

// Model Management
async function fetchAvailableModels(retries = 3, delay = 1000) {
    try {
        const response = await fetch(`${API_URL}/models/available`);
        if (!response.ok) throw new Error('Failed to fetch models');

        const data = await response.json();
        if (data.status === 'success') {
            const modelSelector = document.getElementById('modelSelector');
            if (modelSelector) {
                modelSelector.innerHTML = ''; // Clear existing options

                data.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.id;
                    option.textContent = model.name;
                    modelSelector.appendChild(option);
                });

                // Restore selection if valid
                loadModelPreference();
            }
        }
    } catch (error) {
        console.warn(`Error fetching models (retries left: ${retries}):`, error);
        if (retries > 0) {
            setTimeout(() => fetchAvailableModels(retries - 1, delay * 2), delay);
        } else {
            console.error('Failed to load models after retries');
            const modelSelector = document.getElementById('modelSelector');
            if (modelSelector) {
                modelSelector.innerHTML = '<option value="gpt-4o">GPT-4o</option>';
            }
        }
    }
}
function loadModelPreference() {
    const savedModel = localStorage.getItem('selected_ai_model') || 'gpt-4o';
    currentModel = savedModel;

    if (modelSelector) {
        modelSelector.value = savedModel;
    }
}

function handleModelChange(event) {
    const selectedModel = event.target.value;
    currentModel = selectedModel;
    localStorage.setItem('selected_ai_model', selectedModel);
    console.log('Model changed to:', selectedModel);
}

// Resize textarea
function autoResizeTextarea() {
    messageInput.style.height = 'auto';
    messageInput.style.height = messageInput.scrollHeight + 'px';

    // Scrollable class if at max height
    if (messageInput.scrollHeight > 120) {
        messageInput.classList.add('scrollable');
    } else {
        messageInput.classList.remove('scrollable');
    }
}


// Thinking Indicator
function showThinkingIndicator() {
    // Remove existing if any (cleanup)
    removeThinkingIndicator();

    const messageWrapper = document.createElement('div');
    messageWrapper.className = 'message-wrapper';

    const message = document.createElement('div');
    message.className = 'message aria';
    message.id = 'thinking-indicator-message';

    // Avatar
    const avatar = document.createElement('div');
    avatar.className = 'avatar active'; // Active to show glow
    const avatarImg = document.createElement('img');
    avatarImg.src = 'aria_logo.png';
    avatarImg.alt = 'Aria';
    avatar.appendChild(avatarImg);
    message.appendChild(avatar);

    // Bubble
    const bubble = document.createElement('div');
    bubble.className = 'bubble';

    // Dots
    const dots = document.createElement('div');
    dots.className = 'thinking-dots';
    dots.innerHTML = `
        <div class="thinking-dot"></div>
        <div class="thinking-dot"></div>
        <div class="thinking-dot"></div>
    `;

    bubble.appendChild(dots);
    messageWrapper.appendChild(bubble);
    message.appendChild(messageWrapper);
    chatContainer.appendChild(message);

    // Scroll
    setTimeout(() => {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 10);
}

function removeThinkingIndicator() {
    const message = document.getElementById('thinking-indicator-message');
    if (message) {
        message.remove();
    }
}

// Message Handling
async function handleSendMessage() {
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

    // Show thinking indicator
    showThinkingIndicator();

    // Send to backend
    await sendMessageToBackend(message);
}

async function sendMessageToBackend(message) {
    try {
        const payload = { message, model: currentModel };
        if (currentConversationId) {
            payload.conversation_id = currentConversationId;
        }

        const response = await fetch(`${API_URL}/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        const data = await response.json();

        // Remove thinking indicator before showing response
        removeThinkingIndicator();

        if (data.status === 'success') {
            if (data.conversation_id) {
                currentConversationId = data.conversation_id;
            }

            if (data.response) {
                console.log('DEBUG: Received response from backend. UI Action:', data.ui_action);
                addMessage(data.response, 'aria', data.ui_action);
            }
        }
    } catch (error) {
        console.error('Error sending message:', error);
        removeThinkingIndicator(); // Ensure it's removed on error
        addMessage('Sorry, I encountered an error. Please make sure the backend is running.', 'aria');
    }
}

function addMessage(text, sender, uiAction = null) {
    const messageWrapper = document.createElement('div');
    messageWrapper.className = 'message-wrapper';

    const message = document.createElement('div');
    message.className = `message ${sender}`;

    if (sender === 'aria') {
        // Remove active class from previous avatars
        const previousActive = document.querySelectorAll('.message.aria .avatar.active');
        previousActive.forEach(el => el.classList.remove('active'));

        // Add Avatar for Aria with logo
        const avatar = document.createElement('div');
        avatar.className = 'avatar'; // Start inactive
        const avatarImg = document.createElement('img');
        avatarImg.src = 'aria_logo.png';
        avatarImg.alt = 'Aria';
        avatar.appendChild(avatarImg);
        message.appendChild(avatar);

        // Calculate duration based on text length (approx 400ms per word, min 2s)
        const wordCount = text.split(/\s+/).length;
        const duration = Math.max(2000, wordCount * 400);

        // Start animation after slight delay to sync with TTS generation (approx 500ms)
        setTimeout(() => {
            avatar.classList.add('active');

            // Remove active class after duration
            setTimeout(() => {
                avatar.classList.remove('active');
            }, duration);
        }, 500);
    }

    // Message bubble
    const bubble = document.createElement('div');
    bubble.className = 'bubble';

    if (sender === 'aria') {
        // Parse Markdown for Aria's messages with code block support
        console.log('🔍 DEBUG: Parsing message, has window.api.parseMarkdown?', !!(window.api && window.api.parseMarkdown));
        console.log('🔍 DEBUG: Message text:', text.substring(0, 100));

        try {
            // Always use our custom parser for code block support
            const parsed = parseMessageWithCode(text);
            console.log('🔍 DEBUG: Parsed HTML:', parsed.substring(0, 200));
            bubble.innerHTML = parsed;

            // Replace code-block placeholders with actual formatted code blocks
            const codeBlockPlaceholders = bubble.querySelectorAll('code-block');
            console.log('🔍 DEBUG: Found code blocks:', codeBlockPlaceholders.length);
            codeBlockPlaceholders.forEach(placeholder => {
                const code = placeholder.textContent;
                const language = placeholder.getAttribute('data-language');
                console.log('🔍 DEBUG: Creating code block for language:', language);
                const codeBlock = createCodeBlock(code, language);
                placeholder.replaceWith(codeBlock);
            });
        } catch (e) {
            console.error('❌ Error parsing markdown:', e);
            // Fallback to plain text
            bubble.textContent = text;
        }

        // Handle UI Actions (email confirmation)
        console.log('DEBUG: Checking for UI Action in addMessage:', uiAction);
        if (uiAction && uiAction.type === 'email_confirmation') {
            console.log('DEBUG: Rendering email confirmation UI');
            const emailPreview = document.createElement('div');
            emailPreview.className = 'email-preview';

            // To field
            const toField = document.createElement('div');
            toField.className = 'email-field';
            toField.innerHTML = `<span class="email-label">To:</span> <span class="email-value">${uiAction.data.to}</span>`;

            // Subject field
            const subjectField = document.createElement('div');
            subjectField.className = 'email-field';
            subjectField.innerHTML = `<span class="email-label">Subject:</span> <span class="email-value">${uiAction.data.subject}</span>`;

            // Editable body
            const bodyLabel = document.createElement('div');
            bodyLabel.className = 'email-label';
            bodyLabel.textContent = 'Body:';
            bodyLabel.style.marginTop = '12px';
            bodyLabel.style.marginBottom = '6px';

            const bodyTextarea = document.createElement('textarea');
            bodyTextarea.className = 'email-body-editor';
            bodyTextarea.value = uiAction.data.body || '';
            bodyTextarea.rows = 8;

            // Action buttons
            const buttonContainer = document.createElement('div');
            buttonContainer.className = 'message-actions';

            const confirmBtn = document.createElement('button');
            confirmBtn.className = 'action-btn confirm';
            confirmBtn.textContent = 'Send Email';
            confirmBtn.onclick = () => {
                const editedBody = bodyTextarea.value;
                addMessage('Yes, send it.', 'user');
                sendMessageToBackend('Yes');
                emailPreview.remove();
            };

            const cancelBtn = document.createElement('button');
            cancelBtn.className = 'action-btn cancel';
            cancelBtn.textContent = 'Cancel';
            cancelBtn.onclick = () => {
                addMessage('No, cancel.', 'user');
                sendMessageToBackend('No');
                emailPreview.remove();
            };

            buttonContainer.appendChild(confirmBtn);
            buttonContainer.appendChild(cancelBtn);

            emailPreview.appendChild(toField);
            emailPreview.appendChild(subjectField);
            emailPreview.appendChild(bodyLabel);
            emailPreview.appendChild(bodyTextarea);
            emailPreview.appendChild(buttonContainer);

            bubble.appendChild(emailPreview);
        }
    } else {
        // Plain text for user messages (security)
        bubble.textContent = text;
    }

    messageWrapper.appendChild(bubble);
    message.appendChild(messageWrapper);
    chatContainer.appendChild(message);

    // Scroll to bottom
    setTimeout(() => {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 10);
}

function animateSendButton() {
    sendBtn.style.transform = 'scale(0.9)';
    setTimeout(() => {
        sendBtn.style.transform = 'scale(1)';
    }, 100);
}


// Voice Mode
async function handleToggleVoice() {
    voiceModeActive = !voiceModeActive;

    if (voiceModeActive) {
        voiceBtn.classList.add('active');
        addMessage('🎙️ Voice mode active - Say "Aria" to start', 'aria');

        // Start voice listening
        try {
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
            showThinkingIndicator();
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

function handleDarkModeToggle() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    currentTheme = darkModeToggle.checked ? 'dark' : 'light';
    applyTheme(currentTheme);
    saveTheme(currentTheme);
}

function handleColorThemeChange(theme) {
    currentColorTheme = theme;
    document.body.setAttribute('data-color-theme', theme);

    // Update active state
    document.querySelectorAll('.theme-option').forEach(opt => {
        opt.classList.remove('active');
    });
    const selectedOption = document.querySelector(`.theme-option[data-theme="${theme}"]`);
    if (selectedOption) {
        selectedOption.classList.add('active');
    }

    // Save preference
    localStorage.setItem('colorTheme', theme);
}

function applyTheme(theme) {
    document.body.setAttribute('data-theme', theme);
    if (themeIcon && themeText) {
        themeIcon.textContent = theme === 'light' ? '🌙' : '☀️';
        themeText.textContent = theme === 'light' ? 'Dark Mode' : 'Light Mode';
    }

    // Update dark mode toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.checked = theme === 'dark';
    }
}


function loadTheme() {
    // Load dark/light mode
    const savedTheme = localStorage.getItem('theme') || 'light';
    currentTheme = savedTheme;
    applyTheme(currentTheme);

    // Load color theme
    const savedColorTheme = localStorage.getItem('colorTheme') || 'violet';
    currentColorTheme = savedColorTheme;
    document.body.setAttribute('data-color-theme', savedColorTheme);

    // Update UI
    document.querySelectorAll('.theme-option').forEach(opt => {
        opt.classList.remove('active');
    });
    const savedOption = document.querySelector(`.theme-option[data-theme="${savedColorTheme}"]`);
    if (savedOption) {
        savedOption.classList.add('active');
    }
}

function saveTheme(theme) {
    localStorage.setItem('theme', theme);
}


// Settings Management
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

async function handleNewChat() {
    console.log('New Chat clicked');
    try {
        const response = await fetch(`${API_URL}/conversation/new`, { method: 'POST' });
        const data = await response.json();

        if (data.status === 'success') {
            currentConversationId = data.conversation_id;
            chatContainer.innerHTML = '';
            addMessage('✨ New chat started! How can I help you?', 'aria');

            // Refresh history if open
            if (historySidebar.classList.contains('active')) {
                loadHistory();
            }
        }
    } catch (error) {
        console.error('Error creating new chat:', error);
        addMessage('Error starting new chat.', 'aria');
    }
}


function toggleHistory() {
    console.log('History toggled');
    historySidebar.classList.toggle('active');

    if (historySidebar.classList.contains('active')) {
        loadHistory();
    }
}

async function loadHistory() {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = '<div class="loading">Loading...</div>';

    try {
        const response = await fetch(`${API_URL}/conversations?limit=20`);
        const data = await response.json();

        if (data.status === 'success') {
            renderHistory(data.conversations);
        } else {
            historyList.innerHTML = '<div class="error">Failed to load history</div>';
        }
    } catch (error) {
        console.error('Error loading history:', error);
        historyList.innerHTML = '<div class="error">Error loading history</div>';
    }
}

function renderHistory(conversations) {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = '';

    if (conversations.length === 0) {
        historyList.innerHTML = '<div class="empty-history">No conversations yet</div>';
        return;
    }

    conversations.forEach(conv => {
        const item = document.createElement('div');
        item.className = `history-item ${conv._id === currentConversationId ? 'active' : ''}`;
        item.onclick = () => loadConversation(conv._id);

        const titleSpan = document.createElement('span');
        titleSpan.className = 'history-title';
        titleSpan.textContent = conv.title || 'New Conversation';

        // Actions container
        const actions = document.createElement('div');
        actions.className = 'history-actions';

        // Rename button
        const renameBtn = document.createElement('button');
        renameBtn.className = 'action-btn';
        renameBtn.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>';
        renameBtn.onclick = (e) => {
            e.stopPropagation();
            handleRenameConversation(conv._id, conv.title);
        };

        // Delete button
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'action-btn delete';
        deleteBtn.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            handleDeleteConversation(conv._id);
        };

        actions.appendChild(renameBtn);
        actions.appendChild(deleteBtn);

        item.appendChild(titleSpan);
        item.appendChild(actions);
        historyList.appendChild(item);
    });
}

async function loadConversation(conversationId) {
    try {
        const response = await fetch(`${API_URL}/conversation/${conversationId}`);
        const data = await response.json();

        if (data.status === 'success') {
            currentConversationId = conversationId;
            chatContainer.innerHTML = '';

            // Update active state in sidebar
            document.querySelectorAll('.history-item').forEach(el => el.classList.remove('active'));
            // Re-render history to update active class properly or just reload
            loadHistory();

            // Render messages
            data.conversation.messages.forEach(msg => {
                addMessage(msg.content, msg.role === 'assistant' ? 'aria' : 'user');
            });

            // Close sidebar on mobile/narrow screens if needed
            historySidebar.classList.remove('active');
        }
    } catch (error) {
        console.error('Error loading conversation:', error);
    }
}

async function handleRenameConversation(id, currentTitle) {
    const newTitle = await window.electronAPI.showRenameDialog(currentTitle || '');
    if (newTitle && newTitle !== currentTitle) {
        try {
            const response = await fetch(`${API_URL}/conversation/${id}/rename`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: newTitle })
            });

            if (response.ok) {
                loadHistory(); // Refresh list
            }
        } catch (error) {
            console.error('Error renaming:', error);
        }
    }
}

async function handleDeleteConversation(id) {
    const confirmed = await window.electronAPI.showDeleteDialog();
    if (!confirmed) return;

    try {
        const response = await fetch(`${API_URL}/conversation/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            if (currentConversationId === id) {
                currentConversationId = null;
                chatContainer.innerHTML = '';
                addMessage('Conversation deleted.', 'aria');
            }
            loadHistory();
        }
    } catch (error) {
        console.error('Error deleting:', error);
    }
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
            "Your digital workspace is prepared."
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
            "Let's turn night into opportunity."
        ]
    };

    // Pick a random context message
    const messages = contextMessages[timeOfDay];
    const contextMsg = messages[Math.floor(Math.random() * messages.length)];

    return greeting + contextMsg;
}


// Welcome Message
function displayWelcomeMessage() {
    // Display local greeting immediately
    const greeting = getTimeBasedGreeting();
    addMessage(greeting, 'aria');

    // Optionally try to sync with backend for TTS (non-blocking)
    setTimeout(async () => {
        try {
            await fetch(`${API_URL}/greeting`);
        } catch (error) {
            console.log('Backend greeting skipped:', error.message);
        }
    }, 100);
}

// Export for debugging
window.AriaApp = {
    addMessage,
    handleSendMessage,
    handleToggleVoice,
    handleToggleTheme
};
