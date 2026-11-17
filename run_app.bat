@echo off
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (
    start "" ".venv\Scripts\python.exe" app.py
) else (
    start "" python app.py
)
