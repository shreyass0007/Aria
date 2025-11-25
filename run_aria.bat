@echo off
echo Starting Aria...

:: Start Backend
echo Starting Backend Server...
start "Aria Backend" cmd /k "python backend_fastapi.py"

:: Wait a moment for backend to initialize
timeout /t 5 /nobreak >nul

:: Start Frontend
echo Starting Electron Frontend...
cd electron
start "Aria Frontend" npm start

echo Aria started!
