import customtkinter as ctk

# Enable seamless compatibility for CTk widgets with legacy tkinter .config() and parameters

def _patch_ctk_compatibility():

    def _patch_one_class(cls):

        orig_conf = cls.configure

        def _compat_conf(self, *args, **kwargs):

            if "bg" in kwargs:

                kwargs["fg_color"] = kwargs.pop("bg")

            if "fg" in kwargs:

                kwargs["text_color"] = kwargs.pop("fg")

            if "activebackground" in kwargs:

                kwargs["hover_color"] = kwargs.pop("activebackground")

            if "activeforeground" in kwargs:

                kwargs.pop("activeforeground")

            if "bd" in kwargs:

                kwargs["border_width"] = kwargs.pop("bd")

            if "borderwidth" in kwargs:

                kwargs["border_width"] = kwargs.pop("borderwidth")

            if "highlightthickness" in kwargs:

                kwargs.pop("highlightthickness")

            if "highlightbackground" in kwargs:

                kwargs.pop("highlightbackground")

            if "relief" in kwargs:

                kwargs.pop("relief")

            if "padx" in kwargs and not isinstance(self, (ctk.CTk, ctk.CTkToplevel)):

                kwargs.pop("padx")

            if "pady" in kwargs and not isinstance(self, (ctk.CTk, ctk.CTkToplevel)):

                kwargs.pop("pady")

            return orig_conf(self, *args, **kwargs)

        cls.configure = _compat_conf

        cls.config = _compat_conf

    for cls in [ctk.CTk, ctk.CTkToplevel, ctk.CTkFrame, ctk.CTkButton, ctk.CTkLabel, ctk.CTkEntry, ctk.CTkTextbox, ctk.CTkProgressBar, ctk.CTkCheckBox, ctk.CTkScrollableFrame]:

        _patch_one_class(cls)

_patch_ctk_compatibility()

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

from PIL import Image, ImageDraw, ImageTk

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

APP_NAME = "Path OrderSync Pro"

APP_TAGLINE = "Sync Smarter. Work Faster. Better Quality."

CURRENT_VERSION = "v1.8.0"

GITHUB_REPO = "bishojit-sarker/Path-OrderSync-Pro"

ASSETS_DIR = get_assets_dir()

LOGO_HEADER_PATH = os.path.join(ASSETS_DIR, "logo_header.png")

LOGO_LARGE_PATH = os.path.join(ASSETS_DIR, "logo_64.png")

APP_ICON_PATH = os.path.join(ASSETS_DIR, "app_icon.ico")

# ----------------------------------------------------------------------

# Exact Picture Style Design Tokens (Image 1 Light, Image 2 & 3 Dark)

# ----------------------------------------------------------------------

BRAND_THEMES = {

    "light": {

        "id": "light",

        "name": "Light Theme (Image 1: Ice Slate & Deep Navy)",

        "bg_canvas": "#ebf4fb",       # Soft pastel ice-blue canvas from Image 1

        "bg_card": "#ffffff",         # Pure crisp white cards

        "bg_input": "#ffffff",        # Pure white inputs

        "border": "#d1e1ee",          # Soft clean border

        "text_main": "#1e293b",       # Dark slate text

        "text_muted": "#64748b",      # Muted secondary text

        "primary": "#1e2565",         # Deep Navy / Royal Blue CTA

        "primary_hover": "#141947",

        "secondary": "#93c5fd",       # Soft Sky Blue

        "secondary_hover": "#60a5fa",

        "secondary_text": "#1e3a8a",  # High contrast text for Sky Blue button

        "accent": "#fbbf24",          # Warm Amber / Sunflower

        "supporting": "#818cf8",      # Lavender / Indigo

        "danger": "#ef4444",          # Coral Red

        "danger_hover": "#dc2626",

        "success": "#10b981",         # Emerald Green

        "success_hover": "#059669",

        "tree_bg": "#ffffff",

        "tree_heading": "#f1f6fb",

        "tree_select": "#dbeafe",

        "tree_select_fg": "#1e3a8a",

        "status_local_bg": "#def7ec",

        "status_local_fg": "#046c4e",

        "status_sync_bg": "#e1effe",

        "status_sync_fg": "#1e429f",

        "status_cloud_bg": "#f3f4f6",

        "status_cloud_fg": "#4b5563",

        "status_notfound_bg": "#fde8e8",

        "status_notfound_fg": "#9b1c1c",

        "row_sync_bg": "#e1effe",

        "row_sync_fg": "#1e429f",

        "action_btn_make_local_bg": "#1e2565",

        "action_btn_make_local_fg": "#ffffff",

        "action_btn_free_space_bg": "#93c5fd",

        "action_btn_free_space_fg": "#1e3a8a",

        "action_btn_pause_bg": "#fbbf24",

        "action_btn_pause_fg": "#1e293b",

        "action_btn_stop_bg": "#ef4444",

        "action_btn_stop_fg": "#ffffff",

        "drive_gauge_bg": "#1e2565"

    },

    "dark": {

        "id": "dark",

        "name": "Dark Theme (Image 2 & 3: Midnight Mint & Cyan)",

        "bg_canvas": "#0e1626",       # Deep slate navy canvas from Image 2

        "bg_card": "#1a2436",         # Dark slate card containers

        "bg_input": "#121b2c",        # Dark input fields

        "border": "#2e3d52",          # Subtle border

        "text_main": "#f8fafc",       # Crisp white text

        "text_muted": "#94a3b8",      # Muted secondary text

        "primary": "#10b981",         # Vibrant Mint Green CTA from Image 2

        "primary_hover": "#059669",

        "secondary": "#38bdf8",       # Vivid Sky Blue / Cyan

        "secondary_hover": "#0284c7",

        "secondary_text": "#0b1120",  # Dark text for vibrant cyan

        "accent": "#f59e0b",          # Amber Gold

        "supporting": "#818cf8",      # Indigo

        "danger": "#ef4444",          # Coral Red

        "danger_hover": "#dc2626",

        "success": "#10b981",         # Mint Green

        "success_hover": "#059669",

        "tree_bg": "#121b2c",

        "tree_heading": "#1a2436",

        "tree_select": "#23334d",

        "tree_select_fg": "#38bdf8",

        "status_local_bg": "#064e3b",

        "status_local_fg": "#34d399",

        "status_sync_bg": "#0891b2",

        "status_sync_fg": "#ffffff",

        "status_cloud_bg": "#2a374a",

        "status_cloud_fg": "#94a3b8",

        "status_notfound_bg": "#7f1d1d",

        "status_notfound_fg": "#fca5a5",

        "row_sync_bg": "#0c4a6e",

        "row_sync_fg": "#38bdf8",

        "action_btn_make_local_bg": "#10b981",

        "action_btn_make_local_fg": "#0b1120",

        "action_btn_free_space_bg": "#38bdf8",

        "action_btn_free_space_fg": "#0b1120",

        "action_btn_pause_bg": "#f59e0b",

        "action_btn_pause_fg": "#0b1120",

        "action_btn_stop_bg": "#ef4444",

        "action_btn_stop_fg": "#ffffff",

        "drive_gauge_bg": "#38bdf8"

    }

}

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

    def __init__(self, parent, latest_tag, current_ver, release_body, download_url=None, auto_start=False):

        super().__init__(parent)

        self.parent = parent

        self.latest_tag = latest_tag

        self.current_ver = current_ver

        self.release_body = release_body or "Bug fixes and performance improvements."

        if not download_url:

            download_url = f"https://github.com/{GITHUB_REPO}/releases/download/{latest_tag}/Path_OrderSync_Pro.exe"

        self.download_url = download_url

        self.auto_start = auto_start

        self.title(f"🚀 Update Available: {latest_tag}")

        self.geometry("700x580")

        self.minsize(600, 480)

        self.configure(bg="#1e1e2e")

        self.transient(parent)

        self.grab_set()

        try:

            x = parent.winfo_x() + (parent.winfo_width() // 2) - 350

            y = parent.winfo_y() + (parent.winfo_height() // 2) - 290

            self.geometry(f"+{max(x, 50)}+{max(y, 50)}")

        except Exception:

            pass

        self._create_widgets()

        if self.auto_start:

            self.after(300, self._start_download)

    def _create_widgets(self):

        # 1. Top Header Banner

        header = tk.Frame(self, bg="#252538", bd=1, relief="solid")

        header.pack(side="top", fill="x", padx=16, pady=(14, 10))

        title_box = tk.Frame(header, bg="#252538")

        title_box.pack(fill="x", padx=14, pady=10)

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

        # 2. Bottom Action Buttons Bar (Packed at bottom first so it is NEVER pushed off-screen!)

        self.btn_box = tk.Frame(self, bg="#1e1e2e")

        self.btn_box.pack(side="bottom", fill="x", padx=16, pady=(10, 16))

        self.btn_update = tk.Button(

            self.btn_box,

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

            self.btn_box,

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

        # 3. Download Progress Area (Packed above btn_box)

        self.progress_frame = tk.Frame(self, bg="#1e1e2e")

        self.progress_lbl = tk.Label(self.progress_frame, text="", font=("Segoe UI", 9), bg="#1e1e2e", fg="#93c5fd")

        self.progress_lbl.pack(anchor="w")

        self.prog_bar = ttk.Progressbar(self.progress_frame, mode="determinate")

        self.prog_bar.pack(fill="x", pady=(2, 0))

        # 4. Release Notes & Feature Guide Card (Takes remaining vertical space in middle)

        card = tk.Frame(self, bg="#252538", bd=1, relief="solid")

        card.pack(side="top", fill="both", expand=True, padx=16, pady=(0, 6))

        card_header = tk.Frame(card, bg="#252538")

        card_header.pack(fill="x", padx=14, pady=(10, 4))

        tk.Label(card_header, text="📋 What's New & Feature Guide:", font=("Segoe UI", 10, "bold"), bg="#252538", fg="#f8fafc").pack(side="left")

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

    def _start_download(self):

        if not self.download_url:

            self.download_url = f"https://github.com/{GITHUB_REPO}/releases/download/{self.latest_tag}/Path_OrderSync_Pro.exe"

        cur_exe = sys.executable

        if not (cur_exe.lower().endswith("path_ordersync_pro.exe") or cur_exe.lower().endswith("qc_batch_loader.exe")):

            webbrowser.open(self.download_url)

            self.destroy()

            return

        self.btn_update.config(state="disabled")

        self.btn_cancel.config(state="disabled")

        self.progress_frame.pack(side="bottom", fill="x", padx=16, pady=(4, 6), before=self.btn_box)

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

        t_lbl = tk.Label(title_box, text=f"Welcome to Path OrderSync Pro {self.version}!", font=("Segoe UI", 11, "bold"), bg="#252538", fg="#f8fafc")

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

    """Checks GitHub Releases and repository main branch for new updates with real-time notifications."""

    def _worker():

        try:

            req = urllib.request.Request(

                f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest",

                headers={"User-Agent": "QC-Batch-Loader-Updater"}

            )

            data = None

            try:

                with urllib.request.urlopen(req, timeout=8) as resp:

                    data = json.loads(resp.read().decode("utf-8"))

            except Exception:

                pass

            latest_tag = data.get("tag_name", "").strip() if data else ""

            download_url = None

            release_body = ""

            if latest_tag and data:

                for asset in data.get("assets", []):

                    if asset.get("name") in ["Path_OrderSync_Pro.exe", "QC_Batch_Loader.exe"]:

                        download_url = asset.get("browser_download_url")

                        break

                release_body = data.get("body", "Bug fixes and performance improvements.")

            cur_ver = parse_version_tuple(CURRENT_VERSION)

            latest_ver = parse_version_tuple(latest_tag) if latest_tag else (0, 0, 0)

            # Fallback: If /releases/latest does not have a newer version or executable asset, check raw main branch
            if latest_ver <= cur_ver or not download_url:

                try:

                    raw_req = urllib.request.Request(

                        f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/app.py",

                        headers={"User-Agent": "QC-Batch-Loader-Updater"}

                    )

                    with urllib.request.urlopen(raw_req, timeout=6) as raw_resp:

                        raw_code = raw_resp.read().decode("utf-8")

                    for rline in raw_code.splitlines()[:160]:

                        if rline.strip().startswith("CURRENT_VERSION"):

                            parts = rline.split("=")

                            if len(parts) == 2:

                                remote_v = parts[1].strip().strip('"').strip("'")

                                if parse_version_tuple(remote_v) > cur_ver:

                                    latest_tag = remote_v

                                    latest_ver = parse_version_tuple(remote_v)

                                    download_url = f"https://github.com/{GITHUB_REPO}/raw/main/Path_OrderSync_Pro.exe"

                                    release_body = f"🚀 Path OrderSync Pro {latest_tag}\n\nDownloaded directly from the official GitHub repository main branch."

                                    break

                except Exception:

                    pass

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

            if not download_url:

                if not silent and parent:

                    parent.after(0, lambda: messagebox.showwarning("Update Available", f"Version {latest_tag} is available on GitHub, but executable asset is not attached."))

                return

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

def _hydrate_single_file(fp, chunk_callback=None):

    """Streams the file in chunks to ensure 100% complete local hydration without Photoshop hanging."""

    try:

        kernel32 = ctypes.windll.kernel32 if hasattr(ctypes, "windll") else None

        if kernel32:

            attrs = kernel32.GetFileAttributesW(fp)

            if attrs != -1 and not (attrs & FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS) and not (attrs & FILE_ATTRIBUTE_OFFLINE):

                if chunk_callback:

                    try:

                        sz = os.path.getsize(fp)

                        chunk_callback(sz)

                    except Exception:

                        pass

                return True

        with open(fp, "rb") as fh:

            chunk_size = 128 * 1024  # 128 KB chunks for granular, smooth real-time decimal progress

            while True:

                chunk = fh.read(chunk_size)

                if not chunk:

                    break

                if chunk_callback:

                    try:

                        chunk_callback(len(chunk))

                    except Exception:

                        pass

        return True

    except Exception:

        return False

def free_up_space_cfapi(folder_path):
    """
    Reverts folder and all its contents back to Online-Only (0 bytes on disk)
    using the exact native Windows Explorer / Dropbox context menu action ("Make online-only" / "Free up space").
    Guarantees literal path handling without '#' comment truncation via an isolated .ps1 script.
    """
    if not folder_path or not os.path.exists(folder_path):
        return False

    shell32 = getattr(ctypes, "windll", None) and getattr(ctypes.windll, "shell32", None)

    order_root = folder_path
    base_name = os.path.basename(os.path.normpath(folder_path)).lower()
    if base_name in ["completed", "complete"]:
        parent_candidate = os.path.dirname(folder_path)
        if os.path.isdir(parent_candidate):
            order_root = parent_candidate

    sys_root = os.environ.get("SystemRoot", r"C:\Windows")
    ps_bin = os.path.join(sys_root, "System32", "WindowsPowerShell", "v1.0", "powershell.exe")
    if not os.path.isfile(ps_bin):
        ps_bin = "powershell.exe"

    # 1. Native Windows Attribute Pass (-P +U to unpin)
    try:
        cmd_attr = f'attrib -P +U "{folder_path}\\*.*" /s & attrib -P +U "{folder_path}" /d'
        if order_root != folder_path:
            cmd_attr += f' & attrib -P +U "{order_root}\\*.*" /s & attrib -P +U "{order_root}" /d'
        subprocess.run(cmd_attr, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

    # 2. Native Windows Shell Context Menu Verb Invoker
    # Executes the exact same action as Right-Click -> "Make online-only" / "Free up space" in File Explorer
    ps1_code = f"""$ErrorActionPreference = 'SilentlyContinue'

function Invoke-MakeOnline($itemPath) {{
    if (-not (Test-Path -LiteralPath $itemPath)) {{ return }}
    $parent = [System.IO.Path]::GetDirectoryName($itemPath)
    $leaf = [System.IO.Path]::GetFileName($itemPath)
    $shell = New-Object -ComObject Shell.Application
    $folder = $shell.Namespace($parent)
    if (-not $folder) {{ return }}
    $item = $folder.ParseName($leaf)
    if (-not $item) {{ return }}
    foreach ($v in $item.Verbs()) {{
        $name = $v.Name.Replace('&', '').Trim()
        if ($name -match '(?i)free up space|make online|online-only|smart sync|online') {{
            $v.DoIt()
            break
        }}
    }}
}}

Invoke-MakeOnline '{order_root}'
Invoke-MakeOnline '{folder_path}'

# Also invoke directly on all files inside folder_path
Get-ChildItem -LiteralPath '{folder_path}' -File -Recurse -ErrorAction SilentlyContinue | ForEach-Object {{
    Invoke-MakeOnline $_.FullName
}}
"""
    try:
        temp_dir = os.environ.get("TEMP", os.path.dirname(folder_path))
        temp_ps1 = os.path.join(temp_dir, f"_make_online_{int(time.time()*1000)}.ps1")
        with open(temp_ps1, "w", encoding="utf-8") as f:
            f.write(ps1_code)

        cmd = f'"{ps_bin}" -NoProfile -ExecutionPolicy Bypass -File "{temp_ps1}"'
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
        try:
            os.remove(temp_ps1)
        except Exception:
            pass
    except Exception:
        pass

    # 3. Explorer Icon Refresh Notification
    if shell32 and hasattr(shell32, "SHChangeNotify"):
        try:
            # SHCNE_UPDATEDIR = 0x00001000, SHCNF_PATHW = 0x0005
            shell32.SHChangeNotify(0x00001000, 0x0005, folder_path, None)
            if order_root != folder_path:
                shell32.SHChangeNotify(0x00001000, 0x0005, order_root, None)
        except Exception:
            pass

    return True

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

        self.theme = getattr(parent, "theme", BRAND_THEMES["dark"])

        t = self.theme

        self.configure(bg=t["bg_canvas"])

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

        t = self.theme

        # 1. Top Header

        top_frame = tk.Frame(self, bg=t["bg_card"], bd=1, relief="solid")

        top_frame.pack(fill="x", padx=16, pady=(14, 10))

        h_box = tk.Frame(top_frame, bg=t["bg_card"])

        h_box.pack(fill="x", padx=14, pady=12)

        tk.Label(h_box, text="🔔", font=("Segoe UI", 22), bg=t["bg_card"], fg="#f59e0b").pack(side="left", padx=(0, 10))

        info_box = tk.Frame(h_box, bg=t["bg_card"])

        info_box.pack(side="left", fill="x", expand=True)

        tk.Label(info_box, text="Notification & Update Center", font=("Segoe UI", 13, "bold"), bg=t["bg_card"], fg=t["text_main"]).pack(anchor="w")

        tk.Label(

            info_box,

            text=f"App: {APP_NAME}  |  Current Version: {CURRENT_VERSION}",

            font=("Segoe UI", 9),

            bg=t["bg_card"],

            fg=t["text_muted"]

        ).pack(anchor="w", pady=(2, 0))

        close_btn = tk.Button(

            h_box,

            text="✕ Close",

            command=self.destroy,

            bg=t["border"],

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

        card = tk.Frame(self, bg=t["bg_card"], bd=1, relief="solid")

        card.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        card_title = tk.Frame(card, bg=t["bg_card"])

        card_title.pack(fill="x", padx=14, pady=(10, 6))

        tk.Label(card_title, text="📋 Release History & Feature Changelogs by Date:", font=("Segoe UI", 10, "bold"), bg=t["bg_card"], fg=t["text_main"]).pack(side="left")

        txt_frame = tk.Frame(card, bg=t["bg_input"])

        txt_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        txt = tk.Text(

            txt_frame,

            bg=t["bg_input"],

            fg=t["text_main"],

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

        txt.tag_configure("ver_header", font=("Segoe UI", 11, "bold"), foreground=t["secondary"], spacing1=10, spacing3=4)

        txt.tag_configure("date_badge", font=("Segoe UI", 8), foreground=t["text_muted"])

        txt.tag_configure("section", font=("Segoe UI", 9, "bold"), foreground=t["success"], spacing1=6, spacing3=2)

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

            f"Do you want to update Path OrderSync Pro to {tag} now?\n\n"

            f"The application will download the update and automatically restart.",

            parent=self

        )

        if confirm:

            self.destroy()

            d_url = self.available_update.get("download_url") or self.available_update.get("url") or f"https://github.com/{GITHUB_REPO}/releases/download/{tag}/Path_OrderSync_Pro.exe"

            UpdateDialog(

                self.parent,

                tag,

                CURRENT_VERSION,

                self.available_update.get("body", ""),

                d_url,

                auto_start=True

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

        self.theme = getattr(parent, "theme", BRAND_THEMES["dark"])

        t = self.theme

        self.configure(bg=t["bg_canvas"])

        self.transient(parent)

        self.grab_set()

        try:

            x = parent.winfo_x() + (parent.winfo_width() // 2) - 490

            y = parent.winfo_y() + (parent.winfo_height() // 2) - 310

            self.geometry(f"+{max(x, 50)}+{max(y, 50)}")

        except Exception:

            pass

        self.search_var = tk.StringVar(value="")

        self.path_var = tk.StringVar(value=self.config_data.get("dropbox_path") or DEFAULT_DROPBOX_PATH)

        self.selected_keys = set()

        self.local_items = {}

        self.master_checked = False

        self._create_widgets()

        self._load_local_orders()

    def _create_widgets(self):

        t = self.theme

        # 1. Top Header

        top_frame = tk.Frame(self, bg=t["bg_canvas"])

        top_frame.pack(fill="x", padx=16, pady=(12, 6))

        title_lbl = tk.Label(

            top_frame,

            text="🧹 Local Storage Clean & Free Space",

            font=("Segoe UI", 13, "bold"),

            bg=t["bg_canvas"],

            fg=t["success"]

        )

        title_lbl.pack(side="left")

        sub_lbl = tk.Label(

            top_frame,

            text="Only hydrated orders consuming physical hard drive space are listed here.",

            font=("Segoe UI", 9),

            bg=t["bg_canvas"],

            fg=t["text_muted"]

        )

        sub_lbl.pack(side="left", padx=10, pady=(3, 0))

        close_btn = tk.Button(

            top_frame,

            text="✕ Close",

            command=self.destroy,

            bg=t["border"],

            fg="white",

            relief="flat",

            font=("Segoe UI", 8, "bold"),

            cursor="hand2",

            padx=10,

            pady=3

        )

        close_btn.pack(side="right")

        # 2. Control Bar (Search, Select All, Stats)

        ctrl_card = tk.Frame(self, bg=t["bg_card"], bd=1, relief="solid")

        ctrl_card.pack(fill="x", padx=16, pady=4)

        sel_box = tk.Frame(ctrl_card, bg=t["bg_card"])

        sel_box.pack(side="left", padx=10, pady=6)

        btn_all = tk.Button(

            sel_box,

            text="☑ Select All",

            command=self._select_all,

            bg=t["border"],

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

            bg=t["border"],

            fg="white",

            relief="flat",

            font=("Segoe UI", 8),

            cursor="hand2",

            padx=8,

            pady=2

        )

        btn_none.pack(side="left")

        # Search Bar

        search_box = tk.Frame(ctrl_card, bg=t["bg_card"])

        search_box.pack(side="left", padx=16, pady=6)

        tk.Label(search_box, text="🔍 Search:", bg=t["bg_card"], fg=t["text_muted"], font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 4))

        self.search_entry = tk.Entry(

            search_box,

            textvariable=self.search_var,

            bg=t["bg_input"],

            fg=t["text_main"],

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

            bg=t["bg_card"],

            fg=t["success"],

            font=("Segoe UI", 9, "bold")

        )

        self.stats_lbl.pack(side="right", padx=12, pady=6)

        # 3. Table (Treeview)

        tree_frame = tk.Frame(self, bg=t["bg_input"])

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

        btn_bar = tk.Frame(self, bg=t["bg_canvas"])

        btn_bar.pack(fill="x", padx=16, pady=(8, 12))

        open_btn = tk.Button(

            btn_bar,

            text="📂 Open Selected Folder",

            command=self._open_selected_folder,

            bg=t["border"],

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

            bg=t["border"],

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

        self.theme = getattr(parent, "theme", BRAND_THEMES["dark"])

        t = self.theme

        self.configure(bg=t["bg_canvas"])

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

        t = self.theme

        # 1. Top Header

        top_frame = tk.Frame(self, bg=t["bg_canvas"])

        top_frame.pack(fill="x", padx=16, pady=(12, 6))

        title_lbl = tk.Label(

            top_frame,

            text="🔍 Order Review & Smart File Filter",

            font=("Segoe UI", 13, "bold"),

            bg=t["bg_canvas"],

            fg=t["secondary"]

        )

        title_lbl.pack(side="left")

        sub_lbl = tk.Label(

            top_frame,

            text="Inspect folders and exclude heavy unneeded files (e.g. Raw, Samples) before downloading.",

            font=("Segoe UI", 9),

            bg=t["bg_canvas"],

            fg=t["text_muted"]

        )

        sub_lbl.pack(side="left", padx=10, pady=(3, 0))

        close_btn = tk.Button(

            top_frame,

            text="✕ Close",

            command=self.destroy,

            bg=t["border"],

            fg="white",

            relief="flat",

            font=("Segoe UI", 8, "bold"),

            cursor="hand2",

            padx=10,

            pady=3

        )

        close_btn.pack(side="right")

        # 2. Main Horizontal Panes (Left: Orders List, Right: Subfolder / File Inspector)

        paned = tk.PanedWindow(self, orient="horizontal", bg=t["bg_canvas"], bd=0, sashwidth=4)

        paned.pack(fill="both", expand=True, padx=16, pady=4)

        # Left Card: Orders in Dashboard

        left_card = tk.Frame(paned, bg=t["bg_card"], bd=1, relief="solid")

        paned.add(left_card, minsize=320, width=380)

        left_header = tk.Frame(left_card, bg=t["bg_card"])

        left_header.pack(fill="x", padx=10, pady=8)

        tk.Label(left_header, text="📋 Dashboard Orders:", font=("Segoe UI", 10, "bold"), bg=t["bg_card"], fg=t["text_main"]).pack(side="left")

        tree_frame = tk.Frame(left_card, bg=t["bg_input"])

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

        right_card = tk.Frame(paned, bg=t["bg_card"], bd=1, relief="solid")

        paned.add(right_card, minsize=420)

        self.right_header_lbl = tk.Label(

            right_card,

            text="📁 Select an order on the left to inspect files",

            font=("Segoe UI", 10, "bold"),

            bg=t["bg_card"],

            fg=t["secondary"]

        )

        self.right_header_lbl.pack(anchor="w", padx=12, pady=(10, 4))

        # Quick Preset Buttons

        preset_bar = tk.Frame(right_card, bg=t["bg_card"])

        preset_bar.pack(fill="x", padx=10, pady=(2, 6))

        tk.Button(

            preset_bar,

            text="🎯 QC Images Only (.tif, .psd, .jpg)",

            command=self._preset_qc_only,

            bg=t["border"],

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

            bg=t["border"],

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

            bg=t["border"],

            fg="white",

            relief="flat",

            font=("Segoe UI", 8),

            cursor="hand2",

            padx=6,

            pady=2

        ).pack(side="left")

        # Scrollable Frame for subfolder checkboxes

        sub_canvas_frame = tk.Frame(right_card, bg=t["bg_input"])

        sub_canvas_frame.pack(fill="both", expand=True, padx=10, pady=4)

        self.canvas = tk.Canvas(sub_canvas_frame, bg=t["bg_input"], highlightthickness=0)

        self.canvas_scroll = ttk.Scrollbar(sub_canvas_frame, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=self.canvas_scroll.set)

        self.checkbox_container = tk.Frame(self.canvas, bg=t["bg_input"])

        self.canvas_window = self.canvas.create_window((0, 0), window=self.checkbox_container, anchor="nw")

        self.checkbox_container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas_scroll.pack(side="right", fill="y")

        # Bottom Filter Summary & Save Bar

        bottom_bar = tk.Frame(right_card, bg=t["bg_card"])

        bottom_bar.pack(fill="x", padx=10, pady=(6, 10))

        self.filter_summary_lbl = tk.Label(

            bottom_bar,

            text="Selected: 0 files (0 B) of 0 files (0 B)",

            font=("Segoe UI", 9, "bold"),

            bg=t["bg_card"],

            fg=t["success"]

        )

        self.filter_summary_lbl.pack(side="left")

        self.btn_save_filter = tk.Button(

            bottom_bar,

            text="💾 Save Filter for this Order",

            command=self._save_filter,

            state="disabled",

            bg=t["success"],

            fg="white",

            activebackground=t["success_hover"],

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

            cb_frame = tk.Frame(self.checkbox_container, bg=t["bg_input"])

            cb_frame.pack(fill="x", padx=10, pady=3)

            cb = tk.Checkbutton(

                cb_frame,

                text=f"📁  {g_name}  ({cnt} files, {format_bytes(b_sz)})",

                variable=var,

                command=self._recalculate_selected_size,

                bg=t["bg_input"],

                fg=t["text_main"],

                activebackground="#181825",

                activeforeground=t["secondary"],

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

        self.theme = getattr(parent, "theme", BRAND_THEMES["dark"])

        t = self.theme

        self.configure(bg=t["bg_canvas"])

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

        t = self.theme

        # 1. Top Header Frame

        top_frame = tk.Frame(self, bg=t["bg_canvas"])

        top_frame.pack(fill="x", padx=16, pady=(12, 6))

        title_lbl = tk.Label(

            top_frame,

            text="📜 Pending Orders & History Tracker",

            font=("Segoe UI", 13, "bold"),

            bg=t["bg_canvas"],

            fg=t["secondary"]

        )

        title_lbl.pack(side="left")

        subtitle_lbl = tk.Label(

            top_frame,

            text="Track downloaded orders, search records, and free up hard disk space.",

            font=("Segoe UI", 9),

            bg=t["bg_canvas"],

            fg=t["text_muted"]

        )

        subtitle_lbl.pack(side="left", padx=10, pady=(3, 0))

        close_btn = tk.Button(

            top_frame,

            text="✕ Close",

            command=self.destroy,

            bg=t["border"],

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

        ctrl_card = tk.Frame(self, bg=t["bg_card"], bd=1, relief="solid")

        ctrl_card.pack(fill="x", padx=16, pady=4)

        # Filter Radios on Left

        filter_box = tk.Frame(ctrl_card, bg=t["bg_card"])

        filter_box.pack(side="left", padx=10, pady=6)

        tk.Label(filter_box, text="Filter:", bg=t["bg_card"], fg=t["text_main"], font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 6))

        rb_pending = tk.Radiobutton(

            filter_box,

            text="🔴 Pending Local Only",

            variable=self.filter_var,

            value="pending",

            command=self._refresh_data,

            bg=t["bg_card"],

            fg=t["text_main"],

            activebackground="#252538",

            activeforeground=t["secondary"],

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

            bg=t["bg_card"],

            fg=t["text_muted"],

            activebackground="#252538",

            activeforeground=t["secondary"],

            selectcolor="#181825",

            font=("Segoe UI", 9)

        )

        rb_all.pack(side="left", padx=4)

        # Search Bar in Middle

        search_box = tk.Frame(ctrl_card, bg=t["bg_card"])

        search_box.pack(side="left", padx=14, pady=6)

        tk.Label(search_box, text="🔍 Search:", bg=t["bg_card"], fg=t["text_muted"], font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 4))

        self.search_entry = tk.Entry(

            search_box,

            textvariable=self.search_var,

            bg=t["bg_input"],

            fg=t["text_main"],

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

            bg=t["border"],

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

            bg=t["bg_card"],

            fg=t["secondary"],

            font=("Segoe UI", 9, "bold")

        )

        self.stats_lbl.pack(side="right", padx=12, pady=6)

        # 3. Table (Treeview)

        tree_frame = tk.Frame(self, bg=t["bg_input"])

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

        self.tree.tag_configure("pending_tag", foreground=t["danger"])

        self.tree.tag_configure("online_tag", foreground=t["success"])

        self.tree.bind("<Double-1>", lambda e: self._open_selected_folder())

        # Context Menu

        self.context_menu = tk.Menu(self, tearoff=0, bg=t["bg_card"], fg="white", activebackground=t["primary"], activeforeground="white")

        self.context_menu.add_command(label="📂 Open in File Explorer", command=self._open_selected_folder)

        self.context_menu.add_command(label="☁️ Make this Order Online-Only", command=self._free_selected)

        self.context_menu.add_command(label="📋 Load into Main QC Table", command=self._load_to_main_table)

        self.tree.bind("<Button-3>", self._on_tree_right_click)

        # 4. Action Buttons Bar at Bottom

        btn_bar = tk.Frame(self, bg=t["bg_canvas"])

        btn_bar.pack(fill="x", padx=16, pady=(6, 12))

        # Left Action Group

        left_btns = tk.Frame(btn_bar, bg=t["bg_canvas"])

        left_btns.pack(side="left")

        open_btn = tk.Button(

            left_btns,

            text="📂 Open Folder",

            command=self._open_selected_folder,

            bg=t["border"],

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

            bg=t["border"],

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

            bg=t["bg_card"],

            fg=t["text_muted"],

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

        right_btns = tk.Frame(btn_bar, bg=t["bg_canvas"])

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

            bg=t["success"],

            fg="white",

            activebackground=t["success_hover"],

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

                    free_up_space_cfapi(p)

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

def fetch_all_releases():

    releases = []

    

    # 1. Inspect local versions folder for verified cached builds

    local_versions = {}

    v_dir = os.path.join(APP_DIR, "versions")

    if os.path.exists(v_dir):

        for fname in os.listdir(v_dir):

            if fname.lower().endswith(".exe") and "qc_batch_loader" in fname.lower():

                m = re.search(r"v\d+\.\d+(?:\.\d+)?", fname, re.IGNORECASE)

                if m:

                    tag = m.group(0).lower()

                    local_versions[tag] = os.path.join(v_dir, fname)

    # 2. Query GitHub Releases for published executables

    github_releases = {}

    try:

        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases"

        req = urllib.request.Request(url, headers={"User-Agent": "QC-Batch-Loader"})

        with urllib.request.urlopen(req, timeout=5) as resp:

            data = json.loads(resp.read().decode("utf-8"))

            for r in data:

                tag = r.get("tag_name", "").strip()

                exe_url = None

                for a in r.get("assets", []):

                    if a.get("name", "").lower().endswith(".exe"):

                        exe_url = a.get("browser_download_url")

                        break

                if exe_url:

                    github_releases[tag] = {

                        "tag": tag,

                        "name": r.get("name") or tag,

                        "date": (r.get("published_at") or "")[:10],

                        "body": r.get("body") or "",

                        "download_url": exe_url,

                        "html_url": r.get("html_url") or f"https://github.com/{GITHUB_REPO}/releases/tag/{tag}",

                        "source": "github"

                    }

    except Exception as e:

        print("GitHub releases query note:", e)

    # 3. Read CHANGELOG for metadata & notes

    changelog_meta = {}

    cl_path = os.path.join(APP_DIR, "CHANGELOG.md")

    if os.path.exists(cl_path):

        try:

            with open(cl_path, "r", encoding="utf-8") as f:

                content = f.read()

            pattern = r"## \[([^\]]+)\](?:\s*-\s*([^\n]+))?\n(.*?)(?=\n## \[|\Z)"

            for tag, date_str, body in re.findall(pattern, content, re.DOTALL):

                tag = tag.strip()

                changelog_meta[tag] = {

                    "date": date_str.strip() if date_str else "",

                    "body": body.strip()

                }

        except Exception:

            pass

    # Only include VERIFIED AVAILABLE releases (active build, local binary, or valid GitHub asset)

    candidate_tags = [CURRENT_VERSION, "v1.7.0", "v1.6.0", "v1.5.0", "v1.4.0", "v1.3.0", "v1.2.0"]

    for t in github_releases:

        if t not in candidate_tags:

            candidate_tags.append(t)

    for t in local_versions:

        if t not in candidate_tags:

            candidate_tags.append(t)

    for tag in candidate_tags:

        has_local = tag in local_versions and os.path.exists(local_versions[tag])

        has_github = tag in github_releases and github_releases[tag].get("download_url")

        is_current = (tag == CURRENT_VERSION)

        # Exclude phantom / unavailable versions

        if not (has_local or has_github or is_current):

            continue

        meta = changelog_meta.get(tag, {})

        gh_item = github_releases.get(tag, {})

        date = gh_item.get("date") or meta.get("date") or "2026-11-04"

        body = gh_item.get("body") or meta.get("body") or "Verified stable release build."

        download_url = gh_item.get("download_url")

        if not download_url:

            download_url = f"https://github.com/{GITHUB_REPO}/releases/download/{tag}/Path_OrderSync_Pro.exe"

        releases.append({

            "tag": tag,

            "name": gh_item.get("name") or f"Release {tag}",

            "date": date,

            "body": body,

            "download_url": download_url,

            "local_path": local_versions.get(tag),

            "html_url": gh_item.get("html_url") or f"https://github.com/{GITHUB_REPO}/releases/tag/{tag}",

            "is_available": True

        })

    return releases

class SettingsDialog(ctk.CTkToplevel):
    """
    Settings Center:
    1. Dropbox Root (Automatic save, Browse only, clean heading)
    2. Theme Mode (Light / Dark - Real-time smooth toggle without hanging or freezing)
    3. Version & Updates (Shows active version, update alerts)
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Settings")
        self.geometry("640x500")
        self.minsize(580, 440)
        self.theme = getattr(parent, "theme", BRAND_THEMES["light"])
        t = self.theme
        self.configure(fg_color=t["bg_canvas"])
        # Keep Settings dialog on top and still (do not make transient to prevent Windows from hiding it on theme change)
        self.attributes("-topmost", True)
        self.deiconify()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Destroy>", self._on_destroy_event)

        # Track active dialog on parent to prevent multiple instances or event locks
        parent.settings_dialog = self
        self._section_labels = []

        # Gear Icon for Settings window
        gear_ico = os.path.join(ASSETS_DIR, "gear_icon.ico")
        if os.path.exists(gear_ico):
            try:
                self.iconbitmap(gear_ico)
                self.after(50, lambda: self.iconbitmap(gear_ico))
            except Exception:
                pass

        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - 320
            y = parent.winfo_y() + (parent.winfo_height() // 2) - 250
            self.geometry(f"+{max(x, 40)}+{max(y, 40)}")
        except Exception:
            pass

        self._create_widgets()

    def _create_widgets(self):
        t = self.theme
        is_light = (getattr(self.parent, "theme_name", "light") == "light")

        # Main scrollable body
        self.scroll_body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_body.pack(fill="both", expand=True, padx=16, pady=16)

        # ==============================================================
        # CARD 1: Dropbox Root (Heading: "Dropbox Root", auto-save, Browse only)
        # ==============================================================
        self.card_path = ctk.CTkFrame(self.scroll_body, fg_color=t["bg_card"], corner_radius=12, border_width=1, border_color=t["border"])
        self.card_path.pack(fill="x", pady=(0, 14))

        p_inner = ctk.CTkFrame(self.card_path, fg_color="transparent")
        p_inner.pack(fill="x", padx=16, pady=14)

        lbl_p = ctk.CTkLabel(p_inner, text="Dropbox Root", font=("Segoe UI", 12, "bold"), text_color=t["text_main"])
        lbl_p.pack(anchor="w", pady=(0, 8))
        self._section_labels.append(lbl_p)

        row_p = ctk.CTkFrame(p_inner, fg_color="transparent")
        row_p.pack(fill="x")

        cur_path = self.parent.path_var.get() if hasattr(self.parent, "path_var") else ""
        self.path_entry_var = tk.StringVar(value=cur_path)
        self.path_entry = ctk.CTkEntry(
            row_p,
            textvariable=self.path_entry_var,
            fg_color=t["bg_input"],
            text_color=t["text_main"],
            border_width=1,
            border_color=t["border"],
            corner_radius=8,
            font=("Segoe UI", 11)
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.path_entry.bind("<FocusOut>", self._on_path_entry_focusout)

        self.browse_btn = ctk.CTkButton(
            row_p,
            text="Browse...",
            command=self._browse_path,
            fg_color="#FFFFFF" if is_light else "#253349",
            hover_color="#F1F5F9" if is_light else "#334155",
            text_color=t["text_main"],
            border_width=1,
            border_color=t["border"],
            corner_radius=8,
            width=84,
            height=30,
            font=("Segoe UI", 11)
        )
        self.browse_btn.pack(side="left")

        # ==============================================================
        # CARD 2: Theme Mode (Clean heading, no extra icons)
        # ==============================================================
        self.card_theme = ctk.CTkFrame(self.scroll_body, fg_color=t["bg_card"], corner_radius=12, border_width=1, border_color=t["border"])
        self.card_theme.pack(fill="x", pady=(0, 14))

        t_inner = ctk.CTkFrame(self.card_theme, fg_color="transparent")
        t_inner.pack(fill="x", padx=16, pady=14)

        lbl_t = ctk.CTkLabel(t_inner, text="Theme Mode", font=("Segoe UI", 12, "bold"), text_color=t["text_main"])
        lbl_t.pack(anchor="w", pady=(0, 8))
        self._section_labels.append(lbl_t)

        theme_mode_val = "☀️ Light Mode" if is_light else "🌙 Dark Mode"
        self.theme_segment = ctk.CTkSegmentedButton(
            t_inner,
            values=["☀️ Light Mode", "🌙 Dark Mode"],
            command=self._on_theme_changed,
            font=("Segoe UI", 11, "bold"),
            height=34,
            corner_radius=8
        )
        self.theme_segment.set(theme_mode_val)
        self.theme_segment.pack(fill="x")

        # ==============================================================
        # CARD 3: Version & Updates (Forward Update & Backward Rollback)
        # ==============================================================
        self.card_ver = ctk.CTkFrame(self.scroll_body, fg_color=t["bg_card"], corner_radius=12, border_width=1, border_color=t["border"])
        self.card_ver.pack(fill="x")

        v_inner = ctk.CTkFrame(self.card_ver, fg_color="transparent")
        v_inner.pack(fill="x", padx=16, pady=14)

        # Header of Card 3
        v_top = ctk.CTkFrame(v_inner, fg_color="transparent")
        v_top.pack(fill="x", pady=(0, 10))

        lbl_v = ctk.CTkLabel(v_top, text="Version & Updates", font=("Segoe UI", 12, "bold"), text_color=t["text_main"])
        lbl_v.pack(side="left")
        self._section_labels.append(lbl_v)

        self.ver_status_badge = ctk.CTkLabel(
            v_top,
            text=f"Active: {CURRENT_VERSION}",
            font=("Segoe UI", 10, "bold"),
            text_color=t["success"]
        )
        self.ver_status_badge.pack(side="right")

        # Action Buttons Row (Check for updates, View on GitHub, Update Now)
        action_row = ctk.CTkFrame(v_inner, fg_color="transparent")
        action_row.pack(fill="x", pady=(0, 10))

        self.btn_check_update = ctk.CTkButton(
            action_row,
            text="🔍 Check for Updates",
            command=self._on_check_update_clicked,
            fg_color="#FFFFFF" if is_light else "#253349",
            hover_color="#F1F5F9" if is_light else "#334155",
            text_color=t["text_main"],
            border_width=1,
            border_color=t["border"],
            corner_radius=8,
            height=32,
            font=("Segoe UI", 11)
        )
        self.btn_check_update.pack(side="left", padx=(0, 8))

        self.gh_btn = ctk.CTkButton(
            action_row,
            text="🌐 View on GitHub",
            command=self._open_github_release,
            fg_color="#FFFFFF" if is_light else "#253349",
            hover_color="#F1F5F9" if is_light else "#334155",
            text_color=t["text_main"],
            border_width=1,
            border_color=t["border"],
            corner_radius=8,
            height=32,
            font=("Segoe UI", 11)
        )
        self.gh_btn.pack(side="left")

        # Status / Update Available Button
        has_update = bool(getattr(self.parent, "available_update", None))
        update_info = getattr(self.parent, "available_update", {}) if has_update else {}
        update_tag = update_info.get("tag", "")

        if has_update and update_tag:
            self.btn_status = ctk.CTkButton(
                action_row,
                text=f"🚀 Update Available: {update_tag}",
                state="normal",
                fg_color=t["primary"],
                hover_color=t["primary_hover"],
                text_color="#FFFFFF" if is_light else "#0B1120",
                corner_radius=8,
                height=32,
                font=("Segoe UI", 11, "bold"),
                command=self._open_update_dialog
            )
        else:
            self.btn_status = ctk.CTkButton(
                action_row,
                text="✔️ Up to Date",
                state="disabled",
                fg_color=t["success"],
                hover_color=t["success_hover"],
                text_color="#FFFFFF",
                corner_radius=8,
                height=32,
                font=("Segoe UI", 11, "bold")
            )
        self.btn_status.pack(side="right")

        # Release details textbox
        self.txt_notes = ctk.CTkTextbox(
            v_inner,
            fg_color=t["bg_input"],
            text_color=t["text_main"],
            corner_radius=8,
            border_width=1,
            border_color=t["border"],
            font=("Segoe UI", 10),
            wrap="word",
            height=90
        )
        self.txt_notes.pack(fill="x", pady=(0, 12))
        self._load_current_notes()

        # --- Emergency Rollback Sub-section ---
        divider = ctk.CTkFrame(v_inner, height=1, fg_color=t["border"])
        divider.pack(fill="x", pady=(0, 10))

        lbl_rb = ctk.CTkLabel(
            v_inner,
            text="⏪ Rollback to Previous Version (Emergency Safety Hatch)",
            font=("Segoe UI", 11, "bold"),
            text_color=t["text_main"]
        )
        lbl_rb.pack(anchor="w", pady=(0, 6))
        self._section_labels.append(lbl_rb)

        row_rb = ctk.CTkFrame(v_inner, fg_color="transparent")
        row_rb.pack(fill="x")

        rollback_options = self._scan_rollback_versions()
        self.rollback_var = tk.StringVar(value=rollback_options[0])

        self.rollback_menu = ctk.CTkOptionMenu(
            row_rb,
            variable=self.rollback_var,
            values=rollback_options,
            fg_color="#FFFFFF" if is_light else "#253349",
            text_color=t["text_main"],
            button_color=t["primary"],
            button_hover_color=t["primary_hover"],
            corner_radius=8,
            height=32,
            font=("Segoe UI", 11)
        )
        self.rollback_menu.pack(side="left", fill="x", expand=True, padx=(0, 8))

        has_valid_rollback = any("Verified Cache" in opt for opt in rollback_options)

        self.btn_rollback = ctk.CTkButton(
            row_rb,
            text="⏪ Switch to Selected Version",
            command=self._on_rollback_clicked,
            state="normal" if has_valid_rollback else "disabled",
            fg_color="#F59E0B" if is_light else "#D97706",
            hover_color="#D97706" if is_light else "#B45309",
            text_color="#FFFFFF",
            corner_radius=8,
            height=32,
            font=("Segoe UI", 11, "bold")
        )
        self.btn_rollback.pack(side="left")

    def _scan_rollback_versions(self):
        v_dir = os.path.join(APP_DIR, "versions")
        found = set()
        if os.path.exists(v_dir):
            for fname in os.listdir(v_dir):
                if fname.lower().endswith(".exe"):
                    m = re.search(r"v\d+\.\d+(?:\.\d+)?", fname, re.IGNORECASE)
                    if m:
                        tag = m.group(0).lower()
                        if tag != CURRENT_VERSION.lower():
                            found.add(tag)
        sorted_tags = sorted(list(found), key=lambda x: [int(p) for p in re.findall(r"\d+", x)], reverse=True)
        return [f"{tag} (Verified Cache)" for tag in sorted_tags] if sorted_tags else ["No previous versions cached"]

    def _on_rollback_clicked(self):
        choice = self.rollback_var.get()
        m = re.search(r"v\d+\.\d+(?:\.\d+)?", choice, re.IGNORECASE)
        if not m:
            messagebox.showwarning("Invalid Selection", "Please select a valid cached version.", parent=self)
            return
        tag = m.group(0).lower()

        v_dir = os.path.join(APP_DIR, "versions")
        matched_path = None
        if os.path.exists(v_dir):
            for fname in os.listdir(v_dir):
                if fname.lower().endswith(".exe") and tag in fname.lower():
                    matched_path = os.path.join(v_dir, fname)
                    break

        if not matched_path or not os.path.exists(matched_path):
            messagebox.showerror("Error", f"Executable for {tag} not found in versions folder.", parent=self)
            return

        confirm = messagebox.askyesno(
            "Confirm Rollback",
            f"Are you sure you want to rollback to {tag}?\n\n"
            f"Path OrderSync Pro will replace the active executable and immediately restart into {tag}.",
            parent=self
        )
        if not confirm:
            return

        target_exe = os.path.join(APP_DIR, "Path_OrderSync_Pro.exe")
        legacy_exe = os.path.join(APP_DIR, "QC_Batch_Loader.exe")
        swap_bat = os.path.join(APP_DIR, "_swap_version.bat")

        try:
            with open(swap_bat, "w", encoding="utf-8") as f:
                f.write(f"""@echo off
timeout /t 1 /nobreak >nul
copy /Y "{matched_path}" "{target_exe}" >nul
copy /Y "{matched_path}" "{legacy_exe}" >nul
start "" "{target_exe}"
del "%~f0"
""")
            subprocess.Popen(["cmd.exe", "/c", swap_bat], creationflags=0x08000000 if os.name == "nt" else 0)
            self.parent.destroy()
        except Exception as e:
            messagebox.showerror("Rollback Failed", f"Failed to perform rollback:\n{e}", parent=self)

    def _on_check_update_clicked(self):
        self.btn_check_update.configure(state="disabled", text="⏳ Checking...")
        def _done():
            if self.winfo_exists():
                self.btn_check_update.configure(state="normal", text="🔍 Check for Updates")
                has_update = bool(getattr(self.parent, "available_update", None))
                update_info = getattr(self.parent, "available_update", {}) if has_update else {}
                update_tag = update_info.get("tag", "")
                t = self.theme
                is_light = (getattr(self.parent, "theme_name", "light") == "light")
                if has_update and update_tag:
                    self.btn_status.configure(
                        text=f"🚀 Update Available: {update_tag}",
                        state="normal",
                        fg_color=t["primary"],
                        text_color="#FFFFFF" if is_light else "#0B1120",
                        command=self._open_update_dialog
                    )
                else:
                    self.btn_status.configure(
                        text="✔️ Up to Date",
                        state="disabled",
                        fg_color=t["success"],
                        text_color="#FFFFFF"
                    )
        check_for_updates(self.parent, silent=False)
        self.after(2000, _done)

    def _browse_path(self):
        cur = self.path_entry_var.get()
        chosen = filedialog.askdirectory(initialdir=cur if os.path.isdir(cur) else "C:/", parent=self)
        if chosen:
            self.path_entry_var.set(chosen)
            self._auto_save_path(chosen)

    def _on_path_entry_focusout(self, event=None):
        val = self.path_entry_var.get().strip()
        if val and os.path.isdir(val):
            self._auto_save_path(val)

    def _auto_save_path(self, path):
        if not path or not os.path.isdir(path):
            return
        self.parent.path_var.set(path)
        self.parent.config_data["dropbox_path"] = path
        if hasattr(self.parent, "_save_selected_vendors"):
            try:
                import json
                with open(os.path.join(APP_DIR, "config.json"), "w", encoding="utf-8") as f:
                    json.dump(self.parent.config_data, f, indent=2)
            except Exception:
                pass
        self.parent._scan_vendors()
        self.parent._update_storage_metrics()

    def _on_theme_changed(self, choice):
        new_theme = "light" if "Light" in choice else "dark"
        if getattr(self.parent, "theme_name", "") != new_theme:
            # Smooth real-time switch without freezing
            self.after(20, lambda nt=new_theme: self._apply_new_theme(nt))

    def _apply_new_theme(self, new_theme):
        self.parent._set_theme(new_theme)
        # Keep SettingsDialog still, visible, and focused on top
        try:
            self.deiconify()
            self.lift()
            self.attributes("-topmost", True)
            self.focus_force()
        except Exception:
            pass

    def _apply_dialog_theme(self, t):
        self.theme = t
        is_light = (getattr(self.parent, "theme_name", "light") == "light")
        btn_bg = "#FFFFFF" if is_light else "#253349"
        btn_hover = "#F1F5F9" if is_light else "#334155"

        self.configure(fg_color=t["bg_canvas"])
        cards = [getattr(self, "card_path", None), getattr(self, "card_theme", None), getattr(self, "card_ver", None)]
        for c in cards:
            if c and isinstance(c, ctk.CTkFrame) and c.winfo_exists():
                c.configure(fg_color=t["bg_card"], border_color=t["border"])

        for lbl in getattr(self, "_section_labels", []):
            if lbl and lbl.winfo_exists():
                lbl.configure(text_color=t["text_main"])

        if hasattr(self, "path_entry") and self.path_entry.winfo_exists():
            self.path_entry.configure(fg_color=t["bg_input"], text_color=t["text_main"], border_color=t["border"])

        if hasattr(self, "browse_btn") and self.browse_btn.winfo_exists():
            self.browse_btn.configure(fg_color=btn_bg, hover_color=btn_hover, text_color=t["text_main"], border_color=t["border"])

        if hasattr(self, "txt_notes") and self.txt_notes.winfo_exists():
            self.txt_notes.configure(fg_color=t["bg_input"], text_color=t["text_main"], border_color=t["border"])

        if hasattr(self, "ver_status_badge") and self.ver_status_badge.winfo_exists():
            self.ver_status_badge.configure(text_color=t["success"])

        if hasattr(self, "gh_btn") and self.gh_btn.winfo_exists():
            self.gh_btn.configure(fg_color=btn_bg, hover_color=btn_hover, text_color=t["text_main"], border_color=t["border"])

        if hasattr(self, "btn_check_update") and self.btn_check_update.winfo_exists():
            self.btn_check_update.configure(fg_color=btn_bg, hover_color=btn_hover, text_color=t["text_main"], border_color=t["border"])

        if hasattr(self, "rollback_menu") and self.rollback_menu.winfo_exists():
            self.rollback_menu.configure(fg_color=btn_bg, text_color=t["text_main"], button_color=t["primary"], button_hover_color=t["primary_hover"])

    def _load_current_notes(self):
        self.txt_notes.delete("1.0", "end")
        lines = [
            f"=== {APP_NAME} {CURRENT_VERSION} ===",
            "",
            "• Clean, modern light & dark user interface.",
            "• Direct 1-click 'Open Dropbox' on main dashboard.",
            "• Streamlined Settings with automatic path detection.",
            "• Live update alerts with blinking notification & Settings red dot.",
            "• High-speed parallel multi-vendor indexing & space optimizer."
        ]
        nl = chr(10)
        self.txt_notes.insert("1.0", nl.join(lines))

    def _open_github_release(self):
        webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases")

    def _open_update_dialog(self):
        update_info = getattr(self.parent, "available_update", None)
        if update_info:
            UpdateDialog(
                self.parent,
                latest_tag=update_info.get("tag", CURRENT_VERSION),
                current_ver=CURRENT_VERSION,
                release_body=update_info.get("body", "Bug fixes and improvements."),
                download_url=update_info.get("download_url", "")
            )

    def _on_destroy_event(self, event=None):
        if event is None or event.widget == self:
            if getattr(self.parent, "settings_dialog", None) == self:
                self.parent.settings_dialog = None

    def _on_close(self):
        if getattr(self.parent, "settings_dialog", None) == self:
            self.parent.settings_dialog = None
        try:
            self.destroy()
        except Exception:
            pass


class QCBatchLoaderApp(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title(f"{APP_NAME} {CURRENT_VERSION} — {APP_TAGLINE}")

        self.geometry("1100x640")

        self.minsize(960, 540)

        # Set taskbar/window icon

        try:

            if os.path.exists(APP_ICON_PATH):

                self.iconbitmap(APP_ICON_PATH)

        except Exception:

            pass

        self.config_data = load_config()

        self.theme_name = self.config_data.get("theme", "light")

        ctk.set_appearance_mode(self.theme_name)

        ctk.set_default_color_theme("blue")

        self.theme = BRAND_THEMES.get(self.theme_name, BRAND_THEMES["light"])

        self.configure(fg_color=self.theme["bg_canvas"])

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

        self._create_checkbox_icons()

        self._create_widgets()

        self._update_order_count()

        self._update_leftover_badge()

        self._update_storage_metrics()

        # Real-time Update System: Initial check, periodic polling, and first-launch guide

        self.after(2500, lambda: check_for_updates(self, silent=True))

        self.after(3600000, self._periodic_update_check)

        self.after(1200, self._check_first_launch_whats_new)

    def _create_checkbox_icons(self):
        """
        Generates modern rounded rectangle checkbox icons (18x18px)
        with anti-aliasing (supersampled at 4x) matching the modern UI design.
        """
        is_light = (getattr(self, "theme_name", "light") == "light")
        t = getattr(self, "theme", BRAND_THEMES["light"])

        border_col = (203, 213, 225, 255) if is_light else (71, 85, 105, 255)
        unchecked_bg = (255, 255, 255, 255) if is_light else (26, 36, 54, 255)
        primary_hex = t.get("primary", "#1E2565") if is_light else t.get("success", "#10B981")

        def _hex_to_rgba(h, alpha=255):
            h = h.lstrip("#")
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)

        checked_bg = _hex_to_rgba(primary_hex)
        check_mark_col = (255, 255, 255, 255)

        size = 18
        scale = 4
        canvas_size = (size * scale, size * scale)
        r = int(3.5 * scale)
        margin = int(1.5 * scale)
        border_w = max(1, int(1.3 * scale))

        resample_filter = getattr(getattr(Image, 'Resampling', None), 'LANCZOS', getattr(Image, 'LANCZOS', Image.BICUBIC))

        # 1. Unchecked Box
        img_un = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
        draw_un = ImageDraw.Draw(img_un)
        box = [margin, margin, canvas_size[0] - margin, canvas_size[1] - margin]
        draw_un.rounded_rectangle(box, radius=r, fill=unchecked_bg, outline=border_col, width=border_w)
        img_un_scaled = img_un.resize((size, size), resample_filter)
        self.chk_unchecked_img = ImageTk.PhotoImage(img_un_scaled)

        # 2. Checked Box
        img_ck = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
        draw_ck = ImageDraw.Draw(img_ck)
        draw_ck.rounded_rectangle(box, radius=r, fill=checked_bg, outline=checked_bg, width=border_w)

        # Crisp checkmark coordinates
        p1 = (margin + 3.8 * scale, margin + 7.8 * scale)
        p2 = (margin + 6.8 * scale, margin + 11.2 * scale)
        p3 = (margin + 12.0 * scale, margin + 4.6 * scale)
        ck_width = max(1, int(2.0 * scale))
        draw_ck.line([p1, p2, p3], fill=check_mark_col, width=ck_width, joint="curve")
        img_ck_scaled = img_ck.resize((size, size), resample_filter)
        self.chk_checked_img = ImageTk.PhotoImage(img_ck_scaled)

        # Master Checkbox Icons
        header_bg = (248, 250, 252, 255) if is_light else (30, 41, 59, 255)
        img_m_un = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
        draw_m_un = ImageDraw.Draw(img_m_un)
        draw_m_un.rounded_rectangle(box, radius=r, fill=header_bg, outline=border_col, width=border_w)
        img_m_un_scaled = img_m_un.resize((size, size), resample_filter)
        self.chk_master_unchecked_img = ImageTk.PhotoImage(img_m_un_scaled)
        self.chk_master_checked_img = self.chk_checked_img

    def _setup_style(self):

        t = self.theme

        is_light = (self.theme_name == "light")

        self.configure(fg_color=t["bg_canvas"])

        self.style = ttk.Style(self)

        self.style.theme_use("clam")

        # Custom Treeview Item layout without indicator arrow to keep flat checkbox alignment
        self.style.layout("Custom.Treeview.Item", [
            ('Treeitem.padding', {'sticky': 'nswe', 'children': [
                ('Treeitem.image', {'side': 'left', 'sticky': ''}),
                ('Treeitem.text', {'side': 'left', 'sticky': ''})
            ]})
        ])

        # Custom Treeview Heading layout to ensure header checkbox is on the LEFT of the text
        heading_layout = [
            ('Treeheading.cell', {'sticky': 'nswe', 'children': [
                ('Treeheading.border', {'sticky': 'nswe', 'children': [
                    ('Treeheading.padding', {'sticky': 'nswe', 'children': [
                        ('Treeheading.image', {'side': 'left', 'sticky': ''}),
                        ('Treeheading.text', {'side': 'left', 'sticky': ''})
                    ]})
                ]})
            ]})
        ]
        self.style.layout("Custom.Treeview.Heading", heading_layout)
        self.style.layout("Treeview.Heading", heading_layout)

        # Configure Custom.Treeview

        self.style.configure(

            "Custom.Treeview",

            background=t["bg_card"],

            foreground=t["text_main"],

            fieldbackground=t["bg_card"],

            rowheight=34,

            font=("Segoe UI", 10),

            borderwidth=0,

            indent=0

        )

        self.style.configure(

            "Custom.Treeview.Heading",

            background="#F8FAFC" if is_light else "#1E293B",

            foreground=t["text_muted"],

            font=("Segoe UI", 10, "bold"),

            relief="flat",

            borderwidth=0

        )

        self.style.map(

            "Custom.Treeview",

            background=[("selected", "#EFF6FF" if is_light else "#23334D")],

            foreground=[("selected", "#1E40AF" if is_light else "#38BDF8")]

        )

        # Color Palette tokens

        self.bg_color = t["bg_canvas"]

        self.card_bg = t["bg_card"]

        self.card_border = t["border"]

        self.accent_blue = t["secondary"]

        self.accent_green = t["success"]

        self.accent_orange = t["accent"]

        self.accent_red = t["danger"]

        self.text_main = t["text_main"]

        self.text_muted = t["text_muted"]

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

            self.vendor_btn.config(text="🏢 Vendors: None Found ▼", bg=self.theme["border"], fg=self.theme["text_muted"])

            if hasattr(self, "vendor_reset_btn"):

                self.vendor_reset_btn.pack_forget()

        elif sel_count == total:

            self.vendor_btn.config(text=f"🏢 Vendors: All ({total}) ▼", bg=self.theme["bg_card"], fg=self.theme["text_main"])

            if hasattr(self, "vendor_reset_btn"):

                self.vendor_reset_btn.pack_forget()

        elif sel_count == 1:

            single = next(iter(self.selected_vendors))

            self.vendor_btn.config(text=f"🏢 Vendors: {single} (1/{total}) ▼", bg=self.theme["accent"], fg="#0f172a")

            if hasattr(self, "vendor_reset_btn"):

                self.vendor_reset_btn.pack(side="left", padx=(0, 8), pady=4, after=self.vendor_btn)

        elif sel_count == 0:

            self.vendor_btn.config(text=f"🏢 Vendors: None (0/{total}) ⚠️ ▼", bg=self.theme["danger"], fg="#ffffff")

            if hasattr(self, "vendor_reset_btn"):

                self.vendor_reset_btn.pack(side="left", padx=(0, 8), pady=4, after=self.vendor_btn)

        else:

            names = sorted(list(self.selected_vendors))

            short = f"{names[0]}, {names[1]}" if len(names) == 2 else f"{names[0]} +{sel_count - 1} more"

            self.vendor_btn.config(text=f"🏢 Vendors: {sel_count} Selected ▼", bg=self.theme["accent"], fg="#0f172a")

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

        t = self.theme

        is_light = (self.theme_name == "light")

        # 1. Top Header Bar

        header = ctk.CTkFrame(self, fg_color="transparent")

        header.pack(fill="x", padx=16, pady=(10, 4))

        title_row = ctk.CTkFrame(header, fg_color="transparent")

        title_row.pack(side="left")

        # App Header Brand Logo

        self.header_logo_img = None

        if os.path.exists(LOGO_HEADER_PATH):

            try:

                from PIL import Image

                self.header_logo_img = ctk.CTkImage(

                    light_image=Image.open(LOGO_HEADER_PATH),

                    dark_image=Image.open(LOGO_HEADER_PATH),

                    size=(34, 34)

                )

                ctk.CTkLabel(title_row, text="", image=self.header_logo_img).pack(side="left", padx=(0, 8))

            except Exception:

                pass

        else:

            pass

        text_col = ctk.CTkFrame(title_row, fg_color="transparent")

        text_col.pack(side="left")

        title_head = ctk.CTkFrame(text_col, fg_color="transparent")

        title_head.pack(anchor="w")

        self.app_title_lbl = ctk.CTkLabel(title_head, text=APP_NAME, font=("Segoe UI", 14, "bold"), text_color=t["text_main"])
        self.app_title_lbl.pack(side="left")

        self.app_ver_lbl = ctk.CTkLabel(title_head, text=CURRENT_VERSION, font=("Segoe UI", 9, "bold"), text_color="#FFFFFF" if is_light else "#0B1120", fg_color=t["primary"], corner_radius=6, padx=6, pady=1)
        self.app_ver_lbl.pack(side="left", padx=8)
        self.app_ver_lbl.configure(cursor="hand2")
        self.app_ver_lbl.bind("<Button-1>", lambda e: WhatsNewDialog(self, CURRENT_VERSION))

        self.app_tagline_lbl = ctk.CTkLabel(text_col, text=APP_TAGLINE, font=("Segoe UI", 10), text_color=t["text_muted"])
        self.app_tagline_lbl.pack(anchor="w")

        # Header Right Actions

        header_actions = ctk.CTkFrame(header, fg_color="transparent")

        header_actions.pack(side="right")

        self.settings_btn = ctk.CTkButton(
            header_actions,
            text="⚙️ Settings",
            command=self._open_settings,
            fg_color="#FFFFFF" if is_light else "#1E293B",
            hover_color="#F1F5F9" if is_light else "#334155",
            text_color=t["text_main"],
            border_width=1,
            border_color=t["border"],
            corner_radius=14,
            height=30,
            font=("Segoe UI", 11, "bold")
        )
        self.settings_btn.pack(side="right")

        # Prominent Header Update Pill (Visible only when an update is available)
        self.header_update_btn = ctk.CTkButton(
            header_actions,
            text="🚀 Update Ready",
            command=self._open_update_from_header,
            fg_color=t["primary"],
            hover_color=t["primary_hover"],
            text_color="#FFFFFF" if is_light else "#0B1120",
            corner_radius=14,
            height=30,
            font=("Segoe UI", 11, "bold")
        )
        # Initially hidden until update is detected

        self.notification_btn = ctk.CTkButton(

            header_actions,

            text="🔔",

            command=self._open_notification_center,

            fg_color="#FFFFFF" if is_light else "#1E293B",

            hover_color="#F1F5F9" if is_light else "#334155",

            text_color=t["text_muted"],

            border_width=1,

            border_color=t["border"],

            corner_radius=14,

            width=36,

            height=30,

            font=("Segoe UI", 12)

        )

        self.notification_btn.pack(side="right", padx=(0, 6))

        self.leftover_btn = ctk.CTkButton(

            header_actions,

            text="🕒 History: 0 Local",

            command=self._open_history_tracker,

            fg_color="#FFFFFF" if is_light else "#1E293B",

            hover_color="#F1F5F9" if is_light else "#334155",

            text_color=t["success"],

            border_width=1,

            border_color=t["border"],

            corner_radius=14,

            height=30,

            font=("Segoe UI", 11, "bold")

        )

        self.leftover_btn.pack(side="right", padx=(0, 6))

        # 2. Top Control Strip (3 Pill Cards: Vendors, Drive Space, Local Orders)

        strip = ctk.CTkFrame(self, fg_color="transparent")

        strip.pack(fill="x", padx=16, pady=(4, 6))

        if not hasattr(self, "path_var"):

            self.path_var = tk.StringVar(value=self.config_data.get("dropbox_path") or DEFAULT_DROPBOX_PATH)

        # Pill 1: Vendors Filter

        self.card_vendors = ctk.CTkFrame(strip, fg_color=t["bg_card"], corner_radius=18, border_width=1, border_color=t["border"])

        self.card_vendors.pack(side="left", padx=(0, 8), fill="y")

        self.vendor_btn = ctk.CTkButton(

            self.card_vendors,

            text="🏢 Vendors: All Selected ▾",

            command=self._toggle_vendor_popup,

            fg_color="transparent",

            hover_color="#F1F5F9" if is_light else "#253349",

            text_color=t["text_main"],

            corner_radius=18,

            height=34,

            font=("Segoe UI", 11, "bold")

        )

        self.vendor_btn.pack(padx=6, pady=2)

        # Pill 3: Drive Space Gauge

        drive_card_bg = "#BAE6FD" if is_light else "#1E293B"

        drive_card_border = "#7DD3FC" if is_light else "#334155"

        drive_card_fg = "#0369A1" if is_light else "#38BDF8"

        self.card_drive = ctk.CTkFrame(strip, fg_color=drive_card_bg, corner_radius=18, border_width=1, border_color=drive_card_border)

        self.card_drive.pack(side="left", padx=(0, 8), fill="y")

        self.drive_metric_lbl = ctk.CTkLabel(self.card_drive, text="Drive C: 146.5 GB / 365 GB (40% free)", text_color=drive_card_fg, font=("Segoe UI", 11, "bold"))

        self.drive_metric_lbl.pack(padx=14, pady=6)

        # Pill 4: Local Orders Badge

        self.card_local = ctk.CTkFrame(strip, fg_color=t["bg_card"], corner_radius=18, border_width=1, border_color=t["border"])

        self.card_local.pack(side="left", padx=(0, 8), fill="y")

        # Pill 4: Open Dropbox Button

        self.card_open_dropbox = ctk.CTkFrame(strip, fg_color=t["bg_card"], corner_radius=18, border_width=1, border_color=t["border"])

        self.card_open_dropbox.pack(side="left", fill="y")

        self.btn_open_dropbox = ctk.CTkButton(

            self.card_open_dropbox,

            text="📂 Open Dropbox",

            command=self._open_dropbox_folder,

            fg_color="transparent",

            hover_color="#F1F5F9" if is_light else "#253349",

            text_color=t["text_main"],

            corner_radius=18,

            height=34,

            font=("Segoe UI", 11, "bold")

        )

        self.btn_open_dropbox.pack(padx=8, pady=2)

        self.local_metric_lbl = ctk.CTkLabel(self.card_local, text="● Local QC Orders: 0 (0 B on disk)", text_color=t["success"], font=("Segoe UI", 11, "bold"))

        self.local_metric_lbl.pack(side="left", padx=(12, 6), pady=4)

        self.refresh_local_btn = ctk.CTkButton(

            self.card_local,

            text="🔄",

            command=self._scan_local_in_selected_vendors,

            fg_color="transparent",

            hover_color="#F1F5F9" if is_light else "#253349",

            text_color=t["text_muted"],

            width=28,

            height=28,

            corner_radius=14,

            font=("Segoe UI", 12)

        )

        self.refresh_local_btn.pack(side="right", padx=(0, 6), pady=4)

        # 3. Main Body Split (Left Card + Right Card)

        self.body_container = ctk.CTkFrame(self, fg_color="transparent")

        self.body_container.pack(fill="both", expand=True, padx=16, pady=4)

        # Left Card: Paste Order IDs Drawer

        self.card_left = ctk.CTkFrame(self.body_container, fg_color=t["bg_card"], corner_radius=14, border_width=1, border_color=t["border"], width=250)

        self.card_left.pack(side="left", fill="y", padx=(0, 8))

        self.card_left.pack_propagate(False)

        self.left_frame = self.card_left  # Alias for backward compatibility

        card_left_header = ctk.CTkFrame(self.card_left, fg_color="transparent")

        card_left_header.pack(fill="x", padx=12, pady=(10, 4))

        self.paste_title_lbl = ctk.CTkLabel(card_left_header, text="📋 Paste Order IDs", font=("Segoe UI", 12, "bold"), text_color=t["text_main"])
        self.paste_title_lbl.pack(side="left")

        # Hide & Clear buttons on drawer header

        btn_box_left_head = ctk.CTkFrame(card_left_header, fg_color="transparent")

        btn_box_left_head.pack(side="right")

        self.btn_hide_left = ctk.CTkButton(

            btn_box_left_head,

            text="◀ Hide",

            command=self._toggle_drawer,

            fg_color="transparent",

            hover_color="#F1F5F9" if is_light else "#253349",

            text_color=t["text_muted"],

            border_width=1,

            border_color=t["border"],

            corner_radius=10,

            width=46,

            height=22,

            font=("Segoe UI", 10)

        )

        self.btn_hide_left.pack(side="left", padx=(0, 4))

        self.btn_toggle_drawer = self.btn_hide_left  # Alias for backward compatibility

        self.clear_top_btn = ctk.CTkButton(

            btn_box_left_head,

            text="Clear",

            command=self._clear_input,

            fg_color="transparent",

            hover_color="#F1F5F9" if is_light else "#253349",

            text_color=t["text_muted"],

            border_width=1,

            border_color=t["border"],

            corner_radius=10,

            width=44,

            height=22,

            font=("Segoe UI", 10)

        )

        self.clear_top_btn.pack(side="left")

        self.count_lbl = ctk.CTkLabel(self.card_left, text="Total: 0 | Unique: 0", font=("Segoe UI", 10), text_color=t["text_muted"])

        self.count_lbl.pack(anchor="w", padx=12, pady=(0, 6))

        self.input_text = ctk.CTkTextbox(

            self.card_left,

            fg_color=t["bg_input"],

            text_color=t["text_main"],

            corner_radius=8,

            border_width=1,

            border_color=t["border"],

            font=("Consolas", 11)

        )

        self.input_text.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        self.input_text.bind("<KeyRelease>", self._on_input_text_changed)

        row_util = ctk.CTkFrame(self.card_left, fg_color="transparent")

        row_util.pack(fill="x", padx=12, pady=(0, 8))

        self.paste_btn = ctk.CTkButton(

            row_util,

            text="Paste",

            command=self._paste_clipboard,

            fg_color="#FFFFFF" if is_light else "#1E293B",

            hover_color="#F8FAFC" if is_light else "#334155",

            text_color=t["text_main"],

            border_width=1,

            border_color=t["border"],

            corner_radius=8,

            width=64,

            height=30,

            font=("Segoe UI", 11)

        )

        self.paste_btn.pack(side="left", padx=(0, 6))

        clean_btn_bg = t["success"] if getattr(self, "input_cleaned", False) else (t["danger"] if not is_light else "#FFFFFF")

        clean_btn_fg = "#FFFFFF" if (getattr(self, "input_cleaned", False) or not is_light) else t["text_main"]

        clean_btn_txt = "✔️ Clean & Deduplicate" if getattr(self, "input_cleaned", False) else "🧹 Clean & Deduplicate"

        self.btn_clean_dedup = ctk.CTkButton(

            row_util,

            text=clean_btn_txt,

            command=self._clean_and_deduplicate,

            fg_color=clean_btn_bg,

            hover_color="#F8FAFC" if (is_light and not getattr(self, "input_cleaned", False)) else t["danger_hover"],

            text_color=clean_btn_fg,

            border_width=1,

            border_color=t["border"],

            corner_radius=8,

            height=30,

            font=("Segoe UI", 11)

        )

        self.btn_clean_dedup.pack(side="left", fill="x", expand=True)

        sync_btn_bg = t["primary"] if getattr(self, "input_cleaned", False) else (t["primary"] if is_light else "#1E293B")

        sync_btn_fg = "#FFFFFF" if is_light else "#0B1120"

        self.btn_add_to_sync = ctk.CTkButton(

            self.card_left,

            text="+ Add to sync list",

            command=self._add_to_sync_list,

            fg_color=sync_btn_bg,

            hover_color=t["primary_hover"],

            text_color=sync_btn_fg,

            corner_radius=8,

            height=36,

            font=("Segoe UI", 12, "bold")

        )

        self.btn_add_to_sync.pack(fill="x", padx=12, pady=(0, 12))

        # Right Card: Sync List Dashboard Table

        self.card_right = ctk.CTkFrame(self.body_container, fg_color=t["bg_card"], corner_radius=14, border_width=1, border_color=t["border"])

        self.card_right.pack(side="left", fill="both", expand=True)

        self.right_frame = self.card_right  # Alias

        card_right_header = ctk.CTkFrame(self.card_right, fg_color="transparent")

        card_right_header.pack(fill="x", padx=14, pady=(10, 8))

        self.search_box = ctk.CTkFrame(card_right_header, fg_color=t["bg_card"], corner_radius=16, border_width=1, border_color=t["border"], height=32)

        self.search_box.pack(side="left")

        self.search_icon_lbl = ctk.CTkLabel(self.search_box, text="🔍", text_color=t["text_muted"], font=("Segoe UI", 10))
        self.search_icon_lbl.pack(side="left", padx=(8, 2))

        self.search_entry = ctk.CTkEntry(

            self.search_box,

            textvariable=self.search_var,

            placeholder_text="Search order, vendor...",

            fg_color="transparent",

            border_width=0,

            text_color=t["text_main"],

            font=("Segoe UI", 11),

            width=150,

            height=28

        )

        self.search_entry.pack(side="left", padx=(0, 4))

        self.search_entry.bind("<KeyRelease>", lambda e: self._filter_main_table())

        self.clear_search_btn = ctk.CTkButton(

            self.search_box,

            text="✕",

            command=self._clear_main_search,

            fg_color="transparent",

            hover_color="#F1F5F9" if is_light else "#253349",

            text_color=t["text_muted"],

            width=22,

            height=22,

            corner_radius=11,

            font=("Segoe UI", 10)

        )

        self.clear_search_btn.pack(side="left", padx=(0, 4))

        # Header action buttons on right card (wrapped in dedicated container to prevent squishing)

        header_actions_right = ctk.CTkFrame(card_right_header, fg_color="transparent")

        header_actions_right.pack(side="right")

        self.make_online_top_btn = ctk.CTkButton(

            header_actions_right,

            text="☁️ Make Online",

            command=self._make_selected_online,

            fg_color="#FFFFFF" if is_light else "#1E293B",

            hover_color="#F8FAFC" if is_light else "#334155",

            text_color=t["text_main"],

            border_width=1,

            border_color=t["border"],

            corner_radius=14,

            height=30,

            font=("Segoe UI", 11, "bold")

        )

        self.make_online_top_btn.pack(side="right", padx=(4, 0))

        self.btn_scan_local = ctk.CTkButton(

            header_actions_right,

            text="🔍 Scan Local",

            command=self._scan_local_in_selected_vendors,

            fg_color="#FFFFFF" if is_light else "#1E293B",

            hover_color="#F8FAFC" if is_light else "#334155",

            text_color=t["secondary"] if not is_light else t["secondary_text"],

            border_width=1,

            border_color=t["border"],

            corner_radius=14,

            height=30,

            font=("Segoe UI", 11, "bold")

        )

        self.btn_scan_local.pack(side="right", padx=(4, 0))

        self.btn_clean_dashboard = ctk.CTkButton(

            header_actions_right,

            text="🗑️ Clean Dash",

            command=self._clean_dashboard,

            fg_color="#FFFFFF" if is_light else "#1E293B",

            hover_color="#F8FAFC" if is_light else "#334155",

            text_color=t["danger"],

            border_width=1,

            border_color=t["border"],

            corner_radius=14,

            height=30,

            font=("Segoe UI", 11)

        )

        self.btn_clean_dashboard.pack(side="right", padx=(4, 0))

        self.btn_order_review = ctk.CTkButton(

            header_actions_right,

            text="🔍 Review",

            command=self._open_order_review,

            fg_color="#FFFFFF" if is_light else "#1E293B",

            hover_color="#F8FAFC" if is_light else "#334155",

            text_color=t["text_muted"],

            border_width=1,

            border_color=t["border"],

            corner_radius=14,

            height=30,

            font=("Segoe UI", 11)

        )

        self.btn_order_review.pack(side="right", padx=(4, 0))

        # Table using styled ttk.Treeview inside card_right

        tree_frame = ctk.CTkFrame(self.card_right, fg_color="transparent")

        tree_frame.pack(fill="both", expand=True, padx=14, pady=(0, 10))

        columns = ("vendor", "status", "files", "size", "make_local", "make_online", "open")

        self.tree = ttk.Treeview(tree_frame, columns=columns, show="tree headings", selectmode="extended", style="Custom.Treeview")

        self.tree.heading("#0", text=" Order ID ˅", image=self.chk_master_unchecked_img, anchor="w", command=self._toggle_master_checkbox)

        self.tree.heading("vendor", text="Vendor", image="", anchor="w")

        self.tree.heading("status", text="Sync Status", anchor="center")

        self.tree.heading("files", text="Files", anchor="center")

        self.tree.heading("size", text="File Size", anchor="center")

        self.tree.heading("make_local", text="Make Local", anchor="center")

        self.tree.heading("make_online", text="Make Online", anchor="center")

        self.tree.heading("open", text="Open", anchor="center")

        self.tree.column("#0", width=115, minwidth=90, stretch=True, anchor="w")

        self.tree.column("vendor", width=130, minwidth=100, stretch=True, anchor="w")

        self.tree.column("status", width=125, minwidth=95, stretch=True, anchor="center")

        self.tree.column("files", width=75, minwidth=60, stretch=True, anchor="center")

        self.tree.column("size", width=160, minwidth=135, stretch=True, anchor="center")

        self.tree.column("make_local", width=105, minwidth=85, stretch=True, anchor="center")

        self.tree.column("make_online", width=105, minwidth=85, stretch=True, anchor="center")

        self.tree.column("open", width=60, minwidth=48, stretch=True, anchor="center")

        # Status Tags configuration

        self.tree.tag_configure("row_local", background=t["status_local_bg"], foreground=t["status_local_fg"])

        self.tree.tag_configure("row_syncing", background=t["status_sync_bg"], foreground=t["status_sync_fg"])

        self.tree.tag_configure("row_online", background=t["status_cloud_bg"], foreground=t["status_cloud_fg"])

        self.tree.tag_configure("row_notfound", background=t["status_notfound_bg"], foreground=t["status_notfound_fg"])

        # Scrollbar

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)

        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)

        tree_scroll.pack(side="right", fill="y")

        # Table Footer Bar inside card_right (Moved here directly below table per user request)
        self.table_footer = ctk.CTkFrame(self.card_right, fg_color="transparent")
        self.table_footer.pack(fill="x", padx=14, pady=(2, 10))

        self.total_lbl = ctk.CTkLabel(
            self.table_footer,
            text="Total Orders in Dashboard: 0",
            font=("Segoe UI", 10, "bold"),
            text_color=t["text_main"]
        )
        self.total_lbl.pack(anchor="w", pady=(0, 3))

        self.total_progress = ctk.CTkProgressBar(
            self.table_footer,
            fg_color="#DCE9F5" if is_light else "#253349",
            progress_color=t["primary"],
            corner_radius=6,
            height=10
        )
        self.total_progress.set(0.0)
        self.total_progress.pack(fill="x")

        self.single_lbl = None
        self.single_progress = None

        # Tree Bindings

        self.tree.bind("<Button-1>", self._on_tree_click)

        self.tree.bind("<Double-1>", self._on_tree_double_click)

        self.tree.bind("<Button-3>", self._on_tree_right_click)

        self.tree.bind("<Control-c>", self._copy_selected_order_ids)

        self.tree.bind("<Control-C>", self._copy_selected_order_ids)

        self.tree.bind("<space>", self._on_space_key)

        # Context menu

        self.context_menu = tk.Menu(self, tearoff=0, bg=t["bg_card"], fg=t["text_main"], activebackground=t["primary"], activeforeground="white")

        self.context_menu.add_command(label="📋 Copy Order ID(s) (Ctrl+C)", command=self._copy_selected_order_ids)

        self.context_menu.add_command(label="📂 Open in File Explorer", command=self._open_selected_folder)

        self.context_menu.add_separator()

        self.context_menu.add_command(label="📥 Make Local (Download)", command=self._make_selected_local)

        self.context_menu.add_command(label="☁️ Make Online (Free Space)", command=self._make_selected_online)

        self.context_menu.add_separator()

        self.context_menu.add_command(label="🔍 Review / Filter Files", command=self._open_order_review)

        self.context_menu.add_command(label="🗑️ Remove from Dashboard", command=self._remove_selected_from_dashboard)

        # 4. Bottom Signature 4-Button Action Dock

        dock = ctk.CTkFrame(self, fg_color="transparent")

        dock.pack(fill="x", padx=16, pady=(4, 8))

        btn_row = ctk.CTkFrame(dock, fg_color="transparent")

        btn_row.pack(fill="x", pady=(0, 8))

        self.btn_make_local_all = ctk.CTkButton(

            btn_row,

            text="📥 1. Make Local (Ready for QC)",

            command=self._make_all_local,

            fg_color=t["action_btn_make_local_bg"],

            hover_color=t["primary_hover"],

            text_color=t["action_btn_make_local_fg"],

            corner_radius=10,

            height=44,

            font=("Segoe UI", 12, "bold")

        )

        self.btn_make_local_all.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.btn_make_online_all = ctk.CTkButton(

            btn_row,

            text="☁️ 2. Free Up Space (Make Online-Only)",

            command=self._make_all_online,

            fg_color=t["action_btn_free_space_bg"],

            hover_color=t["secondary_hover"],

            text_color=t["action_btn_free_space_fg"],

            corner_radius=10,

            height=44,

            font=("Segoe UI", 12, "bold")

        )

        self.btn_make_online_all.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.btn_pause = ctk.CTkButton(

            btn_row,

            text="⏸ Pause",

            command=self._toggle_pause,

            fg_color=t["action_btn_pause_bg"],

            hover_color="#F59E0B",

            text_color=t["action_btn_pause_fg"],

            corner_radius=10,

            width=140,

            height=44,

            font=("Segoe UI", 12, "bold")

        )

        self.btn_pause.pack(side="left", padx=(0, 6))

        self.btn_stop = ctk.CTkButton(

            btn_row,

            text="⏹ Stop",

            command=self._request_stop,

            fg_color=t["action_btn_stop_bg"],

            hover_color="#DC2626",

            text_color=t["action_btn_stop_fg"],

            corner_radius=10,

            width=140,

            height=44,

            font=("Segoe UI", 12, "bold")

        )

        self.btn_stop.pack(side="left")

        # Status Ticker line (Clean & compact, dual progress bars moved into card_right footer)

        self.status_var = tk.StringVar(value="⚡ Ready • 0 orders in queue • High speed parallel sync active")

        self.status_pill_lbl = ctk.CTkLabel(dock, textvariable=self.status_var, font=("Segoe UI", 10), text_color=t["text_muted"])

        self.status_pill_lbl.pack(anchor="w", pady=(4, 2))

    def _toggle_theme(self):

        """Switches dynamically between Dark and Light mode following Picture Style."""

        self.theme_name = "dark" if self.theme_name == "light" else "light"

        self.config_data["theme"] = self.theme_name

        save_config(self.config_data)

        ctk.set_appearance_mode(self.theme_name)

        self.theme = BRAND_THEMES[self.theme_name]

        self._rebuild_ui()

    def _rebuild_ui(self):

        """Re-renders UI widgets in the newly selected theme while seamlessly preserving active state."""

        raw_text = self.input_text.get("1.0", "end-1c") if hasattr(self, "input_text") else ""

        cleaned = getattr(self, "input_cleaned", False)

        drawer_was_open = getattr(self, "drawer_open", True)

        search_val = self.search_var.get() if hasattr(self, "search_var") else ""

        existing_items = dict(self.table_items) if hasattr(self, "table_items") else {}

        existing_cb = dict(self.order_checkboxes) if hasattr(self, "order_checkboxes") else {}

        # Clear existing widgets

        for child in self.winfo_children():

            if isinstance(child, (tk.Toplevel, ctk.CTkToplevel)):

                continue

            try:

                child.destroy()

            except Exception:

                pass

        # Re-initialize style and widgets with new theme tokens

        self._setup_style()

        self._create_widgets()

        # Restore input state

        if hasattr(self, "input_text"):

            self.input_text.delete("1.0", "end")

            self.input_text.insert("1.0", raw_text)

            self._update_order_count()

        if cleaned:

            self.input_cleaned = True

            t = self.theme

            self.btn_clean_dedup.configure(

                text="✔️ Clean & Deduplicate",

                fg_color=t["success"],

                hover_color=t["success_hover"],

                text_color="#FFFFFF"

            )

            sync_fg = "white" if self.theme_name == "light" else "#0b1120"

            self.btn_add_to_sync.configure(

                state="normal",

                fg_color=t["primary"],

                hover_color=t["primary_hover"],

                text_color=sync_fg

            )

        if not drawer_was_open:

            self.card_left.pack_forget()

            self.drawer_open = False

            if hasattr(self, "btn_hide_left"):

                self.btn_hide_left.configure(text="▶ Show")

        # Restore table items

        self._create_checkbox_icons()

        m_img = self.chk_master_checked_img if getattr(self, "master_checked", False) else self.chk_master_unchecked_img

        self.tree.heading("#0", text=" Order ID ˅", image=m_img, anchor="w")

        for iid, data in existing_items.items():

            vals = data.get("values", ()) if isinstance(data, dict) else tuple(data)

            tag = data.get("tag", "row_online") if isinstance(data, dict) else "row_online"

            info = self.resolved_orders.get(iid, {})

            order_id = info.get("order_id") or str(iid).split("_")[0]

            chk = existing_cb.get(iid, "☐")

            chk_img = self.chk_checked_img if chk == "☑" else self.chk_unchecked_img

            self.tree.insert("", "end", iid=iid, text=f" #{order_id}", image=chk_img, values=vals, tags=(tag,))

        self.table_items = existing_items

        self.order_checkboxes = existing_cb

        # Restore metrics & badges

        self._update_vendor_btn_label()

        self._update_storage_metrics()

        self._update_leftover_badge()

        self._update_notification_badge()

        tot_cnt = len(self.table_items)

        loc_cnt = sum(1 for v in self.table_items.values() if any("local" in str(x).lower() for x in (v if isinstance(v, (list, tuple)) else [])))

        if hasattr(self, "total_lbl") and self.total_lbl:

            if tot_cnt > 0 and loc_cnt > 0:

                self.total_lbl.configure(text=f"Total Orders in Dashboard: {tot_cnt} ({loc_cnt} Local, {tot_cnt - loc_cnt} Cloud Only)")

            else:

                self.total_lbl.configure(text=f"Total Orders in Dashboard: {tot_cnt}")

        if hasattr(self, "total_progress") and self.total_progress:

            self.total_progress.set(loc_cnt / max(tot_cnt, 1) if tot_cnt > 0 else 0.0)

    def _toggle_drawer(self):

        """Toggles the Paste Order IDs left drawer between collapsed and visible."""

        if getattr(self, "drawer_open", True):

            self.card_left.pack_forget()

            self.drawer_open = False

            self.btn_hide_left.configure(text="▶ Show")

            self.status_var.set("Order IDs drawer closed.")

        else:

            self.card_left.pack(side="left", fill="y", padx=(0, 8), before=self.card_right)

            self.drawer_open = True

            self.btn_hide_left.configure(text="◀ Hide")

            self.status_var.set("Order IDs drawer opened.")

    def _on_input_text_changed(self, event=None):

        self._update_order_count()

        self.input_cleaned = False

        t = self.theme

        is_light = (self.theme_name == "light")

        self.btn_clean_dedup.configure(

            text="🧹 Clean & Deduplicate",

            fg_color="#FFFFFF" if is_light else t["danger"],

            hover_color="#F8FAFC" if is_light else t["danger_hover"],

            text_color=t["text_main"] if is_light else "#FFFFFF"

        )

        self.btn_add_to_sync.configure(

            state="normal" if is_light else "disabled",

            fg_color=t["primary"] if is_light else t["border"],

            text_color="#FFFFFF" if is_light else t["text_muted"]

        )

    def _clean_and_deduplicate(self):

        raw = self.input_text.get("1.0", "end-1c")

        if not raw.strip():

            messagebox.showinfo("Empty Input", "Please enter or paste Order IDs first.", parent=self)

            return

        orders, invalid = self._parse_order_ids()

        if not orders:

            messagebox.showwarning("No Valid Orders", "No valid Order IDs found in the input.", parent=self)

            return

        seen = set()

        unique_orders = []

        for o in orders:

            if o not in seen:

                seen.add(o)

                unique_orders.append(o)

        formatted = "\n".join(f"#{o}" for o in unique_orders)

        self.input_text.delete("1.0", "end")

        self.input_text.insert("1.0", formatted)

        self.input_cleaned = True

        self._update_order_count()

        t = self.theme

        self.btn_clean_dedup.configure(

            text="✔️ Clean & Deduplicate",

            fg_color=t["success"],

            hover_color=t["success_hover"],

            text_color="#FFFFFF"

        )

        self.btn_add_to_sync.configure(

            state="normal",

            fg_color=t["primary"],

            hover_color=t["primary_hover"],

            text_color="#FFFFFF"

        )

        self.status_var.set(f"Cleaned & deduplicated: {len(unique_orders)} unique orders ready.")

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

            if hasattr(self, "total_progress") and self.total_progress:

                self.total_progress.set(0.0)

            if hasattr(self, "total_lbl") and self.total_lbl:

                self.total_lbl.configure(text="Total Orders in Dashboard: 0")

            self.status_var.set("Dashboard cleared.")

    def _toggle_master_checkbox(self):

        all_iids = self.tree.get_children()

        if not all_iids:

            return

        self.master_checked = not getattr(self, "master_checked", False)

        new_mark = "☑" if self.master_checked else "☐"

        m_img = self.chk_master_checked_img if self.master_checked else self.chk_master_unchecked_img

        row_img = self.chk_checked_img if self.master_checked else self.chk_unchecked_img

        self.tree.heading("#0", text=" Order ID ˅", image=m_img, anchor="w")

        for iid in all_iids:

            self.order_checkboxes[iid] = new_mark

            self.tree.item(iid, image=row_img)

        self.status_var.set(f"{'Selected' if self.master_checked else 'Deselected'} all {len(all_iids)} orders.")

    def _toggle_row_checkbox(self, item_id):

        cur = self.order_checkboxes.get(item_id, "☐")

        new_val = "☑" if cur == "☐" else "☐"

        self.order_checkboxes[item_id] = new_val

        new_img = self.chk_checked_img if new_val == "☑" else self.chk_unchecked_img

        self.tree.item(item_id, image=new_img)

        all_iids = self.tree.get_children()

        if all_iids:

            all_checked = all(self.order_checkboxes.get(i, "☐") == "☑" for i in all_iids)

            self.master_checked = all_checked

            m_img = self.chk_master_checked_img if all_checked else self.chk_master_unchecked_img

            self.tree.heading("#0", text=" Order ID ˅", image=m_img, anchor="w")

    def _on_tree_click(self, event):

        col = self.tree.identify_column(event.x)

        row_id = self.tree.identify_row(event.y)

        if not row_id:

            return

        if col == "#0":

            elem = self.tree.identify_element(event.x, event.y)

            if elem in ("Treeitem.image", "image") or event.x <= 40:

                self._toggle_row_checkbox(row_id)

                return "break"

            return

        elif col == "#5":

            # Column 5: 'Make Local'

            vals = self.tree.item(row_id, "values")

            btn_text = vals[4] if len(vals) > 4 else ""

            if "local" in btn_text.lower():

                self._make_single_order_local(row_id)

            return "break"

        elif col == "#6":

            # Column 6: 'Make Online'

            vals = self.tree.item(row_id, "values")

            btn_text = vals[5] if len(vals) > 5 else ""

            if "online" in btn_text.lower():

                self._make_single_order_online(row_id)

            return "break"

        elif col == "#7":

            # Column 7: 'Open'

            vals = self.tree.item(row_id, "values")

            btn_text = vals[6] if len(vals) > 6 else ""

            if "open" in btn_text.lower():

                self.tree.selection_set(row_id)

                self._open_single_order_folder(row_id)

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

                item_text = self.tree.item(iid, "text")

                if item_text:

                    oid = str(item_text).strip().lstrip("#")

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

    def _open_dropbox_folder(self):

        p = self.path_var.get().strip() if hasattr(self, "path_var") else ""

        if p and os.path.isdir(p):

            os.startfile(p)

        else:

            messagebox.showerror("Folder Not Found", "The configured Dropbox folder does not exist.\nPlease configure a valid folder in Settings.", parent=self)

    def _open_settings(self):
        # Acknowledge update indicator on settings button
        if hasattr(self, "settings_btn") and self.settings_btn.winfo_exists():
            t = self.theme
            is_light = (self.theme_name == "light")
            self.settings_btn.configure(
                text="⚙️ Settings",
                fg_color="#FFFFFF" if is_light else "#1E293B",
                hover_color="#F1F5F9" if is_light else "#334155",
                text_color=t["text_main"],
                border_color=t["border"]
            )

        # Focus or deiconify existing Settings dialog cleanly
        dlg = getattr(self, "settings_dialog", None)
        if dlg is not None:
            try:
                if dlg.winfo_exists():
                    dlg.deiconify()
                    dlg.lift()
                    dlg.attributes("-topmost", True)
                    dlg.focus_force()
                    pass
                    return
            except Exception:
                pass
            self.settings_dialog = None

        self.settings_dialog = SettingsDialog(self)
        try:
            self.settings_dialog.lift()
            self.settings_dialog.attributes("-topmost", True)
            self.settings_dialog.focus_force()
            pass
        except Exception:
            pass

    def _set_theme(self, new_theme):
        if new_theme not in BRAND_THEMES:
            return
        self.theme_name = new_theme
        self.config_data["theme"] = self.theme_name
        save_config(self.config_data)
        t = BRAND_THEMES[new_theme]
        self.theme = t
        is_light = (new_theme == "light")

        btn_bg = "#FFFFFF" if is_light else "#1E293B"
        btn_hover = "#F1F5F9" if is_light else "#334155"
        btn_hover_subtle = "#F8FAFC" if is_light else "#334155"

        # 1. Instant CustomTkinter appearance mode switch
        ctk.set_appearance_mode(new_theme)
        self.configure(fg_color=t["bg_canvas"])

        # 2. Update Header Brand Title, Version badge, Tagline & Action Buttons
        if hasattr(self, "app_title_lbl") and self.app_title_lbl.winfo_exists():
            self.app_title_lbl.configure(text_color=t["text_main"])

        if hasattr(self, "app_tagline_lbl") and self.app_tagline_lbl.winfo_exists():
            self.app_tagline_lbl.configure(text_color=t["text_muted"])

        if hasattr(self, "app_ver_lbl") and self.app_ver_lbl.winfo_exists():
            self.app_ver_lbl.configure(
                fg_color=t["primary"],
                text_color="#FFFFFF" if is_light else "#0B1120"
            )

        has_unread = bool(getattr(self, "unread_notifications", 0) > 0)
        has_update = bool(getattr(self, "available_update", None))

        if hasattr(self, "header_update_btn") and self.header_update_btn.winfo_exists():
            self.header_update_btn.configure(
                fg_color=t["primary"],
                hover_color=t["primary_hover"],
                text_color="#FFFFFF" if is_light else "#0B1120"
            )

        if hasattr(self, "settings_btn") and self.settings_btn.winfo_exists():
            s_text = "⚙️ Settings 🔴" if (has_update or has_unread) else "⚙️ Settings"
            self.settings_btn.configure(
                text=s_text,
                fg_color=btn_bg,
                hover_color=btn_hover,
                text_color=t["text_main"],
                border_color=t["border"]
            )

        if hasattr(self, "notification_btn") and self.notification_btn.winfo_exists():
            if not getattr(self, "_is_blinking", False):
                self.notification_btn.configure(
                    fg_color=btn_bg,
                    hover_color=btn_hover,
                    text_color=t["text_muted"],
                    border_color=t["border"]
                )

        if hasattr(self, "leftover_btn") and self.leftover_btn.winfo_exists():
            self.leftover_btn.configure(
                fg_color=btn_bg,
                hover_color=btn_hover,
                text_color=t["success"],
                border_color=t["border"]
            )

        # 3. Update Control Strip Pill Cards and Buttons
        for attr in ["card_vendors", "card_open_dropbox", "card_local"]:
            c = getattr(self, attr, None)
            if c and isinstance(c, ctk.CTkFrame) and c.winfo_exists():
                c.configure(fg_color=t["bg_card"], border_color=t["border"])

        if hasattr(self, "vendor_btn") and self.vendor_btn.winfo_exists():
            self.vendor_btn.configure(
                text_color=t["text_main"],
                hover_color="#F1F5F9" if is_light else "#253349"
            )

        if hasattr(self, "btn_open_dropbox") and self.btn_open_dropbox.winfo_exists():
            self.btn_open_dropbox.configure(
                text_color=t["text_main"],
                hover_color="#F1F5F9" if is_light else "#253349"
            )

        if hasattr(self, "local_metric_lbl") and self.local_metric_lbl.winfo_exists():
            self.local_metric_lbl.configure(text_color=t["success"])

        if hasattr(self, "refresh_local_btn") and self.refresh_local_btn.winfo_exists():
            self.refresh_local_btn.configure(
                text_color=t["text_muted"],
                hover_color="#F1F5F9" if is_light else "#253349"
            )

        if hasattr(self, "card_drive") and self.card_drive.winfo_exists():
            drive_bg = "#BAE6FD" if is_light else "#1E293B"
            drive_border = "#7DD3FC" if is_light else "#334155"
            drive_fg = "#0369A1" if is_light else "#38BDF8"
            self.card_drive.configure(fg_color=drive_bg, border_color=drive_border)
            if hasattr(self, "drive_metric_lbl") and self.drive_metric_lbl.winfo_exists():
                self.drive_metric_lbl.configure(text_color=drive_fg)

        # 4. Update Left Card (Paste Drawer)
        if hasattr(self, "card_left") and self.card_left.winfo_exists():
            self.card_left.configure(fg_color=t["bg_card"], border_color=t["border"])

        if hasattr(self, "paste_title_lbl") and self.paste_title_lbl.winfo_exists():
            self.paste_title_lbl.configure(text_color=t["text_main"])

        if hasattr(self, "count_lbl") and self.count_lbl.winfo_exists():
            self.count_lbl.configure(text_color=t["text_muted"])

        if hasattr(self, "btn_hide_left") and self.btn_hide_left.winfo_exists():
            self.btn_hide_left.configure(text_color=t["text_muted"], border_color=t["border"], hover_color="#F1F5F9" if is_light else "#253349")

        if hasattr(self, "clear_top_btn") and self.clear_top_btn.winfo_exists():
            self.clear_top_btn.configure(text_color=t["text_muted"], border_color=t["border"], hover_color="#F1F5F9" if is_light else "#253349")

        if hasattr(self, "input_text") and self.input_text.winfo_exists():
            self.input_text.configure(
                fg_color=t["bg_input"],
                text_color=t["text_main"],
                border_color=t["border"]
            )

        if hasattr(self, "paste_btn") and self.paste_btn.winfo_exists():
            self.paste_btn.configure(
                fg_color=btn_bg,
                hover_color=btn_hover_subtle,
                text_color=t["text_main"],
                border_color=t["border"]
            )

        if hasattr(self, "btn_clean_dedup") and self.btn_clean_dedup.winfo_exists():
            if getattr(self, "input_cleaned", False):
                self.btn_clean_dedup.configure(fg_color=t["success"], hover_color=t["success_hover"], text_color="#FFFFFF")
            else:
                self.btn_clean_dedup.configure(fg_color=t["danger"], hover_color=t["danger_hover"], text_color="#FFFFFF")

        if hasattr(self, "btn_add_to_sync") and self.btn_add_to_sync.winfo_exists():
            if getattr(self, "input_cleaned", False):
                self.btn_add_to_sync.configure(
                    fg_color=t["primary"],
                    hover_color=t["primary_hover"],
                    text_color="#FFFFFF" if is_light else "#0B1120"
                )
            else:
                self.btn_add_to_sync.configure(
                    fg_color="#1E293B",
                    hover_color=t["primary_hover"],
                    text_color="#FFFFFF" if is_light else "#94A3B8"
                )

        # 5. Update Right Card (Search & Table)
        if hasattr(self, "card_right") and self.card_right.winfo_exists():
            self.card_right.configure(fg_color=t["bg_card"], border_color=t["border"])

        if hasattr(self, "search_box") and self.search_box.winfo_exists():
            self.search_box.configure(fg_color=t["bg_card"], border_color=t["border"])

        if hasattr(self, "search_icon_lbl") and self.search_icon_lbl.winfo_exists():
            self.search_icon_lbl.configure(text_color=t["text_muted"])

        if hasattr(self, "search_entry") and self.search_entry.winfo_exists():
            self.search_entry.configure(text_color=t["text_main"])

        if hasattr(self, "clear_search_btn") and self.clear_search_btn.winfo_exists():
            self.clear_search_btn.configure(text_color=t["text_muted"], hover_color="#F1F5F9" if is_light else "#253349")

        if hasattr(self, "make_online_top_btn") and self.make_online_top_btn.winfo_exists():
            self.make_online_top_btn.configure(fg_color=btn_bg, hover_color=btn_hover_subtle, text_color=t["text_main"], border_color=t["border"])

        if hasattr(self, "btn_scan_local") and self.btn_scan_local.winfo_exists():
            sec_fg = t["secondary_text"] if is_light else t["secondary"]
            self.btn_scan_local.configure(fg_color=btn_bg, hover_color=btn_hover_subtle, text_color=sec_fg, border_color=t["border"])

        if hasattr(self, "btn_clean_dashboard") and self.btn_clean_dashboard.winfo_exists():
            self.btn_clean_dashboard.configure(fg_color=btn_bg, hover_color=btn_hover_subtle, text_color=t["danger"], border_color=t["border"])

        if hasattr(self, "btn_order_review") and self.btn_order_review.winfo_exists():
            self.btn_order_review.configure(fg_color=btn_bg, hover_color=btn_hover_subtle, text_color=t["text_muted"], border_color=t["border"])

        # 6. Update ttk.Treeview in-place
        if hasattr(self, "style"):
            self.style.configure(
                "Custom.Treeview",
                background=t["bg_card"],
                foreground=t["text_main"],
                fieldbackground=t["bg_card"]
            )
            self.style.configure(
                "Custom.Treeview.Heading",
                background="#F8FAFC" if is_light else "#1E293B",
                foreground=t["text_muted"]
            )
            self.style.map(
                "Custom.Treeview",
                background=[("selected", "#EFF6FF" if is_light else "#23334D")],
                foreground=[("selected", "#1E40AF" if is_light else "#38BDF8")]
            )

        self._create_checkbox_icons()
        if hasattr(self, "tree") and self.tree.winfo_exists():
            m_img = self.chk_master_checked_img if getattr(self, "master_checked", False) else self.chk_master_unchecked_img
            self.tree.heading("#0", text=" Order ID ˅", image=m_img, anchor="w")
            self.tree.heading("vendor", text="Vendor", image="", anchor="w")
            for iid in self.tree.get_children():
                chk = self.order_checkboxes.get(iid, "☐")
                row_img = self.chk_checked_img if chk == "☑" else self.chk_unchecked_img
                self.tree.item(iid, image=row_img)
            self.tree.tag_configure("row_local", background=t["status_local_bg"], foreground=t["status_local_fg"])
            self.tree.tag_configure("row_syncing", background=t["status_sync_bg"], foreground=t["status_sync_fg"])
            self.tree.tag_configure("row_online", background=t["status_cloud_bg"], foreground=t["status_cloud_fg"])
            self.tree.tag_configure("row_notfound", background=t["status_notfound_bg"], foreground=t["status_notfound_fg"])

        # 7. Update Context Menu
        if hasattr(self, "context_menu") and self.context_menu:
            try:
                self.context_menu.configure(bg=t["bg_card"], fg=t["text_main"], activebackground=t["primary"])
            except Exception:
                pass

        # 8. Update Bottom Action Dock
        if hasattr(self, "btn_make_local_all") and self.btn_make_local_all.winfo_exists():
            self.btn_make_local_all.configure(
                fg_color=t["action_btn_make_local_bg"],
                hover_color=t["primary_hover"],
                text_color=t["action_btn_make_local_fg"]
            )

        if hasattr(self, "btn_make_online_all") and self.btn_make_online_all.winfo_exists():
            self.btn_make_online_all.configure(
                fg_color=t["action_btn_free_space_bg"],
                hover_color=t["secondary_hover"],
                text_color=t["action_btn_free_space_fg"]
            )

        if hasattr(self, "btn_pause") and self.btn_pause.winfo_exists():
            self.btn_pause.configure(
                fg_color=t["action_btn_pause_bg"],
                text_color=t["action_btn_pause_fg"]
            )

        if hasattr(self, "btn_stop") and self.btn_stop.winfo_exists():
            self.btn_stop.configure(
                fg_color=t["action_btn_stop_bg"],
                text_color=t["action_btn_stop_fg"]
            )

        if hasattr(self, "total_lbl") and self.total_lbl and self.total_lbl.winfo_exists():
            self.total_lbl.configure(text_color=t["text_main"])

        if hasattr(self, "total_progress") and self.total_progress and self.total_progress.winfo_exists():
            self.total_progress.configure(fg_color="#DCE9F5" if is_light else "#253349", progress_color=t["primary"])

        if hasattr(self, "status_pill_lbl") and self.status_pill_lbl.winfo_exists():
            self.status_pill_lbl.configure(text_color=t["text_muted"])

        # 9. Update open SettingsDialog in-place
        if hasattr(self, "settings_dialog") and self.settings_dialog and self.settings_dialog.winfo_exists():
            try:
                self.settings_dialog._apply_dialog_theme(t)
            except Exception:
                pass

    def _open_update_from_header(self):
        if hasattr(self, "available_update") and self.available_update:
            u = self.available_update
            UpdateDialog(
                self,
                latest_tag=u.get("tag", CURRENT_VERSION),
                current_ver=CURRENT_VERSION,
                release_body=u.get("body", "Bug fixes and improvements."),
                download_url=u.get("download_url") or u.get("url") or ""
            )

    def _show_update_available(self, latest_tag, release_body, download_url, silent=False):
        self.available_update = {
            "tag": latest_tag,
            "body": release_body,
            "download_url": download_url,
            "url": download_url
        }
        self.unread_notifications = 1

        t = self.theme
        is_light = (self.theme_name == "light")

        # 1. Show elegant 1-Click Update Pill directly in the Header
        if hasattr(self, "header_update_btn") and self.header_update_btn.winfo_exists():
            self.header_update_btn.configure(
                text=f"🚀 Update Ready: {latest_tag}",
                fg_color=t["primary"],
                hover_color=t["primary_hover"],
                text_color="#FFFFFF" if is_light else "#0B1120"
            )
            self.header_update_btn.pack(side="right", padx=(0, 8), before=self.settings_btn)

        # 2. Update Settings button badge gently without intrusive blinking
        if hasattr(self, "header_update_btn") and self.header_update_btn.winfo_exists():
            self.header_update_btn.configure(
                fg_color=t["primary"],
                hover_color=t["primary_hover"],
                text_color="#FFFFFF" if is_light else "#0B1120"
            )

        if hasattr(self, "settings_btn") and self.settings_btn.winfo_exists():
            self.settings_btn.configure(text="⚙️ Settings 🔴")

        # 3. Synchronize open SettingsDialog if alive
        if hasattr(self, "settings_dialog") and self.settings_dialog and self.settings_dialog.winfo_exists():
            try:
                self.settings_dialog.btn_status.configure(
                    text=f"🚀 Update Available: {latest_tag}",
                    state="normal",
                    fg_color=t["primary"],
                    command=self.settings_dialog._open_update_dialog
                )
            except Exception:
                pass

        if not silent:
            UpdateDialog(self, latest_tag, CURRENT_VERSION, release_body, download_url)
    def _start_notification_blink(self):
        self._is_blinking = True
        self._blink_state = False
        self._run_blink_cycle()

    def _run_blink_cycle(self):
        if not getattr(self, "_is_blinking", False):
            return
        if not hasattr(self, "notification_btn") or not self.notification_btn.winfo_exists():
            return
        self._blink_state = not self._blink_state
        is_light = (getattr(self, "theme_name", "light") == "light")
        if self._blink_state:
            self.notification_btn.configure(
                text="🔔 1",
                fg_color="#EF4444",
                text_color="#FFFFFF"
            )
        else:
            self.notification_btn.configure(
                text="🔔 1",
                fg_color="#FEE2E2" if is_light else "#450A0A",
                text_color="#EF4444"
            )
        self.after(550, self._run_blink_cycle)

    def _stop_notification_blink(self):
        self._is_blinking = False
        is_light = (getattr(self, "theme_name", "light") == "light")
        t = self.theme
        if hasattr(self, "notification_btn") and self.notification_btn.winfo_exists():
            self.notification_btn.configure(
                text="🔔",
                fg_color="#FFFFFF" if is_light else "#1E293B",
                text_color=t["text_muted"]
            )

    def _open_order_review(self):

        OrderReviewDialog(self)

    def _open_local_clean(self):

        LocalCleanDialog(self)

    def _open_notification_center(self):
        self._stop_notification_blink()

        self.unread_notifications = 0

        self._update_notification_badge()

        NotificationCenterDialog(self, available_update=self.available_update)

    def _update_notification_badge(self):

        t = self.theme

        if getattr(self, "unread_notifications", 0) > 0 and self.available_update:

            self.notification_btn.config(

                text="🔔 1",

                bg=t["accent"],

                fg="#000000",

                font=("Segoe UI", 8, "bold")

            )

        else:

            self.notification_btn.config(

                text="🔔",

                bg=t["bg_card"],

                fg=t["text_muted"],

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

            order_info = self.resolved_orders.get(key, {})

            order_id = str(order_info.get("order_id") or str(key).split("_")[0]).lower()

            vendor = str(vals[0]).lower() if len(vals) > 0 else ""

            status = str(vals[1]).lower() if len(vals) > 1 else ""

            if not query or query in order_id or query in vendor or query in status:

                tag = "row_syncing" if "Syncing" in status or "%" in status else ("row_local" if "Local" in status else ("row_notfound" if "Not Found" in status else "row_online"))

                chk = self.order_checkboxes.get(key, "☐")

                chk_img = self.chk_checked_img if chk == "☑" else self.chk_unchecked_img

                self.tree.insert("", "end", iid=key, text=f" #{order_id}", image=chk_img, values=vals, tags=(tag,))

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

                chk_img = self.chk_checked_img if chk == "☑" else self.chk_unchecked_img

                if not self.tree.exists(item_key):

                    row_vals = ("-", "⚠️ Not Found", "0 / 0", "0 B / 0 B", "-", "-", "-")

                    self.tree.insert("", "end", iid=item_key, text=f" #{clean_id}", image=chk_img, values=row_vals, tags=("row_notfound",))

                    self.table_items[item_key] = row_vals

                    info = {"order_id": clean_id, "vendor": "-", "path": None, "status": "⚠️ Not Found", "files": 0, "size_bytes": 0}

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

                    files_disp = f"{local_files} / {total_files}"

                    disp_size = f"{format_bytes(local_bytes)} / {format_bytes(total_size)}"

                    if local_files == total_files and total_files > 0:

                        status_text = "● Local"

                        row_tag = "row_local"

                    elif local_files > 0:

                        status_text = f"⚠️ Local ({local_files}/{total_files})"

                        row_tag = "row_local"

                    else:

                        status_text = "● Cloud Only"

                        row_tag = "row_online"

                    item_key = f"{clean_id}_{vendor}"

                    chk = self.order_checkboxes.get(item_key, "☐")

                    chk_img = self.chk_checked_img if chk == "☑" else self.chk_unchecked_img

                    row_vals = (vendor, status_text, files_disp, disp_size, "📥 Make Local", "☁️ Make Online", "📁 Open")

                    if self.tree.exists(item_key):

                        self.tree.item(item_key, text=f" #{clean_id}", image=chk_img, values=row_vals, tags=(row_tag,))

                    else:

                        self.tree.insert("", "end", iid=item_key, text=f" #{clean_id}", image=chk_img, values=row_vals, tags=(row_tag,))

                    self.table_items[item_key] = row_vals

                    info = {

                        "order_id": clean_id,

                        "vendor": vendor,

                        "path": folder_path,

                        "status": status_text,

                        "files": total_files,

                        "size_bytes": total_size

                    }

                    self.resolved_orders[item_key] = info

                    self.resolved_orders[clean_id] = info

                    self.resolved_orders[f"#{clean_id}"] = info

                    added_count += 1

        total_cnt = len(self.table_items)

        local_cnt = sum(1 for v in self.table_items.values() if any("local" in str(x).lower() for x in (v if isinstance(v, (list, tuple)) else [])))

        if hasattr(self, "total_lbl") and self.total_lbl:

            if total_cnt > 0 and local_cnt > 0:

                self.total_lbl.configure(text=f"Total Orders in Dashboard: {total_cnt} ({local_cnt} Local, {total_cnt - local_cnt} Cloud Only)")

            else:

                self.total_lbl.configure(text=f"Total Orders in Dashboard: {total_cnt}")

        if hasattr(self, "total_progress") and self.total_progress:

            self.total_progress.set(local_cnt / max(total_cnt, 1) if total_cnt > 0 else 0.0)

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

            chk = self.order_checkboxes.get(item_key, "☐")

            chk_img = self.chk_checked_img if chk == "☑" else self.chk_unchecked_img

            tot_f = item["total_files"]

            tot_b_str = format_bytes(item["local_bytes"])

            row_vals = (

                vendor,

                "● Local",

                f"{tot_f} / {tot_f}",

                f"{tot_b_str} / {tot_b_str}",

                "📥 Make Local",

                "☁️ Make Online",

                "📁 Open"

            )

            self.table_items[item_key] = row_vals

            self.tree.insert("", "end", iid=item_key, text=f" #{oid}", image=chk_img, values=row_vals, tags=("row_local",))

            info = {

                "order_id": oid,

                "vendor": vendor,

                "path": item["path"],

                "status": "● Local",

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

        if hasattr(self, "total_lbl") and self.total_lbl:

            self.total_lbl.configure(text=f"Total Orders in Dashboard: {len(found_items)} ({len(found_items)} Local • Ready for QC)")

        if hasattr(self, "total_progress") and self.total_progress:

            self.total_progress.set(1.0 if found_items else 0.0)

    def _get_order_info(self, item_id):
        """
        Reliably resolves order metadata (path, order_id, vendor, files, size)
        from memory or filesystem using item_id, row values, and Dropbox root.
        """
        info = self.resolved_orders.get(item_id)
        if not info or not info.get("path") or not os.path.isdir(info.get("path", "")):
            if self.tree.exists(item_id):
                vals = self.tree.item(item_id, "values")
                item_text = self.tree.item(item_id, "text")
                raw_id = item_text.strip().lstrip("#") if item_text else ""
                clean_id = normalize_order_id(raw_id)
                vendor = str(vals[0]).strip() if vals and len(vals) > 0 else ""
                item_key = f"{clean_id}_{vendor}"
                alt = (
                    self.resolved_orders.get(item_key)
                    or self.resolved_orders.get(clean_id)
                    or self.resolved_orders.get(f"#{clean_id}")
                    or self.resolved_orders.get(raw_id)
                )
                if alt and alt.get("path") and os.path.isdir(alt["path"]):
                    self.resolved_orders[item_id] = alt
                    return alt

                if vendor and vendor != "-":
                    base_path = self.path_var.get()
                    if base_path and os.path.isdir(base_path):
                        candidates = [
                            os.path.join(base_path, vendor, f"#{clean_id}"),
                            os.path.join(base_path, vendor, clean_id),
                            os.path.join(base_path, vendor, f"#{raw_id}"),
                            os.path.join(base_path, vendor, raw_id)
                        ]
                        for cand in candidates:
                            if os.path.isdir(cand):
                                target_p = resolve_target_folder(cand)
                                files_raw = str(vals[2]).strip() if len(vals) > 2 else "0"
                                if "/" in files_raw:
                                    try:
                                        files_cnt = int(files_raw.split("/")[-1].strip())
                                    except Exception:
                                        files_cnt = 0
                                elif files_raw.isdigit():
                                    files_cnt = int(files_raw)
                                else:
                                    files_cnt = 0
                                new_info = {
                                    "order_id": clean_id,
                                    "vendor": vendor,
                                    "path": target_p,
                                    "status": vals[1] if len(vals) > 1 else "● Local",
                                    "files": files_cnt,
                                    "size_bytes": 0
                                }
                                self.resolved_orders[item_id] = new_info
                                self.resolved_orders[item_key] = new_info
                                return new_info
        return info

    def _make_single_order_online(self, item_id):

        info = self._get_order_info(item_id)

        if not info or not info.get("path") or not os.path.isdir(info["path"]):

            messagebox.showwarning("Not Found", "Folder location not found on disk.", parent=self)

            return

        folder_path = info["path"]

        order_id = info.get("order_id", "")

        vendor = info.get("vendor", "")

        file_count = info.get("files", 0)

        # 1. Update row immediately to indicate offloading in progress (zero UI freeze)
        chk = self.order_checkboxes.get(item_id, "☐")
        chk_img = self.chk_checked_img if chk == "☑" else self.chk_unchecked_img

        self.tree.item(item_id, text=f" #{order_id}", image=chk_img, values=(vendor, "⏳ Offloading...", f"0 / {file_count}", "Freeing...", "📥 Make Local", "⏳ Offloading", "📁 Open"), tags=("row_syncing",))

        self.status_var.set(f"☁️ Offloading #{order_id} ({vendor}) to Online-Only...")

        if hasattr(self, "total_lbl") and self.total_lbl:

            self.total_lbl.configure(text=f"Offloading #{order_id} ({vendor}) to Online-Only...")

        def _worker():

            try:

                free_up_space_cfapi(folder_path)

                cur_vals = self.tree.item(item_id, "values")

                raw_sz = cur_vals[3] if len(cur_vals) > 3 and cur_vals[3] not in ("Freeing...", "0 B") else format_bytes(info.get("size_bytes", 0))

                tot_sz_str = raw_sz.split(" / ")[-1].strip() if " / " in raw_sz else raw_sz

                file_sz_str = f"0 B / {tot_sz_str}"

                files_str = f"0 / {file_count}"

                new_vals = (vendor, "● Cloud Only", files_str, file_sz_str, "📥 Make Local", "☁️ Make Online", "📁 Open")

                def _on_done():

                    self.tree.item(item_id, text=f" #{order_id}", image=chk_img, values=new_vals, tags=("row_online",))

                    self.table_items.update({item_id: new_vals})

                    mark_order_history(order_id, vendor, folder_path, "online", file_count, 0)

                    self._update_leftover_badge()

                    self._update_storage_metrics()

                    tot_cnt = len(self.table_items)

                    loc_cnt = sum(1 for v in self.table_items.values() if any("local" in str(x).lower() for x in (v if isinstance(v, (list, tuple)) else [])))

                    if hasattr(self, "total_lbl") and self.total_lbl:

                        self.total_lbl.configure(text=f"Total Orders in Dashboard: {tot_cnt} ({loc_cnt} Local, {tot_cnt - loc_cnt} Cloud Only)")

                    if hasattr(self, "total_progress") and self.total_progress:

                        self.total_progress.set(loc_cnt / max(tot_cnt, 1) if tot_cnt > 0 else 0.0)

                    self.status_var.set(f"☁️ Order #{order_id} ({vendor}) is now Online-Only (0 B on disk).")

                self.after(0, _on_done)

                info["status"] = "● Cloud Only"

                info["size_bytes"] = 0

            except Exception as e:

                self.after(0, lambda: messagebox.showerror("Error", f"Failed to make order online:\n{e}", parent=self))

        threading.Thread(target=_worker, daemon=True).start()

    def _make_single_order_local(self, item_id):

        info = self._get_order_info(item_id)

        if not info or not info.get("path") or not os.path.isdir(info["path"]):

            messagebox.showwarning("Not Found", "Folder location not found on disk.", parent=self)

            return

        folder_path = info["path"]

        order_id = normalize_order_id(str(info.get("order_id", "")))

        vendor = info.get("vendor", "")

        def _worker():

            try:

                chk = self.order_checkboxes.get(item_id, "☐")

                chk_img = self.chk_checked_img if chk == "☑" else self.chk_unchecked_img

                file_list, total_size = collect_folder_files(folder_path)

                if order_id in self.order_file_whitelists:

                    allowed = self.order_file_whitelists[order_id]

                    file_list = [fp for fp in file_list if fp in allowed]

                    total_size = sum(os.path.getsize(fp) for fp in file_list if os.path.exists(fp))

                total_files = len(file_list)

                total_sz_str = format_bytes(total_size)

                init_files = f"0 / {total_files}"

                init_size = f"0 B / {total_sz_str}"

                self.after(0, lambda: self.tree.item(
                    item_id,
                    text=f" #{order_id}",
                    image=chk_img,
                    values=(vendor, "● Syncing 0.0%", init_files, init_size, "⏳ Syncing", "☁️ Make Online", "📁 Open"),
                    tags=("row_syncing",)
                ))

                self.status_var.set(f"⏳ Syncing order #{order_id} ({vendor})...")

                cmd = f'attrib +P -U "{folder_path}\\*.*" /s & attrib +P -U "{folder_path}" /d'

                subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                completed_files = 0
                downloaded_bytes = 0
                bytes_lock = threading.Lock()
                last_ui_time = [0.0]

                def on_chunk(bytes_read):
                    nonlocal downloaded_bytes
                    with bytes_lock:
                        downloaded_bytes = min(downloaded_bytes + bytes_read, total_size)
                        now = time.time()
                        if now - last_ui_time[0] < 0.04 and downloaded_bytes < total_size:
                            return
                        last_ui_time[0] = now
                        cur_b = downloaded_bytes
                        cur_f = completed_files
                    pct = (cur_b / max(total_size, 1)) * 100.0
                    if pct > 99.9 and cur_b < total_size:
                        pct = 99.9
                    prog_text = f"● Syncing {pct:.1f}%"
                    files_prog = f"{cur_f} / {total_files}"
                    size_prog = f"{format_bytes(cur_b)} / {total_sz_str}"
                    cur_vals = (vendor, prog_text, files_prog, size_prog, "⏳ Syncing", "☁️ Make Online", "📁 Open")
                    self.after(0, lambda r=cur_vals, p=prog_text, f=files_prog, s=size_prog: [
                        self.tree.item(
                            item_id,
                            text=f" #{order_id}",
                            image=chk_img,
                            values=r,
                            tags=("row_syncing",)
                        ),
                        self.table_items.update({item_id: r}),
                        self.status_var.set(f"⚡ Syncing #{order_id} ({f} files • {s} - {p.replace('● ', '')})")
                    ])

                workers = min(8, max(total_files, 1))

                if file_list:

                    with ThreadPoolExecutor(max_workers=workers) as executor:

                        futures = {executor.submit(_hydrate_single_file, fp, on_chunk): fp for fp in file_list}

                        for fut in as_completed(futures):

                            with bytes_lock:
                                completed_files += 1
                                cur_f = completed_files
                                cur_b = downloaded_bytes

                            pct = (cur_b / max(total_size, 1)) * 100.0
                            if pct > 99.9 and completed_files < total_files:
                                pct = 99.9

                            prog_text = f"● Syncing {pct:.1f}%"

                            files_prog = f"{cur_f} / {total_files}"

                            size_prog = f"{format_bytes(cur_b)} / {total_sz_str}"

                            cur_vals = (vendor, prog_text, files_prog, size_prog, "⏳ Syncing", "☁️ Make Online", "📁 Open")

                            self.after(0, lambda r=cur_vals, p=prog_text, f=files_prog, s=size_prog: [
                                self.tree.item(
                                    item_id,
                                    text=f" #{order_id}",
                                    image=chk_img,
                                    values=r,
                                    tags=("row_syncing",)
                               ),
                                self.table_items.update({item_id: r}),
                                self.status_var.set(f"⚡ Syncing #{order_id} ({f} files • {s} - {p.replace('● ', '')})")
                            ])

                status_text = "● Local"

                final_files = f"{total_files} / {total_files}"

                final_size = f"{total_sz_str} / {total_sz_str}"

                new_vals = (vendor, status_text, final_files, final_size, "📥 Make Local", "☁️ Make Online", "📁 Open")

                def _on_local_done():

                    self.tree.item(item_id, text=f" #{order_id}", image=chk_img, values=new_vals, tags=("row_local",))

                    self.table_items.update({item_id: new_vals})

                    info["status"] = status_text

                    info["size_bytes"] = total_size

                    info["files"] = len(file_list)

                    mark_order_history(order_id, vendor, folder_path, "local", len(file_list), total_size)

                    self._update_leftover_badge()

                    self._update_storage_metrics()

                    tot_cnt = len(self.table_items)

                    loc_cnt = sum(1 for v in self.table_items.values() if any("local" in str(x).lower() for x in (v if isinstance(v, (list, tuple)) else [])))

                    if hasattr(self, "total_lbl") and self.total_lbl:

                        self.total_lbl.configure(text=f"Total Orders in Dashboard: {tot_cnt} ({loc_cnt} Local, {tot_cnt - loc_cnt} Cloud Only)")

                    if hasattr(self, "total_progress") and self.total_progress:

                        self.total_progress.set(loc_cnt / max(tot_cnt, 1) if tot_cnt > 0 else 0.0)

                    self.status_var.set(f"✅ Order #{order_id} ({vendor}) is now Local ({format_bytes(total_size)}).")

                self.after(0, _on_local_done)

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

        def _worker():

            freed_count = 0

            for item_id in target_iids:

                info = self._get_order_info(item_id)

                if not info or not info.get("path") or not os.path.isdir(info["path"]):

                    continue

                folder_path = info["path"]

                order_id = normalize_order_id(str(info.get("order_id", "")))

                vendor = info.get("vendor", "")

                file_count = info.get("files", 0)

                chk = self.order_checkboxes.get(item_id, "☐")

                chk_img = self.chk_checked_img if chk == "☑" else self.chk_unchecked_img

                self.after(0, lambda iid=item_id, img=chk_img, oid=order_id, v=vendor, fc=file_count: self.tree.item(iid, text=f" #{oid}", image=img, values=(v, "⏳ Offloading...", f"0 / {fc}", "Freeing...", "📥 Make Local", "⏳ Offloading", "📁 Open"), tags=("row_syncing",)))

                try:

                    free_up_space_cfapi(folder_path)

                    status_text = "● Cloud Only"

                    cur_vals = self.tree.item(item_id, "values")

                    raw_sz = cur_vals[3] if len(cur_vals) > 3 and cur_vals[3] not in ("Freeing...", "0 B") else format_bytes(info.get("size_bytes", 0))

                    tot_sz_str = raw_sz.split(" / ")[-1].strip() if " / " in raw_sz else raw_sz

                    file_sz_str = f"0 B / {tot_sz_str}"

                    files_str = f"0 / {file_count}"

                    new_vals = (vendor, status_text, files_str, file_sz_str, "📥 Make Local", "☁️ Make Online", "📁 Open")

                    self.after(0, lambda iid=item_id, img=chk_img, oid=order_id, vals=new_vals: [

                        self.tree.item(iid, text=f" #{oid}", image=img, values=vals, tags=("row_online",)),

                        self.table_items.update({iid: vals})

                    ])

                    info["status"] = status_text

                    mark_order_history(order_id, vendor, folder_path, "online", file_count, 0)

                    freed_count += 1

                except Exception:

                    pass

            def _on_all_freed():

                self._update_leftover_badge()

                self._update_storage_metrics()

                tot_cnt = len(self.table_items)

                loc_cnt = sum(1 for v in self.table_items.values() if any("local" in str(x).lower() for x in (v if isinstance(v, (list, tuple)) else [])))

                if hasattr(self, "total_lbl") and self.total_lbl:

                    self.total_lbl.configure(text=f"Total Orders in Dashboard: {tot_cnt} ({loc_cnt} Local, {tot_cnt - loc_cnt} Cloud Only)")

                if hasattr(self, "total_progress") and self.total_progress:

                    self.total_progress.set(loc_cnt / max(tot_cnt, 1) if tot_cnt > 0 else 0.0)

                self.status_var.set(f"☁️ Made {freed_count} order(s) Online-Only. Disk space freed!")

            self.after(0, _on_all_freed)

            if freed_count > 0:

                self.after(0, lambda: messagebox.showinfo("Space Freed", f"Successfully made {freed_count} order(s) Online-Only!\nDisk space has been freed.", parent=self))

        threading.Thread(target=_worker, daemon=True).start()

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

            item_text = self.tree.item(iid, "text")

            if item_text:

                orders_to_sync.append(item_text.strip().lstrip("#"))

            else:

                info = self.resolved_orders.get(iid)

                if info and info.get("order_id"):

                    orders_to_sync.append(info["order_id"])

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

        def _worker():

            freed = 0

            for iid in all_iids:

                info = self._get_order_info(iid)

                if info and info.get("path") and os.path.isdir(info["path"]):

                    chk = self.order_checkboxes.get(iid, "☐")

                    chk_img = self.chk_checked_img if chk == "☑" else self.chk_unchecked_img

                    self.after(0, lambda i=iid, img=chk_img, inf=info: self.tree.item(i, text=f" #{inf.get('order_id')}", image=img, values=(inf.get("vendor"), "⏳ Offloading...", f"0 / {inf.get('files', 0)}", "Freeing...", "📥 Make Local", "⏳ Offloading", "📁 Open"), tags=("row_syncing",)))

                    try:

                        free_up_space_cfapi(info["path"])

                        cur_vals = self.tree.item(i, "values")

                        raw_sz = cur_vals[3] if len(cur_vals) > 3 and cur_vals[3] not in ("Freeing...", "0 B") else format_bytes(info.get("size_bytes", 0))

                        tot_sz_str = raw_sz.split(" / ")[-1].strip() if " / " in raw_sz else raw_sz

                        file_sz_str = f"0 B / {tot_sz_str}"

                        files_str = f"0 / {info.get('files', 0)}"

                        new_vals = (info.get("vendor"), "● Cloud Only", files_str, file_sz_str, "📥 Make Local", "☁️ Make Online", "📁 Open")

                        self.after(0, lambda i=iid, img=chk_img, oid=info.get("order_id"), vals=new_vals: [

                            self.tree.item(i, text=f" #{oid}", image=img, values=vals, tags=("row_online",)),

                            self.table_items.update({i: vals})

                        ])

                        info["status"] = "● Cloud Only"

                        mark_order_history(info.get("order_id"), info.get("vendor"), info["path"], "online", info.get("files", 0), 0)

                        freed += 1

                    except Exception:

                        pass

            def _on_all_freed_batch():

                self._update_leftover_badge()

                self._update_storage_metrics()

                tot_cnt = len(self.table_items)

                loc_cnt = sum(1 for v in self.table_items.values() if any("local" in str(x).lower() for x in (v if isinstance(v, (list, tuple)) else [])))

                if hasattr(self, "total_lbl") and self.total_lbl:

                    self.total_lbl.configure(text=f"Total Orders in Dashboard: {tot_cnt} ({loc_cnt} Local, {tot_cnt - loc_cnt} Cloud Only)")

                if hasattr(self, "total_progress") and self.total_progress:

                    self.total_progress.set(loc_cnt / max(tot_cnt, 1) if tot_cnt > 0 else 0.0)

                self.status_var.set(f"Made {freed} order(s) Online-Only.")

            self.after(0, _on_all_freed_batch)

        threading.Thread(target=_worker, daemon=True).start()

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

        if hasattr(self, "total_progress") and self.total_progress:

            self.total_progress.set(0.0)

        if hasattr(self, "total_lbl") and self.total_lbl:

            self.total_lbl.configure(text=f"Total Progress: 0% (0 / {total_orders} Orders)")

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

            overall_frac = i / max(total_orders, 1)

            pct = overall_frac * 100.0

            if hasattr(self, "total_lbl") and self.total_lbl:

                self.total_lbl.configure(text=f"Total Progress: {pct:.1f}% ({i} / {total_orders} Orders)")

            if hasattr(self, "total_progress") and self.total_progress:

                self.total_progress.set(overall_frac)

            self.status_var.set(f"Processing #{order_id} ({i+1}/{total_orders})...")

            matches = vendor_index.get(clean_id, [])

            if not matches and selected_v and len(selected_v) < len(self.detected_vendors):

                if full_vendor_index is None:

                    full_vendor_index = build_vendor_index(base_path, selected_vendors=None)

                matches = full_vendor_index.get(clean_id, [])

            if not matches:

                status_text = "⚠️ Not Found"

                item_key = f"{order_id}_notfound"

                chk = self.order_checkboxes.get(item_key, "☐")

                chk_img = self.chk_checked_img if chk == "☑" else self.chk_unchecked_img

                row_vals = ("-", status_text, "0 / 0", "0 B / 0 B", "-", "-", "-")

                self.resolved_orders[item_key] = {"order_id": order_id, "vendor": "-", "path": None, "status": status_text, "files": 0, "size_bytes": 0}

                self.resolved_orders[order_id] = self.resolved_orders[item_key]

                self.table_items[item_key] = row_vals

                if self.tree.exists(item_key):

                    self.tree.item(item_key, text=f" #{order_id}", image=chk_img, values=row_vals, tags=("row_notfound",))

                else:

                    self.tree.insert("", "end", iid=item_key, text=f" #{order_id}", image=chk_img, values=row_vals, tags=("row_notfound",))

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

                    chk_img = self.chk_checked_img if chk == "☑" else self.chk_unchecked_img

                    total_sz_str = format_bytes(total_size)

                    init_files = f"0 / {total_files}"

                    init_size = f"0 B / {total_sz_str}"

                    row_vals = (vendor, "● Syncing 0.0%", init_files, init_size, "⏳ Syncing", "☁️ Make Online", "📁 Open")

                    self.table_items[item_key] = row_vals

                    if self.tree.exists(item_key):

                        self.tree.item(item_key, text=f" #{order_id}", image=chk_img, values=row_vals, tags=("row_syncing",))

                    else:

                        self.tree.insert("", "end", iid=item_key, text=f" #{order_id}", image=chk_img, values=row_vals, tags=("row_syncing",))

                    self.tree.see(item_key)

                    try:

                        cmd = f'attrib +P -U "{folder_path}\\*.*" /s & attrib +P -U "{folder_path}" /d'

                        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        completed_files = 0
                        downloaded_bytes = 0
                        bytes_lock = threading.Lock()
                        last_ui_time = [0.0]

                        def on_chunk(bytes_read):
                            nonlocal downloaded_bytes
                            with bytes_lock:
                                downloaded_bytes = min(downloaded_bytes + bytes_read, total_size)
                                now = time.time()
                                if now - last_ui_time[0] < 0.04 and downloaded_bytes < total_size:
                                    return
                                last_ui_time[0] = now
                                cur_b = downloaded_bytes
                                cur_f = completed_files
                            s_pct = (cur_b / max(total_size, 1)) * 100.0
                            if s_pct > 99.9 and cur_b < total_size:
                                s_pct = 99.9
                            prog_text = f"● Syncing {s_pct:.1f}%"
                            files_prog = f"{cur_f} / {total_files}"
                            size_prog = f"{format_bytes(cur_b)} / {total_sz_str}"
                            cur_vals = (vendor, prog_text, files_prog, size_prog, "⏳ Syncing", "☁️ Make Online", "📁 Open")
                            overall_frac = (i + (cur_b / max(total_size, 1))) / max(total_orders, 1)
                            overall_pct = overall_frac * 100.0
                            self.after(0, lambda r=cur_vals, p=prog_text, b=size_prog, f=files_prog, pct_val=s_pct, o_pct=overall_pct, o_frac=overall_frac: [
                                self.tree.item(item_key, values=r),
                                self.table_items.update({item_key: r}),
                                self.status_var.set(f"⚡ Hydrating #{order_id} ({f} files • {b} - {pct_val:.1f}%) • Parallel sync active"),
                                self.total_progress.set(o_frac) if hasattr(self, "total_progress") and self.total_progress else None,
                                self.total_lbl.configure(text=f"Total Progress: {o_pct:.1f}% (Order {i+1}/{total_orders} • #{order_id} {pct_val:.1f}%)") if hasattr(self, "total_lbl") and self.total_lbl else None
                            ])

                        if file_list:

                            workers = min(8, len(file_list))

                            with ThreadPoolExecutor(max_workers=workers) as executor:

                                futures = {executor.submit(_hydrate_single_file, fp, on_chunk): fp for fp in file_list}

                                for fut in as_completed(futures):

                                    if self.stop_requested:

                                        executor.shutdown(wait=False, cancel_futures=True)

                                        break

                                    self.pause_event.wait()

                                    if self.stop_requested:

                                        executor.shutdown(wait=False, cancel_futures=True)

                                        break

                                    with bytes_lock:
                                        completed_files += 1
                                        cur_f = completed_files
                                        cur_b = downloaded_bytes

                                    s_pct = (cur_b / max(total_size, 1)) * 100.0
                                    if s_pct > 99.9 and completed_files < total_files:
                                        s_pct = 99.9

                                    prog_text = f"● Syncing {s_pct:.1f}%"

                                    files_prog = f"{cur_f} / {total_files}"

                                    size_prog = f"{format_bytes(cur_b)} / {total_sz_str}"

                                    cur_vals = (vendor, prog_text, files_prog, size_prog, "⏳ Syncing", "☁️ Make Online", "📁 Open")

                                    self.tree.item(item_key, text=f" #{order_id}", image=chk_img, values=cur_vals, tags=("row_syncing",))
                                    self.table_items.update({item_key: cur_vals})

                                    overall_frac = (i + (cur_b / max(total_size, 1))) / max(total_orders, 1)

                                    overall_pct = overall_frac * 100.0

                                    if hasattr(self, "total_progress") and self.total_progress:

                                        self.total_progress.set(overall_frac)

                                    if hasattr(self, "total_lbl") and self.total_lbl:

                                        self.total_lbl.configure(text=f"Total Progress: {overall_pct:.1f}% (Order {i+1}/{total_orders} • #{order_id} {s_pct:.1f}%)")

                                    self.status_var.set(f"⚡ Hydrating #{order_id} ({files_prog} files • {size_prog} - {s_pct:.1f}%) • Parallel sync active")

                        status_text = "● Local"

                        success_count += 1

                        mark_order_history(order_id, vendor, folder_path, "local", total_files, total_size)

                    except Exception as e:

                        status_text = f"⚠️ Error: {str(e)[:15]}"

                    final_files = f"{total_files} / {total_files}" if "Local" in status_text else f"0 / {total_files}"

                    final_size = f"{total_sz_str} / {total_sz_str}" if "Local" in status_text else f"0 B / {total_sz_str}"

                    final_vals = (vendor, status_text, final_files, final_size, "📥 Make Local", "☁️ Make Online", "📁 Open")

                    self.table_items[item_key] = final_vals

                    self.tree.item(item_key, text=f" #{order_id}", image=chk_img, values=final_vals, tags=("row_local" if "Local" in status_text else "row_online",))

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

            if hasattr(self, "total_lbl") and self.total_lbl:

                self.total_lbl.configure(text=f"Total Orders in Dashboard: {total_orders} ({success_count} Local • Ready for QC)")

            if hasattr(self, "total_progress") and self.total_progress:

                self.total_progress.set(1.0)

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

            used_pct = int(100 - free_pct)

            if hasattr(self, "drive_metric_lbl"):

                self.drive_metric_lbl.config(

                    text=f"Drive {drive_letter}: {free_str} / {total_str} ({free_pct}% free)"

                )

            if hasattr(self, "drive_progress"):

                self.drive_progress["maximum"] = 100

                self.drive_progress["value"] = used_pct

            count, total_bytes, size_str = get_tracked_local_storage_stats()

            if hasattr(self, "local_metric_lbl"):

                fg_color = self.theme["danger"] if count > 0 else self.theme["success"]

                self.local_metric_lbl.config(

                    text=f"● Local QC Orders: {count} ({size_str} on disk)",

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

            self._open_single_order_folder(row_id)

    def _open_selected_folder(self):

        selected = self.tree.selection()

        if not selected:

            messagebox.showinfo("Select Order", "Please select an order from the list first.", parent=self)

            return

        self._open_single_order_folder(selected[0])

    def _open_single_order_folder(self, item_id):

        if not item_id:

            return

        item = self.tree.item(item_id)

        info = self._get_order_info(item_id)

        if info and info.get("path") and os.path.isdir(info["path"]):

            try:

                os.startfile(info["path"])

                order_name = info.get("order_id", "")

                self.status_var.set(f"📂 Opened folder for order #{order_name}.")

            except Exception as e:

                messagebox.showerror("Error", f"Failed to open folder:\n{e}", parent=self)

        else:

            item_text = self.tree.item(item_id, "text")

            order_name = item_text.strip().lstrip("#") if item_text else "selected"

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

        t = self.theme

        if count > 0:

            total_b = sum(it.get("size_bytes", 0) for it in tracked)

            self.leftover_btn.config(

                text=f"🕒 History: {count} Local",

                fg=t["danger"]

            )

        else:

            self.leftover_btn.config(

                text="🕒 History: 0 Local",

                fg=t["success"]

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

