@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo   🧪 Testing Dropbox Make Online (Dehydration Engine)
echo ========================================================
echo.

if exist .venv\Scripts\python.exe (
    call .venv\Scripts\python.exe test_online.py
) else (
    python test_online.py
)

echo.
pause

