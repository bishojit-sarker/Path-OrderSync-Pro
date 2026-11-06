@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo   🚀 Path OrderSync Pro - 1-Click GitHub Release Publisher
echo ========================================================
echo.

if exist .venv\Scripts\python.exe (
    call .venv\Scripts\python.exe publish_release.py
) else (
    python publish_release.py
)

if errorlevel 1 (
    echo.
    echo [ERROR] Publishing process failed!
    pause
    exit /b 1
)

echo.
echo ========================================================
echo   🎉 Successfully published update to GitHub!
echo ========================================================
pause
