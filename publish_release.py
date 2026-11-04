import os
import sys
import re
import json
import shutil
import subprocess
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).parent.resolve()
APP_PY = BASE_DIR / "app.py"
CHANGELOG_MD = BASE_DIR / "CHANGELOG.md"
EXE_FILE = BASE_DIR / "QC_Batch_Loader.exe"
DIST_EXE = BASE_DIR / "dist" / "QC_Batch_Loader.exe"

def run_cmd(cmd, cwd=BASE_DIR, check=True):
    print(f"  > {cmd}")
    res = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and res.returncode != 0:
        print(f"[ERROR] Command failed with code {res.returncode}:\n{res.stderr}")
        sys.exit(res.returncode)
    return res

def get_current_version():
    with open(APP_PY, "r", encoding="utf-8") as f:
        content = f.read()
    m = re.search(r'CURRENT_VERSION\s*=\s*["\']([^"\']+)["\']', content)
    if not m:
        print("[ERROR] CURRENT_VERSION not found in app.py!")
        sys.exit(1)
    return m.group(1).strip()

def get_release_notes(version):
    if not CHANGELOG_MD.exists():
        return f"Release {version} with bug fixes and improvements."
    with open(CHANGELOG_MD, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = rf'## \[{re.escape(version)}\][^\n]*\n(.*?)(?=\n## \[|\Z)'
    m = re.search(pattern, content, re.DOTALL)
    if m:
        return m.group(1).strip()
    return f"Smart Dropbox QC Batch Loader {version} - Latest improvements."

def main():
    print("=" * 60)
    print("  🚀 QC Batch Loader - 1-Click GitHub Release Publisher")
    print("=" * 60)

    # 1. Version Detection
    version = get_current_version()
    print(f"\n[1/6] Detected Target Version: {version}")

    # 2. Extract Release Notes
    notes = get_release_notes(version)
    print(f"[2/6] Extracted Release Notes ({len(notes)} chars)")

    # 3. Compile Executable with PyInstaller
    print("\n[3/6] Compiling standalone QC_Batch_Loader.exe with PyInstaller...")
    pyinstaller_exe = BASE_DIR / ".venv" / "Scripts" / "pyinstaller.exe"
    if not pyinstaller_exe.exists():
        pyinstaller_exe = "pyinstaller"
    
    spec_file = BASE_DIR / "QC_Batch_Loader.spec"
    if spec_file.exists():
        cmd = f'"{pyinstaller_exe}" QC_Batch_Loader.spec --noconfirm'
    else:
        cmd = f'"{pyinstaller_exe}" --onefile --windowed --name "QC_Batch_Loader" app.py --noconfirm'
    run_cmd(cmd)

    # 4. Update root QC_Batch_Loader.exe
    print("\n[4/6] Updating root QC_Batch_Loader.exe...")
    if not DIST_EXE.exists():
        print(f"[ERROR] Compiled binary not found at {DIST_EXE}")
        sys.exit(1)
    shutil.copy2(DIST_EXE, EXE_FILE)
    print(f"  ✓ Updated {EXE_FILE.name} ({EXE_FILE.stat().st_size / (1024*1024):.2f} MB)")

    # 5. Git Commit & Push
    print("\n[5/6] Checking git status & committing changes...")
    run_cmd("git add -A")
    status_res = run_cmd("git status --porcelain", check=False)
    if status_res.stdout.strip():
        commit_msg = f"release: {version} - Automated feature release and binary build"
        run_cmd(f'git commit -m "{commit_msg}"')
    else:
        print("  ✓ Working tree clean, no new changes to commit.")
    
    print("  Pushing to GitHub (origin main)...")
    run_cmd("git push origin main")

    # 6. Publish Official GitHub Release via `gh` CLI
    print(f"\n[6/6] Publishing official GitHub Release {version}...")
    temp_notes_file = BASE_DIR / "_release_notes_tmp.md"
    with open(temp_notes_file, "w", encoding="utf-8") as f:
        f.write(f"# ⚡ Smart Dropbox QC Batch Loader {version}\n\n")
        f.write(notes + "\n\n")
        f.write("---\n")
        f.write("### 📥 Download & Usage:\n")
        f.write("Download `QC_Batch_Loader.exe` below. Run directly on Windows 10/11. No installation required.\n")

    # Check if release already exists on GitHub
    chk_rel = run_cmd(f'gh release view {version} --repo bishojit-sarker/Smart-Dropbox-QC-Batch-Loader', check=False)
    if chk_rel.returncode == 0:
        print(f"  Release {version} already exists. Updating release notes and executable asset...")
        run_cmd(f'gh release edit {version} --title "Smart Dropbox QC Batch Loader {version}" --notes-file "{temp_notes_file}" --repo bishojit-sarker/Smart-Dropbox-QC-Batch-Loader')
        run_cmd(f'gh release upload {version} "{EXE_FILE}" --clobber --repo bishojit-sarker/Smart-Dropbox-QC-Batch-Loader')
    else:
        print(f"  Creating new official GitHub Release {version}...")
        run_cmd(f'gh release create {version} "{EXE_FILE}" --title "Smart Dropbox QC Batch Loader {version}" --notes-file "{temp_notes_file}" --repo bishojit-sarker/Smart-Dropbox-QC-Batch-Loader')

    if temp_notes_file.exists():
        temp_notes_file.unlink()

    print("\n" + "=" * 60)
    print(f"  🎉 SUCCESS! {version} has been published live to GitHub!")
    print(f"  URL: https://github.com/bishojit-sarker/Smart-Dropbox-QC-Batch-Loader/releases/tag/{version}")
    print("  Users running the app will now immediately receive real-time update notifications!")
    print("=" * 60)

if __name__ == "__main__":
    main()
