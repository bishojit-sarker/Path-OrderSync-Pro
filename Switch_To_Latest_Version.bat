@echo off
title Restore Latest QC Batch Loader
echo ========================================================
echo   Restoring QC Batch Loader to Latest Modified Version
echo ========================================================
echo.
echo Closing any running instances...
taskkill /F /IM QC_Batch_Loader.exe 2>nul
timeout /t 1 /nobreak >nul

if exist "versions\QC_Batch_Loader_latest.exe" (
    echo Restoring from versions\QC_Batch_Loader_latest.exe...
    copy /Y "versions\QC_Batch_Loader_latest.exe" "QC_Batch_Loader.exe" >nul
) else if exist "QC_Batch_Loader.exe.bak" (
    echo Restoring from QC_Batch_Loader.exe.bak...
    copy /Y "QC_Batch_Loader.exe.bak" "QC_Batch_Loader.exe" >nul
) else (
    echo Error: Latest backup executable not found!
    pause
    exit /b 1
)

echo.
echo Successfully restored latest version!
echo Starting QC_Batch_Loader.exe...
start "" "QC_Batch_Loader.exe"
