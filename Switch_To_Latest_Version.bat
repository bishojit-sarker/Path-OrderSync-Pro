@echo off
title Restore Latest Path OrderSync Pro
echo ========================================================
echo   Restoring Path OrderSync Pro to Latest Modified Version
echo ========================================================
echo.
echo Closing any running instances...
taskkill /F /IM Path_OrderSync_Pro.exe 2>nul
timeout /t 1 /nobreak >nul

if exist "versions\Path_OrderSync_Pro_latest.exe" (
    echo Restoring from versions\Path_OrderSync_Pro_latest.exe...
    copy /Y "versions\Path_OrderSync_Pro_latest.exe" "Path_OrderSync_Pro.exe" >nul
) else if exist "Path_OrderSync_Pro.exe.bak" (
    echo Restoring from Path_OrderSync_Pro.exe.bak...
    copy /Y "Path_OrderSync_Pro.exe.bak" "Path_OrderSync_Pro.exe" >nul
) else (
    echo Error: Latest backup executable not found!
    pause
    exit /b 1
)

echo.
echo Successfully restored latest version!
echo Starting Path_OrderSync_Pro.exe...
start "" "Path_OrderSync_Pro.exe"
