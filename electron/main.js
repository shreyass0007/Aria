const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

function createWindow() {
    // Get screen dimensions
    const { screen } = require('electron');
    const primaryDisplay = screen.getPrimaryDisplay();
    const { width: screenWidth, height: screenHeight } = primaryDisplay.workAreaSize;

    // Create the browser window - sidebar style
    mainWindow = new BrowserWindow({
        width: 380,
        height: screenHeight,
        x: 0,
        y: 0,
        frame: true,
        transparent: false,
        resizable: true,
        minWidth: 340,
        minHeight: 600,
        maxWidth: 500,
        backgroundColor: '#e0e7ff',
        alwaysOnTop: false,
        skipTaskbar: false,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false
        },
        icon: path.join(__dirname, 'aria_logo.png')
    });
    mainWindow.setMenuBarVisibility(false);


    // Load the app
    mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));

    // Open DevTools in development mode
    if (process.argv.includes('--dev')) {
        mainWindow.webContents.openDevTools();
    }

    mainWindow.on('closed', function () {
        mainWindow = null;
    });
}

// IPC Handler for rename dialog
ipcMain.handle('show-rename-dialog', async (event, currentTitle) => {
    const { dialog } = require('electron');
    const result = await dialog.showMessageBox(mainWindow, {
        type: 'question',
        title: 'Rename Conversation',
        message: 'Enter new conversation title:',
        buttons: ['Cancel', 'Rename'],
        defaultId: 1,
        cancelId: 0,
        input: true
    });

    // Since Electron dialog doesn't support text input directly, use a simple workaround
    // We'll use BrowserWindow to show a custom input
    return new Promise((resolve) => {
        const inputWindow = new BrowserWindow({
            width: 400,
            height: 200,
            parent: mainWindow,
            modal: true,
            show: false,
            frame: false,
            transparent: true,
            webPreferences: {
                contextIsolation: true,
                nodeIntegration: false,
                preload: path.join(__dirname, 'preload.js')
            }
        });

        const html = `
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body {
                        font-family: 'Inter', -apple-system, sans-serif;
                        background: transparent;
                        padding: 20px;
                    }
                    .dialog {
                        background: #f8f9faaa;
                        backdrop-filter: blur(20px);
                        border-radius: 16px;
                        padding: 24px;
                        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
                    }
                    h3 { margin-bottom: 16px; color: #1e293b; font-size: 18px; }
                    input {
                        width: 100%;
                        padding: 12px;
                        border: 2px solid #e2e8f0;
                        border-radius: 8px;
                        font-size: 14px;
                        margin-bottom: 16px;
                        font-family: inherit;
                    }
                    input:focus { outline: none; border-color: #6366f1; }
                    .buttons {
                        display: flex;
                        gap: 8px;
                        justify-content: flex-end;
                    }
                    button {
                        padding: 8px 16px;
                        border: none;
                        border-radius: 8px;
                        font-size: 14px;
                        cursor: pointer;
                        font-family: inherit;
                    }
                    .cancel { background: #e2e8f0; color: #475569; }
                    .rename { background: #6366f1; color: white; }
                    button:hover { opacity: 0.9; }
                </style>
            </head>
            <body>
                <div class="dialog">
                    <h3>Rename Conversation</h3>
                    <input type="text" id="titleInput" value="${currentTitle.replace(/"/g, '&quot;')}" autofocus>
                    <div class="buttons">
                        <button class="cancel" onclick="window.electronAPI.closeRenameDialog(null)">Cancel</button>
                        <button class="rename" onclick="rename()">Rename</button>
                    </div>
                </div>
                <script>
                    const input = document.getElementById('titleInput');
                    input.select();
                    input.addEventListener('keypress', (e) => {
                        if (e.key === 'Enter') rename();
                        if (e.key === 'Escape') window.electronAPI.closeRenameDialog(null);
                    });
                    function rename() {
                        const value = input.value.trim();
                        if (value) window.electronAPI.closeRenameDialog(value);
                    }
                </script>
            </body>
            </html>
        `;

        inputWindow.loadURL(`data:text/html;charset=UTF-8,${encodeURIComponent(html)}`);
        inputWindow.once('ready-to-show', () => {
            inputWindow.show();
        });

        ipcMain.once('close-rename-dialog', (event, newTitle) => {
            inputWindow.close();
            resolve(newTitle);
        });
    });
});

function startPythonBackend() {
    // Start Python backend server
    const pythonExecutable = process.platform === 'win32'
        ? path.join(__dirname, '..', '.venv', 'Scripts', 'python.exe')
        : path.join(__dirname, '..', '.venv', 'bin', 'python');

    const backendScript = path.join(__dirname, '..', 'backend_api.py');

    pythonProcess = spawn(pythonExecutable, [backendScript]);

    pythonProcess.stdout.on('data', (data) => {
        console.log(`Python Backend: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python Backend Error: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python backend exited with code ${code}`);
    });
}

// App lifecycle
app.whenReady().then(() => {
    createWindow();
    startPythonBackend();

    app.on('activate', function () {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', function () {
    if (pythonProcess) {
        pythonProcess.kill();
    }
    if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', () => {
    if (pythonProcess) {
        pythonProcess.kill();
    }
});

// IPC Handlers
ipcMain.handle('send-message', async (event, message) => {
    // This will be handled via HTTP requests to Python backend
    return { status: 'received', message };
});

ipcMain.handle('toggle-voice', async (event, enabled) => {
    console.log('Voice mode toggled:', enabled);
    return { status: 'success', enabled };
});

ipcMain.handle('get-theme', async () => {
    return { theme: 'light' };
});

ipcMain.handle('set-theme', async (event, theme) => {
    console.log('Theme changed to:', theme);
    return { status: 'success', theme };
});
