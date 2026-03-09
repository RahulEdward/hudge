@echo off
cd /d "%~dp0"
echo Starting Quant AI Lab Backend...
backend\venv\Scripts\python.exe backend\run.py
pause
