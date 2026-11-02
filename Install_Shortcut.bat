@echo off
setlocal
echo ========================================================
echo   Setting up Desktop Shortcut for QC Batch Loader...
echo ========================================================

powershell -NoProfile -ExecutionPolicy Bypass -Command "$dir = (Get-Item -LiteralPath '.').FullName; $target = Join-Path $dir 'QC_Batch_Loader.exe'; $desktop = [Environment]::GetFolderPath('Desktop'); $lnk = Join-Path $desktop 'QC Batch Loader.lnk'; $ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut($lnk); $s.TargetPath = $target; $s.WorkingDirectory = $dir; $s.Description = 'Smart Dropbox QC Batch Loader for Completed Orders'; $s.Save(); Write-Output 'Shortcut created successfully on Desktop!'"

echo.
echo ========================================================
echo   Done! You can now launch QC Batch Loader from Desktop.
echo ========================================================
pause
