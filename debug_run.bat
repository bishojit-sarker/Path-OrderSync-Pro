@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo   ⚡ Path OrderSync Pro - Terminal Log & Debug Runner
echo ========================================================
echo.

if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe app.py
) else (
    python app.py
)

echo.
echo Process exited. Press any key to close...
pause >nul

