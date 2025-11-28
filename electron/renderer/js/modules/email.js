/**
 * Email Module - Gmail integration for composing and sending emails
 */

import { API_URL } from '../config.js';

let emailModal = null;
let confirmationModal = null;
let currentDraft = null;

/**
 * Initialize the Email Module
 */
export async function initEmailModule() {
    console.log('📧 Initializing Email Module...');

    try {
        // Load email components
        await loadEmailComponents();

        // Setup event listeners
        setupEmailEventListeners();

        // Add email button to header (optional)
        addEmailButtonToHeader();

        console.log('✅ Email Module initialized successfully');
        return { success: true };

    } catch (error) {
        console.error('❌ Failed to initialize Email Module:', error);
        throw error;
    }
}

/**
 * Load email HTML components
 */
async function loadEmailComponents() {
    try {
        // Load compose modal
        const composeResponse = await fetch('components/email-compose.html');
        const composeHTML = await composeResponse.text();

        // Load confirmation modal
        const confirmResponse = await fetch('components/email-confirmation.html');
        const confirmHTML = await confirmResponse.text();

        // Append to body
        const container = document.createElement('div');
        container.innerHTML = composeHTML + confirmHTML;
        document.body.appendChild(container);

        // Get modal references
        emailModal = document.getElementById('emailComposeModal');
        confirmationModal = document.getElementById('emailConfirmationModal');

    } catch (error) {
        console.error('Failed to load email components:', error);
        throw error;
    }
}

/**
 * Setup event listeners for email modals
 */
function setupEmailEventListeners() {
    // Compose modal buttons
    const closeComposeBtn = document.getElementById('closeEmailComposeBtn');
    const cancelBtn = document.getElementById('emailCancelBtn');
    const saveDraftBtn = document.getElementById('emailSaveDraftBtn');
    const composeForm = document.getElementById('emailComposeForm');

    if (closeComposeBtn) closeComposeBtn.addEventListener('click', closeEmailCompose);
    if (cancelBtn) cancelBtn.addEventListener('click', closeEmailCompose);
    if (saveDraftBtn) saveDraftBtn.addEventListener('click', saveDraft);
    if (composeForm) composeForm.addEventListener('submit', handlePreview);

    // Confirmation modal buttons
    const closeConfirmBtn = document.getElementById('closeEmailConfirmationBtn');
    const editBtn = document.getElementById('emailEditBtn');
    const confirmCancelBtn = document.getElementById('emailConfirmCancelBtn');
    const sendBtn = document.getElementById('emailSendBtn');

    if (closeConfirmBtn) closeConfirmBtn.addEventListener('click', closeEmailConfirmation);
    if (editBtn) editBtn.addEventListener('click', handleEdit);
    if (confirmCancelBtn) confirmCancelBtn.addEventListener('click', closeEmailConfirmation);
    if (sendBtn) sendBtn.addEventListener('click', handleSend);

    // Close on outside click
    if (emailModal) {
        emailModal.addEventListener('click', (e) => {
            if (e.target === emailModal) closeEmailCompose();
        });
    }

    if (confirmationModal) {
        confirmationModal.addEventListener('click', (e) => {
            if (e.target === confirmationModal) closeEmailConfirmation();
        });
    }
}

/**
 * Add email compose button to header
 */
function addEmailButtonToHeader() {
    const header = document.querySelector('.header-left') || document.querySelector('header');
    if (!header) return;

    const emailBtn = document.createElement('button');
    emailBtn.id = 'composeEmailBtn';
    emailBtn.className = 'icon-btn';
    emailBtn.innerHTML = '✉️';
    emailBtn.title = 'Compose Email';
    emailBtn.setAttribute('aria-label', 'Compose Email');
    emailBtn.addEventListener('click', openEmailCompose);

    header.appendChild(emailBtn);
}

/**
 * Open email compose modal
 */
export function openEmailCompose(recipient = '', subject = '', body = '') {
    if (!emailModal) {
        console.error('Email modal not initialized');
        return;
    }

    // Pre-fill fields if provided
    const toInput = document.getElementById('emailTo');
    const subjectInput = document.getElementById('emailSubject');
    const bodyInput = document.getElementById('emailBody');

    if (toInput) toInput.value = recipient;
    if (subjectInput) subjectInput.value = subject;
    if (bodyInput) bodyInput.value = body;

    emailModal.classList.add('active');
}

/**
 * Close email compose modal
 */
function closeEmailCompose() {
    if (emailModal) {
        emailModal.classList.remove('active');
        // Clear form
        const form = document.getElementById('emailComposeForm');
        if (form) form.reset();
    }
}

/**
 * Save email as draft
 */
function saveDraft() {
    const to = document.getElementById('emailTo').value;
    const subject = document.getElementById('emailSubject').value;
    const body = document.getElementById('emailBody').value;

    currentDraft = { to, subject, body };
    localStorage.setItem('emailDraft', JSON.stringify(currentDraft));

    showNotification('Draft saved!', 'success');
}

/**
 * Handle preview button (form submit)
 */
function handlePreview(e) {
    e.preventDefault();

    const to = document.getElementById('emailTo').value;
    const subject = document.getElementById('emailSubject').value;
    const body = document.getElementById('emailBody').value;

    if (!to || !subject || !body) {
        showNotification('Please fill in all fields', 'error');
        return;
    }

    // Save current draft
    currentDraft = { to, subject, body };

    // Show preview
    showEmailPreview(to, subject, body);

    // Close compose modal
    closeEmailCompose();
}

/**
 * Show email preview in confirmation modal
 */
function showEmailPreview(to, subject, body) {
    if (!confirmationModal) return;

    document.getElementById('emailPreviewTo').textContent = to;
    document.getElementById('emailPreviewSubject').textContent = subject;
    document.getElementById('emailPreviewBody').textContent = body;

    confirmationModal.classList.add('active');
}

/**
 * Close email confirmation modal
 */
function closeEmailConfirmation() {
    if (confirmationModal) {
        confirmationModal.classList.remove('active');
        hideEmailStatus();
    }
}

/**
 * Handle edit button - go back to compose
 */
function handleEdit() {
    closeEmailConfirmation();

    if (currentDraft) {
        openEmailCompose(currentDraft.to, currentDraft.subject, currentDraft.body);
    }
}

/**
 * Handle send button - actually send the email
 */
async function handleSend() {
    if (!currentDraft) return;

    const sendBtn = document.getElementById('emailSendBtn');
    if (sendBtn) {
        sendBtn.disabled = true;
        sendBtn.textContent = '📤 Sending...';
    }

    showEmailStatus('Sending email...', 'loading');

    try {
        const response = await fetch(`${API_URL}/email/send`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                to: currentDraft.to,
                subject: currentDraft.subject,
                body: currentDraft.body
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            showEmailStatus('✅ Email sent successfully!', 'success');

            // Clear draft
            currentDraft = null;
            localStorage.removeItem('emailDraft');

            // Close modal after 2 seconds
            setTimeout(() => {
                closeEmailConfirmation();
            }, 2000);

        } else {
            showEmailStatus('❌ Failed to send email: ' + (data.error || 'Unknown error'), 'error');
        }

    } catch (error) {
        console.error('Error sending email:', error);
        showEmailStatus('❌ Failed to send email: ' + error.message, 'error');
    } finally {
        if (sendBtn) {
            sendBtn.disabled = false;
            sendBtn.textContent = '📤 Send Email';
        }
    }
}

/**
 * Show email status message
 */
function showEmailStatus(message, type) {
    const statusDiv = document.getElementById('emailStatus');
    const messageDiv = statusDiv?.querySelector('.status-message');

    if (!statusDiv || !messageDiv) return;

    messageDiv.textContent = message;
    statusDiv.className = `email-status ${type}`;
    statusDiv.style.display = 'block';
}

/**
 * Hide email status message
 */
function hideEmailStatus() {
    const statusDiv = document.getElementById('emailStatus');
    if (statusDiv) {
        statusDiv.style.display = 'none';
    }
}

/**
 * Show notification (using existing chat notification or custom)
 */
function showNotification(message, type) {
    console.log(`[${type}] ${message}`);
    // You can enhance this to show a toast notification
}
