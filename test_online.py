# -*- coding: utf-8 -*-
"""
Diagnostic & Verification Test for Windows Cloud Files Dehydration (Make Online).
Invokes the exact Windows Explorer native right-click context menu verb ("Make online-only" / "Free up space")
using a generated .ps1 script to guarantee 100% literal path handling with '#' characters.
"""

import os
import sys
import ctypes
import subprocess
import time
import json

def get_app_dir():
    return os.path.dirname(os.path.abspath(__file__))

APP_DIR = get_app_dir()
CONFIG_FILE = os.path.join(APP_DIR, "config.json")
LOG_FILE = os.path.join(APP_DIR, "test_output.log")
PS1_SCRIPT = os.path.join(APP_DIR, "_run_dehydrate.ps1")

log_lines = []

def log(msg):
    print(msg)
    sys.stdout.flush()
    log_lines.append(str(msg))
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(log_lines) + "\n")
    except Exception:
        pass

def get_powershell_exe():
    sys_root = os.environ.get("SystemRoot", r"C:\Windows")
    ps_path = os.path.join(sys_root, "System32", "WindowsPowerShell", "v1.0", "powershell.exe")
    if os.path.isfile(ps_path):
        return ps_path
    for p in os.environ.get("PATH", "").split(os.pathsep):
        cand = os.path.join(p, "powershell.exe")
        if os.path.isfile(cand):
            return cand
    return "powershell.exe"

PS_EXE = get_powershell_exe()

def load_dropbox_path():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                p = data.get("dropbox_path")
                if p and os.path.isdir(p):
                    return p
        except Exception:
            pass
    candidates = [
        r"C:\Users\Zitt\Path Dropbox",
        os.path.join(os.environ.get("USERPROFILE", ""), "Path Dropbox"),
        os.path.join(os.environ.get("USERPROFILE", ""), "Dropbox"),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return c
    return None

def get_physical_size_on_disk(file_path):
    """Retrieves actual physical allocation on disk via Win32 GetCompressedFileSizeW."""
    kernel32 = ctypes.windll.kernel32
    try:
        high_order = ctypes.c_ulong(0)
        low_order = kernel32.GetCompressedFileSizeW(file_path, ctypes.byref(high_order))
        if low_order == 0xFFFFFFFF and kernel32.GetLastError() != 0:
            return os.path.getsize(file_path)
        return (high_order.value << 32) + low_order
    except Exception:
        return os.path.getsize(file_path) if os.path.exists(file_path) else 0

def test_dehydration():
    log("=" * 70)
    log("🧪 Smart Dropbox QC Batch Loader - Native Context Menu Dehydration Test")
    log("=" * 70)
    log(f"PowerShell Binary: {PS_EXE}")

    kernel32 = ctypes.windll.kernel32
    shell32 = ctypes.windll.shell32
    kernel32.GetFileAttributesW.argtypes = [ctypes.c_wchar_p]
    kernel32.GetFileAttributesW.restype = ctypes.c_uint32

    # 1. Locate Target
    dropbox_root = load_dropbox_path()
    log(f"📂 Dropbox Root: {dropbox_root}")
    if not dropbox_root or not os.path.isdir(dropbox_root):
        log("❌ [FAILED] Dropbox Root not found.")
        return False

    order_root = os.path.join(dropbox_root, "Khandoker_graphics", "#457425")
    completed_folder = os.path.join(order_root, "Completed")
    target_folder = completed_folder if os.path.isdir(completed_folder) else order_root
    log(f"🎯 Order Root:   {order_root}")
    log(f"🎯 Target Folder: {target_folder}")

    target_files = []
    if os.path.isdir(target_folder):
        for root, _, files in os.walk(target_folder):
            for f in files:
                if not f.startswith(".") and f.lower() not in ["desktop.ini", "thumbs.db", ".dropbox", ".dropbox.attr"]:
                    target_files.append(os.path.join(root, f))

    if not target_files:
        log("❌ No files found in target folder.")
        return False

    target_file = target_files[0]
    log(f"📄 Target File:   {os.path.basename(target_file)}")
    phys_before = get_physical_size_on_disk(target_file) / (1024 * 1024)
    logical_before = os.path.getsize(target_file) / (1024 * 1024)
    attrs_before = kernel32.GetFileAttributesW(target_file)
    log(f"   • Logical Size:  {logical_before:.2f} MB")
    log(f"   • Physical Disk: {phys_before:.2f} MB")
    log(f"   • Attributes:    0x{attrs_before:08X} (Pinned={bool(attrs_before & 0x80000)}, Unpinned={bool(attrs_before & 0x100000)}, CloudRecall={bool(attrs_before & 0x400000)})")

    # 2. Build Native PowerShell Script using exact literal paths
    ps1_content = f"""# Native Windows Shell Context Menu Verb Invoker
$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Invoke-MakeOnline($itemPath) {{
    Write-Output "--------------------------------------------------"
    Write-Output "Processing: $itemPath"
    if (-not (Test-Path -LiteralPath $itemPath)) {{
        Write-Output "ERROR: Path does not exist!"
        return
    }}

    $parent = [System.IO.Path]::GetDirectoryName($itemPath)
    $leaf = [System.IO.Path]::GetFileName($itemPath)

    $shell = New-Object -ComObject Shell.Application
    $folder = $shell.Namespace($parent)
    if (-not $folder) {{
        Write-Output "ERROR: Cannot get Shell Namespace for: $parent"
        return
    }}

    $item = $folder.ParseName($leaf)
    if (-not $item) {{
        Write-Output "ERROR: Cannot ParseName for: $leaf"
        return
    }}

    $verbs = $item.Verbs()
    Write-Output "Found $($verbs.Count) available context menu verbs:"
    $invoked = $false
    foreach ($v in $verbs) {{
        $name = $v.Name.Replace('&', '').Trim()
        if ($name) {{
            Write-Output "   • Verb: '$name'"
        }}
        if ($name -match '(?i)free up space|make online|online-only|smart sync') {{
            Write-Output "   >>> EXECUTING VERB: '$name' <<<"
            $v.DoIt()
            $invoked = $true
            break
        }}
    }}
    if (-not $invoked) {{
        Write-Output "   ⚠️ No online-only verb matched."
    }}
}}

# 1. Execute on Order Root
Invoke-MakeOnline '{order_root}'

# 2. Execute on Completed Folder
Invoke-MakeOnline '{target_folder}'

# 3. Execute on Target File
Invoke-MakeOnline '{target_file}'
"""

    log("\n" + "=" * 70)
    log("⚡ STEP 1: Executing Native Context Menu Verbs via PowerShell...")
    log("=" * 70)

    with open(PS1_SCRIPT, "w", encoding="utf-8") as f:
        f.write(ps1_content)

    cmd = f'"{PS_EXE}" -NoProfile -ExecutionPolicy Bypass -File "{PS1_SCRIPT}"'
    log(f"Running: {cmd}\n")
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.stdout:
        for line in proc.stdout.splitlines():
            log("  " + line)
    if proc.stderr:
        log("  [STDERR]: " + proc.stderr.strip())

    # 3. Wait for Dropbox / Windows Shell to process eviction
    log("\n" + "=" * 70)
    log("⚡ STEP 2: Waiting for Cloud Sync Engine to evict data blocks...")
    log("=" * 70)

    shell32.SHChangeNotify(0x00001000, 0x0005, target_folder, None)
    shell32.SHChangeNotify(0x00001000, 0x0005, order_root, None)

    for wait_i in range(1, 6):
        time.sleep(1)
        phys_now = get_physical_size_on_disk(target_file) / (1024 * 1024)
        attrs_now = kernel32.GetFileAttributesW(target_file)
        is_cloud_now = bool(attrs_now & 0x00400000)
        is_unpinned_now = bool(attrs_now & 0x00100000)
        is_pinned_now = bool(attrs_now & 0x00080000)
        log(f"  [{wait_i}s] Physical Size: {phys_now:.2f} MB | Pinned: {is_pinned_now} | Unpinned: {is_unpinned_now} | CloudRecall: {is_cloud_now}")
        if phys_now == 0 or is_cloud_now:
            log("\n  🎉 SUCCESS! File is now 0 B on disk (Cloud Placeholder)!")
            break

    log("\n" + "=" * 70)
    log("🏁 RESULT CHECK COMPLETE")
    log("=" * 70)
    return True

if __name__ == "__main__":
    try:
        test_dehydration()
    except Exception as e:
        log(f"❌ Test error: {e}")
    input("\nPress Enter to exit...")
