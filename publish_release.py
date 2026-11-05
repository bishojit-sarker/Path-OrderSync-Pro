import os
import sys
import re
import json
import time
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

def kill_running_app():
    """Stops any running QC_Batch_Loader instance so Windows does not lock the file."""
    try:
        subprocess.run("taskkill /F /IM QC_Batch_Loader.exe /T", shell=True, capture_output=True)
    except Exception:
        pass
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Get-Process QC_Batch_Loader* -ErrorAction SilentlyContinue | Stop-Process -Force"],
            shell=True,
            capture_output=True
        )
    except Exception:
        pass
    time.sleep(1)

def extract_current_version():
    content = APP_PY.read_text(encoding="utf-8")
    for line in content.splitlines():
        if line.startswith("CURRENT_VERSION"):
            parts = line.split("=")
            if len(parts) == 2:
                return parts[1].strip().strip('"').strip("'")
    print("[ERROR] Could not extract CURRENT_VERSION from app.py")
    sys.exit(1)

def extract_release_notes(version):
    content = CHANGELOG_MD.read_text(encoding="utf-8")
    pattern = rf'## \[{re.escape(version)}\][^\n]*\n(.*?)(?=\n## \[|\Z)'
    m = re.search(pattern, content, re.DOTALL)
    if not m:
        print(f"[WARNING] Could not find release notes for {version} in CHANGELOG.md. Using default notes.")
        return "Bug fixes, performance improvements, and UI enhancements."
    return m.group(1).strip()

def main():
    print("=" * 60)
    print("  🚀 Path OrderSync Studio - 1-Click GitHub Release Publisher")
    print("=" * 60)

    # 1. Detect Version
    version = extract_current_version()
    print(f"\n[1/6] Detected Target Version: {version}")

    # 2. Extract Changelog Notes
    notes = extract_release_notes(version)
    print(f"[2/6] Extracted Release Notes ({len(notes)} chars)")

    # 3. Compile Executable with PyInstaller
    print("\n[3/6] Compiling standalone QC_Batch_Loader.exe with PyInstaller...")
    kill_running_app()

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

    kill_running_app()
    max_retries = 5
    for attempt in range(max_retries):
        try:
            if EXE_FILE.exists():
                try:
                    # Windows NTFS allows renaming locked running executables
                    old_backup = BASE_DIR / f"QC_Batch_Loader.exe.{int(time.time())}.old"
                    EXE_FILE.rename(old_backup)
                    try:
                        old_backup.unlink(missing_ok=True)
                    except Exception:
                        pass
                except Exception:
                    pass
            shutil.copy2(DIST_EXE, EXE_FILE)
            break
        except PermissionError:
            if attempt < max_retries - 1:
                print(f"  [Notice] File in use, forcefully terminating process and retrying ({attempt+1}/{max_retries})...")
                kill_running_app()
                time.sleep(2)
            else:
                raise

    print(f"  ✓ Updated {EXE_FILE.name} ({EXE_FILE.stat().st_size / (1024*1024):.2f} MB)")

    # 5. Git Commit & Push
    repo_url = "https://github.com/bishojit-sarker/Smart-Dropbox-QC-Batch-Loader.git"
    git_dir = BASE_DIR / ".git"

    if not git_dir.exists():
        print("\n[5/6] .git directory not found. Initializing Git repository...")
        run_cmd("git init")
        run_cmd("git branch -M main")
        run_cmd(f'git remote add origin "{repo_url}"', check=False)
        print("  Syncing branch with remote GitHub repository...")
        fetch_res = run_cmd("git fetch origin main", check=False)
        if fetch_res.returncode == 0:
            print("  Aligning tree with origin/main history...")
            run_cmd("git reset origin/main", check=False)

    # Ensure Git author identity is configured
    name_check = run_cmd("git config user.name", check=False)
    if not name_check.stdout.strip():
        run_cmd('git config --global user.name "Bishojit Sarker"', check=False)
        run_cmd('git config user.name "Bishojit Sarker"', check=False)

    email_check = run_cmd("git config user.email", check=False)
    if not email_check.stdout.strip():
        run_cmd('git config --global user.email "bishojit-sarker@users.noreply.github.com"', check=False)
        run_cmd('git config user.email "bishojit-sarker@users.noreply.github.com"', check=False)

    print("\n[5/6] Checking git status & committing changes...")
    run_cmd("git add -A")
    status_res = run_cmd("git status --porcelain", check=False)
    if status_res.stdout.strip():
        commit_msg = f"release: {version} - Path OrderSync Studio release and binary build"
        run_cmd(f'git commit -m "{commit_msg}"', check=False)
    else:
        print("  ✓ Working tree clean, no new changes to commit.")

    print("  Pushing to GitHub (origin main)...")
    push_res = run_cmd("git push origin main", check=False)
    if push_res.returncode != 0:
        print("  [Notice] Standard push failed. Trying with upstream set...")
        push_res = run_cmd("git push -u origin main", check=False)
        if push_res.returncode != 0:
            print("  [Notice] Syncing with remote before pushing...")
            run_cmd("git pull origin main --rebase --autostash", check=False)
            push_res = run_cmd("git push -u origin main", check=False)
            if push_res.returncode != 0:
                print(f"  [Notice] Git push message:\n{push_res.stderr}")

    # 6. Publish Official GitHub Release via `gh` CLI
    print(f"\n[6/6] Publishing official GitHub Release {version}...")
    temp_notes_file = BASE_DIR / "_release_notes_tmp.md"
    with open(temp_notes_file, "w", encoding="utf-8") as f:
        f.write(f"# 🚀 Path OrderSync Studio {version}\n\n")
        f.write(notes + "\n\n")
        f.write("---\n")
        f.write("### 📥 Download & Usage:\n")
        f.write("Download `QC_Batch_Loader.exe` below. Run directly on Windows 10/11. No installation required.\n")

    gh_check = run_cmd("gh --version", check=False)
    if gh_check.returncode != 0:
        print("  [Notice] GitHub CLI ('gh') is not installed or not in PATH.")
        print("  Git commit & push was completed successfully.")
        print("  To enable 1-click GitHub Release asset uploads, install gh CLI: https://cli.github.com")
    else:
        # Check if release already exists on GitHub
        chk_rel = run_cmd(f'gh release view {version} --repo bishojit-sarker/Smart-Dropbox-QC-Batch-Loader', check=False)
        # Use relative paths without '#' character so GitHub CLI doesn't treat '#' as an asset label delimiter
        rel_exe_name = "QC_Batch_Loader.exe"
        rel_notes_name = "_release_notes_tmp.md"

        if chk_rel.returncode == 0:
            print(f"  Release {version} already exists. Updating release notes and executable asset...")
            run_cmd(f'gh release edit {version} --title "Path OrderSync Studio {version}" --notes-file "{rel_notes_name}" --repo bishojit-sarker/Smart-Dropbox-QC-Batch-Loader', check=False)
            run_cmd(f'gh release upload {version} "{rel_exe_name}" --clobber --repo bishojit-sarker/Smart-Dropbox-QC-Batch-Loader', check=False)
        else:
            print(f"  Creating new official GitHub Release {version}...")
            rel_res = run_cmd(f'gh release create {version} "{rel_exe_name}" --title "Path OrderSync Studio {version}" --notes-file "{rel_notes_name}" --repo bishojit-sarker/Smart-Dropbox-QC-Batch-Loader', check=False)
            if rel_res.returncode != 0:
                print(f"  [Notice] gh release create note:\n{rel_res.stderr}")

    if temp_notes_file.exists():
        try:
            temp_notes_file.unlink()
        except Exception:
            pass

    print("\n" + "=" * 60)
    print(f"  🎉 SUCCESS! {version} build and release process completed!")
    print(f"  URL: https://github.com/bishojit-sarker/Smart-Dropbox-QC-Batch-Loader/releases/tag/{version}")
    print("  Users running the app will now immediately receive real-time update notifications!")
    print("=" * 60)

if __name__ == "__main__":
    main()
