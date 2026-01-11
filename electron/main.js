const electron = require('electron');
// Handle case where require('electron') returns a string path (known issue)
const { app, BrowserWindow, ipcMain, nativeImage } = typeof electron === 'string' ? require(electron) : electron;

const path = require('path');
const { spawn } = require('child_process');
const axios = require('axios');

let mainWindow;
let pythonProcess;

function createWindow() {
    // Get screen dimensions
    const { screen } = require('electron');
    const primaryDisplay = screen.getPrimaryDisplay();
    const { width: screenWidth, height: screenHeight } = primaryDisplay.workAreaSize;

    // Create the browser window - sidebar style
    mainWindow = new BrowserWindow({
        width: 300,
        height: screenHeight,
        x: 0,
        y: 0,
        frame: false, // Remove default title bar
        transparent: false,
        resizable: true,
        minWidth: 300,
        minHeight: 600,
        maxWidth: screenWidth,
        backgroundColor: '#e0e7ff',
        alwaysOnTop: false,
        skipTaskbar: false,
        titleBarStyle: 'hidden',
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false
        },
        icon: path.join(__dirname, 'aria_logo.png')
    });
    mainWindow.setMenuBarVisibility(false);

    // Handle new windows (links) to ensure they have the Aria icon
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        return {
            action: 'allow',
            overrideBrowserWindowOptions: {
                autoHideMenuBar: true,
                title: "Aria Browser",
                // Don't enforce icon here, let dynamic fetcher handle it
            }
        };
    });

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

// Function to fetch and set dynamic favicon
async function setDynamicIcon(win, url) {
    try {
        if (!url || !url.startsWith('http')) return;

        const hostname = new URL(url).hostname;
        // Use Google's favicon service for reliable 64px icons
        const iconUrl = `https://www.google.com/s2/favicons?domain=${hostname}&sz=64`;

        console.log(`Fetching icon for ${hostname} from ${iconUrl}`);

        const response = await axios.get(iconUrl, { responseType: 'arraybuffer' });
        const buffer = Buffer.from(response.data);
        const image = nativeImage.createFromBuffer(buffer);

        if (!win.isDestroyed()) {
            win.setIcon(image);
        }
    } catch (error) {
        console.error('Failed to set dynamic icon:', error.message);
        // Fallback to Aria logo if fetch fails
        if (!win.isDestroyed()) {
            win.setIcon(path.join(__dirname, 'aria_logo.png'));
        }
    }
}

// Listen for new windows to apply dynamic icons
app.on('browser-window-created', (event, win) => {
    if (win === mainWindow) return;

    // Wait for navigation or use initial title/url if available
    win.webContents.once('did-start-loading', () => {
        const url = win.webContents.getURL();
        if (url) {
            setDynamicIcon(win, url);
        }
    });

    // Update if they navigate elsewhere
    win.webContents.on('did-navigate', (event, url) => {
        setDynamicIcon(win, url);
    });
});


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

let isQuitting = false;

function startPythonBackend() {
    if (isQuitting) return;

    // Start Python backend server
    const pythonExecutable = process.platform === 'win32'
        ? path.join(__dirname, '..', '.venv', 'Scripts', 'python.exe')
        : path.join(__dirname, '..', '.venv', 'bin', 'python');

    const backendScript = path.join(__dirname, '..', 'backend', 'main.py');
    console.log('DEBUG: Selection Python Path:', pythonExecutable);

    console.log('Starting Python backend...');
    pythonProcess = spawn(pythonExecutable, [backendScript], {
        cwd: path.join(__dirname, '..')
    });

    pythonProcess.on('error', (err) => {
        console.error('Failed to start Python backend:', err);
    });

    pythonProcess.stdout.on('data', (data) => {
        console.log(`Python Backend: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python Backend Error: ${data}`);
    });

    pythonProcess.on('close', (code, signal) => {
        console.log(`Python backend exited with code ${code} and signal ${signal}`);
        pythonProcess = null;

        if (!isQuitting) {
            console.log('Restarting backend in 2 seconds...');
            setTimeout(startPythonBackend, 2000);
        }
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
    console.log('Window all closed, quitting app...');
    isQuitting = true;
    if (pythonProcess) {
        pythonProcess.kill();
    }
    if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', () => {
    console.log('Before quit event received...');
    isQuitting = true;
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

// Window control handlers
ipcMain.on('window-minimize', () => {
    if (mainWindow) mainWindow.minimize();
});

ipcMain.on('window-maximize', () => {
    if (mainWindow) {
        if (mainWindow.isMaximized()) {
            mainWindow.unmaximize();
        } else {
            mainWindow.maximize();
        }
    }
});

ipcMain.on('window-close', () => {
    if (mainWindow) mainWindow.close();
});
