@echo off
setlocal
echo ========================================================
echo   Setting up Desktop Shortcut for QC Batch Loader...
echo ========================================================

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut(\"$([Environment]::GetFolderPath('Desktop'))\QC Batch Loader.lnk\"); $s.TargetPath = '%~dp0QC_Batch_Loader.exe'; $s.WorkingDirectory = '%~dp0'; $s.Description = 'Smart Dropbox QC Batch Loader for Completed Orders'; $s.Save(); Write-Output 'Shortcut created successfully on Desktop!'"

echo.
echo ========================================================
echo   Done! You can now launch QC Batch Loader from Desktop.
echo ========================================================
pause
