# Native Windows Shell Context Menu Verb Invoker
$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Invoke-MakeOnline($itemPath) {
    Write-Output "--------------------------------------------------"
    Write-Output "Processing: $itemPath"
    if (-not (Test-Path -LiteralPath $itemPath)) {
        Write-Output "ERROR: Path does not exist!"
        return
    }

    $parent = Split-Path -Parent -LiteralPath $itemPath
    $leaf = Split-Path -Leaf -LiteralPath $itemPath

    $shell = New-Object -ComObject Shell.Application
    $folder = $shell.Namespace($parent)
    if (-not $folder) {
        Write-Output "ERROR: Cannot get Shell Namespace for: $parent"
        return
    }

    $item = $folder.ParseName($leaf)
    if (-not $item) {
        Write-Output "ERROR: Cannot ParseName for: $leaf"
        return
    }

    $verbs = $item.Verbs()
    Write-Output "Found $($verbs.Count) available context menu verbs:"
    $invoked = $false
    foreach ($v in $verbs) {
        $name = $v.Name.Replace('&', '').Trim()
        if ($name) {
            Write-Output "   • Verb: '$name'"
        }
        if ($name -match '(?i)free up space|make online|online-only|smart sync') {
            Write-Output "   >>> EXECUTING VERB: '$name' <<<"
            $v.DoIt()
            $invoked = $true
            break
        }
    }
    if (-not $invoked) {
        Write-Output "   ⚠️ No online-only verb matched."
    }
}

# 1. Execute on Order Root
Invoke-MakeOnline 'C:\Users\Zitt\Path Dropbox\Khandoker_graphics\#457425'

# 2. Execute on Completed Folder
Invoke-MakeOnline 'C:\Users\Zitt\Path Dropbox\Khandoker_graphics\#457425\Completed'

# 3. Execute on Target File
Invoke-MakeOnline 'C:\Users\Zitt\Path Dropbox\Khandoker_graphics\#457425\Completed\Sandler.Stockbridge.8.20.266173 copy.psd'
