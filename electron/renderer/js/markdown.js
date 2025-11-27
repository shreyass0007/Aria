export function parseMessageWithCode(text) {
    const codeBlocks = [];

    // Parse fenced code blocks first (```language\ncode\n```)
    text = text.replace(/```(\w+)?\s*[\r\n]+([\s\S]*?)```/g, (match, language, code) => {
        const lang = language || 'plaintext';
        const placeholder = `__CODE_BLOCK_${codeBlocks.length}__`;
        codeBlocks.push({
            placeholder,
            html: `<code-block data-language="${lang}">${escapeHtml(code.trim())}</code-block>`
        });
        return placeholder;
    });

    // Parse inline code (`code`)
    text = text.replace(/`([^`]+)`/g, (match, code) => {
        const placeholder = `__CODE_BLOCK_${codeBlocks.length}__`;
        codeBlocks.push({
            placeholder,
            html: `<code class="inline-code">${escapeHtml(code)}</code>`
        });
        return placeholder;
    });

    // Parse markdown links
    text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" style="color: #4f46e5; text-decoration: underline;">$1</a>');

    // Parse line breaks
    text = text.replace(/\n/g, '<br>');

    // Restore code blocks
    codeBlocks.forEach(block => {
        text = text.split(block.placeholder).join(block.html);
    });

    return text;
}

export function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

export function createCodeBlock(code, language) {
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
