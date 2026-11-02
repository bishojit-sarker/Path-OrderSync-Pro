@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo   ⚡ QC Batch Loader - Auto Build & GitHub Publisher
echo ========================================================
echo.

:: 1. Compile with PyInstaller
echo [1/4] Compiling updated standalone executable...
call .venv\Scripts\pyinstaller.exe --onefile --windowed --name "QC_Batch_Loader" app.py
if errorlevel 1 (
    echo [ERROR] PyInstaller compilation failed!
    pause
    exit /b 1
)

:: 2. Copy to root
echo [2/4] Updating root executable...
copy /y "dist\QC_Batch_Loader.exe" "QC_Batch_Loader.exe" >nul

:: 3. Git Stage & Commit
echo [3/4] Staging files for Git...
git add .

set /p MSG="Enter commit message (Press Enter for auto-update): "
if "%MSG%"=="" set MSG=Update QC Batch Loader - %date% %time%

git commit -m "%MSG%"

:: 4. Push to GitHub
echo [4/4] Pushing to GitHub...
git push origin main

echo.
echo ========================================================
echo   ✅ Successfully published update to GitHub!
echo ========================================================
pause
