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
    // Create a custom input window for renaming
    return new Promise((resolve) => {
        const inputWindow = new BrowserWindow({
            width: 320,
            height: 160,
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

        const filePath = path.join(__dirname, 'rename.html');
        inputWindow.loadFile(filePath, { query: { title: currentTitle } });

        inputWindow.once('ready-to-show', () => {
            inputWindow.show();
        });

        ipcMain.once('close-rename-dialog', (event, newTitle) => {
            if (!inputWindow.isDestroyed()) {
                inputWindow.close();
            }
            resolve(newTitle);
        });

        // Handle window closed by user (e.g. Alt+F4)
        inputWindow.on('closed', () => {
            resolve(null);
        });
    });
});

// IPC Handler for delete confirmation dialog
ipcMain.handle('show-delete-dialog', async (event) => {
    return new Promise((resolve) => {
        const confirmWindow = new BrowserWindow({
            width: 320,
            height: 160,
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

        const filePath = path.join(__dirname, 'delete.html');
        confirmWindow.loadFile(filePath);

        confirmWindow.once('ready-to-show', () => {
            confirmWindow.show();
        });

        ipcMain.once('close-delete-dialog', (event, confirmed) => {
            if (!confirmWindow.isDestroyed()) {
                confirmWindow.close();
            }
            resolve(confirmed);
        });

        // Handle window closed by user
        confirmWindow.on('closed', () => {
            resolve(false);
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
