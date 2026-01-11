const electron = require('electron');
console.log('--- TEST START ---');
console.log('Typeof electron:', typeof electron);
console.log('Keys:', Object.keys(electron));
try {
    const { app, ipcMain } = electron;
    console.log('app:', typeof app);
    console.log('ipcMain:', typeof ipcMain);
} catch (e) {
    console.error('Destructuring failed:', e);
}
console.log('--- TEST END ---');
app.quit();
