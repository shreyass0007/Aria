const { contextBridge, ipcRenderer } = require('electron');

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('api', {
    sendMessage: (message) => ipcRenderer.invoke('send-message', message),
    toggleVoice: (enabled) => ipcRenderer.invoke('toggle-voice', enabled),
    getTheme: () => ipcRenderer.invoke('get-theme'),
    setTheme: (theme) => ipcRenderer.invoke('set-theme', theme)
});

// Expose electronAPI for rename dialog
contextBridge.exposeInMainWorld('electronAPI', {
    showRenameDialog: (currentTitle) => ipcRenderer.invoke('show-rename-dialog', currentTitle),
    closeRenameDialog: (newTitle) => ipcRenderer.send('close-rename-dialog', newTitle)
});
