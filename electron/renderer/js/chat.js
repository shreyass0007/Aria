import { parseMessageWithCode, createCodeBlock } from './markdown.js';
import { sendToBackend } from './api.js';

export function addMessage(text, sender, uiAction = null) {
    const chatContainer = document.getElementById('chatContainer');
    const messageWrapper = document.createElement('div');
    messageWrapper.className = 'message-wrapper';

    const message = document.createElement('div');
    message.className = `message ${sender}`;

    if (sender === 'aria') {
        const previousActive = document.querySelectorAll('.message.aria .avatar.active');
        previousActive.forEach(el => el.classList.remove('active'));

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        const avatarImg = document.createElement('img');
        avatarImg.src = 'aria_logo.png';
        avatarImg.alt = 'Aria';
        avatar.appendChild(avatarImg);
        message.appendChild(avatar);

        const wordCount = text.split(/\s+/).length;
        const duration = Math.max(2000, wordCount * 400);

        setTimeout(() => {
            avatar.classList.add('active');
            setTimeout(() => {
                avatar.classList.remove('active');
            }, duration);
        }, 500);
    }

    const bubble = document.createElement('div');
    bubble.className = 'bubble';

    if (sender === 'aria') {
        try {
            let parsedHtml = text;
            if (window.api && window.api.parseMarkdown) {
                parsedHtml = window.api.parseMarkdown(text);

                // If API parser failed to parse code blocks (left raw backticks), use local parser
                if (parsedHtml.includes('```')) {
                    console.log('⚠️ API parser left raw backticks, using local fallback');
                    parsedHtml = parseMessageWithCode(text);
                }
            } else {
                parsedHtml = parseMessageWithCode(text);
            }

            bubble.innerHTML = parsedHtml;

            const preBlocks = bubble.querySelectorAll('pre code');
            preBlocks.forEach(codeElement => {
                const preElement = codeElement.parentElement;
                const code = codeElement.textContent;
                let language = 'plaintext';
                codeElement.classList.forEach(cls => {
                    if (cls.startsWith('language-')) {
                        language = cls.replace('language-', '');
                    }
                });
                const customBlock = createCodeBlock(code, language);
                preElement.replaceWith(customBlock);
            });

            // Handle custom <code-block> elements from fallback parser
            const customBlocks = bubble.querySelectorAll('code-block');
            customBlocks.forEach(block => {
                const language = block.getAttribute('data-language');
                const code = block.textContent; // textContent decodes HTML entities
                const customBlock = createCodeBlock(code, language);
                block.replaceWith(customBlock);
            });

        } catch (e) {
            console.error('Error parsing markdown:', e);
            bubble.textContent = text;
        }

        if (uiAction && uiAction.type === 'email_confirmation') {
            const emailPreview = document.createElement('div');
            emailPreview.className = 'email-preview';

            const toField = document.createElement('div');
            toField.className = 'email-field';
            toField.innerHTML = `<span class="email-label">To:</span> <span class="email-value">${uiAction.data.to}</span>`;

            const subjectField = document.createElement('div');
            subjectField.className = 'email-field';
            subjectField.innerHTML = `<span class="email-label">Subject:</span> <span class="email-value">${uiAction.data.subject}</span>`;

            const bodyLabel = document.createElement('div');
            bodyLabel.className = 'email-label';
            bodyLabel.textContent = 'Body:';
            bodyLabel.style.marginTop = '12px';
            bodyLabel.style.marginBottom = '6px';

            const bodyTextarea = document.createElement('textarea');
            bodyTextarea.className = 'email-body-editor';
            bodyTextarea.value = uiAction.data.body || '';
            bodyTextarea.rows = 8;

            const buttonContainer = document.createElement('div');
            buttonContainer.className = 'message-actions';

            const confirmBtn = document.createElement('button');
            confirmBtn.className = 'action-btn confirm';
            confirmBtn.textContent = 'Send Email';
            confirmBtn.onclick = async () => {
                // const editedBody = bodyTextarea.value; // Not used in backend call currently?
                addMessage('Yes, send it.', 'user');
                const data = await sendToBackend('Yes');
                emailPreview.remove();
                if (data.response) {
                    addMessage(data.response, 'aria', data.ui_action);
                }
            };

            const cancelBtn = document.createElement('button');
            cancelBtn.className = 'action-btn cancel';
            cancelBtn.textContent = 'Cancel';
            cancelBtn.onclick = async () => {
                addMessage('No, cancel.', 'user');
                const data = await sendToBackend('No');
                emailPreview.remove();
                if (data.response) {
                    addMessage(data.response, 'aria', data.ui_action);
                }
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
        bubble.textContent = text;
    }

    messageWrapper.appendChild(bubble);
    message.appendChild(messageWrapper);
    chatContainer.appendChild(message);

    setTimeout(() => {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 10);
}

export function showThinkingIndicator() {
    removeThinkingIndicator();
    const chatContainer = document.getElementById('chatContainer');

    const messageWrapper = document.createElement('div');
    messageWrapper.className = 'message-wrapper';

    const message = document.createElement('div');
    message.className = 'message aria';
    message.id = 'thinking-indicator-message';

    const avatar = document.createElement('div');
    avatar.className = 'avatar active';
    const avatarImg = document.createElement('img');
    avatarImg.src = 'aria_logo.png';
    avatarImg.alt = 'Aria';
    avatar.appendChild(avatarImg);
    message.appendChild(avatar);

    const bubble = document.createElement('div');
    bubble.className = 'bubble';

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

    setTimeout(() => {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 10);
}

export function removeThinkingIndicator() {
    const message = document.getElementById('thinking-indicator-message');
    if (message) {
        message.remove();
    }
}

export function animateSendButton() {
    const sendBtn = document.getElementById('sendBtn');
    if (sendBtn) {
        sendBtn.style.transform = 'scale(0.9)';
        setTimeout(() => {
            sendBtn.style.transform = 'scale(1)';
        }, 100);
    }
}
