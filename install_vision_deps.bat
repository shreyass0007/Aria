@echo off
echo Installing Vision Dependencies (PaddleOCR) into .venv_vision...
call .venv_vision\Scripts\activate.bat
pip install paddlepaddle paddleocr
echo.
echo Installation attempt complete.
pause
