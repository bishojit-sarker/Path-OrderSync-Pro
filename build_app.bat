@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo   🔨 Building Path OrderSync Studio (QC_Batch_Loader.exe)
echo ========================================================
echo.

if exist .venv\Scripts\python.exe (
    call .venv\Scripts\python.exe publish_release.py
) else (
    python publish_release.py
)

echo.
pause

