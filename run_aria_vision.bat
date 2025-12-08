@echo off
echo Starting Aria with Vision Support (Python 3.12)...
call .venv_vision\Scripts\activate.bat
:: Check if requirements are satisfied (optional, but good for first run)
:: pip install -r requirements.txt
python main.py
pause
