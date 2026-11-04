import os
import sys
import json
import re
import time
import shutil
import subprocess
import threading
import ctypes
import urllib.request
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

def get_app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_assets_dir():
    # Check bundled _MEIPASS first when frozen
    if hasattr(sys, "_MEIPASS"):
        bundled = os.path.join(sys._MEIPASS, "assets")
        if os.path.isdir(bundled):
            return bundled
    app_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    return os.path.join(app_dir, "assets")

APP_DIR = get_app_dir()
CONFIG_FILE = os.path.join(APP_DIR, "config.json")
HISTORY_FILE = os.path.join(APP_DIR, "history.json")
APP_NAME = "Path OrderSync Studio"
APP_TAGLINE = "Smart Batch Order Sync & Space Optimizer"
CURRENT_VERSION = "v1.6.0"
GITHUB_REPO = "bishojit-sarker/Smart-Dropbox-QC-Batch-Loader"

ASSETS_DIR = get_assets_dir()
LOGO_HEADER_PATH = os.path.join(ASSETS_DIR, "logo_header.png")
LOGO_LARGE_PATH = os.path.join(ASSETS_DIR, "logo_64.png")
APP_ICON_PATH = os.path.join(ASSETS_DIR, "app_icon.ico")

# Windows Cloud Filter Attributes
FILE_ATTRIBUTE_PINNED = 0x80000
FILE_ATTRIBUTE_UNPINNED = 0x100000
FILE_ATTRIBUTE_REPARSE_POINT = 0x400
FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS = 0x400000
FILE_ATTRIBUTE_OFFLINE = 0x1000

def format_bytes(num_bytes):
    """Formats raw bytes into human-readable B, KB, MB, GB, TB."""
    if not num_bytes or num_bytes <= 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_idx = 0
    size = float(num_bytes)
    while size >= 1024.0 and unit_idx < len(units) - 1:
        size /= 1024.0
        unit_idx += 1
    if unit_idx == 0:
        return f"{int(size)} B"
    return f"{size:.2f} {units[unit_idx]}"

def get_drive_space_info(path):
    """Returns disk usage metrics for the drive containing path."""
    try:
        target = path if (path and os.path.exists(path)) else os.environ.get("SystemDrive", "C:")
        usage = shutil.disk_usage(target)
        drive = os.path.splitdrive(os.path.abspath(target))[0].upper()
        if not drive:
            drive = "C:"
        free_pct = (usage.free / usage.total) * 100 if usage.total > 0 else 0
        return {
            "drive": drive,
            "free": usage.free,
            "total": usage.total,
            "used": usage.used,
            "free_pct": free_pct,
            "free_str": format_bytes(usage.free),
            "total_str": format_bytes(usage.total),
            "used_str": format_bytes(usage.used)
        }
    except Exception:
        return {
            "drive": "C:",
            "free": 0, "total": 0, "used": 0, "free_pct": 0,
            "free_str": "N/A", "total_str": "N/A", "used_str": "N/A"
        }

def get_folder_size_bytes(folder_path):
    """Calculates total physical file size inside folder_path."""
    total = 0
    if not folder_path or not os.path.isdir(folder_path):
        return 0
    try:
        for root, _, files in os.walk(folder_path):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    total += os.path.getsize(fp)
                except Exception:
                    pass
    except Exception:
        pass
    return total

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_history(hist):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(hist, f, indent=2)
    except Exception:
        pass

def mark_order_history(order_id, vendor, folder_path, status, file_count=0, size_bytes=None):
    hist = load_history()
    key = f"{order_id}_{vendor}" if vendor and vendor != "-" else str(order_id)
    entry = hist.get(key, {})
    now_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    if status == "local":
        if size_bytes is None or size_bytes <= 0:
            size_bytes = get_folder_size_bytes(folder_path) if folder_path else 0
    else:
        size_bytes = 0

    entry.update({
        "order_id": str(order_id),
        "vendor": vendor,
        "path": folder_path,
        "status": status,  # "local" or "online"
        "files": file_count,
        "size_bytes": size_bytes,
        "last_updated": now_str
    })
    if status == "local" and "downloaded_at" not in entry:
        entry["downloaded_at"] = now_str
    elif status == "online":
        entry["freed_at"] = now_str

    hist[key] = entry
    save_history(hist)

def get_tracked_local_orders():
    hist = load_history()
    local_orders = []
    for key, item in hist.items():
        if item.get("status") == "local":
            p = item.get("path")
            if p and os.path.isdir(p):
                local_orders.append(item)
    return local_orders

def get_tracked_local_storage_stats():
    """
    Calculates total orders and bytes currently tracked as local on disk.
    Returns (order_count, total_bytes, formatted_size_str).
    """
    tracked = get_tracked_local_orders()
    total_bytes = 0
    for it in tracked:
        sz = it.get("size_bytes")
        if sz is not None and isinstance(sz, (int, float)) and sz > 0:
            total_bytes += sz
        else:
            p = it.get("path")
            if p and os.path.isdir(p):
                calc_sz = get_folder_size_bytes(p)
                it["size_bytes"] = calc_sz
                total_bytes += calc_sz
    return len(tracked), total_bytes, format_bytes(total_bytes)

def is_folder_local_on_disk(folder_path):
    if not os.path.isdir(folder_path):
        return False, 0
    kernel32 = ctypes.windll.kernel32 if hasattr(ctypes, "windll") else None
    if not kernel32:
        return False, 0

    has_local = False
    file_count = 0
    for root, _, files in os.walk(folder_path):
        for f in files:
            file_count += 1
            fp = os.path.join(root, f)
            try:
                attrs = kernel32.GetFileAttributesW(fp)
                if attrs != -1 and (attrs & FILE_ATTRIBUTE_PINNED):
                    has_local = True
                    break
            except Exception:
                pass
        if has_local:
            break
    return has_local, file_count

def parse_version_tuple(tag):
    """Extracts integer version components e.g. 'v1.4.0' -> (1, 4, 0)."""
    nums = re.findall(r"\d+", str(tag))
    return tuple(int(n) for n in nums) if nums else (0, 0, 0)

def cleanup_old_executable():
    try:
        old_exe = sys.executable + ".old"
        if os.path.exists(old_exe):
            os.remove(old_exe)
    except Exception:
        pass

def get_local_version_notes(version):
    """Extracts changelog release notes for the specified version from CHANGELOG.md."""
    changelog_path = os.path.join(APP_DIR, "CHANGELOG.md")
    if os.path.exists(changelog_path):
        try:
            with open(changelog_path, "r", encoding="utf-8") as f:
                content = f.read()
            pattern = rf'## \[{re.escape(version)}\][^\n]*\n(.*?)(?=\n## \[|\Z)'
            m = re.search(pattern, content, re.DOTALL)
            if m:
                return m.group(1).strip()
        except Exception:
            pass
    return "Bug fixes, performance improvements, and reliability updates."

class UpdateDialog(tk.Toplevel):
    """Modern interactive dialog displaying update details, release notes, and real-time 1-click update progress."""
    def __init__(self, parent, latest_tag, current_ver, release_body, download_url):
        super().__init__(parent)
        self.parent = parent
        self.latest_tag = latest_tag
        self.current_ver = current_ver
        self.release_body = release_body or "Bug fixes and performance improvements."
        self.download_url = download_url

        self.title(f"🚀 Update Available: {latest_tag}")
        self.geometry("680x560")
        self.minsize(580, 460)
        self.configure(bg="#1e1e2e")
        self.transient(parent)
        self.grab_set()

        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - 340
            y = parent.winfo_y() + (parent.winfo_height() // 2) - 280
            self.geometry(f"+{max(x, 50)}+{max(y, 50)}")
        except Exception:
            pass

        self._create_widgets()

    def _create_widgets(self):
        # 1. Top Header Banner
        header = tk.Frame(self, bg="#252538", bd=1, relief="solid")
        header.pack(fill="x", padx=16, pady=(16, 10))

        title_box = tk.Frame(header, bg="#252538")
        title_box.pack(fill="x", padx=14, pady=12)

        tk.Label(title_box, text="🚀", font=("Segoe UI", 24), bg="#252538", fg="#38bdf8").pack(side="left", padx=(0, 10))

        text_box = tk.Frame(title_box, bg="#252538")
        text_box.pack(side="left", fill="x", expand=True)

        tk.Label(text_box, text="A New Update is Ready!", font=("Segoe UI", 12, "bold"), bg="#252538", fg="#f8fafc").pack(anchor="w")

        v_lbl = tk.Label(
            text_box,
            text=f"Current: {self.current_ver}   ➔   Latest: {self.latest_tag}",
            font=("Segoe UI", 9),
            bg="#252538",
            fg="#94a3b8"
        )
        v_lbl.pack(anchor="w", pady=(2, 0))

        # 2. Release Notes & How to Use Guide Card
        card = tk.Frame(self, bg="#252538", bd=1, relief="solid")
        card.pack(fill="both", expand=True, padx=16, pady=4)

        card_header = tk.Frame(card, bg="#252538")
        card_header.pack(fill="x", padx=14, pady=(10, 4))
        tk.Label(card_header, text="📋 What's New & Feature Guide:", font=("Segoe UI", 10, "bold"), bg="#252538", fg="#f8fafc").pack(side="left")

        # Scrollable text widget
        txt_frame = tk.Frame(card, bg="#181825")
        txt_frame.pack(fill="both", expand=True, padx=12, pady=(4, 12))

        self.txt = tk.Text(
            txt_frame,
            bg="#181825",
            fg="#f8fafc",
            insertbackground="#ffffff",
            relief="flat",
            font=("Segoe UI", 9),
            wrap="word",
            padx=10,
            pady=10
        )
        scroll = tk.Scrollbar(txt_frame, orient="vertical", command=self.txt.yview)
        self.txt.configure(yscrollcommand=scroll.set)

        self.txt.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.txt.insert("1.0", self.release_body.strip())
        self.txt.config(state="disabled")

        # 3. Download Progress Area
        self.progress_frame = tk.Frame(self, bg="#1e1e2e")
        self.progress_frame.pack(fill="x", padx=16, pady=(4, 6))

        self.progress_lbl = tk.Label(self.progress_frame, text="", font=("Segoe UI", 9), bg="#1e1e2e", fg="#93c5fd")
        self.progress_lbl.pack(anchor="w")

        self.prog_bar = ttk.Progressbar(self.progress_frame, mode="determinate")
        self.prog_bar.pack(fill="x", pady=(2, 0))
        self.progress_frame.pack_forget()

        # 4. Action Buttons
        btn_box = tk.Frame(self, bg="#1e1e2e")
        btn_box.pack(fill="x", padx=16, pady=(10, 16))

        self.btn_update = tk.Button(
            btn_box,
            text="🚀 Update & Restart Now",
            command=self._start_download,
            bg="#10b981",
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            padx=16,
            pady=6
        )
        self.btn_update.pack(side="right", padx=(8, 0))

        self.btn_cancel = tk.Button(
            btn_box,
            text="✕ Remind Me Later",
            command=self.destroy,
            bg="#374151",
            fg="white",
            activebackground="#4b5563",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 9),
            cursor="hand2",
            padx=12,
            pady=6
        )
        self.btn_cancel.pack(side="right")

    def _start_download(self):
        if not self.download_url:
            messagebox.showerror("Error", "Download URL is not available.")
            return

        cur_exe = sys.executable
        if not cur_exe.lower().endswith("qc_batch_loader.exe"):
            webbrowser.open(self.download_url)
            self.destroy()
            return

        self.btn_update.config(state="disabled")
        self.btn_cancel.config(state="disabled")
        self.progress_frame.pack(fill="x", padx=16, pady=(4, 6))
        self.prog_bar["value"] = 0
        self.progress_lbl.config(text=f"Connecting to GitHub to download {self.latest_tag}...")

        threading.Thread(target=self._worker_download, daemon=True).start()

    def _worker_download(self):
        cur_exe = sys.executable
        old_exe = cur_exe + ".old"
        new_exe_tmp = cur_exe + ".tmp"

        try:
            req = urllib.request.Request(self.download_url, headers={"User-Agent": "QC-Batch-Loader-Updater"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                total_len = resp.headers.get("Content-Length")
                total_bytes = int(total_len) if total_len and total_len.isdigit() else 0
                downloaded = 0
                chunk_size = 64 * 1024

                with open(new_exe_tmp, "wb") as out_f:
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        out_f.write(chunk)
                        downloaded += len(chunk)
                        if total_bytes > 0:
                            pct = int((downloaded / total_bytes) * 100)
                            cur_mb = downloaded / (1024 * 1024)
                            tot_mb = total_bytes / (1024 * 1024)
                            self.after(0, lambda p=pct, c=cur_mb, t=tot_mb: self._update_progress(p, f"Downloading {self.latest_tag}: {p}% ({c:.1f} MB / {t:.1f} MB)..."))
                        else:
                            cur_mb = downloaded / (1024 * 1024)
                            self.after(0, lambda c=cur_mb: self._update_progress(50, f"Downloading {self.latest_tag}: {c:.1f} MB..."))

            if os.path.exists(old_exe):
                try:
                    os.remove(old_exe)
                except Exception:
                    pass

            os.rename(cur_exe, old_exe)
            os.rename(new_exe_tmp, cur_exe)

            self.after(0, self._on_download_complete)
        except Exception as e:
            try:
                if os.path.exists(new_exe_tmp):
                    os.remove(new_exe_tmp)
            except Exception:
                pass
            self.after(0, lambda err=e: self._on_download_error(err))

    def _update_progress(self, pct, label_text):
        self.prog_bar["value"] = pct
        self.progress_lbl.config(text=label_text)

    def _on_download_complete(self):
        cur_exe = sys.executable
        messagebox.showinfo("Update Complete", f"Successfully updated to {self.latest_tag}!\nThe application will now restart with the new version.")
        subprocess.Popen([cur_exe])
        os._exit(0)

    def _on_download_error(self, err):
        self.btn_update.config(state="normal")
        self.btn_cancel.config(state="normal")
        self.progress_lbl.config(text="Download failed.", fg="#ef4444")
        messagebox.showerror("Update Error", f"Failed to complete automatic update:\n{err}")

class WhatsNewDialog(tk.Toplevel):
    """Welcome dialog shown on first launch of a new version to guide user on new capabilities."""
    def __init__(self, parent, version, notes_text=None):
        super().__init__(parent)
        self.parent = parent
        self.version = version
        self.notes_text = notes_text or get_local_version_notes(version)

        self.title(f"✨ What's New in {version}")
        self.geometry("680x540")
        self.minsize(580, 440)
        self.configure(bg="#1e1e2e")
        self.transient(parent)

        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - 340
            y = parent.winfo_y() + (parent.winfo_height() // 2) - 270
            self.geometry(f"+{max(x, 50)}+{max(y, 50)}")
        except Exception:
            pass

        self._create_widgets()

    def _create_widgets(self):
        header = tk.Frame(self, bg="#252538", bd=1, relief="solid")
        header.pack(fill="x", padx=16, pady=(16, 10))

        title_box = tk.Frame(header, bg="#252538")
        title_box.pack(fill="x", padx=14, pady=12)

        tk.Label(title_box, text="✨", font=("Segoe UI", 22), bg="#252538", fg="#facc15").pack(side="left", padx=(0, 10))

        t_lbl = tk.Label(title_box, text=f"Welcome to Smart Dropbox QC Batch Loader {self.version}!", font=("Segoe UI", 11, "bold"), bg="#252538", fg="#f8fafc")
        t_lbl.pack(anchor="w")

        sub_lbl = tk.Label(title_box, text="Review the latest features, enhancements, and usage guide below.", font=("Segoe UI", 8), bg="#252538", fg="#94a3b8")
        sub_lbl.pack(anchor="w", pady=(2, 0))

        card = tk.Frame(self, bg="#252538", bd=1, relief="solid")
        card.pack(fill="both", expand=True, padx=16, pady=4)

        txt_frame = tk.Frame(card, bg="#181825")
        txt_frame.pack(fill="both", expand=True, padx=12, pady=12)

        txt = tk.Text(
            txt_frame,
            bg="#181825",
            fg="#f8fafc",
            insertbackground="#ffffff",
            relief="flat",
            font=("Segoe UI", 9),
            wrap="word",
            padx=10,
            pady=10
        )
        scroll = tk.Scrollbar(txt_frame, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=scroll.set)
        txt.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        txt.insert("1.0", self.notes_text)
        txt.config(state="disabled")

        btn_box = tk.Frame(self, bg="#1e1e2e")
        btn_box.pack(fill="x", padx=16, pady=(10, 16))

        ok_btn = tk.Button(
            btn_box,
            text="👍 Got It! (Start QC)",
            command=self.destroy,
            bg="#3b82f6",
            fg="white",
            activebackground="#2563eb",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=16,
            pady=6
        )
        ok_btn.pack(side="right")

def check_for_updates(parent=None, silent=True):
    """Checks GitHub Releases for new updates with real-time notifications."""
    def _worker():
        try:
            req = urllib.request.Request(
                f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest",
                headers={"User-Agent": "QC-Batch-Loader-Updater"}
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            latest_tag = data.get("tag_name", "").strip()
            if not latest_tag:
                return

            latest_ver = parse_version_tuple(latest_tag)
            cur_ver = parse_version_tuple(CURRENT_VERSION)

            if latest_ver <= cur_ver:
                if not silent and parent:
                    def _show_up_to_date():
                        ans = messagebox.askyesno(
                            "Up to Date",
                            f"You are using the latest version ({CURRENT_VERSION})!\n\nWould you like to review the What's New guide for this version?"
                        )
                        if ans:
                            WhatsNewDialog(parent, CURRENT_VERSION)
                    parent.after(0, _show_up_to_date)
                return

            download_url = None
            for asset in data.get("assets", []):
                if asset.get("name") == "QC_Batch_Loader.exe":
                    download_url = asset.get("browser_download_url")
                    break

            if not download_url:
                if not silent and parent:
                    parent.after(0, lambda: messagebox.showwarning("Update Available", f"Version {latest_tag} is available on GitHub, but executable asset is not attached."))
                return

            release_body = data.get("body", "Bug fixes and performance improvements.")
            if parent:
                parent.after(0, lambda: parent._show_update_available(latest_tag, release_body, download_url, silent))
        except Exception as e:
            if not silent and parent:
                parent.after(0, lambda: messagebox.showerror("Update Check Failed", f"Could not check for updates:\n{e}"))

    threading.Thread(target=_worker, daemon=True).start()

def auto_detect_dropbox_path():
    candidate_json_paths = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Dropbox", "info.json"),
        os.path.join(os.environ.get("APPDATA", ""), "Dropbox", "info.json"),
    ]
    for json_path in candidate_json_paths:
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for account_type in ["business", "personal"]:
                    acc = data.get(account_type)
                    if isinstance(acc, dict):
                        if "root_path" in acc and os.path.isdir(acc["root_path"]):
                            return acc["root_path"]
                        if "path" in acc and os.path.isdir(acc["path"]):
                            return acc["path"]
            except Exception:
                pass

    user_profile = os.environ.get("USERPROFILE", os.path.expanduser("~"))
    if os.path.isdir(user_profile):
        try:
            for entry in os.listdir(user_profile):
                full_p = os.path.join(user_profile, entry)
                if os.path.isdir(full_p) and "dropbox" in entry.lower():
                    return full_p
        except Exception:
            pass

    return os.path.join(user_profile, "Dropbox")

DEFAULT_DROPBOX_PATH = auto_detect_dropbox_path()

def load_config():
    detected_path = auto_detect_dropbox_path()
    cfg = {"dropbox_path": detected_path, "last_seen_version": CURRENT_VERSION}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    cfg.update(loaded)
                    if not cfg.get("dropbox_path") or not os.path.isdir(cfg.get("dropbox_path")):
                        cfg["dropbox_path"] = detected_path
        except Exception:
            pass
    return cfg

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

def normalize_order_id(s):
    """Normalizes an Order ID for ultra-fast, robust matching across all vendors."""
    if not s:
        return ""
    c = re.sub(r"^#\s*", "", str(s)).strip()
    c = re.sub(r"\s*\([^)]*\)", "", c).strip()
    c = re.split(r"[-_]", c)[0].strip()
    return c.lower()

def build_vendor_index(base_path, selected_vendors=None):
    """
    Builds a lightning-fast in-memory map of clean order IDs to vendor locations:
    {
        clean_order_id: [
            {
                "vendor": vendor,
                "folder_name": entry_name,
                "order_dir": full_order_dir
            }, ...
        ]
    }
    Scans thousands of orders across selected vendors in ~15 milliseconds.
    """
    index = {}
    if not base_path or not os.path.isdir(base_path):
        return index

    try:
        vendors = [
            d for d in os.listdir(base_path)
            if not d.startswith(".") and os.path.isdir(os.path.join(base_path, d))
        ]
    except Exception:
        return index

    if selected_vendors:
        vendors = [d for d in vendors if d in selected_vendors]

    for vendor in vendors:
        v_dir = os.path.join(base_path, vendor)
        try:
            entries = os.listdir(v_dir)
        except Exception:
            continue

        for entry in entries:
            clean = normalize_order_id(entry)
            if not clean:
                continue

            if clean not in index:
                index[clean] = []

            index[clean].append({
                "vendor": vendor,
                "folder_name": entry,
                "order_dir": os.path.join(v_dir, entry)
            })

    return index

def resolve_target_folder(order_dir):
    """Checks if order folder has a 'Completed' or 'Complete' subfolder."""
    if not os.path.isdir(order_dir):
        return order_dir
    for sub in ["Completed", "Complete", "completed", "complete"]:
        c_sub = os.path.join(order_dir, sub)
        if os.path.isdir(c_sub):
            return c_sub
    return order_dir

def collect_folder_files(target_dir):
    """Collects file paths and total size in bytes."""
    files = []
    total_size = 0
    if not os.path.isdir(target_dir):
        return files, 0
    try:
        for root, _, fs in os.walk(target_dir):
            for f in fs:
                fp = os.path.join(root, f)
                files.append(fp)
                try:
                    total_size += os.path.getsize(fp)
                except Exception:
                    pass
    except Exception:
        pass
    return files, total_size

def _hydrate_single_file(fp):
    """Streams the file in chunks to ensure 100% complete local hydration without Photoshop hanging."""
    try:
        kernel32 = ctypes.windll.kernel32 if hasattr(ctypes, "windll") else None
        if kernel32:
            attrs = kernel32.GetFileAttributesW(fp)
            if attrs != -1 and not (attrs & FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS) and not (attrs & FILE_ATTRIBUTE_OFFLINE):
                return True
        with open(fp, "rb") as fh:
            while True:
                chunk = fh.read(4 * 1024 * 1024)
                if not chunk:
                    break
        return True
    except Exception:
        return False


# -*- coding: utf-8 -*-
import os
import sys
import re
import json
import threading
import subprocess
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

def get_all_changelog_releases():
    """Parses CHANGELOG.md for all release entries."""
    releases = []
    changelog_path = os.path.join(APP_DIR, "CHANGELOG.md")
    if os.path.exists(changelog_path):
        try:
            with open(changelog_path, "r", encoding="utf-8") as f:
                content = f.read()
            pattern = r'## \[([^\]]+)\](?:\s*-\s*([^\n]+))?\n(.*?)(?=\n## \[|\Z)'
            matches = re.findall(pattern, content, re.DOTALL)
            for tag, date_str, body in matches:
                releases.append({
                    "version": tag.strip(),
                    "date": date_str.strip() if date_str else "N/A",
                    "notes": body.strip()
                })
        except Exception:
            pass
    if not releases:
        releases.append({
            "version": CURRENT_VERSION,
            "date": "2026-11-04",
            "notes": "Smart Batch Order Sync & Space Optimizer with high-speed multi-vendor engine."
        })
    return releases


class NotificationCenterDialog(tk.Toplevel):
    """
    Notification & Update Center displaying current version, update notifications,
    and date-based release history with formatted changelogs.
    """
    def __init__(self, parent, available_update=None):
        super().__init__(parent)
        self.parent = parent
        self.available_update = available_update
        self.title("🔔 Notification & Update Center")
        self.geometry("740x580")
        self.minsize(620, 480)
        self.configure(bg="#1e1e2e")
        self.transient(parent)
        self.grab_set()

        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - 370
            y = parent.winfo_y() + (parent.winfo_height() // 2) - 290
            self.geometry(f"+{max(x, 50)}+{max(y, 50)}")
        except Exception:
            pass

        self._create_widgets()

    def _create_widgets(self):
        # 1. Top Header
        top_frame = tk.Frame(self, bg="#252538", bd=1, relief="solid")
        top_frame.pack(fill="x", padx=16, pady=(14, 10))

        h_box = tk.Frame(top_frame, bg="#252538")
        h_box.pack(fill="x", padx=14, pady=12)

        tk.Label(h_box, text="🔔", font=("Segoe UI", 22), bg="#252538", fg="#f59e0b").pack(side="left", padx=(0, 10))

        info_box = tk.Frame(h_box, bg="#252538")
        info_box.pack(side="left", fill="x", expand=True)

        tk.Label(info_box, text="Notification & Update Center", font=("Segoe UI", 13, "bold"), bg="#252538", fg="#f8fafc").pack(anchor="w")
        tk.Label(
            info_box,
            text=f"App: {APP_NAME}  |  Current Version: {CURRENT_VERSION}",
            font=("Segoe UI", 9),
            bg="#252538",
            fg="#94a3b8"
        ).pack(anchor="w", pady=(2, 0))

        close_btn = tk.Button(
            h_box,
            text="✕ Close",
            command=self.destroy,
            bg="#374151",
            fg="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=10,
            pady=3
        )
        close_btn.pack(side="right")

        # 2. Update Banner Card (if update available)
        if self.available_update:
            tag = self.available_update.get("tag", "New Version")
            banner = tk.Frame(self, bg="#1e3a5f", bd=1, relief="solid")
            banner.pack(fill="x", padx=16, pady=(0, 10))

            b_inner = tk.Frame(banner, bg="#1e3a5f")
            b_inner.pack(fill="x", padx=14, pady=10)

            tk.Label(b_inner, text="🚀", font=("Segoe UI", 18), bg="#1e3a5f", fg="#38bdf8").pack(side="left", padx=(0, 10))

            b_txt = tk.Frame(b_inner, bg="#1e3a5f")
            b_txt.pack(side="left", fill="x", expand=True)

            tk.Label(b_txt, text=f"Update Ready: {tag}", font=("Segoe UI", 11, "bold"), bg="#1e3a5f", fg="#38bdf8").pack(anchor="w")
            tk.Label(b_txt, text="A new version with performance and feature improvements is ready to install.", font=("Segoe UI", 8), bg="#1e3a5f", fg="#cbd5e1").pack(anchor="w")

            up_btn = tk.Button(
                b_inner,
                text="🚀 Install Update",
                command=self._confirm_install_update,
                bg="#0284c7",
                fg="white",
                activebackground="#0369a1",
                activeforeground="white",
                relief="flat",
                font=("Segoe UI", 9, "bold"),
                cursor="hand2",
                padx=12,
                pady=6
            )
            up_btn.pack(side="right")

        # 3. Release History Card
        card = tk.Frame(self, bg="#252538", bd=1, relief="solid")
        card.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        card_title = tk.Frame(card, bg="#252538")
        card_title.pack(fill="x", padx=14, pady=(10, 6))
        tk.Label(card_title, text="📋 Release History & Feature Changelogs by Date:", font=("Segoe UI", 10, "bold"), bg="#252538", fg="#f8fafc").pack(side="left")

        txt_frame = tk.Frame(card, bg="#181825")
        txt_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        txt = tk.Text(
            txt_frame,
            bg="#181825",
            fg="#f8fafc",
            insertbackground="#ffffff",
            relief="flat",
            font=("Segoe UI", 9),
            wrap="word",
            padx=12,
            pady=12
        )
        scroll = tk.Scrollbar(txt_frame, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=scroll.set)
        txt.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        txt.tag_configure("ver_header", font=("Segoe UI", 11, "bold"), foreground="#60a5fa", spacing1=10, spacing3=4)
        txt.tag_configure("date_badge", font=("Segoe UI", 8), foreground="#94a3b8")
        txt.tag_configure("section", font=("Segoe UI", 9, "bold"), foreground="#34d399", spacing1=6, spacing3=2)
        txt.tag_configure("bullet", font=("Segoe UI", 9), foreground="#e2e8f0", lmargin1=16, lmargin2=28)

        releases = get_all_changelog_releases()
        for rel in releases:
            v = rel.get("version", "")
            d = rel.get("date", "")
            notes = rel.get("notes", "")

            txt.insert(tk.END, f"📦 Release {v}   ", "ver_header")
            txt.insert(tk.END, f"📅 {d}\n", "date_badge")

            lines = notes.splitlines()
            for line in lines:
                sline = line.strip()
                if not sline:
                    txt.insert(tk.END, "\n")
                elif sline.startswith("### "):
                    txt.insert(tk.END, f"{sline[4:]}\n", "section")
                elif sline.startswith("- **") or sline.startswith("* **"):
                    txt.insert(tk.END, f"• {sline[2:]}\n", "bullet")
                elif sline.startswith("- ") or sline.startswith("* "):
                    txt.insert(tk.END, f"    {sline[2:]}\n", "bullet")
                else:
                    txt.insert(tk.END, f"{sline}\n", "bullet")
            txt.insert(tk.END, "\n" + "─" * 60 + "\n\n")

        txt.config(state="disabled")

    def _confirm_install_update(self):
        if not self.available_update:
            return
        tag = self.available_update.get("tag", "latest")
        confirm = messagebox.askyesno(
            "Confirm Update",
            f"Do you want to update Path OrderSync Studio to {tag} now?\n\n"
            f"The application will download the update and automatically restart.",
            parent=self
        )
        if confirm:
            self.destroy()
            UpdateDialog(
                self.parent,
                tag,
                CURRENT_VERSION,
                self.available_update.get("body", ""),
                self.available_update.get("url")
            )


class LocalCleanDialog(tk.Toplevel):
    """
    Dedicated tool for discovering and releasing physical local disk space taken by QC orders.
    Lists hydrated orders with checkboxes, allowing single or batch cloud-offloading.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("🧹 Local Storage Clean & Free Space Optimizer")
        self.geometry("980x620")
        self.minsize(820, 500)
        self.configure(bg="#1e1e2e")
        self.transient(parent)
        self.grab_set()

        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - 490
            y = parent.winfo_y() + (parent.winfo_height() // 2) - 310
            self.geometry(f"+{max(x, 50)}+{max(y, 50)}")
        except Exception:
            pass

        self.search_var = tk.StringVar(value="")
        self.selected_keys = set()
        self.local_items = {}
        self.master_checked = False

        self._create_widgets()
        self._load_local_orders()

    def _create_widgets(self):
        # 1. Top Header
        top_frame = tk.Frame(self, bg="#1e1e2e")
        top_frame.pack(fill="x", padx=16, pady=(12, 6))

        title_lbl = tk.Label(
            top_frame,
            text="🧹 Local Storage Clean & Free Space",
            font=("Segoe UI", 13, "bold"),
            bg="#1e1e2e",
            fg="#34d399"
        )
        title_lbl.pack(side="left")

        sub_lbl = tk.Label(
            top_frame,
            text="Only hydrated orders consuming physical hard drive space are listed here.",
            font=("Segoe UI", 9),
            bg="#1e1e2e",
            fg="#94a3b8"
        )
        sub_lbl.pack(side="left", padx=10, pady=(3, 0))

        close_btn = tk.Button(
            top_frame,
            text="✕ Close",
            command=self.destroy,
            bg="#374151",
            fg="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=10,
            pady=3
        )
        close_btn.pack(side="right")

        # 2. Control Bar (Search, Select All, Stats)
        ctrl_card = tk.Frame(self, bg="#252538", bd=1, relief="solid")
        ctrl_card.pack(fill="x", padx=16, pady=4)

        sel_box = tk.Frame(ctrl_card, bg="#252538")
        sel_box.pack(side="left", padx=10, pady=6)

        btn_all = tk.Button(
            sel_box,
            text="☑ Select All",
            command=self._select_all,
            bg="#374151",
            fg="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=8,
            pady=2
        )
        btn_all.pack(side="left", padx=(0, 4))

        btn_none = tk.Button(
            sel_box,
            text="☐ Deselect All",
            command=self._deselect_all,
            bg="#374151",
            fg="white",
            relief="flat",
            font=("Segoe UI", 8),
            cursor="hand2",
            padx=8,
            pady=2
        )
        btn_none.pack(side="left")

        # Search Bar
        search_box = tk.Frame(ctrl_card, bg="#252538")
        search_box.pack(side="left", padx=16, pady=6)

        tk.Label(search_box, text="🔍 Search:", bg="#252538", fg="#94a3b8", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 4))
        self.search_entry = tk.Entry(
            search_box,
            textvariable=self.search_var,
            bg="#181825",
            fg="#f8fafc",
            insertbackground="#ffffff",
            relief="flat",
            font=("Segoe UI", 9),
            width=18
        )
        self.search_entry.pack(side="left", ipady=2)
        self.search_entry.bind("<KeyRelease>", lambda e: self._render_rows())

        # Stats Label
        self.stats_lbl = tk.Label(
            ctrl_card,
            text="Local Orders: 0 | Selected: 0 B",
            bg="#252538",
            fg="#34d399",
            font=("Segoe UI", 9, "bold")
        )
        self.stats_lbl.pack(side="right", padx=12, pady=6)

        # 3. Table (Treeview)
        tree_frame = tk.Frame(self, bg="#181825")
        tree_frame.pack(fill="both", expand=True, padx=16, pady=4)

        columns = ("sel", "order_id", "vendor", "files", "size", "path", "date")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="extended")
        self.tree.heading("sel", text="☐", command=self._toggle_master_checkbox)
        self.tree.heading("order_id", text="Order ID")
        self.tree.heading("vendor", text="Vendor")
        self.tree.heading("files", text="Files")
        self.tree.heading("size", text="Disk Size")
        self.tree.heading("path", text="Folder Location")
        self.tree.heading("date", text="Downloaded Date")

        self.tree.column("sel", width=36, anchor="center")
        self.tree.column("order_id", width=105, anchor="w")
        self.tree.column("vendor", width=125, anchor="w")
        self.tree.column("files", width=65, anchor="center")
        self.tree.column("size", width=95, anchor="center")
        self.tree.column("path", width=300, anchor="w")
        self.tree.column("date", width=150, anchor="center")

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        self.tree.bind("<Button-1>", self._on_tree_click)
        self.tree.bind("<space>", lambda e: self._toggle_selected_rows())

        # 4. Action Buttons Bar
        btn_bar = tk.Frame(self, bg="#1e1e2e")
        btn_bar.pack(fill="x", padx=16, pady=(8, 12))

        open_btn = tk.Button(
            btn_bar,
            text="📂 Open Selected Folder",
            command=self._open_selected_folder,
            bg="#374151",
            fg="white",
            relief="flat",
            font=("Segoe UI", 9),
            cursor="hand2",
            padx=12,
            pady=5
        )
        open_btn.pack(side="left")

        rescan_btn = tk.Button(
            btn_bar,
            text="🔄 Rescan Local Storage",
            command=self._load_local_orders,
            bg="#4b5563",
            fg="white",
            relief="flat",
            font=("Segoe UI", 9),
            cursor="hand2",
            padx=12,
            pady=5
        )
        rescan_btn.pack(side="left", padx=8)

        self.btn_free = tk.Button(
            btn_bar,
            text="☁️ Make Online (Free Space)",
            command=self._make_selected_online,
            bg="#0284c7",
            fg="white",
            activebackground="#0369a1",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=16,
            pady=5
        )
        self.btn_free.pack(side="right")

    def _load_local_orders(self):
        hist = load_history()
        self.local_items.clear()
        self.selected_keys.clear()

        for key, item in hist.items():
            if item.get("status") == "local":
                p = item.get("path")
                sz = item.get("size_bytes", 0)
                if not sz and p and os.path.isdir(p):
                    sz = get_folder_size_bytes(p)
                    item["size_bytes"] = sz
                self.local_items[key] = item

        self._render_rows()

    def _render_rows(self):
        self.tree.delete(*self.tree.get_children())
        query = self.search_var.get().strip().lower()

        total_bytes = 0
        selected_bytes = 0

        for key, item in self.local_items.items():
            oid = str(item.get("order_id", "")).strip()
            vendor = str(item.get("vendor", "")).strip()
            p = str(item.get("path", "")).strip()
            files = str(item.get("files", 0))
            sz = item.get("size_bytes", 0)
            date_str = str(item.get("downloaded_at", item.get("last_updated", "N/A")))

            total_bytes += sz
            is_sel = key in self.selected_keys
            if is_sel:
                selected_bytes += sz

            if query:
                text_blob = f"{oid} {vendor} {p}".lower()
                if query not in text_blob:
                    continue

            chk = "☑" if is_sel else "☐"
            vals = (chk, f"#{oid}", vendor, files, format_bytes(sz), p, date_str)
            self.tree.insert("", "end", iid=key, values=vals)

        sel_count = len(self.selected_keys)
        tot_count = len(self.local_items)
        self.stats_lbl.config(
            text=f"Local Orders: {tot_count} ({format_bytes(total_bytes)}) | Selected: {sel_count} ({format_bytes(selected_bytes)})"
        )
        self.btn_free.config(
            text=f"☁️ Free Up {format_bytes(selected_bytes)} ({sel_count} Orders)" if sel_count > 0 else "☁️ Make Online (Free Space)"
        )

    def _toggle_master_checkbox(self):
        self.master_checked = not self.master_checked
        if self.master_checked:
            self.selected_keys = set(self.local_items.keys())
        else:
            self.selected_keys.clear()
        self.tree.heading("sel", text="☑" if self.master_checked else "☐")
        self._render_rows()

    def _select_all(self):
        self.selected_keys = set(self.local_items.keys())
        self.master_checked = True
        self.tree.heading("sel", text="☑")
        self._render_rows()

    def _deselect_all(self):
        self.selected_keys.clear()
        self.master_checked = False
        self.tree.heading("sel", text="☐")
        self._render_rows()

    def _on_tree_click(self, event):
        col = self.tree.identify_column(event.x)
        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return
        if col == "#1":
            if row_id in self.selected_keys:
                self.selected_keys.remove(row_id)
            else:
                self.selected_keys.add(row_id)
            self._render_rows()
            return "break"

    def _toggle_selected_rows(self):
        for row_id in self.tree.selection():
            if row_id in self.selected_keys:
                self.selected_keys.remove(row_id)
            else:
                self.selected_keys.add(row_id)
        self._render_rows()

    def _open_selected_folder(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Order", "Please select an order from the list first.", parent=self)
            return
        item = self.local_items.get(selected[0])
        if item and item.get("path") and os.path.isdir(item["path"]):
            os.startfile(item["path"])
        else:
            messagebox.showwarning("Not Found", "Folder location not found on disk.", parent=self)

    def _make_selected_online(self):
        if not self.selected_keys:
            messagebox.showinfo("No Selection", "Please check at least one order to make online.", parent=self)
            return

        to_free = [self.local_items[k] for k in self.selected_keys if k in self.local_items]
        total_sz = sum(it.get("size_bytes", 0) for it in to_free)

        confirm = messagebox.askyesno(
            "Free Up Local Storage",
            f"Make {len(to_free)} selected order(s) ({format_bytes(total_sz)}) Online-Only?\n\n"
            "This will instantly reclaim physical hard drive space while preserving all files safely in Dropbox cloud.",
            parent=self
        )
        if not confirm:
            return

        def _worker():
            hist = load_history()
            for it in to_free:
                p = it.get("path")
                oid = it.get("order_id")
                vendor = it.get("vendor")
                if p and os.path.isdir(p):
                    try:
                        free_up_space_cfapi(p)
                        mark_order_history(oid, vendor, p, "online", it.get("files", 0), 0)
                    except Exception:
                        pass
            self.parent.after(0, lambda: [
                self._load_local_orders(),
                self.parent._update_storage_metrics(),
                self.parent._update_leftover_badge(),
                messagebox.showinfo("Completed", f"Successfully freed {format_bytes(total_sz)} across {len(to_free)} orders!", parent=self)
            ])

        threading.Thread(target=_worker, daemon=True).start()


class OrderReviewDialog(tk.Toplevel):
    """
    Inspects queued orders in the Sync List Dashboard, analyzes folder size/files,
    and allows selective downloading/filtering of subfolders (e.g. Raw, Sample, Batch).
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("🔍 Order Review & Smart File Filter")
        self.geometry("960x620")
        self.minsize(800, 500)
        self.configure(bg="#1e1e2e")
        self.transient(parent)
        self.grab_set()

        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - 480
            y = parent.winfo_y() + (parent.winfo_height() // 2) - 310
            self.geometry(f"+{max(x, 50)}+{max(y, 50)}")
        except Exception:
            pass

        self.current_order_id = None
        self.current_folder_path = None
        self.subfolder_vars = {}
        self.subfolder_stats = {}

        self._create_widgets()
        self._load_dashboard_orders()

    def _create_widgets(self):
        # 1. Top Header
        top_frame = tk.Frame(self, bg="#1e1e2e")
        top_frame.pack(fill="x", padx=16, pady=(12, 6))

        title_lbl = tk.Label(
            top_frame,
            text="🔍 Order Review & Smart File Filter",
            font=("Segoe UI", 13, "bold"),
            bg="#1e1e2e",
            fg="#60a5fa"
        )
        title_lbl.pack(side="left")

        sub_lbl = tk.Label(
            top_frame,
            text="Inspect folders and exclude heavy unneeded files (e.g. Raw, Samples) before downloading.",
            font=("Segoe UI", 9),
            bg="#1e1e2e",
            fg="#94a3b8"
        )
        sub_lbl.pack(side="left", padx=10, pady=(3, 0))

        close_btn = tk.Button(
            top_frame,
            text="✕ Close",
            command=self.destroy,
            bg="#374151",
            fg="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=10,
            pady=3
        )
        close_btn.pack(side="right")

        # 2. Main Horizontal Panes (Left: Orders List, Right: Subfolder / File Inspector)
        paned = tk.PanedWindow(self, orient="horizontal", bg="#1e1e2e", bd=0, sashwidth=4)
        paned.pack(fill="both", expand=True, padx=16, pady=4)

        # Left Card: Orders in Dashboard
        left_card = tk.Frame(paned, bg="#252538", bd=1, relief="solid")
        paned.add(left_card, minsize=320, width=380)

        left_header = tk.Frame(left_card, bg="#252538")
        left_header.pack(fill="x", padx=10, pady=8)
        tk.Label(left_header, text="📋 Dashboard Orders:", font=("Segoe UI", 10, "bold"), bg="#252538", fg="#f8fafc").pack(side="left")

        tree_frame = tk.Frame(left_card, bg="#181825")
        tree_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        cols = ("order_id", "vendor", "files", "size", "filter")
        self.orders_tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        self.orders_tree.heading("order_id", text="Order ID")
        self.orders_tree.heading("vendor", text="Vendor")
        self.orders_tree.heading("files", text="Files")
        self.orders_tree.heading("size", text="Disk Size")
        self.orders_tree.heading("filter", text="Filter")

        self.orders_tree.column("order_id", width=95, anchor="w")
        self.orders_tree.column("vendor", width=105, anchor="w")
        self.orders_tree.column("files", width=55, anchor="center")
        self.orders_tree.column("size", width=80, anchor="center")
        self.orders_tree.column("filter", width=85, anchor="center")

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=tree_scroll.set)
        self.orders_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
        self.orders_tree.bind("<<TreeviewSelect>>", self._on_order_selected)

        # Right Card: Folder Structure & Filter Controls
        right_card = tk.Frame(paned, bg="#252538", bd=1, relief="solid")
        paned.add(right_card, minsize=420)

        self.right_header_lbl = tk.Label(
            right_card,
            text="📁 Select an order on the left to inspect files",
            font=("Segoe UI", 10, "bold"),
            bg="#252538",
            fg="#93c5fd"
        )
        self.right_header_lbl.pack(anchor="w", padx=12, pady=(10, 4))

        # Quick Preset Buttons
        preset_bar = tk.Frame(right_card, bg="#252538")
        preset_bar.pack(fill="x", padx=10, pady=(2, 6))

        tk.Button(
            preset_bar,
            text="🎯 QC Images Only (.tif, .psd, .jpg)",
            command=self._preset_qc_only,
            bg="#374151",
            fg="white",
            relief="flat",
            font=("Segoe UI", 8),
            cursor="hand2",
            padx=6,
            pady=2
        ).pack(side="left", padx=(0, 4))

        tk.Button(
            preset_bar,
            text="⚡ Exclude RAW / Samples",
            command=self._preset_exclude_raw,
            bg="#374151",
            fg="white",
            relief="flat",
            font=("Segoe UI", 8),
            cursor="hand2",
            padx=6,
            pady=2
        ).pack(side="left", padx=(0, 4))

        tk.Button(
            preset_bar,
            text="☑ All",
            command=self._preset_all,
            bg="#374151",
            fg="white",
            relief="flat",
            font=("Segoe UI", 8),
            cursor="hand2",
            padx=6,
            pady=2
        ).pack(side="left")

        # Scrollable Frame for subfolder checkboxes
        sub_canvas_frame = tk.Frame(right_card, bg="#181825")
        sub_canvas_frame.pack(fill="both", expand=True, padx=10, pady=4)

        self.canvas = tk.Canvas(sub_canvas_frame, bg="#181825", highlightthickness=0)
        self.canvas_scroll = ttk.Scrollbar(sub_canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.canvas_scroll.set)

        self.checkbox_container = tk.Frame(self.canvas, bg="#181825")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.checkbox_container, anchor="nw")

        self.checkbox_container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas_scroll.pack(side="right", fill="y")

        # Bottom Filter Summary & Save Bar
        bottom_bar = tk.Frame(right_card, bg="#252538")
        bottom_bar.pack(fill="x", padx=10, pady=(6, 10))

        self.filter_summary_lbl = tk.Label(
            bottom_bar,
            text="Selected: 0 files (0 B) of 0 files (0 B)",
            font=("Segoe UI", 9, "bold"),
            bg="#252538",
            fg="#34d399"
        )
        self.filter_summary_lbl.pack(side="left")

        self.btn_save_filter = tk.Button(
            bottom_bar,
            text="💾 Save Filter for this Order",
            command=self._save_filter,
            state="disabled",
            bg="#10b981",
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=12,
            pady=4
        )
        self.btn_save_filter.pack(side="right")

    def _load_dashboard_orders(self):
        self.orders_tree.delete(*self.orders_tree.get_children())
        for key, info in self.parent.resolved_orders.items():
            if not isinstance(info, dict) or not info.get("path"):
                continue
            oid = str(info.get("order_id", "")).strip()
            vendor = str(info.get("vendor", "")).strip()
            files = str(info.get("files", 0))
            sz = info.get("size_bytes", 0)
            clean_id = normalize_order_id(oid)

            f_status = "Custom" if clean_id in self.parent.order_file_whitelists else "All Files"
            vals = (f"#{clean_id}", vendor, files, format_bytes(sz), f_status)
            if not self.orders_tree.exists(key):
                self.orders_tree.insert("", "end", iid=key, values=vals)

    def _on_order_selected(self, event):
        sel = self.orders_tree.selection()
        if not sel:
            return
        key = sel[0]
        info = self.parent.resolved_orders.get(key)
        if not info or not info.get("path") or not os.path.isdir(info["path"]):
            return

        self.current_order_id = normalize_order_id(str(info.get("order_id", "")))
        self.current_folder_path = info["path"]
        vendor = info.get("vendor", "")

        self.right_header_lbl.config(
            text=f"📁 Inspecting: #{self.current_order_id} ({vendor}) — {os.path.basename(self.current_folder_path)}"
        )
        self._analyze_folder(self.current_folder_path)

    def _analyze_folder(self, folder_path):
        for widget in self.checkbox_container.winfo_children():
            widget.destroy()

        self.subfolder_vars.clear()
        self.subfolder_stats.clear()

        existing_whitelist = self.parent.order_file_whitelists.get(self.current_order_id)

        groups = {}
        for root_dir, _, files in os.walk(folder_path):
            rel_dir = os.path.relpath(root_dir, folder_path)
            parts = rel_dir.split(os.sep) if rel_dir != "." else []
            group_name = parts[0] if parts else "[Direct Folder Files]"

            if group_name not in groups:
                groups[group_name] = {"files": 0, "bytes": 0, "file_list": []}

            for f in files:
                if f.lower() in {"desktop.ini", ".dropbox", ".dropbox.attr", "thumbs.db"}:
                    continue
                fp = os.path.join(root_dir, f)
                try:
                    f_sz = os.path.getsize(fp)
                except Exception:
                    f_sz = 0
                groups[group_name]["files"] += 1
                groups[group_name]["bytes"] += f_sz
                groups[group_name]["file_list"].append(fp)

        self.subfolder_stats = groups

        for g_name, data in groups.items():
            cnt = data["files"]
            b_sz = data["bytes"]

            init_val = True
            if existing_whitelist is not None:
                group_fps = set(data["file_list"])
                init_val = bool(group_fps.intersection(existing_whitelist))

            var = tk.BooleanVar(value=init_val)
            self.subfolder_vars[g_name] = var

            cb_frame = tk.Frame(self.checkbox_container, bg="#181825")
            cb_frame.pack(fill="x", padx=10, pady=3)

            cb = tk.Checkbutton(
                cb_frame,
                text=f"📁  {g_name}  ({cnt} files, {format_bytes(b_sz)})",
                variable=var,
                command=self._recalculate_selected_size,
                bg="#181825",
                fg="#f8fafc",
                activebackground="#181825",
                activeforeground="#60a5fa",
                selectcolor="#252538",
                font=("Segoe UI", 9)
            )
            cb.pack(side="left")

        self.btn_save_filter.config(state="normal")
        self._recalculate_selected_size()

    def _recalculate_selected_size(self):
        tot_files = 0
        tot_bytes = 0
        sel_files = 0
        sel_bytes = 0

        for g_name, data in self.subfolder_stats.items():
            tot_files += data["files"]
            tot_bytes += data["bytes"]
            var = self.subfolder_vars.get(g_name)
            if var and var.get():
                sel_files += data["files"]
                sel_bytes += data["bytes"]

        self.filter_summary_lbl.config(
            text=f"Selected: {sel_files} files ({format_bytes(sel_bytes)}) / Total {tot_files} files ({format_bytes(tot_bytes)})"
        )

    def _preset_qc_only(self):
        allowed_exts = {".tif", ".tiff", ".psd", ".jpg", ".jpeg", ".png"}
        for g_name, data in self.subfolder_stats.items():
            has_qc = any(os.path.splitext(fp)[1].lower() in allowed_exts for fp in data["file_list"])
            var = self.subfolder_vars.get(g_name)
            if var:
                var.set(has_qc)
        self._recalculate_selected_size()

    def _preset_exclude_raw(self):
        for g_name, data in self.subfolder_stats.items():
            is_raw = any(k in g_name.lower() for k in ["raw", "sample", "reference", "source"])
            var = self.subfolder_vars.get(g_name)
            if var:
                var.set(not is_raw)
        self._recalculate_selected_size()

    def _preset_all(self):
        for var in self.subfolder_vars.values():
            var.set(True)
        self._recalculate_selected_size()

    def _save_filter(self):
        if not self.current_order_id:
            return
        allowed_fps = set()
        for g_name, data in self.subfolder_stats.items():
            var = self.subfolder_vars.get(g_name)
            if var and var.get():
                allowed_fps.update(data["file_list"])

        self.parent.order_file_whitelists[self.current_order_id] = allowed_fps
        self._load_dashboard_orders()
        self.parent.status_var.set(f"Filter saved for #{self.current_order_id}: {len(allowed_fps)} files will be synced.")
        messagebox.showinfo(
            "Filter Applied",
            f"Successfully applied custom filter to #{self.current_order_id}!\nOnly {len(allowed_fps)} selected file(s) will be downloaded.",
            parent=self
        )

class HistoryTrackerDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("📜 Pending Orders & History Tracker")
        self.geometry("960x600")
        self.minsize(800, 480)
        self.configure(bg="#1e1e2e")
        self.transient(parent)
        self.grab_set()

        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - 480
            y = parent.winfo_y() + (parent.winfo_height() // 2) - 300
            self.geometry(f"+{max(x, 50)}+{max(y, 50)}")
        except Exception:
            pass

        self.filter_var = tk.StringVar(value="pending")
        self.search_var = tk.StringVar(value="")
        self._create_widgets()
        self._refresh_data()

    def _create_widgets(self):
        # 1. Top Header Frame
        top_frame = tk.Frame(self, bg="#1e1e2e")
        top_frame.pack(fill="x", padx=16, pady=(12, 6))

        title_lbl = tk.Label(
            top_frame,
            text="📜 Pending Orders & History Tracker",
            font=("Segoe UI", 13, "bold"),
            bg="#1e1e2e",
            fg="#60a5fa"
        )
        title_lbl.pack(side="left")

        subtitle_lbl = tk.Label(
            top_frame,
            text="Track downloaded orders, search records, and free up hard disk space.",
            font=("Segoe UI", 9),
            bg="#1e1e2e",
            fg="#94a3b8"
        )
        subtitle_lbl.pack(side="left", padx=10, pady=(3, 0))

        close_btn = tk.Button(
            top_frame,
            text="✕ Close",
            command=self.destroy,
            bg="#374151",
            fg="white",
            activebackground="#4b5563",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=10,
            pady=3
        )
        close_btn.pack(side="right")

        # 2. Control Bar (Filter, Search & Stats)
        ctrl_card = tk.Frame(self, bg="#252538", bd=1, relief="solid")
        ctrl_card.pack(fill="x", padx=16, pady=4)

        # Filter Radios on Left
        filter_box = tk.Frame(ctrl_card, bg="#252538")
        filter_box.pack(side="left", padx=10, pady=6)

        tk.Label(filter_box, text="Filter:", bg="#252538", fg="#f8fafc", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 6))

        rb_pending = tk.Radiobutton(
            filter_box,
            text="🔴 Pending Local Only",
            variable=self.filter_var,
            value="pending",
            command=self._refresh_data,
            bg="#252538",
            fg="#f8fafc",
            activebackground="#252538",
            activeforeground="#60a5fa",
            selectcolor="#181825",
            font=("Segoe UI", 9, "bold")
        )
        rb_pending.pack(side="left", padx=4)

        rb_all = tk.Radiobutton(
            filter_box,
            text="📋 All History",
            variable=self.filter_var,
            value="all",
            command=self._refresh_data,
            bg="#252538",
            fg="#94a3b8",
            activebackground="#252538",
            activeforeground="#60a5fa",
            selectcolor="#181825",
            font=("Segoe UI", 9)
        )
        rb_all.pack(side="left", padx=4)

        # Search Bar in Middle
        search_box = tk.Frame(ctrl_card, bg="#252538")
        search_box.pack(side="left", padx=14, pady=6)

        tk.Label(search_box, text="🔍 Search:", bg="#252538", fg="#94a3b8", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 4))
        self.search_entry = tk.Entry(
            search_box,
            textvariable=self.search_var,
            bg="#181825",
            fg="#f8fafc",
            insertbackground="#ffffff",
            relief="flat",
            font=("Segoe UI", 9),
            width=20
        )
        self.search_entry.pack(side="left", ipady=2)
        self.search_entry.bind("<KeyRelease>", lambda e: self._refresh_data())

        search_clear_btn = tk.Button(
            search_box,
            text="✕",
            command=self._clear_search,
            bg="#374151",
            fg="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=5,
            pady=1
        )
        search_clear_btn.pack(side="left", padx=(2, 0))

        # Stats Label on Right
        self.stats_lbl = tk.Label(
            ctrl_card,
            text="Pending: 0 | Online: 0 | Total: 0",
            bg="#252538",
            fg="#93c5fd",
            font=("Segoe UI", 9, "bold")
        )
        self.stats_lbl.pack(side="right", padx=12, pady=6)

        # 3. Table (Treeview)
        tree_frame = tk.Frame(self, bg="#181825")
        tree_frame.pack(fill="both", expand=True, padx=16, pady=4)

        columns = ("order_id", "vendor", "status", "files", "size", "time")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="extended")
        self.tree.heading("order_id", text="Order ID")
        self.tree.heading("vendor", text="Vendor")
        self.tree.heading("status", text="Sync Status")
        self.tree.heading("files", text="Files")
        self.tree.heading("size", text="Disk Size")
        self.tree.heading("time", text="Downloaded / Updated")

        self.tree.column("order_id", width=110, anchor="w")
        self.tree.column("vendor", width=130, anchor="w")
        self.tree.column("status", width=160, anchor="center")
        self.tree.column("files", width=60, anchor="center")
        self.tree.column("size", width=95, anchor="center")
        self.tree.column("time", width=170, anchor="center")

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        self.tree.tag_configure("pending_tag", foreground="#f87171")
        self.tree.tag_configure("online_tag", foreground="#34d399")

        self.tree.bind("<Double-1>", lambda e: self._open_selected_folder())

        # Context Menu
        self.context_menu = tk.Menu(self, tearoff=0, bg="#252538", fg="white", activebackground="#3b82f6", activeforeground="white")
        self.context_menu.add_command(label="📂 Open in File Explorer", command=self._open_selected_folder)
        self.context_menu.add_command(label="☁️ Make this Order Online-Only", command=self._free_selected)
        self.context_menu.add_command(label="📋 Load into Main QC Table", command=self._load_to_main_table)
        self.tree.bind("<Button-3>", self._on_tree_right_click)

        # 4. Action Buttons Bar at Bottom
        btn_bar = tk.Frame(self, bg="#1e1e2e")
        btn_bar.pack(fill="x", padx=16, pady=(6, 12))

        # Left Action Group
        left_btns = tk.Frame(btn_bar, bg="#1e1e2e")
        left_btns.pack(side="left")

        open_btn = tk.Button(
            left_btns,
            text="📂 Open Folder",
            command=self._open_selected_folder,
            bg="#374151",
            fg="white",
            relief="flat",
            font=("Segoe UI", 9),
            cursor="hand2",
            padx=10,
            pady=4
        )
        open_btn.pack(side="left", padx=(0, 6))

        load_btn = tk.Button(
            left_btns,
            text="📋 Load to QC Table",
            command=self._load_to_main_table,
            bg="#4b5563",
            fg="white",
            relief="flat",
            font=("Segoe UI", 9),
            cursor="hand2",
            padx=10,
            pady=4
        )
        load_btn.pack(side="left", padx=(0, 6))

        clear_hist_btn = tk.Button(
            left_btns,
            text="🗑️ Clear Completed History",
            command=self._clear_online_history,
            bg="#252538",
            fg="#94a3b8",
            activebackground="#ef4444",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8),
            cursor="hand2",
            padx=8,
            pady=4
        )
        clear_hist_btn.pack(side="left")

        clean_all_hist_btn = tk.Button(
            left_btns,
            text="🗑️ Clean All History",
            command=self._clean_all_history,
            bg="#7f1d1d",
            fg="#fca5a5",
            activebackground="#ef4444",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=8,
            pady=4
        )
        clean_all_hist_btn.pack(side="left", padx=(6, 0))

        # Right Action Group (Primary Cleanup Actions)
        right_btns = tk.Frame(btn_bar, bg="#1e1e2e")
        right_btns.pack(side="right")

        single_online_btn = tk.Button(
            right_btns,
            text="☁️ Make Selected Online",
            command=self._free_selected,
            bg="#0284c7",
            fg="white",
            activebackground="#0369a1",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=12,
            pady=5
        )
        single_online_btn.pack(side="left", padx=(0, 6))

        free_all_btn = tk.Button(
            right_btns,
            text="⚡ Make ALL Pending Online (Free Space)",
            command=self._free_all_pending,
            bg="#10b981",
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=14,
            pady=5
        )
        free_all_btn.pack(side="left")

    def _clear_search(self):
        self.search_var.set("")
        self._refresh_data()

    def _on_tree_right_click(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.context_menu.post(event.x_root, event.y_root)

    def _refresh_data(self):
        self.tree.delete(*self.tree.get_children())
        hist = load_history()
        filter_mode = self.filter_var.get()
        query = self.search_var.get().strip().lower()

        local_count = 0
        online_count = 0
        total_local_bytes = 0

        # Count and sync with existing paths
        updated = False
        for key, item in list(hist.items()):
            p = item.get("path")
            if item.get("status") == "local":
                if not p or not os.path.isdir(p):
                    item["status"] = "online"
                    item["size_bytes"] = 0
                    hist[key] = item
                    updated = True

            if item.get("status") == "local":
                local_count += 1
                b = item.get("size_bytes", 0)
                if not b and p and os.path.isdir(p):
                    b = get_folder_size_bytes(p)
                    item["size_bytes"] = b
                    updated = True
                total_local_bytes += b or 0
            else:
                online_count += 1

        if updated:
            save_history(hist)

        self.stats_lbl.config(
            text=f"🔴 Pending Local: {local_count} | 🟢 Online: {online_count} | 📁 Total: {len(hist)} | 📦 Local Size: {format_bytes(total_local_bytes)}"
        )

        sorted_keys = sorted(
            hist.keys(),
            key=lambda k: (
                0 if hist[k].get("status") == "local" else 1,
                hist[k].get("last_updated") or hist[k].get("downloaded_at") or ""
            ),
            reverse=False
        )

        for key in sorted_keys:
            entry = hist[key]
            status = entry.get("status", "online")
            order_id = str(entry.get("order_id", key))
            vendor = str(entry.get("vendor", "-"))

            if filter_mode == "pending" and status != "local":
                continue

            if query:
                if query not in order_id.lower() and query not in vendor.lower() and query not in status.lower():
                    continue

            status_display = "🔴 Local (Disk Active)" if status == "local" else "🟢 Online (0 Bytes)"
            tag = "pending_tag" if status == "local" else "online_tag"
            time_display = entry.get("downloaded_at") or entry.get("last_updated") or "-"
            files_display = str(entry.get("files", 0))
            size_display = format_bytes(entry.get("size_bytes", 0)) if status == "local" else "0 B (Cloud)"

            self.tree.insert(
                "",
                "end",
                iid=key,
                values=(
                    f"#{order_id}",
                    vendor,
                    status_display,
                    files_display,
                    size_display,
                    time_display
                ),
                tags=(tag,)
            )

    def _open_selected_folder(self):
        selected = self.tree.selection()
        if not selected:
            return
        item_key = selected[0]
        hist = load_history()
        entry = hist.get(item_key)
        if entry and entry.get("path") and os.path.isdir(entry["path"]):
            try:
                os.startfile(entry["path"])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open folder:\n{e}", parent=self)
        else:
            messagebox.showwarning("Folder Missing", "Folder path was not found on this computer.", parent=self)

    def _free_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Order", "Please select at least one order from the list.", parent=self)
            return

        hist = load_history()
        count = 0
        for item_key in selected:
            entry = hist.get(item_key)
            if not entry:
                continue
            p = entry.get("path")
            if p and os.path.isdir(p):
                try:
                    cmd = f'attrib -P +U "{p}\\*.*" /s & attrib -P +U "{p}" /d'
                    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass
            mark_order_history(entry["order_id"], entry.get("vendor"), p, "online", entry.get("files", 0), 0)
            count += 1

        self._refresh_data()
        self.parent._update_leftover_badge()
        self.parent._update_storage_metrics()
        messagebox.showinfo("Online Complete", f"Successfully converted {count} order(s) to Online-Only!", parent=self)

    def _free_all_pending(self):
        tracked = get_tracked_local_orders()
        if not tracked:
            messagebox.showinfo("Clean Drive", "🎉 Excellent! No pending local orders found. Your disk space is clean.", parent=self)
            return

        confirm = messagebox.askyesno(
            "Make All Pending Online",
            f"You have {len(tracked)} pending local order(s) taking disk space.\n\n"
            f"Do you want to convert these {len(tracked)} order(s) to Online-Only to free up hard drive space?\n\n"
            "(No other Dropbox folders will be affected.)",
            parent=self
        )
        if not confirm:
            return

        self.parent._free_orders_in_background(tracked)
        self._refresh_data()
        self.parent._update_leftover_badge()
        self.parent._update_storage_metrics()
        messagebox.showinfo(
            "Space Freed",
            f"Successfully converted {len(tracked)} pending order(s) to Online-Only!\nHard drive space has been recovered.",
            parent=self
        )

    def _load_to_main_table(self):
        selected = self.tree.selection()
        hist = load_history()
        orders_to_load = []

        if selected:
            for s in selected:
                if s in hist:
                    orders_to_load.append(hist[s])
        else:
            for iid in self.tree.get_children():
                if iid in hist:
                    orders_to_load.append(hist[iid])

        if not orders_to_load:
            messagebox.showinfo("Info", "No orders available to load.", parent=self)
            return

        unique_ids = list(dict.fromkeys([it["order_id"] for it in orders_to_load]))
        formatted = "\n".join([f"#{oid}" for oid in unique_ids])
        self.parent.input_text.delete("1.0", "end")
        self.parent.input_text.insert("1.0", formatted)
        self.parent._update_order_count()
        self.parent.status_var.set(f"Loaded {len(unique_ids)} order(s) from history into QC input.")
        messagebox.showinfo("Success", f"Loaded {len(unique_ids)} order ID(s) into the main QC window!", parent=self)
        self.destroy()

    def _clear_online_history(self):
        hist = load_history()
        cleaned_hist = {k: v for k, v in hist.items() if v.get("status") == "local"}
        cleared_count = len(hist) - len(cleaned_hist)
        if cleared_count == 0:
            messagebox.showinfo("History Clean", "No completed online records to clear.", parent=self)
            return

        confirm = messagebox.askyesno(
            "Clear Completed History",
            f"Clear {cleared_count} completed (Online) order record(s) from history?\n\n"
            "(Pending local orders will be kept safely.)",
            parent=self
        )
        if confirm:
            save_history(cleaned_hist)
            self._refresh_data()
            self.parent._update_leftover_badge()
            messagebox.showinfo("Completed", f"Cleared {cleared_count} completed record(s) from history.", parent=self)


    def _clean_all_history(self):
        hist = load_history()
        if not hist:
            messagebox.showinfo("History Clean", "History is already empty.", parent=self)
            return

        confirm = messagebox.askyesno(
            "Clean All History",
            f"⚠️ WARNING: This will permanently delete ALL {len(hist)} order record(s) from history (both pending local and online).\n\n"
            "Are you sure you want to proceed?",
            icon="warning",
            parent=self
        )
        if confirm:
            save_history({})
            self._refresh_data()
            self.parent._update_leftover_badge()
            self.parent._update_storage_metrics()
            messagebox.showinfo("Completed", "All order history has been deleted.", parent=self)

class QCBatchLoaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"🚀 {APP_NAME} {CURRENT_VERSION} — {APP_TAGLINE}")
        self.geometry("980x780")
        self.minsize(860, 620)

        # Set taskbar/window icon
        try:
            if os.path.exists(APP_ICON_PATH):
                self.iconbitmap(APP_ICON_PATH)
        except Exception:
            pass

        self.config_data = load_config()

        # Threading & Process Control state
        self.is_running = False
        self.is_paused = False
        self.stop_requested = False
        self.pause_event = threading.Event()
        self.pause_event.set()

        # Vendor Selector state
        self.detected_vendors = []
        self.selected_vendors = set()
        self.vendor_popup = None
        self.vendor_check_vars = {}
        self.vendor_row_widgets = {}

        # Lookups and caches
        self.resolved_orders = {}
        self.table_items = {}
        self.search_var = tk.StringVar(value="")

        # Advanced V1.5 / V1.6 features state
        self.order_file_whitelists = {}
        self.drawer_open = True
        self.input_cleaned = False
        self.order_checkboxes = {}
        self.master_checked = False
        self.available_update = None
        self.unread_notifications = 0

        self._scan_vendors()
        self._setup_style()
        self._create_widgets()
        self._update_order_count()
        self._update_leftover_badge()
        self._update_storage_metrics()

        # Real-time Update System: Initial check, periodic polling, and first-launch guide
        self.after(2500, lambda: check_for_updates(self, silent=True))
        self.after(3600000, self._periodic_update_check)
        self.after(1200, self._check_first_launch_whats_new)

    def _setup_style(self):
        self.configure(bg="#1e1e2e")
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Color Palette
        self.bg_color = "#1e1e2e"
        self.card_bg = "#252538"
        self.card_border = "#3a3a54"
        self.accent_blue = "#3b82f6"
        self.accent_green = "#10b981"
        self.accent_orange = "#f59e0b"
        self.accent_red = "#ef4444"
        self.text_main = "#f8fafc"
        self.text_muted = "#94a3b8"

        self.style.configure(".", background=self.bg_color, foreground=self.text_main, font=("Segoe UI", 9))
        self.style.configure("Card.TFrame", background=self.card_bg)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_main)
        self.style.configure("Card.TLabel", background=self.card_bg, foreground=self.text_main)
        self.style.configure("Muted.TLabel", background=self.card_bg, foreground=self.text_muted)
        
        self.style.configure("Total.Horizontal.TProgressbar", thickness=10, background="#10b981", troughcolor="#181825")
        self.style.configure("Single.Horizontal.TProgressbar", thickness=8, background="#3b82f6", troughcolor="#181825")
        
        # Treeview styling
        self.style.configure(
            "Treeview",
            background="#181825",
            foreground=self.text_main,
            fieldbackground="#181825",
            rowheight=26,
            font=("Segoe UI", 9)
        )
        self.style.configure(
            "Treeview.Heading",
            background="#2b2b40",
            foreground=self.text_main,
            font=("Segoe UI", 9, "bold")
        )
        self.style.map("Treeview", background=[("selected", "#3b82f6")], foreground=[("selected", "#ffffff")])

    def _scan_vendors(self, keep_selection=False):
        """Scans the Dropbox root folder for all vendor directories."""
        base_path = self.path_var.get() if hasattr(self, "path_var") else self.config_data.get("dropbox_path") or DEFAULT_DROPBOX_PATH
        vendors = []
        if base_path and os.path.isdir(base_path):
            try:
                vendors = [
                    d for d in os.listdir(base_path)
                    if not d.startswith(".") and os.path.isdir(os.path.join(base_path, d))
                ]
                vendors.sort(key=lambda x: x.lower())
            except Exception:
                vendors = []

        self.detected_vendors = vendors

        if not keep_selection or not self.selected_vendors:
            saved_sel = self.config_data.get("selected_vendors")
            if saved_sel and isinstance(saved_sel, list):
                valid_saved = {v for v in saved_sel if v in self.detected_vendors}
                self.selected_vendors = valid_saved if valid_saved else set(self.detected_vendors)
            else:
                self.selected_vendors = set(self.detected_vendors)
        else:
            self.selected_vendors = {v for v in self.selected_vendors if v in self.detected_vendors}
            if not self.selected_vendors and self.detected_vendors:
                self.selected_vendors = set(self.detected_vendors)

        if hasattr(self, "vendor_btn"):
            self._update_vendor_btn_label()

    def _update_vendor_btn_label(self):
        """Updates the vendor dropdown button text and styling based on active selection."""
        if not hasattr(self, "vendor_btn"):
            return

        total = len(self.detected_vendors)
        sel_count = len(self.selected_vendors)

        if total == 0:
            self.vendor_btn.config(text="🏢 Vendors: None Found ▼", bg="#374151", fg="#94a3b8")
            if hasattr(self, "vendor_reset_btn"):
                self.vendor_reset_btn.pack_forget()
        elif sel_count == total:
            self.vendor_btn.config(text=f"🏢 Vendors: All ({total}) ▼", bg="#252538", fg="#f8fafc")
            if hasattr(self, "vendor_reset_btn"):
                self.vendor_reset_btn.pack_forget()
        elif sel_count == 1:
            single = next(iter(self.selected_vendors))
            self.vendor_btn.config(text=f"🏢 Filter: {single} (1/{total}) ▼", bg="#d97706", fg="#ffffff")
            if hasattr(self, "vendor_reset_btn"):
                self.vendor_reset_btn.pack(side="left", padx=(0, 8), pady=4, after=self.vendor_btn)
        elif sel_count == 0:
            self.vendor_btn.config(text=f"🏢 Filter: None (0/{total}) ⚠️ ▼", bg="#ef4444", fg="#ffffff")
            if hasattr(self, "vendor_reset_btn"):
                self.vendor_reset_btn.pack(side="left", padx=(0, 8), pady=4, after=self.vendor_btn)
        else:
            names = sorted(list(self.selected_vendors))
            short = f"{names[0]}, {names[1]}" if len(names) == 2 else f"{names[0]} +{sel_count - 1} more"
            self.vendor_btn.config(text=f"🏢 Filter: {short} ({sel_count}/{total}) ▼", bg="#d97706", fg="#ffffff")
            if hasattr(self, "vendor_reset_btn"):
                self.vendor_reset_btn.pack(side="left", padx=(0, 8), pady=4, after=self.vendor_btn)

    def _reset_vendor_filter(self):
        """Resets active vendor selection to all detected vendors."""
        self.selected_vendors = set(self.detected_vendors)
        for v_name, var in self.vendor_check_vars.items():
            var.set(True)
        self._save_selected_vendors()
        self._update_vendor_btn_label()
        self.status_var.set(f"Vendor filter reset: All {len(self.detected_vendors)} vendors active.")

    def _close_vendor_popup(self, event=None):
        if self.vendor_popup and self.vendor_popup.winfo_exists():
            try:
                self.vendor_popup.destroy()
            except Exception:
                pass
        self.vendor_popup = None
        try:
            self.unbind_all("<Button-1>")
        except Exception:
            pass

    def _toggle_vendor_popup(self):
        """Displays a multi-select dropdown popup directly beneath the Vendor button."""
        if self.vendor_popup and self.vendor_popup.winfo_exists():
            self._close_vendor_popup()
            return

        self.vendor_popup = tk.Toplevel(self)
        self.vendor_popup.wm_overrideredirect(True)
        self.vendor_popup.configure(bg="#252538", bd=1, relief="solid")

        x = self.vendor_btn.winfo_rootx()
        y = self.vendor_btn.winfo_rooty() + self.vendor_btn.winfo_height() + 2
        self.vendor_popup.geometry(f"+{x}+{y}")

        # Search bar inside popup
        search_frame = tk.Frame(self.vendor_popup, bg="#252538")
        search_frame.pack(fill="x", padx=8, pady=(6, 2))
        tk.Label(search_frame, text="🔍", bg="#252538", fg="#94a3b8", font=("Segoe UI", 8)).pack(side="left", padx=(0, 2))

        search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame, textvariable=search_var, bg="#181825", fg="#f8fafc",
            insertbackground="white", relief="flat", font=("Segoe UI", 8), width=26
        )
        search_entry.pack(side="left", fill="x", expand=True, ipady=2)

        # Action Buttons
        act_frame = tk.Frame(self.vendor_popup, bg="#252538")
        act_frame.pack(fill="x", padx=8, pady=(2, 4))

        all_sel = (len(self.selected_vendors) == len(self.detected_vendors) and len(self.detected_vendors) > 0)
        self.master_vendor_var = tk.BooleanVar(value=all_sel)

        def toggle_master():
            is_checked = self.master_vendor_var.get()
            if is_checked:
                self.selected_vendors.update(self.detected_vendors)
                for var in self.vendor_check_vars.values():
                    var.set(True)
            else:
                self.selected_vendors.clear()
                for var in self.vendor_check_vars.values():
                    var.set(False)
            self._update_vendor_btn_label()
            update_status_label()
            self._save_selected_vendors()

        master_cb = tk.Checkbutton(
            act_frame,
            text="Select / Deselect All",
            variable=self.master_vendor_var,
            command=toggle_master,
            bg="#252538",
            fg="#f8fafc",
            selectcolor="#181825",
            activebackground="#252538",
            activeforeground="white",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2"
        )
        master_cb.pack(side="left", padx=(0, 4))

        def rescan():
            self._scan_vendors(keep_selection=True)
            self._close_vendor_popup()
            self._toggle_vendor_popup()

        tk.Button(act_frame, text="🔄", command=rescan, bg="#374151", fg="#93c5fd", relief="flat", font=("Segoe UI", 8), padx=5).pack(side="left", padx=2)
        tk.Button(act_frame, text="✕ Done", command=self._close_vendor_popup, bg="#10b981", fg="white", relief="flat", font=("Segoe UI", 8, "bold"), padx=8).pack(side="right")

        # Scrollable list
        canvas_frame = tk.Frame(self.vendor_popup, bg="#181825")
        canvas_frame.pack(fill="both", expand=True, padx=8, pady=4)

        canvas_height = min(max(len(self.detected_vendors) * 26, 60), 220)
        canvas = tk.Canvas(canvas_frame, bg="#181825", highlightthickness=0, height=canvas_height, width=270)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#181825")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=252)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel scrolling handler
        def _on_mousewheel(e):
            step = int(-1 * (e.delta / 120))
            canvas.yview_scroll(step, "units")

        self.vendor_popup.bind("<MouseWheel>", _on_mousewheel)
        canvas_frame.bind("<MouseWheel>", _on_mousewheel)
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scroll_frame.bind("<MouseWheel>", _on_mousewheel)

        self.vendor_check_vars.clear()
        self.vendor_row_widgets.clear()

        for v in self.detected_vendors:
            row = tk.Frame(scroll_frame, bg="#181825")
            row.pack(fill="x", pady=1)
            row.bind("<MouseWheel>", _on_mousewheel)
            self.vendor_row_widgets[v] = row

            var = tk.BooleanVar(value=(v in self.selected_vendors))
            self.vendor_check_vars[v] = var

            def on_toggle(v_name=v, v_var=var):
                if v_var.get():
                    self.selected_vendors.add(v_name)
                else:
                    self.selected_vendors.discard(v_name)
                all_checked = (len(self.selected_vendors) == len(self.detected_vendors) and len(self.detected_vendors) > 0)
                self.master_vendor_var.set(all_checked)
                self._update_vendor_btn_label()
                update_status_label()
                self._save_selected_vendors()

            cb = tk.Checkbutton(
                row, text=v, variable=var, command=on_toggle,
                bg="#181825", fg="white", selectcolor="#252538",
                activebackground="#181825", activeforeground="white",
                anchor="w", font=("Segoe UI", 8)
            )
            cb.pack(side="left", fill="x", expand=True)
            cb.bind("<MouseWheel>", _on_mousewheel)

            def select_only(v_name=v):
                self.selected_vendors.clear()
                self.selected_vendors.add(v_name)
                for name, chk in self.vendor_check_vars.items():
                    chk.set(name == v_name)
                self.master_vendor_var.set(len(self.detected_vendors) == 1)
                self._update_vendor_btn_label()
                update_status_label()
                self._save_selected_vendors()

            only_btn = tk.Button(
                row, text="Only", command=select_only,
                bg="#374151", fg="#93c5fd", activebackground="#3b82f6", activeforeground="white",
                relief="flat", font=("Segoe UI", 7, "bold"), padx=4
            )
            only_btn.pack(side="right", padx=2)
            only_btn.bind("<MouseWheel>", _on_mousewheel)

        def on_search(event=None):
            q = search_var.get().strip().lower()
            for v_name, w in self.vendor_row_widgets.items():
                if not q or q in v_name.lower():
                    w.pack(fill="x", pady=1)
                else:
                    w.pack_forget()

        search_entry.bind("<KeyRelease>", on_search)

        # Bottom status label
        b_frame = tk.Frame(self.vendor_popup, bg="#252538")
        b_frame.pack(fill="x", padx=8, pady=(2, 6))
        status_lbl = tk.Label(b_frame, text="", bg="#252538", fg="#94a3b8", font=("Segoe UI", 8))
        status_lbl.pack(side="left")

        def update_status_label():
            status_lbl.config(text=f"{len(self.selected_vendors)} of {len(self.detected_vendors)} selected")

        update_status_label()

        def _on_outside_click(event):
            if self.vendor_popup and self.vendor_popup.winfo_exists():
                x, y = event.x_root, event.y_root
                px, py = self.vendor_popup.winfo_rootx(), self.vendor_popup.winfo_rooty()
                pw, ph = self.vendor_popup.winfo_width(), self.vendor_popup.winfo_height()
                bx, by = self.vendor_btn.winfo_rootx(), self.vendor_btn.winfo_rooty()
                bw, bh = self.vendor_btn.winfo_width(), self.vendor_btn.winfo_height()
                if not (px <= x <= px + pw and py <= y <= py + ph) and not (bx <= x <= bx + bw and by <= y <= by + bh):
                    self._close_vendor_popup()

        self.after(100, lambda: self.bind_all("<Button-1>", _on_outside_click))

    def _save_selected_vendors(self):
        try:
            self.config_data["selected_vendors"] = list(self.selected_vendors)
            save_config(self.config_data)
        except Exception:
            pass

    def _create_widgets(self):
        # 1. Top Header
        top_frame = tk.Frame(self, bg=self.bg_color)
        top_frame.pack(fill="x", padx=16, pady=(10, 4))

        title_box = tk.Frame(top_frame, bg=self.bg_color)
        title_box.pack(side="left")

        # Window & Taskbar Icon
        try:
            if os.path.exists(APP_ICON_PATH):
                self.iconbitmap(APP_ICON_PATH)
        except Exception:
            pass

        # Logo Header Image
        try:
            if os.path.exists(LOGO_HEADER_PATH):
                self.logo_img = tk.PhotoImage(file=LOGO_HEADER_PATH)
                logo_lbl = tk.Label(title_box, image=self.logo_img, bg=self.bg_color)
                logo_lbl.pack(side="left", padx=(0, 10))
        except Exception:
            pass

        text_title_box = tk.Frame(title_box, bg=self.bg_color)
        text_title_box.pack(side="left")

        title_row = tk.Frame(text_title_box, bg=self.bg_color)
        title_row.pack(anchor="w")

        title_lbl = tk.Label(
            title_row,
            text=APP_NAME,
            font=("Segoe UI", 14, "bold"),
            bg=self.bg_color,
            fg="#60a5fa"
        )
        title_lbl.pack(side="left")

        version_badge = tk.Label(
            title_row,
            text=CURRENT_VERSION,
            font=("Segoe UI", 8, "bold"),
            bg="#3b82f6",
            fg="white",
            padx=5,
            pady=1
        )
        version_badge.pack(side="left", padx=8)

        subtitle_lbl = tk.Label(
            text_title_box,
            text=APP_TAGLINE,
            font=("Segoe UI", 8),
            bg=self.bg_color,
            fg=self.text_muted
        )
        subtitle_lbl.pack(anchor="w", pady=(1, 0))

        # Top Right Action Buttons
        header_actions = tk.Frame(top_frame, bg=self.bg_color)
        header_actions.pack(side="right")

        self.notification_btn = tk.Button(
            header_actions,
            text="🔔",
            command=self._open_notification_center,
            bg="#252538",
            fg="#94a3b8",
            activebackground="#3b82f6",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 9),
            cursor="hand2",
            padx=8,
            pady=3
        )
        self.notification_btn.pack(side="right")

        self.leftover_btn = tk.Button(
            header_actions,
            text="📜 History: 0 Local",
            command=self._open_history_tracker,
            bg="#252538",
            fg="#10b981",
            activebackground="#3b82f6",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=9,
            pady=3
        )
        self.leftover_btn.pack(side="right", padx=(0, 6))

        self.local_clean_btn = tk.Button(
            header_actions,
            text="🧹 Local Clean",
            command=self._open_local_clean,
            bg="#252538",
            fg="#34d399",
            activebackground="#059669",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=9,
            pady=3
        )
        self.local_clean_btn.pack(side="right", padx=(0, 6))

        # 2. Unified Compact Dropbox Path & Drive Space Bar
        path_card = tk.Frame(self, bg=self.card_bg, bd=1, relief="solid")
        path_card.pack(fill="x", padx=16, pady=(3, 3))

        path_lbl = tk.Label(path_card, text="📁 Dropbox Root:", bg=self.card_bg, fg=self.text_main, font=("Segoe UI", 9, "bold"))
        path_lbl.pack(side="left", padx=(10, 4), pady=5)

        self.path_var = tk.StringVar(value=self.config_data.get("dropbox_path") or DEFAULT_DROPBOX_PATH)
        path_entry = tk.Entry(
            path_card,
            textvariable=self.path_var,
            bg="#181825",
            fg="#f8fafc",
            insertbackground="#ffffff",
            relief="flat",
            font=("Segoe UI", 9),
            width=26
        )
        path_entry.pack(side="left", padx=(0, 4), pady=5, ipady=2)

        browse_btn = tk.Button(
            path_card,
            text="Browse...",
            command=self._browse_dropbox_path,
            bg="#374151",
            fg="white",
            activebackground="#4b5563",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=8,
            pady=2
        )
        browse_btn.pack(side="left", padx=(0, 10), pady=5)

        # Drive Space Metric Label & Local Orders Metric Label
        self.drive_metric_lbl = tk.Label(
            path_card,
            text="💾 Drive Free: Calculating...",
            bg=self.card_bg,
            fg="#93c5fd",
            font=("Segoe UI", 8, "bold")
        )
        self.drive_metric_lbl.pack(side="left", padx=(4, 8), pady=5)

        self.local_metric_lbl = tk.Label(
            path_card,
            text="📦 Local: 0 B",
            bg=self.card_bg,
            fg="#34d399",
            font=("Segoe UI", 8, "bold")
        )
        self.local_metric_lbl.pack(side="left", padx=4, pady=5)

        refresh_metric_btn = tk.Button(
            path_card,
            text="🔄 Refresh",
            command=self._update_storage_metrics,
            bg="#374151",
            fg="white",
            activebackground="#4b5563",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8),
            cursor="hand2",
            padx=8,
            pady=1
        )
        refresh_metric_btn.pack(side="right", padx=(0, 10), pady=5)

        # 3. Smart Toolbar (Paste Order IDs, Vendors, Order Review, Clean Dashboard, Make Local/Online All)
        toolbar_card = tk.Frame(self, bg=self.card_bg, bd=1, relief="solid")
        toolbar_card.pack(fill="x", padx=16, pady=(1, 4))

        # Toggle Paste Order IDs Button
        self.btn_toggle_drawer = tk.Button(
            toolbar_card,
            text="📋 Paste Order IDs",
            command=self._toggle_drawer,
            bg="#3b82f6",
            fg="white",
            activebackground="#2563eb",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=10,
            pady=3
        )
        self.btn_toggle_drawer.pack(side="left", padx=(10, 6), pady=4)

        # Vendors Filter Dropdown
        self.vendor_btn = tk.Button(
            toolbar_card,
            text="🏢 Vendors: All ▼",
            command=self._toggle_vendor_popup,
            bg="#252538",
            fg="#f8fafc",
            activebackground="#374151",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=10,
            pady=3
        )
        self.vendor_btn.pack(side="left", padx=(0, 6), pady=4)

        self.vendor_reset_btn = tk.Button(
            toolbar_card,
            text="✕ Reset All",
            command=self._reset_vendor_filter,
            bg="#4b5563",
            fg="#ffffff",
            activebackground="#374151",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8),
            cursor="hand2",
            padx=6,
            pady=3
        )

        self._update_vendor_btn_label()

        # Order Review Button
        self.btn_order_review = tk.Button(
            toolbar_card,
            text="🔍 Order Review",
            command=self._open_order_review,
            bg="#252538",
            fg="#93c5fd",
            activebackground="#374151",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=10,
            pady=3
        )
        self.btn_order_review.pack(side="left", padx=(0, 6), pady=4)

        # Clean Dashboard Button
        self.btn_clean_dashboard = tk.Button(
            toolbar_card,
            text="🗑️ Clean Dashboard",
            command=self._clean_dashboard,
            bg="#252538",
            fg="#f87171",
            activebackground="#ef4444",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8),
            cursor="hand2",
            padx=8,
            pady=3
        )
        self.btn_clean_dashboard.pack(side="left", padx=(0, 6), pady=4)

        # Right Action Buttons: Make Local All & Make Online All
        self.btn_make_online_all = tk.Button(
            toolbar_card,
            text="☁️ Make Online All",
            command=self._make_all_online,
            bg="#0284c7",
            fg="white",
            activebackground="#0369a1",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=10,
            pady=3
        )
        self.btn_make_online_all.pack(side="right", padx=(0, 10), pady=4)

        self.btn_make_local_all = tk.Button(
            toolbar_card,
            text="📥 Make Local All",
            command=self._make_all_local,
            bg=self.accent_green,
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=10,
            pady=3
        )
        self.btn_make_local_all.pack(side="right", padx=(0, 6), pady=4)

        # 4. Main Split Panes (Left Drawer for Order IDs, Right for Dashboard Table)
        self.paned = tk.PanedWindow(self, orient="horizontal", bg=self.bg_color, bd=0, sashwidth=4)
        self.paned.pack(fill="both", expand=True, padx=16, pady=4)
        paned = self.paned

        # Left Pane: Order ID Input Drawer
        self.left_frame = tk.Frame(paned, bg=self.card_bg, bd=1, relief="solid")
        paned.add(self.left_frame, minsize=270, width=290)
        self.drawer_open = True

        left_header = tk.Frame(self.left_frame, bg=self.card_bg)
        left_header.pack(fill="x", padx=10, pady=(8, 4))

        tk.Label(left_header, text="📋 Paste Order IDs:", bg=self.card_bg, fg=self.text_main, font=("Segoe UI", 9, "bold")).pack(side="left")
        self.count_lbl = tk.Label(left_header, text="0 orders", bg=self.card_bg, fg=self.text_muted, font=("Segoe UI", 8))
        self.count_lbl.pack(side="right")

        self.input_text = tk.Text(
            self.left_frame,
            bg="#181825",
            fg="#f8fafc",
            insertbackground="#ffffff",
            relief="flat",
            font=("Consolas", 10),
            wrap="word",
            padx=8,
            pady=8
        )
        self.input_text.pack(fill="both", expand=True, padx=10, pady=4)
        self.input_text.bind("<KeyRelease>", self._on_input_text_changed)

        # Row 1 below text input: Clear, Paste, Clean Duplicate
        btn_row_left = tk.Frame(self.left_frame, bg=self.card_bg)
        btn_row_left.pack(fill="x", padx=10, pady=(4, 2))

        clear_btn = tk.Button(
            btn_row_left,
            text="Clear",
            command=self._clear_input,
            bg="#374151",
            fg="white",
            relief="flat",
            font=("Segoe UI", 8),
            cursor="hand2",
            padx=6,
            pady=2
        )
        clear_btn.pack(side="left", padx=(0, 4))

        paste_btn = tk.Button(
            btn_row_left,
            text="Paste",
            command=self._paste_clipboard,
            bg="#4b5563",
            fg="white",
            relief="flat",
            font=("Segoe UI", 8),
            cursor="hand2",
            padx=6,
            pady=2
        )
        paste_btn.pack(side="left", padx=(0, 4))

        # Clean Duplicate Button (Dynamic Red/Green State)
        self.btn_clean_dedup = tk.Button(
            btn_row_left,
            text="🧹 Clean Duplicate",
            command=self._clean_and_deduplicate,
            bg="#ef4444",
            fg="white",
            activebackground="#dc2626",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=6,
            pady=2
        )
        self.btn_clean_dedup.pack(side="right")

        # Row 2 below text input: Add to Sync List Button (starts disabled)
        sync_row_left = tk.Frame(self.left_frame, bg=self.card_bg)
        sync_row_left.pack(fill="x", padx=10, pady=(2, 6))

        self.btn_add_to_sync = tk.Button(
            sync_row_left,
            text="➕ Add to Sync List",
            command=self._add_to_sync_list,
            state="disabled",
            bg="#374151",
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="arrow",
            pady=4
        )
        self.btn_add_to_sync.pack(fill="x")

        # Right Pane: Sync List Dashboard Table
        self.right_frame = tk.Frame(paned, bg=self.card_bg, bd=1, relief="solid")
        paned.add(self.right_frame, minsize=480)

        right_header = tk.Frame(self.right_frame, bg=self.card_bg)
        right_header.pack(fill="x", padx=10, pady=(8, 4))

        # Modern Pill Search Bar with inside 🔍 and integrated inside ✕ clear button
        search_pill = tk.Frame(right_header, bg="#181825", bd=1, relief="solid")
        search_pill.pack(side="left")

        tk.Label(search_pill, text="🔍", bg="#181825", fg="#94a3b8", font=("Segoe UI", 8)).pack(side="left", padx=(6, 2))

        self.search_entry = tk.Entry(
            search_pill,
            textvariable=self.search_var,
            bg="#181825",
            fg="#f8fafc",
            insertbackground="#ffffff",
            relief="flat",
            font=("Segoe UI", 8),
            width=20
        )
        self.search_entry.pack(side="left", ipady=2, padx=(0, 2))
        self.search_entry.bind("<KeyRelease>", lambda e: self._filter_main_table())

        clear_search_btn = tk.Button(
            search_pill,
            text="✕",
            command=self._clear_main_search,
            bg="#181825",
            fg="#94a3b8",
            activebackground="#252538",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            bd=0,
            padx=6,
            pady=1
        )
        clear_search_btn.pack(side="left")

        # Header Right Actions: Open Folder & Scan Local
        open_btn = tk.Button(
            right_header,
            text="📂 Open",
            command=self._open_selected_folder,
            bg="#3b82f6",
            fg="white",
            activebackground="#2563eb",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=8,
            pady=2
        )
        open_btn.pack(side="right", padx=(4, 0))

        self.btn_scan_local = tk.Button(
            right_header,
            text="🔍 Scan Local Orders",
            command=self._scan_local_in_selected_vendors,
            bg="#7c3aed",
            fg="white",
            activebackground="#6d28d9",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=8,
            pady=2
        )
        self.btn_scan_local.pack(side="right", padx=(4, 0))

        # Dashboard Treeview Table
        tree_frame = tk.Frame(self.right_frame, bg="#181825")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=4)

        columns = ("sel", "order_id", "vendor", "status", "files", "size", "actions")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="extended")
        self.tree.heading("sel", text="☐", command=self._toggle_master_checkbox)
        self.tree.heading("order_id", text="Order ID")
        self.tree.heading("vendor", text="Vendor")
        self.tree.heading("status", text="Sync Status")
        self.tree.heading("files", text="Files")
        self.tree.heading("size", text="Disk Size")
        self.tree.heading("actions", text="Action")

        self.tree.column("sel", width=36, anchor="center")
        self.tree.column("order_id", width=105, anchor="w")
        self.tree.column("vendor", width=125, anchor="w")
        self.tree.column("status", width=155, anchor="center")
        self.tree.column("files", width=65, anchor="center")
        self.tree.column("size", width=90, anchor="center")
        self.tree.column("actions", width=110, anchor="center")

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        # Treeview Tag Styling
        self.tree.tag_configure("row_syncing", background="#2a2b4a", foreground="#38bdf8")
        self.tree.tag_configure("row_local", foreground="#34d399")
        self.tree.tag_configure("row_online", foreground="#94a3b8")
        self.tree.tag_configure("row_notfound", foreground="#f87171")

        # Treeview Bindings
        self.tree.bind("<Button-1>", self._on_tree_click)
        self.tree.bind("<Double-1>", self._on_tree_double_click)
        self.tree.bind("<Button-3>", self._on_tree_right_click)
        self.tree.bind("<Control-c>", self._copy_selected_order_ids)
        self.tree.bind("<Control-C>", self._copy_selected_order_ids)
        self.tree.bind("<space>", self._on_space_key)

        # Context menu for right-click on table rows
        self.context_menu = tk.Menu(self, tearoff=0, bg="#252538", fg="white", activebackground="#3b82f6", activeforeground="white")
        self.context_menu.add_command(label="📋 Copy Order ID(s) (Ctrl+C)", command=self._copy_selected_order_ids)
        self.context_menu.add_command(label="📂 Open in File Explorer", command=self._open_selected_folder)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📥 Make Local (Download)", command=self._make_selected_local)
        self.context_menu.add_command(label="☁️ Make Online (Free Space)", command=self._make_selected_online)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🔍 Review / Filter Files", command=self._open_order_review)
        self.context_menu.add_command(label="🗑️ Remove from Dashboard", command=self._remove_selected_from_dashboard)

        # 5. Floating Bottom Progress & Controls Dock
        dock_card = tk.Frame(self, bg=self.card_bg, bd=1, relief="solid")
        dock_card.pack(fill="x", padx=16, pady=(3, 6))

        dock_inner = tk.Frame(dock_card, bg=self.card_bg)
        dock_inner.pack(fill="x", padx=12, pady=6)

        # Left: Status indicator
        status_box = tk.Frame(dock_inner, bg=self.card_bg)
        status_box.pack(side="left", fill="x", expand=True)

        self.status_var = tk.StringVar(value="Ready. Paste Order IDs and click Add to Sync List.")
        self.status_pill_lbl = tk.Label(
            status_box,
            textvariable=self.status_var,
            bg=self.card_bg,
            fg="#93c5fd",
            font=("Segoe UI", 9)
        )
        self.status_pill_lbl.pack(anchor="w")

        self.total_lbl = tk.Label(
            status_box,
            text="Total Progress: 0% (0 / 0 Orders)",
            font=("Segoe UI", 8, "bold"),
            bg=self.card_bg,
            fg=self.text_muted
        )
        self.total_lbl.pack(anchor="w", pady=(1, 0))

        self.total_progress = ttk.Progressbar(status_box, style="Total.Horizontal.TProgressbar", mode="determinate")
        self.total_progress.pack(fill="x", pady=(2, 0))

        # Hidden single order progress for internal hydration tracking
        self.single_lbl = tk.Label(self, text="")
        self.single_progress = ttk.Progressbar(self, mode="determinate")

        # Right: Quick Global Controls (Pause All & Stop All)
        ctrl_box = tk.Frame(dock_inner, bg=self.card_bg)
        ctrl_box.pack(side="right", padx=(12, 0))

        self.btn_pause = tk.Button(
            ctrl_box,
            text="⏸️ Pause All",
            command=self._toggle_pause,
            state="disabled",
            bg=self.accent_orange,
            fg="white",
            activebackground="#d97706",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=10,
            pady=4
        )
        self.btn_pause.pack(side="left", padx=(0, 4))

        self.btn_stop = tk.Button(
            ctrl_box,
            text="⏹️ Stop All",
            command=self._request_stop,
            state="disabled",
            bg=self.accent_red,
            fg="white",
            activebackground="#dc2626",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=10,
            pady=4
        )
        self.btn_stop.pack(side="left")

    def _toggle_drawer(self):
        """Toggles the Paste Order IDs left drawer between collapsed and visible."""
        if getattr(self, "drawer_open", True):
            self.paned.forget(self.left_frame)
            self.drawer_open = False
            self.btn_toggle_drawer.config(bg="#252538", fg="#94a3b8")
            self.status_var.set("Order IDs drawer closed.")
        else:
            if hasattr(self, "right_frame") and self.right_frame in self.paned.panes():
                self.paned.add(self.left_frame, before=self.right_frame, minsize=270, width=290)
            else:
                self.paned.add(self.left_frame, minsize=270, width=290)
            self.drawer_open = True
            self.btn_toggle_drawer.config(bg="#3b82f6", fg="white")
            self.status_var.set("Order IDs drawer opened.")

    def _on_input_text_changed(self, event=None):
        self._update_order_count()
        self.input_cleaned = False
        self.btn_clean_dedup.config(
            text="🧹 Clean Duplicate",
            bg="#ef4444",
            activebackground="#dc2626"
        )
        self.btn_add_to_sync.config(
            state="disabled",
            bg="#374151",
            cursor="arrow"
        )

    def _clean_and_deduplicate(self):
        unique_orders, total_lines = self._parse_order_ids()
        if not unique_orders:
            messagebox.showinfo("Clean Duplicate", "No valid Order IDs found to clean.", parent=self)
            return

        formatted = "\n".join([f"#{oid}" for oid in unique_orders])
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", formatted)
        self._update_order_count()

        self.input_cleaned = True
        self.btn_clean_dedup.config(
            text="✅ Clean Duplicate",
            bg="#10b981",
            activebackground="#059669"
        )
        self.btn_add_to_sync.config(
            state="normal",
            bg="#10b981",
            cursor="hand2"
        )
        self.status_var.set(f"Deduplicated! {total_lines} lines cleaned into {len(unique_orders)} unique orders. Ready to Add.")

    def _clean_dashboard(self):
        if self.is_running:
            messagebox.showwarning("Busy", "Cannot clean dashboard while a process is running.", parent=self)
            return
        if not self.tree.get_children():
            messagebox.showinfo("Dashboard Empty", "Sync List Dashboard is already empty.", parent=self)
            return
        ans = messagebox.askyesno(
            "Clean Dashboard",
            "Are you sure you want to clear all orders and information from the Sync List Dashboard?",
            parent=self
        )
        if ans:
            self.tree.delete(*self.tree.get_children())
            self.resolved_orders.clear()
            self.table_items.clear()
            self.order_checkboxes.clear()
            self.order_file_whitelists.clear()
            self.total_progress["value"] = 0
            self.single_progress["value"] = 0
            self.total_lbl.config(text="Total Progress: 0% (0 / 0 Orders)")
            self.status_var.set("Dashboard cleared.")

    def _toggle_master_checkbox(self):
        all_iids = self.tree.get_children()
        if not all_iids:
            return
        self.master_checked = not getattr(self, "master_checked", False)
        new_mark = "☑" if self.master_checked else "☐"
        self.tree.heading("sel", text=new_mark)
        for iid in all_iids:
            self.order_checkboxes[iid] = new_mark
            vals = list(self.tree.item(iid, "values"))
            if vals:
                vals[0] = new_mark
                self.tree.item(iid, values=vals)
        self.status_var.set(f"{'Selected' if self.master_checked else 'Deselected'} all {len(all_iids)} orders.")

    def _toggle_row_checkbox(self, item_id):
        cur = self.order_checkboxes.get(item_id, "☐")
        new_val = "☑" if cur == "☐" else "☐"
        self.order_checkboxes[item_id] = new_val
        vals = list(self.tree.item(item_id, "values"))
        if vals:
            vals[0] = new_val
            self.tree.item(item_id, values=vals)

    def _on_tree_click(self, event):
        col = self.tree.identify_column(event.x)
        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return
        if col == "#1":
            self._toggle_row_checkbox(row_id)
            return "break"
        elif col == "#7":
            vals = self.tree.item(row_id, "values")
            action_text = vals[6] if len(vals) > 6 else ""
            if "Make Online" in action_text:
                self._make_single_order_online(row_id)
            elif "Make Local" in action_text:
                self._make_single_order_local(row_id)
            return "break"

    def _on_space_key(self, event=None):
        for iid in self.tree.selection():
            self._toggle_row_checkbox(iid)

    def _copy_selected_order_ids(self, event=None):
        selected_iids = list(self.tree.selection())
        checked_iids = [k for k, v in self.order_checkboxes.items() if v == "☑"]
        target_iids = list(dict.fromkeys(selected_iids + checked_iids))

        if not target_iids:
            target_iids = list(self.tree.get_children())

        if not target_iids:
            self.status_var.set("No order IDs to copy.")
            return

        order_ids = []
        for iid in target_iids:
            info = self.resolved_orders.get(iid)
            if info and info.get("order_id"):
                oid = str(info["order_id"]).strip().lstrip("#")
            else:
                vals = self.tree.item(iid, "values")
                if vals and len(vals) > 1:
                    oid = str(vals[1]).strip().lstrip("#")
                else:
                    oid = str(iid).split("_")[0].lstrip("#")
            if oid and oid not in order_ids:
                order_ids.append(oid)

        if order_ids:
            clipboard_text = "\n".join(f"#{oid}" for oid in order_ids)
            self.clipboard_clear()
            self.clipboard_append(clipboard_text)
            self.status_var.set(f"Copied {len(order_ids)} Order ID(s) to clipboard.")
        else:
            self.status_var.set("No valid Order IDs found to copy.")

    def _open_order_review(self):
        OrderReviewDialog(self)

    def _open_local_clean(self):
        LocalCleanDialog(self)

    def _open_notification_center(self):
        self.unread_notifications = 0
        self._update_notification_badge()
        NotificationCenterDialog(self, available_update=self.available_update)

    def _update_notification_badge(self):
        if getattr(self, "unread_notifications", 0) > 0 and self.available_update:
            self.notification_btn.config(
                text="🔔 1",
                bg="#f59e0b",
                fg="#000000",
                font=("Segoe UI", 8, "bold")
            )
        else:
            self.notification_btn.config(
                text="🔔",
                bg="#252538",
                fg="#94a3b8",
                font=("Segoe UI", 9)
            )

    def _remove_selected_from_dashboard(self):
        selected = list(self.tree.selection())
        for iid in selected:
            self.tree.delete(iid)
            self.table_items.pop(iid, None)
            self.order_checkboxes.pop(iid, None)
        self.status_var.set(f"Removed {len(selected)} order(s) from dashboard.")

    def _filter_main_table(self):
        query = self.search_var.get().strip().lower()
        self.tree.delete(*self.tree.get_children())
        for key, vals in self.table_items.items():
            order_id = str(vals[1]).lower() if len(vals) > 1 else ""
            vendor = str(vals[2]).lower() if len(vals) > 2 else ""
            status = str(vals[3]).lower() if len(vals) > 3 else ""
            if not query or query in order_id or query in vendor or query in status:
                tag = "row_syncing" if "Syncing" in status or "%" in status else ("row_local" if "Local" in status else ("row_notfound" if "Not Found" in status else "row_online"))
                self.tree.insert("", "end", iid=key, values=vals, tags=(tag,))

    def _clear_main_search(self):
        self.search_var.set("")
        self._filter_main_table()
    def _add_to_sync_list(self):
        """Parses order IDs and resolves their current state into the table without downloading yet."""
        if self.is_running:
            messagebox.showinfo("Busy", "A task is currently running. Please wait for it to finish.", parent=self)
            return

        orders, invalid = self._parse_order_ids()
        if not orders:
            messagebox.showwarning("No Orders", "Please paste or enter at least one Order ID.", parent=self)
            return

        base_path = self.path_var.get()
        if not base_path or not os.path.isdir(base_path):
            messagebox.showwarning("Invalid Dropbox Path", "Please configure a valid Dropbox Root path first.", parent=self)
            return

        self.status_var.set(f"Resolving {len(orders)} order(s) into sync list...")
        selected_v = set(self.selected_vendors) if hasattr(self, "selected_vendors") and self.selected_vendors else None
        vendor_index = build_vendor_index(base_path, selected_vendors=selected_v)
        full_vendor_index = None

        kernel32 = ctypes.windll.kernel32 if hasattr(ctypes, "windll") else None
        added_count = 0
        IGNORE_FILES = {"desktop.ini", ".dropbox", ".dropbox.attr", "thumbs.db"}

        for order_id in orders:
            clean_id = normalize_order_id(order_id)
            matches = vendor_index.get(clean_id, [])

            if not matches and selected_v and len(selected_v) < len(self.detected_vendors):
                if full_vendor_index is None:
                    full_vendor_index = build_vendor_index(base_path, selected_vendors=None)
                matches = full_vendor_index.get(clean_id, [])

            if not matches:
                item_key = f"{clean_id}_notfound"
                chk = self.order_checkboxes.get(item_key, "☐")
                if not self.tree.exists(item_key):
                    row_vals = (chk, f"#{clean_id}", "-", "❌ Not Found", "0", "0 B", "-")
                    self.tree.insert("", "end", iid=item_key, values=row_vals, tags=("row_notfound",))
                    self.table_items[item_key] = row_vals
                    info = {"order_id": clean_id, "vendor": "-", "path": None, "status": "❌ Not Found", "files": 0, "size_bytes": 0}
                    self.resolved_orders[item_key] = info
                    self.resolved_orders[clean_id] = info
                added_count += 1
            else:
                for match in matches:
                    vendor = match["vendor"]
                    order_dir = match["order_dir"]
                    folder_path = resolve_target_folder(order_dir)
                    file_list, total_size = collect_folder_files(folder_path)
                    total_files = len(file_list)

                    local_files = 0
                    local_bytes = 0
                    if kernel32 and file_list:
                        for fp in file_list:
                            if os.path.basename(fp).lower() in IGNORE_FILES:
                                continue
                            try:
                                attrs = kernel32.GetFileAttributesW(fp)
                                if attrs != -1 and not (attrs & FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS) and not (attrs & FILE_ATTRIBUTE_OFFLINE):
                                    local_files += 1
                                    local_bytes += os.path.getsize(fp)
                            except Exception:
                                pass

                    if local_files == total_files and total_files > 0:
                        status_text = "✅ Local (Ready)"
                        disp_size = format_bytes(local_bytes)
                        action_text = "☁️ Make Online"
                        row_tag = "row_local"
                    elif local_files > 0:
                        status_text = f"⚠️ Local ({local_files}/{total_files})"
                        disp_size = format_bytes(local_bytes)
                        action_text = "☁️ Make Online"
                        row_tag = "row_local"
                    else:
                        status_text = "☁️ Online-Only"
                        disp_size = "0 B"
                        action_text = "📥 Make Local"
                        row_tag = "row_online"

                    item_key = f"{clean_id}_{vendor}"
                    chk = self.order_checkboxes.get(item_key, "☐")
                    row_vals = (chk, f"#{clean_id}", vendor, status_text, str(total_files), disp_size, action_text)
                    if self.tree.exists(item_key):
                        self.tree.item(item_key, values=row_vals, tags=(row_tag,))
                    else:
                        self.tree.insert("", "end", iid=item_key, values=row_vals, tags=(row_tag,))
                    self.table_items[item_key] = row_vals
                    info = {
                        "order_id": clean_id,
                        "vendor": vendor,
                        "path": folder_path,
                        "status": status_text,
                        "files": total_files,
                        "size_bytes": local_bytes if local_files > 0 else 0
                    }
                    self.resolved_orders[item_key] = info
                    self.resolved_orders[clean_id] = info
                    self.resolved_orders[f"#{clean_id}"] = info
                    added_count += 1

        self.total_lbl.config(text=f"Total Orders in Dashboard: {len(self.table_items)}")
        self.status_var.set(f"Added/updated {added_count} order item(s) in sync list.")

    def _thread_scan_local_orders(self, base_path, target_vendors):
        self._set_controls_running(True)
        self.status_var.set(f"Scanning local orders across {len(target_vendors)} vendor(s)...")
        self.tree.delete(*self.tree.get_children())
        self.resolved_orders = {}
        self.table_items = {}
        self.order_checkboxes = {}

        kernel32 = ctypes.windll.kernel32 if hasattr(ctypes, "windll") else None
        IGNORE_FILES = {"desktop.ini", ".dropbox", ".dropbox.attr", "thumbs.db"}

        def scan_single_order(entry_path, vendor_name, order_name):
            local_count = 0
            total_files = 0
            local_bytes = 0
            try:
                for root_dir, _, files in os.walk(entry_path):
                    for f in files:
                        if f.lower() in IGNORE_FILES:
                            continue
                        total_files += 1
                        fp = os.path.join(root_dir, f)
                        if kernel32:
                            try:
                                attrs = kernel32.GetFileAttributesW(fp)
                                if attrs != -1 and not (attrs & FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS) and not (attrs & FILE_ATTRIBUTE_OFFLINE):
                                    local_count += 1
                                    local_bytes += os.path.getsize(fp)
                            except Exception:
                                pass
            except Exception:
                pass
            if local_count > 0:
                return {
                    "order_id": order_name,
                    "vendor": vendor_name,
                    "path": entry_path,
                    "local_count": local_count,
                    "total_files": total_files,
                    "local_bytes": local_bytes
                }
            return None

        tasks = []
        with ThreadPoolExecutor(max_workers=8) as executor:
            for v_name in target_vendors:
                v_path = os.path.join(base_path, v_name)
                if not os.path.isdir(v_path):
                    continue
                try:
                    for entry in os.scandir(v_path):
                        if entry.is_dir():
                            tasks.append(executor.submit(scan_single_order, entry.path, v_name, entry.name))
                except Exception:
                    pass

            found_items = []
            for fut in as_completed(tasks):
                res = fut.result()
                if res:
                    found_items.append(res)

        total_local_bytes = sum(item["local_bytes"] for item in found_items)
        for item in found_items:
            oid = item["order_id"]
            vendor = item["vendor"]
            item_key = f"{oid}_{vendor}"
            row_vals = (
                "☐",
                f"#{oid}",
                vendor,
                "✅ Local (Ready)",
                str(item["total_files"]),
                format_bytes(item["local_bytes"]),
                "☁️ Make Online"
            )
            self.table_items[item_key] = row_vals
            self.tree.insert("", "end", iid=item_key, values=row_vals, tags=("row_local",))
            info = {
                "order_id": oid,
                "vendor": vendor,
                "path": item["path"],
                "status": "✅ Local (Ready)",
                "files": item["total_files"],
                "size_bytes": item["local_bytes"]
            }
            self.resolved_orders[item_key] = info
            self.resolved_orders[oid] = info
            self.resolved_orders[f"#{oid}"] = info
            mark_order_history(oid, vendor, item["path"], "local", item["total_files"], item["local_bytes"])

        self._set_controls_running(False)
        self.status_var.set(f"Scan complete: Found {len(found_items)} local order(s) taking {format_bytes(total_local_bytes)}.")
        self._update_leftover_badge()
        self._update_storage_metrics()
        self.total_lbl.config(text=f"Total Orders in Dashboard: {len(found_items)}")

    def _make_single_order_online(self, item_id):
        info = self.resolved_orders.get(item_id)
        if not info or not info.get("path") or not os.path.isdir(info["path"]):
            messagebox.showwarning("Not Found", "Folder location not found on disk.", parent=self)
            return

        folder_path = info["path"]
        order_id = info.get("order_id", "")
        vendor = info.get("vendor", "")
        file_count = info.get("files", 0)

        try:
            free_up_space_cfapi(folder_path)
            chk = self.order_checkboxes.get(item_id, "☐")
            new_vals = (chk, f"#{order_id}", vendor, "☁️ Online-Only", str(file_count), "0 B", "📥 Make Local")
            self.tree.item(item_id, values=new_vals, tags=("row_online",))
            self.table_items[item_id] = new_vals
            info["status"] = "☁️ Online-Only"
            info["size_bytes"] = 0
            mark_order_history(order_id, vendor, folder_path, "online", file_count, 0)
            self._update_leftover_badge()
            self._update_storage_metrics()
            self.status_var.set(f"☁️ Order #{order_id} ({vendor}) is now Online-Only.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to make order online:\n{e}", parent=self)

    def _make_single_order_local(self, item_id):
        info = self.resolved_orders.get(item_id)
        if not info or not info.get("path") or not os.path.isdir(info["path"]):
            messagebox.showwarning("Not Found", "Folder location not found on disk.", parent=self)
            return

        folder_path = info["path"]
        order_id = normalize_order_id(str(info.get("order_id", "")))
        vendor = info.get("vendor", "")

        def _worker():
            try:
                chk = self.order_checkboxes.get(item_id, "☐")
                self.after(0, lambda: self.tree.item(item_id, values=(chk, f"#{order_id}", vendor, "⏳ Syncing...", str(info.get("files", 0)), format_bytes(info.get("size_bytes", 0)), "⏳ Syncing"), tags=("row_syncing",)))
                file_list, total_size = collect_folder_files(folder_path)

                if order_id in self.order_file_whitelists:
                    allowed = self.order_file_whitelists[order_id]
                    file_list = [fp for fp in file_list if fp in allowed]
                    total_size = sum(os.path.getsize(fp) for fp in file_list if os.path.exists(fp))

                cmd = f'attrib +P -U "{folder_path}\\*.*" /s & attrib +P -U "{folder_path}" /d'
                subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                workers = min(8, max(len(file_list), 1))
                with ThreadPoolExecutor(max_workers=workers) as executor:
                    list(executor.map(_hydrate_single_file, file_list))

                status_text = "✅ Local (Ready)"
                new_vals = (chk, f"#{order_id}", vendor, status_text, str(len(file_list)), format_bytes(total_size), "☁️ Make Online")
                self.after(0, lambda: [
                    self.tree.item(item_id, values=new_vals, tags=("row_local",)),
                    self.table_items.update({item_id: new_vals}),
                    mark_order_history(order_id, vendor, folder_path, "local", len(file_list), total_size),
                    self._update_leftover_badge(),
                    self._update_storage_metrics(),
                    self.status_var.set(f"✅ Order #{order_id} ({vendor}) is now Local and ready for QC.")
                ])
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to hydrate order:\n{e}", parent=self))

        threading.Thread(target=_worker, daemon=True).start()

    def _make_selected_online(self):
        checked_iids = [k for k, v in self.order_checkboxes.items() if v == "☑"]
        selected_iids = list(self.tree.selection())
        target_iids = list(dict.fromkeys(checked_iids + selected_iids))

        if not target_iids:
            messagebox.showinfo("Select Order", "Please select or check one or more orders from the list first.", parent=self)
            return

        freed_count = 0
        for item_id in target_iids:
            info = self.resolved_orders.get(item_id)
            if not info or not info.get("path") or not os.path.isdir(info["path"]):
                continue

            folder_path = info["path"]
            order_id = normalize_order_id(str(info.get("order_id", "")))
            vendor = info.get("vendor", "")
            file_count = info.get("files", 0)

            try:
                free_up_space_cfapi(folder_path)
                status_text = "☁️ Online-Only"
                chk = self.order_checkboxes.get(item_id, "☐")
                new_vals = (chk, f"#{order_id}", vendor, status_text, str(file_count), "0 B", "📥 Make Local")
                self.tree.item(item_id, values=new_vals, tags=("row_online",))
                self.table_items[item_id] = new_vals
                info["status"] = status_text
                info["size_bytes"] = 0
                mark_order_history(order_id, vendor, folder_path, "online", file_count, 0)
                freed_count += 1
            except Exception:
                pass

        self._update_leftover_badge()
        self._update_storage_metrics()
        if freed_count > 0:
            self.status_var.set(f"☁️ Made {freed_count} order(s) Online-Only. Disk space freed!")
            messagebox.showinfo("Space Freed", f"Successfully made {freed_count} order(s) Online-Only!\nDisk space has been freed.", parent=self)

    def _make_selected_local(self):
        checked_iids = [k for k, v in self.order_checkboxes.items() if v == "☑"]
        selected_iids = list(self.tree.selection())
        target_iids = list(dict.fromkeys(checked_iids + selected_iids))

        if not target_iids:
            messagebox.showinfo("Select Order", "Please select or check one or more orders from the list first.", parent=self)
            return

        for item_id in target_iids:
            self._make_single_order_local(item_id)

    def _make_all_local(self):
        all_iids = list(self.tree.get_children())
        if not all_iids:
            messagebox.showinfo("Dashboard Empty", "No orders in dashboard to make local.", parent=self)
            return
        orders_to_sync = []
        for iid in all_iids:
            vals = self.tree.item(iid, "values")
            if vals and len(vals) > 1:
                orders_to_sync.append(str(vals[1]).lstrip("#"))
        if orders_to_sync:
            self._start_make_local_from_list(orders_to_sync)

    def _make_all_online(self):
        all_iids = list(self.tree.get_children())
        if not all_iids:
            messagebox.showinfo("Dashboard Empty", "No orders in dashboard to make online.", parent=self)
            return
        confirm = messagebox.askyesno(
            "Make All Online",
            f"Make all {len(all_iids)} orders in the Dashboard Online-Only to free disk space?",
            parent=self
        )
        if not confirm:
            return
        freed = 0
        for iid in all_iids:
            info = self.resolved_orders.get(iid)
            if info and info.get("path") and os.path.isdir(info["path"]):
                try:
                    free_up_space_cfapi(info["path"])
                    chk = self.order_checkboxes.get(iid, "☐")
                    new_vals = (chk, f"#{info.get('order_id')}", info.get("vendor"), "☁️ Online-Only", str(info.get("files", 0)), "0 B", "📥 Make Local")
                    self.tree.item(iid, values=new_vals, tags=("row_online",))
                    self.table_items[iid] = new_vals
                    mark_order_history(info.get("order_id"), info.get("vendor"), info["path"], "online", info.get("files", 0), 0)
                    freed += 1
                except Exception:
                    pass
        self._update_leftover_badge()
        self._update_storage_metrics()
        self.status_var.set(f"Made {freed} order(s) Online-Only.")

    def _start_make_local_from_list(self, orders):
        if self.is_running:
            return
        base_path = self.path_var.get()
        if not base_path or not os.path.isdir(base_path):
            messagebox.showwarning("Invalid Dropbox Path", "Please configure a valid Dropbox Root path first.", parent=self)
            return

        self.is_running = True
        self.is_paused = False
        self.stop_requested = False
        self.pause_event.set()
        self._set_controls_running(True)

        threading.Thread(target=self._process_make_local, args=(orders,), daemon=True).start()

    def _process_make_local(self, orders):
        base_path = self.path_var.get()
        total_orders = len(orders)

        self.total_progress["maximum"] = max(total_orders, 1)
        self.total_progress["value"] = 0

        selected_v = set(self.selected_vendors) if hasattr(self, "selected_vendors") and self.selected_vendors else None
        self.status_var.set("Indexing vendors for ultra-fast lookup...")
        vendor_index = build_vendor_index(base_path, selected_vendors=selected_v)
        full_vendor_index = None

        success_count = 0
        not_found_count = 0

        for i, order_id in enumerate(orders):
            if self.stop_requested:
                break
            self.pause_event.wait()
            if self.stop_requested:
                break

            clean_id = normalize_order_id(order_id)
            pct = int((i / max(total_orders, 1)) * 100)
            self.total_lbl.config(text=f"Total Progress: {pct}% ({i} / {total_orders} Orders)")
            self.total_progress["value"] = i
            self.status_var.set(f"Processing #{order_id} ({i+1}/{total_orders})...")

            matches = vendor_index.get(clean_id, [])
            if not matches and selected_v and len(selected_v) < len(self.detected_vendors):
                if full_vendor_index is None:
                    full_vendor_index = build_vendor_index(base_path, selected_vendors=None)
                matches = full_vendor_index.get(clean_id, [])

            if not matches:
                status_text = "❌ Not Found"
                item_key = f"{order_id}_notfound"
                chk = self.order_checkboxes.get(item_key, "☐")
                row_vals = (chk, f"#{order_id}", "-", status_text, "0", "0 B", "-")
                self.resolved_orders[item_key] = {"order_id": order_id, "vendor": "-", "path": None, "status": status_text, "files": 0, "size_bytes": 0}
                self.resolved_orders[order_id] = self.resolved_orders[item_key]
                self.table_items[item_key] = row_vals
                if self.tree.exists(item_key):
                    self.tree.item(item_key, values=row_vals, tags=("row_notfound",))
                else:
                    self.tree.insert("", "end", iid=item_key, values=row_vals, tags=("row_notfound",))
                not_found_count += 1
            else:
                for match in matches:
                    if self.stop_requested:
                        break
                    self.pause_event.wait()
                    if self.stop_requested:
                        break

                    vendor = match["vendor"]
                    order_dir = match["order_dir"]
                    folder_path = resolve_target_folder(order_dir)
                    file_list, total_size = collect_folder_files(folder_path)

                    # Check whitelist from OrderReview
                    if clean_id in self.order_file_whitelists:
                        allowed = self.order_file_whitelists[clean_id]
                        file_list = [fp for fp in file_list if fp in allowed]
                        total_size = sum(os.path.getsize(fp) for fp in file_list if os.path.exists(fp))

                    total_files = len(file_list)
                    item_key = f"{order_id}_{vendor}"
                    chk = self.order_checkboxes.get(item_key, "☐")

                    row_vals = (chk, f"#{order_id}", vendor, "⏳ Syncing 0%", str(total_files), format_bytes(total_size), "⏳ Syncing")
                    self.table_items[item_key] = row_vals
                    if self.tree.exists(item_key):
                        self.tree.item(item_key, values=row_vals, tags=("row_syncing",))
                    else:
                        self.tree.insert("", "end", iid=item_key, values=row_vals, tags=("row_syncing",))
                    self.tree.see(item_key)

                    try:
                        cmd = f'attrib +P -U "{folder_path}\\*.*" /s & attrib +P -U "{folder_path}" /d'
                        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        completed_files = 0
                        if file_list:
                            workers = min(8, len(file_list))
                            with ThreadPoolExecutor(max_workers=workers) as executor:
                                futures = {executor.submit(_hydrate_single_file, fp): fp for fp in file_list}
                                for fut in as_completed(futures):
                                    if self.stop_requested:
                                        executor.shutdown(wait=False, cancel_futures=True)
                                        break
                                    self.pause_event.wait()
                                    if self.stop_requested:
                                        executor.shutdown(wait=False, cancel_futures=True)
                                        break

                                    completed_files += 1
                                    s_pct = int((completed_files / max(total_files, 1)) * 100)
                                    prog_text = f"⏳ Syncing {s_pct}% ({completed_files}/{total_files})"
                                    cur_vals = (chk, f"#{order_id}", vendor, prog_text, str(total_files), format_bytes(total_size), "⏳ Syncing")
                                    self.tree.item(item_key, values=cur_vals, tags=("row_syncing",))
                                    self.status_var.set(f"Hydrating #{order_id} ({completed_files}/{total_files} files)")

                        status_text = "✅ Local (Ready)"
                        action_text = "☁️ Make Online"
                        success_count += 1
                        mark_order_history(order_id, vendor, folder_path, "local", total_files, total_size)
                    except Exception as e:
                        status_text = f"⚠️ Error: {str(e)[:15]}"
                        action_text = "📥 Make Local"

                    final_vals = (chk, f"#{order_id}", vendor, status_text, str(total_files), format_bytes(total_size), action_text)
                    self.table_items[item_key] = final_vals
                    self.tree.item(item_key, values=final_vals, tags=("row_local" if "Local" in status_text else "row_online",))
                    order_info = {
                        "order_id": order_id,
                        "vendor": vendor,
                        "path": folder_path,
                        "status": status_text,
                        "files": total_files,
                        "size_bytes": total_size
                    }
                    self.resolved_orders[item_key] = order_info
                    self.resolved_orders[order_id] = order_info
                    self.resolved_orders[f"#{order_id}"] = order_info

        if self.stop_requested:
            self.status_var.set("⏹️ Process stopped by user.")
            messagebox.showwarning("Stopped", "Process was stopped by user.", parent=self)
        else:
            self.total_lbl.config(text=f"Total Progress: 100% ({total_orders} / {total_orders} Orders)")
            self.total_progress["value"] = total_orders
            self.status_var.set(f"Done! {success_count} folders ready locally, {not_found_count} not found.")
            messagebox.showinfo(
                "Batch Complete",
                f"Successfully prepared {success_count} vendor folders locally for QC!\n\n"
                f"Not found: {not_found_count} orders.",
                parent=self
            )

        self._set_controls_running(False)
        self.after(0, self._update_leftover_badge)
        self.after(0, self._update_storage_metrics)

    def _update_storage_metrics(self):
        """Calculates and refreshes live drive free space and local QC orders size."""
        try:
            cur_path = self.path_var.get() if hasattr(self, "path_var") else DEFAULT_DROPBOX_PATH
            d_info = get_drive_space_info(cur_path)
            drive_letter = d_info.get("drive", "C:")
            free_str = d_info.get("free_str", "N/A")
            total_str = d_info.get("total_str", "N/A")
            free_pct = int(d_info.get("free_pct", 0))

            if hasattr(self, "drive_metric_lbl"):
                self.drive_metric_lbl.config(
                    text=f"💾 Drive ({drive_letter}) Free: {free_str} / {total_str} ({free_pct}% free)"
                )

            count, total_bytes, size_str = get_tracked_local_storage_stats()
            if hasattr(self, "local_metric_lbl"):
                fg_color = "#f87171" if count > 0 else "#34d399"
                self.local_metric_lbl.config(
                    text=f"📦 Local: {size_str} ({count} Orders)",
                    fg=fg_color
                )
        except Exception:
            pass

    def _browse_dropbox_path(self):
        chosen = filedialog.askdirectory(initialdir=self.path_var.get(), title="Select Dropbox Root Folder")
        if chosen:
            self.path_var.set(chosen)
            self.config_data["dropbox_path"] = chosen
            save_config(self.config_data)
            self._scan_vendors()
            self._update_storage_metrics()

    def _clear_input(self):
        self.input_text.delete("1.0", "end")
        self._on_input_text_changed()

    def _paste_clipboard(self):
        try:
            clip = self.clipboard_get()
            self.input_text.insert("end", clip)
            self._on_input_text_changed()
        except Exception:
            pass

    def _parse_order_ids(self):
        raw = self.input_text.get("1.0", "end")
        tokens = re.split(r"[\r\n,;\t\s]+", raw)
        cleaned = []
        raw_non_empty = 0
        for t in tokens:
            t = t.strip()
            if not t:
                continue
            raw_non_empty += 1
            t_clean = re.sub(r"^#\s*", "", t)
            t_clean = re.sub(r"\s*\([^)]*\)", "", t_clean).strip()
            t_clean = re.split(r"[-_]", t_clean)[0].strip()
            if t_clean and t_clean not in cleaned:
                cleaned.append(t_clean)
        return cleaned, raw_non_empty

    def _update_order_count(self):
        unique_orders, total_lines = self._parse_order_ids()
        self.count_lbl.config(text=f"Total: {total_lines} lines | Unique: {len(unique_orders)}")

    def _on_tree_double_click(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self._open_selected_folder()

    def _open_selected_folder(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Order", "Please select an order from the list first.", parent=self)
            return

        item_id = selected[0]
        item = self.tree.item(item_id)
        info = self.resolved_orders.get(item_id)
        if not info:
            vals = item.get("values", [])
            raw_id = str(vals[1] if len(vals) > 1 else vals[0]).strip()
            clean_id = normalize_order_id(raw_id)
            info = self.resolved_orders.get(clean_id) or self.resolved_orders.get(f"#{clean_id}")

        if info and info.get("path") and os.path.isdir(info["path"]):
            try:
                os.startfile(info["path"])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open folder:\n{e}", parent=self)
        else:
            order_name = item["values"][1] if (item.get("values") and len(item["values"]) > 1) else "selected"
            messagebox.showwarning("Not Found", f"Folder path for order {order_name} is not available on disk.", parent=self)

    def _on_tree_right_click(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            if row_id not in self.tree.selection():
                self.tree.selection_set(row_id)
            self.context_menu.post(event.x_root, event.y_root)

    def _periodic_update_check(self):
        if not getattr(self, "is_running", False):
            check_for_updates(self, silent=True)
        self.after(3600000, self._periodic_update_check)

    def _show_update_available(self, latest_tag, release_body, download_url, silent=False):
        self.available_update = {
            "tag": latest_tag,
            "body": release_body,
            "url": download_url
        }
        self.unread_notifications = 1
        self._update_notification_badge()
        if not silent:
            NotificationCenterDialog(self, available_update=self.available_update)

    def _check_first_launch_whats_new(self):
        cfg = load_config()
        last_seen = cfg.get("last_seen_version")
        if last_seen != CURRENT_VERSION:
            cfg["last_seen_version"] = CURRENT_VERSION
            save_config(cfg)
            WhatsNewDialog(self, CURRENT_VERSION)

    def _scan_local_in_selected_vendors(self):
        if self.is_running:
            messagebox.showinfo("Busy", "A task is currently running. Please wait for it to finish.", parent=self)
            return

        base_path = self.path_var.get()
        if not base_path or not os.path.isdir(base_path):
            messagebox.showwarning("Invalid Dropbox Path", "Please configure a valid Dropbox Root path first.", parent=self)
            return

        target_vendors = list(self.selected_vendors) if (hasattr(self, "selected_vendors") and self.selected_vendors) else list(self.detected_vendors)
        if not target_vendors:
            messagebox.showwarning("No Vendors Selected", "Please select at least one vendor from the Vendors dropdown.", parent=self)
            return

        threading.Thread(target=self._thread_scan_local_orders, args=(base_path, target_vendors), daemon=True).start()

    def _update_leftover_badge(self):
        tracked = get_tracked_local_orders()
        count = len(tracked)
        if count > 0:
            total_b = sum(it.get("size_bytes", 0) for it in tracked)
            self.leftover_btn.config(
                text=f"📜 History: {count} Local ({format_bytes(total_b)})",
                fg="#f87171"
            )
        else:
            self.leftover_btn.config(
                text="📜 History: 0 Local",
                fg="#10b981"
            )

    def _open_history_tracker(self):
        HistoryTrackerDialog(self)

    def _free_orders_in_background(self, orders_to_free, on_done_callback=None):
        def _worker():
            for item in orders_to_free:
                p = item.get("path")
                oid = item.get("order_id")
                vendor = item.get("vendor")
                if p and os.path.isdir(p):
                    try:
                        free_up_space_cfapi(p)
                        mark_order_history(oid, vendor, p, "online", item.get("files", 0), 0)
                    except Exception:
                        pass
            if on_done_callback:
                self.after(0, on_done_callback)
            self.after(0, self._update_leftover_badge)
            self.after(0, self._update_storage_metrics)
        threading.Thread(target=_worker, daemon=True).start()

    def _set_controls_running(self, running):
        self.is_running = running
        if running:
            self.btn_pause.config(state="normal", text="⏸️ Pause All", bg=self.accent_orange)
            self.btn_stop.config(state="normal")
            if hasattr(self, "btn_make_local_all"):
                self.btn_make_local_all.config(state="disabled")
            if hasattr(self, "btn_make_online_all"):
                self.btn_make_online_all.config(state="disabled")
            if hasattr(self, "btn_scan_local"):
                self.btn_scan_local.config(state="disabled")
        else:
            self.btn_pause.config(state="disabled", text="⏸️ Pause All")
            self.btn_stop.config(state="disabled")
            if hasattr(self, "btn_make_local_all"):
                self.btn_make_local_all.config(state="normal")
            if hasattr(self, "btn_make_online_all"):
                self.btn_make_online_all.config(state="normal")
            if hasattr(self, "btn_scan_local"):
                self.btn_scan_local.config(state="normal")

    def _toggle_pause(self):
        if not self.is_running:
            return
        if self.is_paused:
            self.is_paused = False
            self.pause_event.set()
            self.btn_pause.config(text="⏸️ Pause All", bg=self.accent_orange)
            self.status_var.set("Resumed process.")
        else:
            self.is_paused = True
            self.pause_event.clear()
            self.btn_pause.config(text="▶️ Resume All", bg=self.accent_green)
            self.status_var.set("Paused by user. Click Resume to continue.")

    def _request_stop(self):
        if not self.is_running:
            return
        self.stop_requested = True
        if self.is_paused:
            self.pause_event.set()
        self.status_var.set("Stopping process, please wait...")

    def _start_make_local(self):
        orders, invalid = self._parse_order_ids()
        if not orders:
            messagebox.showwarning("No Orders", "Please paste or enter at least one Order ID.", parent=self)
            return
        self._start_make_local_from_list(orders)

    def _start_make_online(self):
        self._make_selected_online()


if __name__ == "__main__":
    cleanup_old_executable()
    app = QCBatchLoaderApp()
    app.mainloop()
