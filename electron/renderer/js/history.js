import { state } from './state.js';

const BASE_URL = 'http://localhost:8000';

/**
 * Format timestamp to readable format
 */
function formatTimestamp(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    // Format as date for older items
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

/**
 * Load and display conversation history
 */
export async function loadConversationHistory() {
    const historyList = document.getElementById('historyList');
    if (!historyList) return;

    // Show loading state
    historyList.innerHTML = `
        <div class="history-loading">
            <div class="loading-spinner"></div>
            <p>Loading conversations...</p>
        </div>
    `;

    try {
        const response = await fetch(`${BASE_URL}/conversations?limit=20`);
        const data = await response.json();

        if (data.status === 'success' && data.conversations) {
            renderHistoryList(data.conversations);
        } else {
            showEmptyState();
        }
    } catch (error) {
        console.error('Error loading conversation history:', error);
        showErrorState();
    }
}

/**
 * Render the list of conversations
 */
/**
 * Render the list of conversations
 */
function renderHistoryList(conversations) {
    const historyList = document.getElementById('historyList');
    if (!historyList) return;

    if (!conversations || conversations.length === 0) {
        showEmptyState();
        return;
    }

    historyList.innerHTML = '';

    conversations.forEach((conv, index) => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.style.animationDelay = `${index * 0.05}s`;

        // Check if this is the current conversation
        const isActive = state.currentConversationId === conv._id;
        if (isActive) {
            historyItem.classList.add('active');
        }

        historyItem.innerHTML = `
            <div class="history-content">
                <div class="history-title">${escapeHtml(conv.title)}</div>
                <div class="history-timestamp">${formatTimestamp(conv.updated_at)}</div>
            </div>
            <div class="history-actions">
                <button class="more-options-btn" title="More options">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="1"></circle>
                        <circle cx="19" cy="12" r="1"></circle>
                        <circle cx="5" cy="12" r="1"></circle>
                    </svg>
                </button>
                <div class="history-dropdown">
                    <button class="dropdown-item rename-btn">
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
                        </svg>
                        Rename
                    </button>
                    <button class="dropdown-item delete-btn delete">
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="3 6 5 6 21 6"></polyline>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        </svg>
                        Delete
                    </button>
                </div>
            </div>
        `;

        // Add click handler to load conversation
        historyItem.addEventListener('click', (e) => {
            if (!e.target.closest('.history-actions')) {
                loadConversation(conv._id);
            }
        });

        // Dropdown toggle logic
        const moreBtn = historyItem.querySelector('.more-options-btn');
        const dropdown = historyItem.querySelector('.history-dropdown');
        const actionsContainer = historyItem.querySelector('.history-actions');

        moreBtn.addEventListener('click', (e) => {
            e.stopPropagation();

            // Close all other dropdowns
            document.querySelectorAll('.history-dropdown.active').forEach(d => {
                if (d !== dropdown) {
                    d.classList.remove('active');
                    d.closest('.history-actions').classList.remove('active');
                    d.closest('.more-options-btn')?.classList.remove('active');
                }
            });

            dropdown.classList.toggle('active');
            actionsContainer.classList.toggle('active');
            moreBtn.classList.toggle('active');
        });

        // Add rename handler
        const renameBtn = historyItem.querySelector('.rename-btn');
        renameBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdown.classList.remove('active');
            promptRenameConversation(conv._id, conv.title);
        });

        // Add delete handler
        const deleteBtn = historyItem.querySelector('.delete-btn');
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdown.classList.remove('active');
            confirmDeleteConversation(conv._id, conv.title);
        });

        historyList.appendChild(historyItem);
    });

    // Global click listener to close dropdowns
    // Remove existing listener to avoid duplicates if called multiple times
    if (!window.historyDropdownListenerAdded) {
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.history-actions')) {
                document.querySelectorAll('.history-dropdown.active').forEach(d => {
                    d.classList.remove('active');
                    d.closest('.history-actions').classList.remove('active');
                    d.closest('.more-options-btn')?.classList.remove('active');
                });
            }
        });
        window.historyDropdownListenerAdded = true;
    }
}

/**
 * Load a specific conversation
 */
export async function loadConversation(conversationId) {
    try {
        const response = await fetch(`${BASE_URL}/conversation/${conversationId}`);
        const data = await response.json();

        if (data.status === 'success' && data.conversation) {
            // Clear current chat
            const chatContainer = document.getElementById('chatContainer');
            if (chatContainer) {
                chatContainer.innerHTML = '';
            }

            // Set current conversation ID
            state.currentConversationId = conversationId;

            // Load messages (import addMessage from chat.js)
            const { addMessage } = await import('./chat.js');

            const messages = data.conversation.messages || [];
            messages.forEach(msg => {
                addMessage(msg.content, msg.role === 'user' ? 'user' : 'aria');
            });

            // Close history sidebar
            const historySidebar = document.getElementById('historySidebar');
            if (historySidebar) {
                historySidebar.classList.remove('active');
            }

            // Update active state in history list
            document.querySelectorAll('.history-item').forEach(item => {
                item.classList.remove('active');
            });
            const activeItem = document.querySelector(`.history-item [data-id="${conversationId}"]`)?.closest('.history-item');
            if (activeItem) {
                activeItem.classList.add('active');
            }
        }
    } catch (error) {
        console.error('Error loading conversation:', error);
        alert('Failed to load conversation. Please try again.');
    }
}

let conversationToRenameId = null;
let conversationToDeleteId = null;
let modalsInitialized = false;

/**
 * Initialize modal event listeners
 */
function initializeHistoryModals() {
    if (modalsInitialized) return;

    const renameModal = document.getElementById('renameModal');
    const deleteModal = document.getElementById('deleteModal');
    const renameInput = document.getElementById('renameInput');

    // Rename Modal Buttons
    document.getElementById('cancelRenameBtn')?.addEventListener('click', () => {
        renameModal.classList.remove('active');
        conversationToRenameId = null;
    });

    document.getElementById('confirmRenameBtn')?.addEventListener('click', async () => {
        if (conversationToRenameId && renameInput.value.trim()) {
            await renameConversation(conversationToRenameId, renameInput.value.trim());
            renameModal.classList.remove('active');
            conversationToRenameId = null;
        }
    });

    // Delete Modal Buttons
    document.getElementById('cancelDeleteBtn')?.addEventListener('click', () => {
        deleteModal.classList.remove('active');
        conversationToDeleteId = null;
    });

    document.getElementById('confirmDeleteBtn')?.addEventListener('click', async () => {
        if (conversationToDeleteId) {
            await deleteConversation(conversationToDeleteId);
            deleteModal.classList.remove('active');
            conversationToDeleteId = null;
        }
    });

    // Close on overlay click
    renameModal?.addEventListener('click', (e) => {
        if (e.target === renameModal) renameModal.classList.remove('active');
    });

    deleteModal?.addEventListener('click', (e) => {
        if (e.target === deleteModal) deleteModal.classList.remove('active');
    });

    modalsInitialized = true;
}

/**
 * Prompt user to rename a conversation
 */
function promptRenameConversation(conversationId, currentTitle) {
    initializeHistoryModals(); // Ensure listeners are attached
    const renameModal = document.getElementById('renameModal');
    const renameInput = document.getElementById('renameInput');

    if (renameModal && renameInput) {
        conversationToRenameId = conversationId;
        renameInput.value = currentTitle;
        renameModal.classList.add('active');
        renameInput.focus();
    }
}

/**
 * Rename a conversation
 */
async function renameConversation(conversationId, newTitle) {
    try {
        const response = await fetch(`${BASE_URL}/conversation/${conversationId}/rename`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title: newTitle }),
        });

        const data = await response.json();

        if (data.status === 'success') {
            // Reload history to show updated title
            await loadConversationHistory();
        } else {
            alert('Failed to rename conversation.');
        }
    } catch (error) {
        console.error('Error renaming conversation:', error);
        alert('Failed to rename conversation. Please try again.');
    }
}

/**
 * Confirm and delete a conversation
 */
function confirmDeleteConversation(conversationId, title) {
    initializeHistoryModals(); // Ensure listeners are attached
    const deleteModal = document.getElementById('deleteModal');

    if (deleteModal) {
        conversationToDeleteId = conversationId;
        deleteModal.classList.add('active');
    }
}

/**
 * Delete a conversation
 */
async function deleteConversation(conversationId) {
    try {
        const response = await fetch(`${BASE_URL}/conversation/${conversationId}`, {
            method: 'DELETE',
        });

        const data = await response.json();

        if (data.status === 'success') {
            // If this was the current conversation, clear it
            if (state.currentConversationId === conversationId) {
                state.currentConversationId = null;
                const chatContainer = document.getElementById('chatContainer');
                if (chatContainer) {
                    chatContainer.innerHTML = '';
                }
                // Show welcome message
                const { addMessage } = await import('./chat.js');
                addMessage('Hello! I am Aria. How can I help you today?', 'aria');
            }

            // Reload history
            await loadConversationHistory();
        } else {
            alert('Failed to delete conversation.');
        }
    } catch (error) {
        console.error('Error deleting conversation:', error);
        alert('Failed to delete conversation. Please try again.');
    }
}

/**
 * Show empty state
 */
function showEmptyState() {
    const historyList = document.getElementById('historyList');
    if (!historyList) return;

    historyList.innerHTML = `
        <div class="history-empty">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            <p>No conversations yet</p>
            <span>Start chatting to see your history here</span>
        </div>
    `;
}

/**
 * Show error state
 */
function showErrorState() {
    const historyList = document.getElementById('historyList');
    if (!historyList) return;

    historyList.innerHTML = `
        <div class="history-empty">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <p>Failed to load conversations</p>
            <span>Please check your connection and try again</span>
        </div>
    `;
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
