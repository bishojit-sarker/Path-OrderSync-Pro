@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ========================================================
echo   🚀 Path OrderSync Pro - Push to GitHub
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
    git remote add origin https://github.com/bishojit-sarker/Path-OrderSync-Pro.git
    echo [*] Syncing with remote repository...
    git fetch origin main
    git reset origin/main
) else (
    git remote set-url origin https://github.com/bishojit-sarker/Path-OrderSync-Pro.git
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
git commit -m "release: v1.8.0 - Path OrderSync Pro v1.8.0 release"

echo [*] Pushing to GitHub (origin main)...
git push -u origin main
if %ERRORLEVEL% neq 0 (
    echo [*] Syncing remote before retry...
    git pull origin main --rebase --autostash
    git push -u origin main
)

echo [*] Creating and pushing Git tag v1.8.0...
git tag -fa v1.8.0 -m "release: v1.8.0 - Path OrderSync Pro v1.8.0 release"
git push origin v1.8.0 --force

echo.
where gh >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [*] Publishing / Updating Release v1.8.0 on GitHub...
    if exist "Path_OrderSync_Pro.exe" (
        gh release view v1.8.0 --repo bishojit-sarker/Path-OrderSync-Pro >nul 2>nul
        if !ERRORLEVEL! equ 0 (
            gh release upload v1.8.0 "Path_OrderSync_Pro.exe" --clobber --repo bishojit-sarker/Path-OrderSync-Pro
        ) else (
            gh release create v1.8.0 "Path_OrderSync_Pro.exe" --title "Path OrderSync Pro v1.8.0" --notes "Path OrderSync Pro v1.8.0 Release" --repo bishojit-sarker/Path-OrderSync-Pro
        )
    )
) else (
    echo [Notice] GitHub CLI (gh) not found. Standard Git push and tag completed.
    echo [*] Opening GitHub New Release page in your browser...
    powershell -NoProfile -Command "Start-Process 'https://github.com/bishojit-sarker/Path-OrderSync-Pro/releases/new?tag=v1.8.0'"
    echo.
    echo Tip: On the opened webpage, attach "Path_OrderSync_Pro.exe" and click "Publish release"!
)

echo.
echo ========================================================
echo   🎉 Done! Code and v1.8.0 tag pushed to GitHub!
echo ========================================================
echo.
pause
