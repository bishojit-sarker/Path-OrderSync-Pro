@echo off
setlocal
echo ========================================================
echo   Setting up Desktop Shortcut for Path OrderSync Pro...
echo ========================================================

powershell -NoProfile -ExecutionPolicy Bypass -Command "$dir = (Get-Item -LiteralPath '.').FullName; $target = Join-Path $dir 'Path_OrderSync_Pro.exe'; $desktop = [Environment]::GetFolderPath('Desktop'); $lnk = Join-Path $desktop 'Path OrderSync Pro.lnk'; $ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut($lnk); $s.TargetPath = $target; $s.WorkingDirectory = $dir; $s.Description = 'Path OrderSync Pro - Sync Smarter. Work Faster. Better Quality.'; $s.Save(); Write-Output 'Shortcut created successfully on Desktop!'"

echo.
echo ========================================================
echo   Done! You can now launch Path OrderSync Pro from Desktop.
echo ========================================================
pause
