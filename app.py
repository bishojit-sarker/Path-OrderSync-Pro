import os
import sys
import json
import re
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

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")
CURRENT_VERSION = "v1.4.0"
GITHUB_REPO = "bishojit-sarker/Smart-Dropbox-QC-Batch-Loader"

# Windows Cloud Filter Attributes
FILE_ATTRIBUTE_PINNED = 0x80000
FILE_ATTRIBUTE_UNPINNED = 0x100000
FILE_ATTRIBUTE_REPARSE_POINT = 0x400

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

def check_for_updates(parent=None, silent=True):
    def _worker():
        try:
            req = urllib.request.Request(
                f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest",
                headers={"User-Agent": "QC-Batch-Loader-Updater"}
            )
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            latest_tag = data.get("tag_name", "").strip()
            if not latest_tag:
                return

            latest_ver = parse_version_tuple(latest_tag)
            cur_ver = parse_version_tuple(CURRENT_VERSION)

            # Strictly require GitHub version to be newer than current version
            if latest_ver <= cur_ver:
                if not silent and parent:
                    parent.after(0, lambda: messagebox.showinfo("Up to Date", f"You are using the latest version ({CURRENT_VERSION})!"))
                return

            download_url = None
            for asset in data.get("assets", []):
                if asset.get("name") == "QC_Batch_Loader.exe":
                    download_url = asset.get("browser_download_url")
                    break

            if not download_url:
                return

            def _prompt():
                body = data.get("body", "Bug fixes and performance improvements.")
                msg = (
                    f"A new version ({latest_tag}) is available!\n"
                    f"Your current version: {CURRENT_VERSION}\n\n"
                    f"What's New:\n{body[:300]}\n\n"
                    "Would you like to automatically update now?"
                )
                ans = messagebox.askyesno("Update Available", msg)
                if ans:
                    _perform_update(download_url, latest_tag, parent)

            if parent:
                parent.after(0, _prompt)
        except Exception as e:
            if not silent and parent:
                parent.after(0, lambda: messagebox.showerror("Update Check Failed", f"Could not check for updates:\n{e}"))

    threading.Thread(target=_worker, daemon=True).start()

def _perform_update(download_url, latest_tag, parent=None):
    try:
        cur_exe = sys.executable
        if not cur_exe.lower().endswith("qc_batch_loader.exe"):
            webbrowser.open(download_url)
            return

        old_exe = cur_exe + ".old"
        new_exe_tmp = cur_exe + ".tmp"

        if parent:
            parent.status_var.set(f"Downloading update {latest_tag} from GitHub...")

        urllib.request.urlretrieve(download_url, new_exe_tmp)

        if os.path.exists(old_exe):
            try:
                os.remove(old_exe)
            except Exception:
                pass

        os.rename(cur_exe, old_exe)
        os.rename(new_exe_tmp, cur_exe)

        messagebox.showinfo("Update Complete", f"Successfully updated to {latest_tag}! The application will now restart.")
        subprocess.Popen([cur_exe])
        os._exit(0)
    except Exception as e:
        messagebox.showerror("Update Error", f"Failed to complete automatic update:\n{e}")

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
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                saved_path = cfg.get("dropbox_path")
                if saved_path and os.path.isdir(saved_path):
                    return cfg
        except Exception:
            pass
    return {"dropbox_path": detected_path}

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
    """Streams 1 KB of the file to force Dropbox to hydrate it locally."""
    try:
        with open(fp, "rb") as fh:
            fh.read(1024)
        return True
    except Exception:
        return False


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


class QCBatchLoaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"⚡ Smart Dropbox QC Batch Loader {CURRENT_VERSION}")
        self.geometry("950x780")
        self.minsize(820, 620)

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

        # Stores lookup details: {row_key: {"order_id": ..., "vendor": ..., "path": ..., "status": ..., "files": ..., "size_bytes": ...}}
        self.resolved_orders = {}
        # Stores table rows for live search filter: {row_key: (values_tuple)}
        self.table_items = {}

        self.search_var = tk.StringVar(value="")

        self._scan_vendors()
        self._setup_style()
        self._create_widgets()
        self._update_order_count()
        self._update_leftover_badge()
        self._update_storage_metrics()

        # Check for updates in background 2.5s after launch
        self.after(2500, lambda: check_for_updates(self, silent=True))

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
        elif sel_count == total:
            self.vendor_btn.config(text=f"🏢 Vendors: All ({total}) ▼", bg="#252538", fg="#f8fafc")
        elif sel_count == 1:
            single = next(iter(self.selected_vendors))
            self.vendor_btn.config(text=f"🏢 Vendor: {single} ▼", bg="#0284c7", fg="#ffffff")
        elif sel_count == 0:
            self.vendor_btn.config(text="🏢 Vendors: None (0) ⚠️ ▼", bg="#ef4444", fg="#ffffff")
        else:
            names = sorted(list(self.selected_vendors))
            short = f"{names[0]}, {names[1]}" if len(names) == 2 else f"{sel_count} Selected ({names[0]}, {names[1]}...)"
            self.vendor_btn.config(text=f"🏢 Vendors: {short} ▼", bg="#4f46e5", fg="#ffffff")

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

        def select_all():
            self.selected_vendors.update(self.detected_vendors)
            for v_name, var in self.vendor_check_vars.items():
                var.set(True)
            self._update_vendor_btn_label()
            update_status_label()
            self._save_selected_vendors()

        def select_none():
            self.selected_vendors.clear()
            for v_name, var in self.vendor_check_vars.items():
                var.set(False)
            self._update_vendor_btn_label()
            update_status_label()
            self._save_selected_vendors()

        def rescan():
            self._scan_vendors(keep_selection=True)
            self._close_vendor_popup()
            self._toggle_vendor_popup()

        tk.Button(act_frame, text="All", command=select_all, bg="#374151", fg="white", relief="flat", font=("Segoe UI", 8), padx=6).pack(side="left", padx=(0, 2))
        tk.Button(act_frame, text="None", command=select_none, bg="#374151", fg="white", relief="flat", font=("Segoe UI", 8), padx=6).pack(side="left", padx=2)
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

        self.vendor_check_vars.clear()
        self.vendor_row_widgets.clear()

        for v in self.detected_vendors:
            row = tk.Frame(scroll_frame, bg="#181825")
            row.pack(fill="x", pady=1)
            self.vendor_row_widgets[v] = row

            var = tk.BooleanVar(value=(v in self.selected_vendors))
            self.vendor_check_vars[v] = var

            def on_toggle(v_name=v, v_var=var):
                if v_var.get():
                    self.selected_vendors.add(v_name)
                else:
                    self.selected_vendors.discard(v_name)
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

            def select_only(v_name=v):
                self.selected_vendors.clear()
                self.selected_vendors.add(v_name)
                for name, chk in self.vendor_check_vars.items():
                    chk.set(name == v_name)
                self._update_vendor_btn_label()
                update_status_label()
                self._save_selected_vendors()

            only_btn = tk.Button(
                row, text="Only", command=select_only,
                bg="#374151", fg="#93c5fd", activebackground="#3b82f6", activeforeground="white",
                relief="flat", font=("Segoe UI", 7, "bold"), padx=4
            )
            only_btn.pack(side="right", padx=2)

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
        top_frame.pack(fill="x", padx=16, pady=(12, 6))

        title_lbl = tk.Label(
            top_frame,
            text="⚡ Smart Dropbox QC Batch Loader",
            font=("Segoe UI", 15, "bold"),
            bg=self.bg_color,
            fg="#60a5fa"
        )
        title_lbl.pack(side="left")

        version_badge = tk.Label(
            top_frame,
            text=CURRENT_VERSION,
            font=("Segoe UI", 8, "bold"),
            bg="#3b82f6",
            fg="white",
            padx=6,
            pady=1
        )
        version_badge.pack(side="left", padx=8, pady=(4, 0))

        subtitle_lbl = tk.Label(
            top_frame,
            text="Automated Multi-Vendor Offline Sync & Space Cleaner",
            font=("Segoe UI", 9),
            bg=self.bg_color,
            fg=self.text_muted
        )
        subtitle_lbl.pack(side="left", padx=6, pady=(4, 0))

        update_btn = tk.Button(
            top_frame,
            text="🔄 Check Updates",
            command=lambda: check_for_updates(self, silent=False),
            bg="#252538",
            fg="#93c5fd",
            activebackground="#3b82f6",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8),
            cursor="hand2",
            padx=8,
            pady=2
        )
        update_btn.pack(side="right")

        self.leftover_btn = tk.Button(
            top_frame,
            text="📜 History: 0 Local (Clean)",
            command=self._open_history_tracker,
            bg="#252538",
            fg="#10b981",
            activebackground="#3b82f6",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=10,
            pady=2
        )
        self.leftover_btn.pack(side="right", padx=(0, 6))

        # 2. Dropbox Path Bar
        path_card = tk.Frame(self, bg=self.card_bg, bd=1, relief="solid")
        path_card.pack(fill="x", padx=16, pady=(4, 2))

        path_lbl = tk.Label(path_card, text="📁 Dropbox Root:", bg=self.card_bg, fg=self.text_main, font=("Segoe UI", 9, "bold"))
        path_lbl.pack(side="left", padx=(10, 6), pady=6)

        self.path_var = tk.StringVar(value=self.config_data.get("dropbox_path") or DEFAULT_DROPBOX_PATH)
        path_entry = tk.Entry(
            path_card,
            textvariable=self.path_var,
            bg="#181825",
            fg="#f8fafc",
            insertbackground="#ffffff",
            relief="flat",
            font=("Segoe UI", 9)
        )
        path_entry.pack(side="left", fill="x", expand=True, padx=4, pady=6, ipady=3)

        browse_btn = tk.Button(
            path_card,
            text="Browse...",
            command=self._browse_dropbox_path,
            bg="#3b82f6",
            fg="white",
            activebackground="#2563eb",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=10
        )
        browse_btn.pack(side="right", padx=10, pady=6)

        # 3. Live Storage Metrics & Vendor Filter Bar
        metrics_card = tk.Frame(self, bg=self.card_bg, bd=1, relief="solid")
        metrics_card.pack(fill="x", padx=16, pady=(2, 4))

        # Vendor Multi-Select Dropdown Button
        self.vendor_btn = tk.Button(
            metrics_card,
            text="🏢 Vendors: All ▼",
            command=self._toggle_vendor_popup,
            bg="#252538",
            fg="#f8fafc",
            activebackground="#374151",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=10,
            pady=3
        )
        self.vendor_btn.pack(side="left", padx=(10, 8), pady=4)
        self._update_vendor_btn_label()

        self.drive_metric_lbl = tk.Label(
            metrics_card,
            text="💾 Drive Free Space: Calculating...",
            bg=self.card_bg,
            fg="#93c5fd",
            font=("Segoe UI", 9, "bold")
        )
        self.drive_metric_lbl.pack(side="left", padx=(8, 12), pady=5)

        self.local_metric_lbl = tk.Label(
            metrics_card,
            text="📦 Local QC Orders: 0 B (0 Orders on disk)",
            bg=self.card_bg,
            fg="#34d399",
            font=("Segoe UI", 9, "bold")
        )
        self.local_metric_lbl.pack(side="left", padx=4, pady=5)

        refresh_metric_btn = tk.Button(
            metrics_card,
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
        refresh_metric_btn.pack(side="right", padx=(0, 10), pady=4)

        # 4. Main Split Panes (Input on Left, Table on Right)
        paned = tk.PanedWindow(self, orient="horizontal", bg=self.bg_color, bd=0, sashwidth=4)
        paned.pack(fill="both", expand=True, padx=16, pady=4)

        # Left Pane: Order ID Input
        left_frame = tk.Frame(paned, bg=self.card_bg, bd=1, relief="solid")
        paned.add(left_frame, minsize=270, width=290)

        left_header = tk.Frame(left_frame, bg=self.card_bg)
        left_header.pack(fill="x", padx=10, pady=(8, 4))

        tk.Label(left_header, text="📋 Paste Order IDs:", bg=self.card_bg, fg=self.text_main, font=("Segoe UI", 9, "bold")).pack(side="left")
        self.count_lbl = tk.Label(left_header, text="0 orders", bg=self.card_bg, fg=self.text_muted, font=("Segoe UI", 8))
        self.count_lbl.pack(side="right")

        self.input_text = tk.Text(
            left_frame,
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
        self.input_text.bind("<KeyRelease>", lambda e: self._update_order_count())

        # Buttons below text input
        btn_row_left = tk.Frame(left_frame, bg=self.card_bg)
        btn_row_left.pack(fill="x", padx=10, pady=(4, 8))

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

        dedup_btn = tk.Button(
            btn_row_left,
            text="🧹 Clean & Deduplicate",
            command=self._clean_and_deduplicate,
            bg="#6366f1",
            fg="white",
            activebackground="#4f46e5",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=6,
            pady=2
        )
        dedup_btn.pack(side="right")

        # Right Pane: Order Status Table
        right_frame = tk.Frame(paned, bg=self.card_bg, bd=1, relief="solid")
        paned.add(right_frame, minsize=480)

        right_header = tk.Frame(right_frame, bg=self.card_bg)
        right_header.pack(fill="x", padx=10, pady=(8, 4))
        tk.Label(right_header, text="📊 Orders:", bg=self.card_bg, fg=self.text_main, font=("Segoe UI", 9, "bold")).pack(side="left")

        # Live Search Entry in Main Table
        search_box = tk.Frame(right_header, bg=self.card_bg)
        search_box.pack(side="left", padx=(8, 0))

        tk.Label(search_box, text="🔍", bg=self.card_bg, fg="#94a3b8", font=("Segoe UI", 9)).pack(side="left", padx=(0, 2))
        self.search_entry = tk.Entry(
            search_box,
            textvariable=self.search_var,
            bg="#181825",
            fg="#f8fafc",
            insertbackground="#ffffff",
            relief="flat",
            font=("Segoe UI", 8),
            width=16
        )
        self.search_entry.pack(side="left", ipady=2)
        self.search_entry.bind("<KeyRelease>", lambda e: self._filter_main_table())

        search_btn = tk.Button(
            search_box,
            text="Search",
            command=self._filter_main_table,
            bg="#3b82f6",
            fg="white",
            activebackground="#2563eb",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=6,
            pady=1
        )
        search_btn.pack(side="left", padx=(2, 2))

        search_clear_btn = tk.Button(
            search_box,
            text="✕",
            command=self._clear_main_search,
            bg="#374151",
            fg="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=5,
            pady=1
        )
        search_clear_btn.pack(side="left")

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

        free_single_btn = tk.Button(
            right_header,
            text="☁️ Make Online",
            command=self._make_selected_online,
            bg="#0284c7",
            fg="white",
            activebackground="#0369a1",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=8,
            pady=2
        )
        free_single_btn.pack(side="right")

        tree_frame = tk.Frame(right_frame, bg="#181825")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=4)

        columns = ("order_id", "vendor", "status", "files", "size")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("order_id", text="Order ID")
        self.tree.heading("vendor", text="Vendor")
        self.tree.heading("status", text="Sync Status")
        self.tree.heading("files", text="Files")
        self.tree.heading("size", text="Disk Size")

        self.tree.column("order_id", width=110, anchor="w")
        self.tree.column("vendor", width=130, anchor="w")
        self.tree.column("status", width=140, anchor="center")
        self.tree.column("files", width=60, anchor="center")
        self.tree.column("size", width=85, anchor="center")

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", self._on_tree_double_click)
        self.tree.bind("<Button-3>", self._on_tree_right_click)

        # Context menu for right-click on table rows
        self.context_menu = tk.Menu(self, tearoff=0, bg="#252538", fg="white", activebackground="#3b82f6", activeforeground="white")
        self.context_menu.add_command(label="📂 Open in File Explorer", command=self._open_selected_folder)
        self.context_menu.add_command(label="☁️ Make this Order Online-Only", command=self._make_selected_online)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📥 Re-download (Make Local)", command=self._make_selected_local)

        # 5. Action Buttons & Controls Card
        action_card = tk.Frame(self, bg=self.card_bg, bd=1, relief="solid")
        action_card.pack(fill="x", padx=16, pady=4)

        btn_container = tk.Frame(action_card, bg=self.card_bg)
        btn_container.pack(fill="x", padx=12, pady=6)

        # Make Local Button
        self.btn_make_local = tk.Button(
            btn_container,
            text="📥 1. Make Local (Ready for QC)",
            command=self._start_make_local,
            bg=self.accent_green,
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            padx=12,
            pady=7
        )
        self.btn_make_local.pack(side="left", fill="x", expand=True, padx=(0, 4))

        # Free Up Space Button
        self.btn_make_online = tk.Button(
            btn_container,
            text="☁️ 2. Free Up Space (Make Online-Only)",
            command=self._start_make_online,
            bg="#0284c7",
            fg="white",
            activebackground="#0369a1",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            padx=12,
            pady=7
        )
        self.btn_make_online.pack(side="left", fill="x", expand=True, padx=(4, 8))

        # Pause / Resume Button
        self.btn_pause = tk.Button(
            btn_container,
            text="⏸️ Pause",
            command=self._toggle_pause,
            state="disabled",
            bg=self.accent_orange,
            fg="white",
            activebackground="#d97706",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=12,
            pady=7
        )
        self.btn_pause.pack(side="left", padx=(0, 4))

        # Stop Button
        self.btn_stop = tk.Button(
            btn_container,
            text="⏹️ Stop",
            command=self._request_stop,
            state="disabled",
            bg=self.accent_red,
            fg="white",
            activebackground="#dc2626",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=12,
            pady=7
        )
        self.btn_stop.pack(side="left")

        # 6. Dual Progress Indicators Card (Total & Single Order)
        progress_card = tk.Frame(self, bg=self.card_bg, bd=1, relief="solid")
        progress_card.pack(fill="x", padx=16, pady=4)

        # Total Progress Row
        total_p_row = tk.Frame(progress_card, bg=self.card_bg)
        total_p_row.pack(fill="x", padx=12, pady=(5, 2))

        self.total_lbl = tk.Label(
            total_p_row,
            text="Total Progress: 0% (0 / 0 Orders)",
            font=("Segoe UI", 9, "bold"),
            bg=self.card_bg,
            fg=self.text_main
        )
        self.total_lbl.pack(side="left")

        self.total_progress = ttk.Progressbar(progress_card, style="Total.Horizontal.TProgressbar", mode="determinate")
        self.total_progress.pack(fill="x", padx=12, pady=(0, 3))

        # Single Order Progress Row
        single_p_row = tk.Frame(progress_card, bg=self.card_bg)
        single_p_row.pack(fill="x", padx=12, pady=(2, 2))

        self.single_lbl = tk.Label(
            single_p_row,
            text="Single Order: 0% (0 / 0 Files)",
            font=("Segoe UI", 8),
            bg=self.card_bg,
            fg=self.text_muted
        )
        self.single_lbl.pack(side="left")

        self.single_progress = ttk.Progressbar(progress_card, style="Single.Horizontal.TProgressbar", mode="determinate")
        self.single_progress.pack(fill="x", padx=12, pady=(0, 5))

        # 7. Bottom Status Bar
        bottom_frame = tk.Frame(self, bg=self.bg_color)
        bottom_frame.pack(fill="x", padx=16, pady=(2, 6))

        self.status_var = tk.StringVar(value="Ready. Paste Order IDs and choose an action.")
        status_lbl = tk.Label(
            bottom_frame,
            textvariable=self.status_var,
            bg=self.bg_color,
            fg="#93c5fd",
            font=("Segoe UI", 9)
        )
        status_lbl.pack(side="left")

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
                    text=f"💾 Drive ({drive_letter}) Free Space: {free_str} / {total_str} ({free_pct}% free)"
                )

            count, total_bytes, size_str = get_tracked_local_storage_stats()
            if hasattr(self, "local_metric_lbl"):
                fg_color = "#f87171" if count > 0 else "#34d399"
                self.local_metric_lbl.config(
                    text=f"📦 Local QC Orders: {size_str} ({count} Orders on disk)",
                    fg=fg_color
                )
        except Exception:
            pass

    def _filter_main_table(self):
        """Filters the main QC table by Order ID or Vendor using search query."""
        query = self.search_var.get().strip().lower()
        self.tree.delete(*self.tree.get_children())
        for key, vals in self.table_items.items():
            order_id = str(vals[0]).lower()
            vendor = str(vals[1]).lower()
            status = str(vals[2]).lower()
            if not query or query in order_id or query in vendor or query in status:
                self.tree.insert("", "end", iid=key, values=vals)

    def _clear_main_search(self):
        self.search_var.set("")
        self._filter_main_table()

    def _browse_dropbox_path(self):
        chosen = filedialog.askdirectory(initialdir=self.path_var.get(), title="Select Dropbox Root Folder")
        if chosen:
            self.path_var.set(chosen)
            self.config_data["dropbox_path"] = chosen
            save_config(self.config_data)
            self._scan_vendors(keep_selection=False)
            self._update_storage_metrics()

    def _clear_input(self):
        self.input_text.delete("1.0", "end")
        self._update_order_count()

    def _paste_clipboard(self):
        try:
            clip = self.clipboard_get()
            self.input_text.insert("end", clip)
            self._update_order_count()
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

    def _clean_and_deduplicate(self):
        unique_orders, total_lines = self._parse_order_ids()
        if not unique_orders:
            messagebox.showinfo("Deduplicate", "No Order IDs found to clean.")
            return
        formatted = "\n".join([f"#{oid}" for oid in unique_orders])
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", formatted)
        self._update_order_count()
        self.status_var.set(f"Deduplicated! {total_lines} lines cleaned into {len(unique_orders)} unique orders.")

    def _on_tree_double_click(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self._open_selected_folder()

    def _open_selected_folder(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Order", "Please select an order from the list first.")
            return

        item = self.tree.item(selected[0])
        item_id = selected[0]
        
        info = self.resolved_orders.get(item_id)
        if not info:
            raw_id = str(item["values"][0]).strip()
            clean_id = normalize_order_id(raw_id)
            info = self.resolved_orders.get(clean_id) or self.resolved_orders.get(f"#{clean_id}")

        if info and info.get("path") and os.path.isdir(info["path"]):
            try:
                os.startfile(info["path"])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open folder:\n{e}")
        else:
            order_name = item["values"][0] if item.get("values") else "selected"
            messagebox.showwarning("Not Found", f"Folder path for order {order_name} is not available on disk.")

    def _on_tree_right_click(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.context_menu.post(event.x_root, event.y_root)

    def _make_selected_online(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Order", "Please select an order from the list first.")
            return

        item_id = selected[0]
        item = self.tree.item(item_id)
        info = self.resolved_orders.get(item_id)
        if not info:
            raw_id = str(item["values"][0]).strip()
            clean_id = normalize_order_id(raw_id)
            info = self.resolved_orders.get(clean_id) or self.resolved_orders.get(f"#{clean_id}")

        if not info or not info.get("path") or not os.path.isdir(info["path"]):
            order_name = item["values"][0] if item.get("values") else "selected"
            messagebox.showwarning("Not Found", f"Folder path for order {order_name} is not available on disk.")
            return

        folder_path = info["path"]
        order_id = info.get("order_id", item["values"][0])
        vendor = info.get("vendor", item["values"][1])
        file_count = info.get("files", item["values"][3])

        try:
            cmd = f'attrib -P +U "{folder_path}\\*.*" /s & attrib -P +U "{folder_path}" /d'
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            status_text = "☁️ Online-Only"
            new_vals = (f"#{order_id}", vendor, status_text, str(file_count), "0 B")
            self.tree.item(item_id, values=new_vals)
            self.table_items[item_id] = new_vals
            info["status"] = status_text
            mark_order_history(order_id, vendor, folder_path, "online", file_count, 0)
            self._update_leftover_badge()
            self._update_storage_metrics()
            self.status_var.set(f"☁️ Order #{order_id} ({vendor}) is now Online-Only. Disk space freed!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to free space:\n{e}")

    def _make_selected_local(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Order", "Please select an order from the list first.")
            return

        item_id = selected[0]
        item = self.tree.item(item_id)
        info = self.resolved_orders.get(item_id)
        if not info:
            raw_id = str(item["values"][0]).strip()
            clean_id = normalize_order_id(raw_id)
            info = self.resolved_orders.get(clean_id) or self.resolved_orders.get(f"#{clean_id}")

        if not info or not info.get("path") or not os.path.isdir(info["path"]):
            order_name = item["values"][0] if item.get("values") else "selected"
            messagebox.showwarning("Not Found", f"Folder path for order {order_name} is not available on disk.")
            return

        folder_path = info["path"]
        order_id = info.get("order_id", item["values"][0])
        vendor = info.get("vendor", item["values"][1])

        try:
            cmd = f'attrib +P -U "{folder_path}\\*.*" /s & attrib +P -U "{folder_path}" /d'
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            file_list, total_size = collect_folder_files(folder_path)
            workers = min(8, max(len(file_list), 1))
            with ThreadPoolExecutor(max_workers=workers) as executor:
                list(executor.map(_hydrate_single_file, file_list))

            status_text = "✅ Local (Ready)"
            new_vals = (f"#{order_id}", vendor, status_text, str(len(file_list)), format_bytes(total_size))
            self.tree.item(item_id, values=new_vals)
            self.table_items[item_id] = new_vals
            info["status"] = status_text
            mark_order_history(order_id, vendor, folder_path, "local", len(file_list), total_size)
            self._update_leftover_badge()
            self._update_storage_metrics()
            self.status_var.set(f"✅ Order #{order_id} ({vendor}) is now Local and ready for QC.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to make local:\n{e}")

    def _update_leftover_badge(self):
        try:
            tracked = get_tracked_local_orders()
            count = len(tracked)
            _, _, size_str = get_tracked_local_storage_stats()
            if hasattr(self, "leftover_btn"):
                if count > 0:
                    self.leftover_btn.config(
                        text=f"⚠️ Pending Local: {count} Orders ({size_str})",
                        bg="#f59e0b",
                        fg="#111827",
                        activebackground="#d97706",
                        activeforeground="#ffffff"
                    )
                else:
                    self.leftover_btn.config(
                        text="📜 History: 0 Local (Clean)",
                        bg="#252538",
                        fg="#10b981",
                        activebackground="#3b82f6",
                        activeforeground="#ffffff"
                    )
        except Exception:
            pass

    def _open_history_tracker(self):
        HistoryTrackerDialog(self)

    def _free_orders_in_background(self, order_items):
        for it in order_items:
            folder_path = it.get("path")
            oid = it.get("order_id")
            vendor = it.get("vendor", "-")
            files = it.get("files", 0)
            if folder_path and os.path.isdir(folder_path):
                try:
                    cmd = f'attrib -P +U "{folder_path}\\*.*" /s & attrib -P +U "{folder_path}" /d'
                    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass
            mark_order_history(oid, vendor, folder_path, "online", files, 0)
        self._update_leftover_badge()
        self._update_storage_metrics()

    def _set_controls_running(self, running):
        self.is_running = running
        self.is_paused = False
        self.stop_requested = False
        self.pause_event.set()

        state_actions = "disabled" if running else "normal"
        state_controls = "normal" if running else "disabled"

        self.btn_make_local.config(state=state_actions)
        self.btn_make_online.config(state=state_actions)
        if hasattr(self, "leftover_btn"):
            self.leftover_btn.config(state=state_actions)
        if hasattr(self, "vendor_btn"):
            self.vendor_btn.config(state=state_actions)
        self.btn_pause.config(state=state_controls, text="⏸️ Pause", bg=self.accent_orange)
        self.btn_stop.config(state=state_controls)

    def _toggle_pause(self):
        if not self.is_running:
            return

        if self.is_paused:
            self.is_paused = False
            self.pause_event.set()
            self.btn_pause.config(text="⏸️ Pause", bg=self.accent_orange)
            self.status_var.set("Resumed processing...")
        else:
            self.is_paused = True
            self.pause_event.clear()
            self.btn_pause.config(text="▶️ Resume", bg=self.accent_green)
            self.status_var.set("⏸️ Paused by user. Click Resume to continue.")

    def _request_stop(self):
        if not self.is_running:
            return

        confirm = messagebox.askyesno("Stop Process", "Are you sure you want to stop the current batch?")
        if confirm:
            self.stop_requested = True
            self.pause_event.set()
            self.status_var.set("Stopping process, please wait...")

    def _start_make_local(self):
        if self.is_running:
            return
        orders, _ = self._parse_order_ids()
        if not orders:
            messagebox.showwarning("No Orders", "Please paste or enter at least one Order ID.")
            return

        if hasattr(self, "selected_vendors") and not self.selected_vendors:
            messagebox.showwarning(
                "No Vendors Selected",
                "Please select at least one vendor from the 'Vendors' filter dropdown before proceeding."
            )
            return

        # Storage Shield: Prompt Guard for previous local orders
        tracked_local = get_tracked_local_orders()
        prev_local = [it for it in tracked_local if it.get("order_id") not in orders]

        if prev_local:
            count = len(prev_local)
            sample_ids = ", ".join([f"#{it.get('order_id')}" for it in prev_local[:5]])
            if count > 5:
                sample_ids += f" and {count - 5} more"

            msg = (
                f"⚠️ Storage Guard Alert:\n\n"
                f"You have {count} order(s) that you previously worked on still saved locally on disk:\n"
                f"({sample_ids})\n\n"
                "Would you like to make ONLY your previous orders Online-Only now to free up disk space?\n\n"
                "• Click [Yes] to free your previous orders and proceed with new batch.\n"
                "• Click [No] to keep them local and proceed.\n"
                "• Click [Cancel] to abort.\n\n"
                "(No other orders on Dropbox will be touched)."
            )
            ans = messagebox.askyesnocancel("Storage Guard", msg)
            if ans is None:
                return
            if ans is True:
                self.status_var.set(f"Freeing {count} previous local orders...")
                self._free_orders_in_background(prev_local)

        self._set_controls_running(True)
        threading.Thread(target=self._process_make_local, args=(orders,), daemon=True).start()

    def _process_make_local(self, orders):
        base_path = self.path_var.get()
        total_orders = len(orders)

        self.total_progress["maximum"] = total_orders
        self.total_progress["value"] = 0
        self.single_progress["maximum"] = 100
        self.single_progress["value"] = 0

        self.tree.delete(*self.tree.get_children())
        self.resolved_orders = {}
        self.table_items = {}

        selected_v = set(self.selected_vendors) if hasattr(self, "selected_vendors") and self.selected_vendors else None
        if selected_v and len(selected_v) < len(self.detected_vendors):
            self.status_var.set(f"Indexing {len(selected_v)} selected vendor(s) for ultra-fast lookup...")
        else:
            self.status_var.set("Indexing vendors for ultra-fast multi-vendor lookup...")
        vendor_index = build_vendor_index(base_path, selected_vendors=selected_v)

        success_count = 0
        not_found_count = 0

        for i, order_id in enumerate(orders):
            if self.stop_requested:
                break
            self.pause_event.wait()
            if self.stop_requested:
                break

            clean_id = normalize_order_id(order_id)

            pct = int((i / total_orders) * 100)
            self.total_lbl.config(text=f"Total Progress: {pct}% ({i} / {total_orders} Orders)")
            self.total_progress["value"] = i
            self.status_var.set(f"Processing #{order_id} ({i+1}/{total_orders})...")

            matches = vendor_index.get(clean_id, [])

            if not matches:
                status_text = "❌ Not Found"
                item_key = f"{order_id}_notfound"
                row_vals = (f"#{order_id}", "-", status_text, "0", "0 B")
                self.resolved_orders[item_key] = {"order_id": order_id, "vendor": "-", "path": None, "status": status_text, "files": 0, "size_bytes": 0}
                self.resolved_orders[order_id] = self.resolved_orders[item_key]
                self.table_items[item_key] = row_vals
                self.tree.insert("", "end", iid=item_key, values=row_vals)
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
                    total_files = len(file_list)

                    item_key = f"{order_id}_{vendor}"
                    row_vals = (f"#{order_id}", vendor, "⏳ Syncing...", str(total_files), format_bytes(total_size))
                    self.table_items[item_key] = row_vals
                    item_id = self.tree.insert("", "end", iid=item_key, values=row_vals)
                    self.tree.see(item_id)

                    try:
                        # 1. Combined Windows Pin attributes
                        cmd = f'attrib +P -U "{folder_path}\\*.*" /s & attrib +P -U "{folder_path}" /d'
                        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        # 2. Parallel Hydration with ThreadPoolExecutor (Smooth progress)
                        self.single_progress["maximum"] = max(total_files, 1)
                        self.single_progress["value"] = 0
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
                                    fp = futures[fut]
                                    fname = os.path.basename(fp)
                                    s_pct = int((completed_files / max(total_files, 1)) * 100)
                                    self.single_lbl.config(
                                        text=f"Current: #{order_id} ({vendor}) - {s_pct}% ({completed_files}/{total_files} files)"
                                    )
                                    self.single_progress["value"] = completed_files
                                    self.status_var.set(f"Hydrating ({completed_files}/{total_files}): {fname}")

                        status_text = "✅ Local (Ready)"
                        success_count += 1
                        mark_order_history(order_id, vendor, folder_path, "local", total_files, total_size)
                    except Exception as e:
                        status_text = f"⚠️ Error: {str(e)[:15]}"

                    final_vals = (f"#{order_id}", vendor, status_text, str(total_files), format_bytes(total_size))
                    self.table_items[item_key] = final_vals
                    self.tree.item(item_key, values=final_vals)
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

        # Completion or Stop state
        if self.stop_requested:
            self.status_var.set("⏹️ Process stopped by user.")
            messagebox.showwarning("Stopped", "Process was stopped by user.")
        else:
            self.total_lbl.config(text=f"Total Progress: 100% ({total_orders} / {total_orders} Orders)")
            self.total_progress["value"] = total_orders
            self.single_lbl.config(text="Single Order: 100% Complete")
            self.single_progress["value"] = 100
            self.status_var.set(f"Done! {success_count} folders ready locally, {not_found_count} not found.")
            messagebox.showinfo(
                "Batch Complete",
                f"Successfully prepared {success_count} vendor folders locally for QC!\n\n"
                f"Not found: {not_found_count} orders."
            )

        self._set_controls_running(False)
        self.after(0, self._update_leftover_badge)
        self.after(0, self._update_storage_metrics)

    def _start_make_online(self):
        if self.is_running:
            return
        orders, _ = self._parse_order_ids()
        if not orders:
            messagebox.showwarning("No Orders", "Please paste or enter at least one Order ID.")
            return

        if hasattr(self, "selected_vendors") and not self.selected_vendors:
            messagebox.showwarning(
                "No Vendors Selected",
                "Please select at least one vendor from the 'Vendors' filter dropdown before proceeding."
            )
            return

        confirm = messagebox.askyesno(
            "Free Up Space",
            f"Are you sure you want to make {len(orders)} orders Online-Only?\n"
            "This will revert the files to 0-byte cloud placeholders and free up disk space."
        )
        if not confirm:
            return

        self._set_controls_running(True)
        threading.Thread(target=self._process_make_online, args=(orders,), daemon=True).start()

    def _process_make_online(self, orders):
        base_path = self.path_var.get()
        total_orders = len(orders)

        self.total_progress["maximum"] = total_orders
        self.total_progress["value"] = 0
        self.single_progress["maximum"] = 100
        self.single_progress["value"] = 0

        self.tree.delete(*self.tree.get_children())
        self.resolved_orders = {}
        self.table_items = {}

        selected_v = set(self.selected_vendors) if hasattr(self, "selected_vendors") and self.selected_vendors else None
        if selected_v and len(selected_v) < len(self.detected_vendors):
            self.status_var.set(f"Indexing {len(selected_v)} selected vendor(s) for ultra-fast lookup...")
        else:
            self.status_var.set("Indexing vendors for ultra-fast multi-vendor lookup...")
        vendor_index = build_vendor_index(base_path, selected_vendors=selected_v)

        freed_count = 0
        not_found_count = 0

        for i, order_id in enumerate(orders):
            if self.stop_requested:
                break
            self.pause_event.wait()
            if self.stop_requested:
                break

            clean_id = normalize_order_id(order_id)

            pct = int((i / total_orders) * 100)
            self.total_lbl.config(text=f"Total Progress: {pct}% ({i} / {total_orders} Orders)")
            self.total_progress["value"] = i
            self.status_var.set(f"Freeing space for #{order_id} ({i+1}/{total_orders})...")

            matches = vendor_index.get(clean_id, [])

            if not matches:
                status_text = "❌ Not Found"
                item_key = f"{order_id}_notfound"
                row_vals = (f"#{order_id}", "-", status_text, "0", "0 B")
                self.resolved_orders[item_key] = {"order_id": order_id, "vendor": "-", "path": None, "status": status_text, "files": 0, "size_bytes": 0}
                self.resolved_orders[order_id] = self.resolved_orders[item_key]
                self.table_items[item_key] = row_vals
                self.tree.insert("", "end", iid=item_key, values=row_vals)
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
                    file_list, _ = collect_folder_files(folder_path)
                    total_files = len(file_list)

                    item_key = f"{order_id}_{vendor}"
                    row_vals = (f"#{order_id}", vendor, "⏳ Freeing...", str(total_files), "0 B")
                    self.table_items[item_key] = row_vals
                    item_id = self.tree.insert("", "end", iid=item_key, values=row_vals)
                    self.tree.see(item_id)

                    try:
                        cmd = f'attrib -P +U "{folder_path}\\*.*" /s & attrib -P +U "{folder_path}" /d'
                        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        self.single_lbl.config(text=f"Current Order: #{order_id} ({vendor}) - 100% Space Freed")
                        self.single_progress["value"] = 100

                        status_text = "☁️ Online-Only"
                        freed_count += 1
                        mark_order_history(order_id, vendor, folder_path, "online", total_files, 0)
                    except Exception as e:
                        status_text = f"⚠️ Error: {str(e)[:15]}"

                    final_vals = (f"#{order_id}", vendor, status_text, str(total_files), "0 B")
                    self.table_items[item_key] = final_vals
                    self.tree.item(item_key, values=final_vals)
                    order_info = {
                        "order_id": order_id,
                        "vendor": vendor,
                        "path": folder_path,
                        "status": status_text,
                        "files": total_files,
                        "size_bytes": 0
                    }
                    self.resolved_orders[item_key] = order_info
                    self.resolved_orders[order_id] = order_info
                    self.resolved_orders[f"#{order_id}"] = order_info

        if self.stop_requested:
            self.status_var.set("⏹️ Process stopped by user.")
            messagebox.showwarning("Stopped", "Process was stopped by user.")
        else:
            self.total_lbl.config(text=f"Total Progress: 100% ({total_orders} / {total_orders} Orders)")
            self.total_progress["value"] = total_orders
            self.single_lbl.config(text="Single Order: 100% Freed")
            self.single_progress["value"] = 100
            self.status_var.set(f"Done! {freed_count} folders reverted to Online-Only. Disk space recovered!")
            messagebox.showinfo(
                "Space Recovered",
                f"Successfully made {freed_count} vendor folders Online-Only!\n"
                "Hard drive space has been recovered."
            )

        self._set_controls_running(False)
        self.after(0, self._update_leftover_badge)
        self.after(0, self._update_storage_metrics)


if __name__ == "__main__":
    cleanup_old_executable()
    app = QCBatchLoaderApp()
    app.mainloop()
