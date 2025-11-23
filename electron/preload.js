const { contextBridge, ipcRenderer } = require('electron');
let marked = null;
let markedError = null;

// Try to load marked library
try {
    // Load from local file to avoid path resolution issues
    const markedModule = require('./marked.min.js');
    marked = markedModule.marked || markedModule;
    console.log('✅ Preload: marked library loaded successfully from local file');
} catch (e) {
    markedError = e;
    console.error('❌ Preload: Failed to load marked library:', e.message);
    console.log('📝 Preload: Will use simple fallback parser');
}

// Configure marked if loaded successfully
if (marked && typeof marked.setOptions === 'function') {
    try {
        marked.setOptions({
            breaks: true,
            gfm: true,
            headerIds: false,
            mangle: false
        });
        console.log('✅ Preload: marked configured successfully');
    } catch (e) {
        console.error('❌ Preload: Failed to configure marked:', e);
    }
}

// Simple markdown parser fallback (doesn't require external dependencies)
function simpleMarkdownParser(text) {
    if (!text) return '';

    let html = text;

    // Convert **bold** to <strong>
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Convert *italic* to <em>  
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

    // Convert numbered lists (1. item)
    html = html.replace(/^\d+\.\s+\*\*(.+?)\*\*:/gm, '<li><strong>$1</strong>:');
    html = html.replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>');

    // Wrap consecutive <li> items in <ol>
    html = html.replace(/(<li>.*?<\/li>\n?)+/g, function (match) {
        return '<ol>' + match + '</ol>';
    });

    // Convert line breaks - double newlines to paragraphs
    const paragraphs = html.split('\n\n');
    html = paragraphs.map(p => {
        if (p.trim().startsWith('<ol>') || p.trim().startsWith('<ul>')) {
            return p;
        }
        return '<p>' + p.replace(/\n/g, '<br>') + '</p>';
    }).join('');

    return html;
}

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('api', {
    sendMessage: (message) => ipcRenderer.invoke('send-message', message),
    toggleVoice: (enabled) => ipcRenderer.invoke('toggle-voice', enabled),
    getTheme: () => ipcRenderer.invoke('get-theme'),
    setTheme: (theme) => ipcRenderer.invoke('set-theme', theme),
    parseMarkdown: (text) => {
        console.log('🔍 Preload: parseMarkdown called');

        // If marked library failed to load, use simple parser
        if (markedError || !marked) {
            console.log('📝 Preload: Using simple fallback parser');
            try {
                const result = simpleMarkdownParser(text);
                console.log('✅ Preload: Parsed with fallback (first 50 chars):', result.substring(0, 50));
                return result;
            } catch (e) {
                console.error('❌ Preload: Fallback parser error:', e);
                return text;
            }
        }

        // Use marked library
        try {
            console.log('📝 Preload: Using marked library');
            const result = marked(text);
            console.log('✅ Preload: Parsed with marked (first 50 chars):', result.substring(0, 50));
            return result;
        } catch (e) {
            console.error('❌ Preload: Markdown parsing error:', e);
            // Fall back to simple parser
            console.log('📝 Preload: Falling back to simple parser');
            return simpleMarkdownParser(text);
        }
    }
});

console.log('✅ Preload: window.api exposed with parseMarkdown');

// Expose electronAPI for rename dialog
contextBridge.exposeInMainWorld('electronAPI', {
    showRenameDialog: (currentTitle) => ipcRenderer.invoke('show-rename-dialog', currentTitle),
    closeRenameDialog: (newTitle) => ipcRenderer.send('close-rename-dialog', newTitle),
    showDeleteDialog: () => ipcRenderer.invoke('show-delete-dialog'),
    closeDeleteDialog: (confirmed) => ipcRenderer.send('close-delete-dialog', confirmed)
});

console.log('✅ Preload: window.electronAPI exposed');
