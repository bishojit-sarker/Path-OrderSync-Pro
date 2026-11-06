@echo off
setlocal enabledelayedexpansion
title Path OrderSync Pro - Emergency Rollback Utility
cd /d "%~dp0"

echo ========================================================
echo   ⏪ Path OrderSync Pro - Emergency Rollback Utility
echo ========================================================
echo.
echo Closing any running instances...
taskkill /F /IM Path_OrderSync_Pro.exe /IM QC_Batch_Loader.exe 2>nul
timeout /t 1 /nobreak >nul

if not exist "versions" (
    echo [ERROR] 'versions' folder not found. Cannot rollback.
    pause
    exit /b 1
)

echo Scanning available cached versions...
echo.

set count=0
for %%F in (versions\*.exe) do (
    set "fname=%%~nxF"
    rem Exclude latest pointer to avoid confusion
    echo !fname! | findstr /i "latest" >nul
    if errorlevel 1 (
        set /a count+=1
        set "ver_!count!=%%F"
        set "name_!count!=!fname!"
        echo   [!count!] !fname!
    )
)

if %count% equ 0 (
    echo [ERROR] No cached rollback binaries found in 'versions' folder.
    pause
    exit /b 1
)

echo.
set /p choice="Enter the version number to restore (1-%count%): "

if not defined ver_%choice% (
    echo [ERROR] Invalid selection. Operation aborted.
    pause
    exit /b 1
)

set "chosen_file=!ver_%choice%!"
set "chosen_name=!name_%choice%!"

echo.
echo Restoring to !chosen_name!...
copy /Y "!chosen_file!" "Path_OrderSync_Pro.exe" >nul
copy /Y "!chosen_file!" "QC_Batch_Loader.exe" >nul

echo.
echo ========================================================
echo   🎉 Successfully restored to !chosen_name!!
echo   Starting Path OrderSync Pro...
echo ========================================================
start "" "Path_OrderSync_Pro.exe"
timeout /t 2 /nobreak >nul

