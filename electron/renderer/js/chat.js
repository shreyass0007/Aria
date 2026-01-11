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

            if (window.marked) {
                try {
                    // Configure marked to handle line breaks and GFM
                    const markedParser = window.marked.parse || window.marked;
                    parsedHtml = markedParser(text, {
                        breaks: true,
                        gfm: true
                    });
                } catch (err) {
                    console.error('Error using marked library:', err);
                    // Fallback to basic parser
                    parsedHtml = parseMessageWithCode(text);
                }
            } else if (window.api && window.api.parseMarkdown) {
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

            // --- Citation Processing ---
            // Convert [1], [2] to clickable citations <span class="citation-link" onclick="window.highlightExSource(1)">1</span>
            bubble.innerHTML = bubble.innerHTML.replace(/\[(\d+)\]/g, (match, num) => {
                return `<span class="citation-link" onclick="window.highlightExSource(${num})">${num}</span>`;
            });
            // ---------------------------

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
            console.log('📧 DEBUG: Rendering email preview with uiAction:', uiAction);

            // Safety check for data
            if (!uiAction.data) {
                console.error('❌ DEBUG: uiAction.data is missing!', uiAction);
                return;
            }

            const emailPreview = document.createElement('div');
            emailPreview.className = 'email-preview';

            // Email fields container
            const emailFields = document.createElement('div');
            emailFields.className = 'email-fields';

            const toField = document.createElement('div');
            toField.className = 'email-field';
            toField.innerHTML = `<span class="email-label">To:</span><span class="email-value">${uiAction.data.to || 'Unknown'}</span>`;

            const subjectField = document.createElement('div');
            subjectField.className = 'email-field';
            subjectField.innerHTML = `<span class="email-label">Subject:</span><span class="email-value">${uiAction.data.subject || 'No Subject'}</span>`;

            emailFields.appendChild(toField);
            emailFields.appendChild(subjectField);

            // Body section
            const bodySection = document.createElement('div');
            bodySection.className = 'email-body-section';

            const bodyLabel = document.createElement('div');
            bodyLabel.className = 'email-body-label';
            bodyLabel.innerHTML = '<span>📝</span><span>Message</span>';

            const bodyTextarea = document.createElement('textarea');
            bodyTextarea.className = 'email-body-editor';
            bodyTextarea.value = uiAction.data.body || '';
            bodyTextarea.rows = 3;
            bodyTextarea.placeholder = 'Edit your message...';

            bodySection.appendChild(bodyLabel);
            bodySection.appendChild(bodyTextarea);

            // Action buttons with new styling
            const buttonContainer = document.createElement('div');
            buttonContainer.className = 'email-actions';

            const cancelBtn = document.createElement('button');
            cancelBtn.className = 'email-btn email-btn-cancel';
            cancelBtn.innerHTML = '<span>Cancel</span>';
            cancelBtn.onclick = async () => {
                addMessage('No, cancel.', 'user');
                const data = await sendToBackend('No');
                emailPreview.remove();
                if (data.response) {
                    addMessage(data.response, 'aria', data.ui_action);
                }
            };

            const confirmBtn = document.createElement('button');
            confirmBtn.className = 'email-btn email-btn-send';
            confirmBtn.innerHTML = '<span class="email-btn-icon">📤</span><span>Send Email</span>';
            confirmBtn.onclick = async () => {
                const editedBody = bodyTextarea.value;
                addMessage('Yes, send it.', 'user');

                // Add sending state
                emailPreview.classList.add('sending');
                confirmBtn.disabled = true;
                confirmBtn.innerHTML = '<span>Sending...</span>';

                // Send confirmation with updated body
                const data = await sendToBackend('Yes', { updated_body: editedBody });

                emailPreview.remove();
                if (data.response) {
                    addMessage(data.response, 'aria', data.ui_action);
                }
            };

            buttonContainer.appendChild(cancelBtn);
            buttonContainer.appendChild(confirmBtn);

            // Assemble the email preview
            emailPreview.appendChild(emailFields);
            emailPreview.appendChild(bodySection);
            emailPreview.appendChild(buttonContainer);

            bubble.appendChild(emailPreview);
        } else if (uiAction && uiAction.type === 'music_playing') {
            // Show music player when music starts playing
            if (window.musicPlayer && uiAction.data && uiAction.data.track_info) {
                window.musicPlayer.onTrackChanged(uiAction.data.track_info);
            }
        } else if (uiAction && uiAction.type === 'search_results') {
            // Render Search Result Cards (Perplexity Style: Top Row)
            if (uiAction.data && uiAction.data.results) {
                const resultsContainer = document.createElement('div');
                resultsContainer.className = 'search-results-deck';

                // Header
                const header = document.createElement('div');
                header.className = 'search-results-header';
                // "Sources" Icon (Stack/Library style)
                const sourcesIconSvg = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="search-header-icon">
                    <path d="M4 6C4 4.89543 4.89543 4 6 4H18C19.1046 4 20 4.89543 20 6V18C20 19.1046 19.1046 20 18 20H6C4.89543 20 4 19.1046 4 18V6Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M8 8H16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M8 12H16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M8 16H12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>`;

                header.innerHTML = `${sourcesIconSvg} <span>SOURCES</span>`;
                resultsContainer.appendChild(header);

                // Scrollable Card Container
                const cardsScroll = document.createElement('div');
                cardsScroll.className = 'search-cards-scroll';

                uiAction.data.results.forEach((res, index) => {
                    const card = document.createElement('div');
                    card.className = 'search-card';
                    card.onclick = () => {
                        if (window.api && window.api.openExternal) {
                            window.api.openExternal(res.url);
                        } else {
                            window.open(res.url, '_blank');
                        }
                    };

                    // 1. Source (Icon + Name)
                    const source = document.createElement('div');
                    source.className = 'search-card-source';
                    try {
                        const domain = new URL(res.url).hostname.replace('www.', '');
                        source.innerHTML = `<img src="https://www.google.com/s2/favicons?domain=${domain}&sz=64" onError="this.style.display='none'" alt="icon"/> ${domain}`;
                    } catch (e) {
                        source.textContent = 'Source';
                    }

                    // 2. Title (Compact)
                    const title = document.createElement('div');
                    title.className = 'search-card-title';
                    title.textContent = res.title;

                    // 3. Index Badge
                    const indexBadge = document.createElement('div');
                    indexBadge.className = 'search-card-index';
                    indexBadge.textContent = index + 1;

                    card.appendChild(source);
                    card.appendChild(title);
                    card.appendChild(indexBadge);
                    cardsScroll.appendChild(card);
                });

                resultsContainer.appendChild(cardsScroll);

                // PREPEND to appear at the top
                if (bubble.firstChild) {
                    bubble.insertBefore(resultsContainer, bubble.firstChild);
                } else {
                    bubble.appendChild(resultsContainer);
                }
            }
        }

    } else {
        bubble.textContent = text;
    }

    message.appendChild(messageWrapper);
    messageWrapper.appendChild(bubble);
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

// --- Citation Handler ---
window.highlightExSource = function (index) {
    // Index is 1-based from citation
    console.log('Highlighting source:', index);

    const cards = document.querySelectorAll('.search-card');
    // Find the card where the index badge text equals the citation index
    let targetCard = null;
    cards.forEach(card => {
        const badge = card.querySelector('.search-card-index');
        if (badge && badge.textContent.trim() === String(index)) {
            targetCard = card;
        }
    });

    if (targetCard) {
        // Scroll container to show card
        targetCard.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });

        // Add Highlight Effect
        targetCard.classList.add('highlight-pulse');
        setTimeout(() => {
            targetCard.classList.remove('highlight-pulse');
        }, 2000);
    }
};
