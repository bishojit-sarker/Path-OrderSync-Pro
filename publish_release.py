import os
import sys
import re
import json
import time
import shutil
import subprocess
import webbrowser
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).parent.resolve()
APP_PY = BASE_DIR / "app.py"
CHANGELOG_MD = BASE_DIR / "CHANGELOG.md"
EXE_FILE = BASE_DIR / "Path_OrderSync_Pro.exe"
LEGACY_EXE_FILE = BASE_DIR / "QC_Batch_Loader.exe"
DIST_EXE = BASE_DIR / "dist" / "Path_OrderSync_Pro.exe"
VERSIONS_DIR = BASE_DIR / "versions"
GITHUB_REPO = "bishojit-sarker/Path-OrderSync-Pro"

def run_cmd(cmd, cwd=BASE_DIR, check=True):
    print(f"  > {cmd}")
    res = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and res.returncode != 0:
        print(f"[ERROR] Command failed with code {res.returncode}:\n{res.stderr}")
        sys.exit(res.returncode)
    return res

def kill_running_app():
    """Stops any running Path_OrderSync_Pro instance so Windows does not lock the file."""
    try:
        subprocess.run("taskkill /F /IM Path_OrderSync_Pro.exe /T", shell=True, capture_output=True)
    except Exception:
        pass
    try:
        subprocess.run("taskkill /F /IM QC_Batch_Loader.exe /T", shell=True, capture_output=True)
    except Exception:
        pass
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Get-Process Path_OrderSync_Pro*,QC_Batch_Loader* -ErrorAction SilentlyContinue | Stop-Process -Force"],
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

def get_github_token():
    """Retrieves GitHub token from environment variables or Windows Git Credential Manager."""
    for var in ["GITHUB_TOKEN", "GH_TOKEN"]:
        val = os.environ.get(var)
        if val and val.strip():
            return val.strip()
    try:
        p = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            text=True,
            capture_output=True,
            check=False
        )
        for line in p.stdout.splitlines():
            if line.startswith("password="):
                tok = line.split("=", 1)[1].strip()
                if tok:
                    return tok
    except Exception:
        pass
    return None

def publish_via_github_api(repo, version, notes_content, exe_paths, token):
    """Creates/updates GitHub release and uploads binaries directly using GitHub REST API."""
    headers = {
        "User-Agent": "Path-OrderSync-Pro-Publisher",
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    title = f"Path OrderSync Pro {version}"
    rel_url = f"https://api.github.com/repos/{repo}/releases/tags/{version}"
    req = urllib.request.Request(rel_url, headers=headers)
    release_data = None
    try:
        with urllib.request.urlopen(req) as resp:
            release_data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"  [Notice] API check returned HTTP {e.code}: {e.reason}")

    if release_data:
        rel_id = release_data["id"]
        print(f"  Release {version} exists on GitHub (ID: {rel_id}). Updating title and release notes...")
        patch_url = f"https://api.github.com/repos/{repo}/releases/{rel_id}"
        patch_body = json.dumps({"name": title, "body": notes_content}).encode("utf-8")
        patch_req = urllib.request.Request(patch_url, data=patch_body, headers=headers, method="PATCH")
        with urllib.request.urlopen(patch_req) as resp:
            release_data = json.loads(resp.read().decode("utf-8"))
    else:
        print(f"  Creating new official GitHub Release {version}...")
        create_url = f"https://api.github.com/repos/{repo}/releases"
        create_body = json.dumps({
            "tag_name": version,
            "name": title,
            "body": notes_content,
            "draft": False,
            "prerelease": False
        }).encode("utf-8")
        create_req = urllib.request.Request(create_url, data=create_body, headers=headers, method="POST")
        with urllib.request.urlopen(create_req) as resp:
            release_data = json.loads(resp.read().decode("utf-8"))
        rel_id = release_data["id"]

    # Delete existing matching assets to avoid duplicate conflict
    existing_assets = {a["name"]: a["id"] for a in release_data.get("assets", [])}
    for file_path in exe_paths:
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"  [WARNING] Asset file {file_path} not found, skipping.")
            continue
        asset_name = file_path.name
        if asset_name in existing_assets:
            del_id = existing_assets[asset_name]
            print(f"  Removing existing asset {asset_name} (ID: {del_id}) on GitHub before overwrite...")
            del_url = f"https://api.github.com/repos/{repo}/releases/assets/{del_id}"
            del_req = urllib.request.Request(del_url, headers=headers, method="DELETE")
            try:
                with urllib.request.urlopen(del_req) as _:
                    pass
            except Exception as e:
                print(f"  Warning deleting old asset: {e}")

        # Upload asset binary
        upload_url = f"https://uploads.github.com/repos/{repo}/releases/{rel_id}/assets?name={urllib.parse.quote(asset_name)}"
        file_size = file_path.stat().st_size
        print(f"  Uploading {asset_name} ({file_size / (1024*1024):.2f} MB) to GitHub Release...")
        with open(file_path, "rb") as f_data:
            binary_data = f_data.read()

        up_headers = {
            "User-Agent": "Path-OrderSync-Pro-Publisher",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/octet-stream",
            "Content-Length": str(len(binary_data))
        }
        up_req = urllib.request.Request(upload_url, data=binary_data, headers=up_headers, method="POST")
        with urllib.request.urlopen(up_req) as up_resp:
            res_json = json.loads(up_resp.read().decode("utf-8"))
            print(f"  ✓ Uploaded {asset_name} successfully! ({res_json.get('browser_download_url')})")

    return release_data.get("html_url") or f"https://github.com/{repo}/releases/tag/{version}"

def main():
    print("=" * 60)
    print("  🚀 Path OrderSync Pro - 1-Click GitHub Release Publisher")
    print("=" * 60)

    # 1. Detect Version
    version = extract_current_version()
    print(f"\n[1/6] Detected Target Version: {version}")

    # 2. Extract Changelog Notes
    notes = extract_release_notes(version)
    print(f"[2/6] Extracted Release Notes ({len(notes)} chars)")

    # 3. Compile Executable with PyInstaller
    print("\n[3/6] Compiling standalone Path_OrderSync_Pro.exe with PyInstaller...")
    kill_running_app()

    pyinstaller_exe = BASE_DIR / ".venv" / "Scripts" / "pyinstaller.exe"
    if not pyinstaller_exe.exists():
        pyinstaller_exe = "pyinstaller"

    spec_file = BASE_DIR / "Path_OrderSync_Pro.spec"
    if spec_file.exists():
        cmd = f'"{pyinstaller_exe}" Path_OrderSync_Pro.spec --noconfirm'
    else:
        cmd = f'"{pyinstaller_exe}" --onefile --windowed --name "Path_OrderSync_Pro" --icon "assets/app_icon.ico" --add-data "assets;assets" app.py --noconfirm'
    run_cmd(cmd)

    # 4. Update root Path_OrderSync_Pro.exe & QC_Batch_Loader.exe
    print("\n[4/6] Updating root Path_OrderSync_Pro.exe and legacy QC_Batch_Loader.exe...")
    if not DIST_EXE.exists():
        print(f"[ERROR] Compiled binary not found at {DIST_EXE}")
        sys.exit(1)

    kill_running_app()
    max_retries = 5
    for attempt in range(max_retries):
        try:
            if EXE_FILE.exists():
                try:
                    old_backup = BASE_DIR / f"Path_OrderSync_Pro.exe.{int(time.time())}.old"
                    EXE_FILE.rename(old_backup)
                    try:
                        old_backup.unlink(missing_ok=True)
                    except Exception:
                        pass
                except Exception:
                    pass
            shutil.copy2(DIST_EXE, EXE_FILE)
            shutil.copy2(DIST_EXE, LEGACY_EXE_FILE)
            break
        except PermissionError:
            if attempt < max_retries - 1:
                print(f"  [Notice] File in use, retrying ({attempt+1}/{max_retries})...")
                kill_running_app()
                time.sleep(2)
            else:
                raise

    print(f"  ✓ Updated {EXE_FILE.name} ({EXE_FILE.stat().st_size / (1024*1024):.2f} MB)")
    print(f"  ✓ Updated {LEGACY_EXE_FILE.name} ({LEGACY_EXE_FILE.stat().st_size / (1024*1024):.2f} MB)")

    # Archive to versions directory
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(EXE_FILE, VERSIONS_DIR / f"Path_OrderSync_Pro_{version}.exe")
        shutil.copy2(EXE_FILE, VERSIONS_DIR / "Path_OrderSync_Pro_latest.exe")
        shutil.copy2(LEGACY_EXE_FILE, VERSIONS_DIR / f"QC_Batch_Loader_{version}.exe")
        shutil.copy2(LEGACY_EXE_FILE, VERSIONS_DIR / "QC_Batch_Loader_latest.exe")
        print(f"  ✓ Archived binaries to {VERSIONS_DIR.name}/ folder")
    except Exception as e:
        print(f"  [Notice] Could not copy to versions folder: {e}")

    # 5. Git Commit & Push
    repo_url = f"https://github.com/{GITHUB_REPO}.git"
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
        commit_msg = f"release: {version} - Path OrderSync Pro release and binary build"
        run_cmd(f'git commit -m "{commit_msg}"', check=False)
    else:
        print("  ✓ Working tree clean, no new changes to commit.")

    br_res = run_cmd("git rev-parse --abbrev-ref HEAD", check=False)
    current_branch = br_res.stdout.strip() if br_res.returncode == 0 and br_res.stdout.strip() else "Development"
    if current_branch == "HEAD":
        current_branch = "Development"

    print(f"  Pushing to GitHub (origin {current_branch})...")
    push_res = run_cmd(f"git push origin {current_branch}", check=False)
    if push_res.returncode != 0:
        print("  [Notice] Standard push failed. Trying with upstream set...")
        push_res = run_cmd(f"git push -u origin {current_branch}", check=False)
        if push_res.returncode != 0:
            print("  [Notice] Syncing with remote before pushing...")
            run_cmd(f"git pull origin {current_branch} --rebase --autostash", check=False)
            push_res = run_cmd(f"git push -u origin {current_branch}", check=False)
            if push_res.returncode != 0:
                print(f"  [Notice] Git push message:\n{push_res.stderr}")

    print(f"\n[*] Creating and pushing Git tag {version}...")
    run_cmd(f'git tag -fa {version} -m "release: {version} - Path OrderSync Pro {version}"', check=False)
    run_cmd(f"git push origin {version} --force", check=False)

    # 6. Publish Official GitHub Release
    print(f"\n[6/6] Publishing official GitHub Release {version}...")
    full_release_body = (
        f"# 🚀 Path OrderSync Pro {version}\n\n"
        f"{notes}\n\n"
        "---\n"
        "### 📥 Download & Usage:\n"
        "- Download **`Path_OrderSync_Pro.exe`** below.\n"
        "- Run directly on Windows 10/11. No installation required.\n"
        "- For backward compatibility, `QC_Batch_Loader.exe` is also provided.\n"
    )

    temp_notes_file = BASE_DIR / "_release_notes_tmp.md"
    with open(temp_notes_file, "w", encoding="utf-8") as f:
        f.write(full_release_body)

    rel_url = f"https://github.com/{GITHUB_REPO}/releases/new?tag={version}&title=Path+OrderSync+Pro+{version}"
    published_url = None

    # Check gh CLI first
    gh_check = run_cmd("gh --version", check=False)
    if gh_check.returncode == 0:
        auth_check = run_cmd("gh auth status", check=False)
        if auth_check.returncode == 0:
            print("  Using GitHub CLI (gh) to publish release...")
            chk_rel = run_cmd(f"gh release view {version} --repo {GITHUB_REPO}", check=False)
            if chk_rel.returncode == 0:
                print(f"  Release {version} exists. Updating release notes and assets...")
                run_cmd(f'gh release edit {version} --title "Path OrderSync Pro {version}" --notes-file "{temp_notes_file.name}" --repo {GITHUB_REPO}', check=False)
                run_cmd(f'gh release upload {version} "{EXE_FILE.name}" "{LEGACY_EXE_FILE.name}" --clobber --repo {GITHUB_REPO}', check=False)
            else:
                print(f"  Creating new official GitHub Release {version} via gh...")
                run_cmd(f'gh release create {version} "{EXE_FILE.name}" "{LEGACY_EXE_FILE.name}" --title "Path OrderSync Pro {version}" --notes-file "{temp_notes_file.name}" --repo {GITHUB_REPO}', check=False)
            published_url = f"https://github.com/{GITHUB_REPO}/releases/tag/{version}"

    # If gh CLI was not used, use direct GitHub REST API with Git token
    if not published_url:
        token = get_github_token()
        if token:
            print("  Authenticating via GitHub token from Git Credential Manager...")
            try:
                published_url = publish_via_github_api(
                    repo=GITHUB_REPO,
                    version=version,
                    notes_content=full_release_body,
                    exe_paths=[EXE_FILE, LEGACY_EXE_FILE],
                    token=token
                )
            except Exception as e:
                print(f"  [ERROR] GitHub API upload failed: {e}")
        else:
            print("  [Notice] No GitHub token found in credentials.")

    if not published_url:
        print("  Opening GitHub New Release page in your browser...")
        try:
            webbrowser.open(rel_url)
        except Exception:
            pass
        published_url = rel_url
        print(f"  Release Web URL: {rel_url}")
        print("  Tip: On the webpage, attach 'Path_OrderSync_Pro.exe' and click 'Publish release'!")

    if temp_notes_file.exists():
        try:
            temp_notes_file.unlink()
        except Exception:
            pass

    print("\n" + "=" * 60)
    print(f"  🎉 SUCCESS! {version} build and release process completed!")
    print(f"  URL: {published_url}")
    print("  Users running the app will now immediately receive real-time update notifications!")
    print("=" * 60)

if __name__ == "__main__":
    main()
