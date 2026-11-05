@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ========================================================
echo   🚀 Path OrderSync Studio - Push to GitHub
echo ========================================================
echo.

where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Git is not installed or not in your system PATH.
    echo Please install Git for Windows: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

if not exist ".git" (
    echo [*] .git directory not found. Initializing repository...
    git init
    git branch -M main
    git remote add origin https://github.com/bishojit-sarker/Smart-Dropbox-QC-Batch-Loader.git
    echo [*] Syncing with remote repository...
    git fetch origin main
    git reset origin/main
) else (
    git remote set-url origin https://github.com/bishojit-sarker/Smart-Dropbox-QC-Batch-Loader.git
)

git config user.name >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [*] Setting Git user.name...
    git config --global user.name "Bishojit Sarker"
    git config user.name "Bishojit Sarker"
)

git config user.email >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [*] Setting Git user.email...
    git config --global user.email "bishojit-sarker@users.noreply.github.com"
    git config user.email "bishojit-sarker@users.noreply.github.com"
)

echo.
echo [*] Staging all files...
git add -A

echo [*] Committing changes...
git commit -m "release: v1.8.0 - Path OrderSync Studio v1.8.0 release"

echo [*] Pushing to GitHub (origin main)...
git push -u origin main
if %ERRORLEVEL% neq 0 (
    echo [*] Syncing remote before retry...
    git pull origin main --rebase --autostash
    git push -u origin main
)

echo.
where gh >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [*] Publishing / Updating Release v1.8.0 on GitHub...
    if exist "QC_Batch_Loader.exe" (
        gh release view v1.8.0 --repo bishojit-sarker/Smart-Dropbox-QC-Batch-Loader >nul 2>nul
        if !ERRORLEVEL! equ 0 (
            gh release upload v1.8.0 "QC_Batch_Loader.exe" --clobber --repo bishojit-sarker/Smart-Dropbox-QC-Batch-Loader
        ) else (
            gh release create v1.8.0 "QC_Batch_Loader.exe" --title "Path OrderSync Studio v1.8.0" --notes "Path OrderSync Studio v1.8.0 Release" --repo bishojit-sarker/Smart-Dropbox-QC-Batch-Loader
        )
    )
) else (
    echo [Notice] GitHub CLI (gh) not found. Standard Git push completed.
    echo To enable 1-click GitHub Release asset uploads, install gh CLI: https://cli.github.com
)

echo.
echo ========================================================
echo   🎉 Done! Code pushed to GitHub!
echo ========================================================
echo.
pause
